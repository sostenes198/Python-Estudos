import os
import requests
import sys
import shutil
import subprocess
import uuid
import google.generativeai as genai

# --- CONFIGURAÇÕES (HARDCODED) ---
GEMINI_API_KEY = ''
BB_TOKEN = ''

# Dados do Repositório
WORKSPACE = 'UNDEFINED'
REPO_SLUG = 'UNDEFINED'
PR_ID = 'UNDEFINED'

# Configuração de diretórios
BASE_CLONE_DIR = "CLONED_REPOS"

# Limite de segurança (1 Milhão de Tokens para Gemini 2.5 Flash)
SAFE_LIMIT = 950000
# SAFE_LIMIT = 300000

# 1. Pastas onde o código real vive (Foco da análise)
PRIORITY_ROOT_DIRS = {'src', 'test', 'tests', 'lib', 'app', 'internal', 'pkg', 'packages'}

# 2. Arquivos de configuração vitais na raiz (Contexto de arquitetura)
# O package.json é crucial para entender as dependências do projeto TS/JS
PRIORITY_ROOT_FILES = {'package.json'}

# --- EXTENSÕES PERMITIDAS (WHITELIST) ---
# Apenas código fonte relevante. Adicionei .tsx/.jsx para garantir compatibilidade se houver React.
ALLOWED_EXTENSIONS = {'.ts', '.js', '.tsx', '.jsx'}

# --- LISTA NEGRA DE DIRETÓRIOS (Para performance) ---
# Ignoramos a navegação nestas pastas para economizar tempo de disco
IGNORED_DIRS = {
    'node_modules', '.git', '.idea', '.vscode', '__pycache__', '.husky',
    'dist', 'build', 'coverage', 'venv', '.env', 'target', 'bin', 'obj',
    'terraform'
}

# Validação
if not GEMINI_API_KEY or not BB_TOKEN:
    print("❌ Erro: Chaves não configuradas.")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)


def get_headers():
    return {
        "Authorization": f"Bearer {BB_TOKEN}",
        "Accept": "application/json"
    }


def get_pr_source_branch():
    """Descobre qual é o nome do branch de origem do PR"""
    url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests/{PR_ID}"
    r = requests.get(url, headers=get_headers())
    if r.status_code != 200:
        print(f"❌ Erro ao buscar dados do PR: {r.text}")
        sys.exit(1)

    return r.json()['source']['branch']['name']


def get_changed_files_list():
    """Retorna o conjunto de arquivos alterados (diffstat)"""
    print("🔍 Buscando lista de arquivos alterados...")
    url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests/{PR_ID}/diffstat"

    changed = set()
    while url:
        r = requests.get(url, headers=get_headers())
        if r.status_code != 200: break
        data = r.json()
        for val in data.get('values', []):
            if val.get('status') != 'removed':
                changed.add(val['new']['path'])
        url = data.get('next')
    return changed


def clone_repo():
    """Clona o repositório e retorna o caminho da pasta"""
    branch_name = get_pr_source_branch()
    execution_id = str(uuid.uuid4())[:8]
    clone_dir = os.path.join(BASE_CLONE_DIR, f"{REPO_SLUG}_{execution_id}")

    print(f"🔄 Clonando branch '{branch_name}' em '{clone_dir}'...")
    os.makedirs(BASE_CLONE_DIR, exist_ok=True)
    git_url = f"https://x-token-auth:{BB_TOKEN}@bitbucket.org/{WORKSPACE}/{REPO_SLUG}.git"

    subprocess.check_call([
        "git", "clone", "--depth", "1", "--branch", branch_name,
        git_url, clone_dir
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("✅ Clone realizado com sucesso.")
    return clone_dir


def read_file_safe(path, display_path):
    """Lê arquivo com limite de tamanho para evitar travar a memória"""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if len(content) > 100000:  # 100kb limit
                content = content[:100000] + "\n...(truncado)..."
            return f"\n\n--- ARQUIVO: {display_path} ---\n{content}"
    except Exception:
        return ""


def build_project_context_focused(clone_dir):
    """
    ESTRATÉGIA 1 (OTIMIZADA):
    1. Lê arquivos vitais na raiz (package.json).
    2. Lê recursivamente APENAS as pastas prioritárias, filtrando por EXTENSÃO PERMITIDA.
    """
    print("📂 Estratégia 1: Montando contexto (Arquivos Raiz + Pastas Prioritárias)...")
    context = ""
    file_count = 0

    # 1. Busca arquivos prioritários na raiz (ex: package.json)
    root_files = os.listdir(clone_dir)
    found_root_files = [f for f in root_files if f in PRIORITY_ROOT_FILES]

    for f in found_root_files:
        full_path = os.path.join(clone_dir, f)
        context += read_file_safe(full_path, f)
        file_count += 1

    # 2. Busca pastas prioritárias
    found_dirs = [d for d in root_files if d in PRIORITY_ROOT_DIRS and os.path.isdir(os.path.join(clone_dir, d))]

    if not found_dirs and not found_root_files:
        print(f"   -> ERRO: Nenhuma pasta {PRIORITY_ROOT_DIRS} ou arquivo {PRIORITY_ROOT_FILES} encontrado.")
        return None

    print(f"   -> Lendo raiz: {found_root_files}")
    print(f"   -> Lendo pastas: {found_dirs}")

    # Itera explicitamente apenas nas pastas alvo
    for target_dir in found_dirs:
        target_path = os.path.join(clone_dir, target_dir)

        for root, dirs, files in os.walk(target_path):
            # Filtra diretórios ignorados (ex: node_modules dentro de src, se houver)
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

            for file in files:
                # --- FILTRO DE ALLOWLIST ---
                # Aceita apenas se terminar com .ts, .js, .tsx ou .jsx
                if not any(file.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                    continue

                full_path = os.path.join(root, file)
                display_path = os.path.relpath(full_path, clone_dir)

                context += read_file_safe(full_path, display_path)
                file_count += 1

    print(f"✅ Contexto Completo: {file_count} arquivos lidos.")
    return context


def build_smart_context(clone_dir):
    """
    ESTRATÉGIA 2 (FALLBACK): Lê apenas arquivos alterados e seus vizinhos.
    Também inclui o package.json para garantir contexto mínimo de deps.
    """
    print("⚠️ Estratégia 2 (Smart Context): Lendo apenas alterados e vizinhos...")
    changed_files = get_changed_files_list()
    changed_dirs = {os.path.dirname(p) for p in changed_files}

    context = ""
    file_count = 0

    # Força inclusão de arquivos de config na raiz mesmo no modo smart
    root_files = os.listdir(clone_dir)
    for f in root_files:
        if f in PRIORITY_ROOT_FILES:
            context += read_file_safe(os.path.join(clone_dir, f), f)
            file_count += 1

    for root, dirs, files in os.walk(clone_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for file in files:
            # --- FILTRO DE ALLOWLIST ---
            if not any(file.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                continue

            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, clone_dir)

            is_changed = rel_path in changed_files
            is_neighbor = os.path.dirname(rel_path) in changed_dirs

            if is_changed or is_neighbor:
                label = "ALTERADO" if is_changed else "VIZINHO"
                content = read_file_safe(full_path, rel_path)
                context += content.replace("--- ARQUIVO:", f"--- ARQUIVO ({label}):")
                file_count += 1

    print(f"✅ Smart Context: {file_count} arquivos lidos.")
    return context


def get_pr_diff():
    print(f"📥 Baixando DIFF do PR {PR_ID}...")
    url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests/{PR_ID}/diff"
    response = requests.get(url, headers=get_headers())
    if response.status_code != 200:
        print(f"❌ Erro diff: {response.text}")
        sys.exit(1)
    return response.text


def delete_previous_bot_comments():
    print("🧹 Verificando comentários antigos...")
    url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests/{PR_ID}/comments"
    r = requests.get(url, headers=get_headers())
    if r.status_code == 200:
        count = 0
        for comment in r.json().get('values', []):
            content = comment['content']['raw']
            if "**IA Auditor**" in content or "**BLOQUEIO DE IA Auditor**" in content:
                requests.delete(f"{url}/{comment['id']}", headers=get_headers())
                count += 1
        if count > 0: print(f"   - {count} comentários antigos removidos.")


def count_tokens_dry_run(model, prompt):
    """Apenas conta os tokens sem enviar"""
    try:
        count_result = model.count_tokens(prompt)
        return count_result.total_tokens
    except Exception as e:
        print(f"⚠️ Erro ao contar tokens: {e}")
        return 999999999  # Força falha se der erro


def run_analysis_pipeline():
    """
    Orquestrador Principal
    """
    # delete_previous_bot_comments()

    clone_dir = None
    strategy_used = "Desconhecida"

    try:
        clone_dir = clone_repo()
        diff_raw = get_pr_diff()

        model = genai.GenerativeModel('gemini-2.5-flash')

        # --- TENTATIVA 1: CONTEXTO COMPLETO ---
        project_context = build_project_context_focused(clone_dir)

        if project_context is None:
            return f"VEREDICTO: APROVADO COM RESSALVAS (ERRO: Nenhuma pasta {PRIORITY_ROOT_DIRS} ou arquivo {PRIORITY_ROOT_FILES} encontrado)."

        prompt = create_prompt(project_context, diff_raw)

        tokens = count_tokens_dry_run(model, prompt)
        print(f"📊 Tokens (Estratégia 1 - Full): {tokens}")

        strategy_used = "FullContext"

        if tokens > SAFE_LIMIT:
            print(f"⚠️ Limite excedido ({tokens} > {SAFE_LIMIT}). Tentando fallback...")

            # --- TENTATIVA 2: SMART CONTEXT ---
            project_context = build_smart_context(clone_dir)
            prompt = create_prompt(project_context, diff_raw)

            tokens = count_tokens_dry_run(model, prompt)
            print(f"📊 Tokens (Estratégia 2 - Smart): {tokens}")

            strategy_used = "SmartContext"

            if tokens > SAFE_LIMIT:
                print("❌ Contexto ainda muito grande mesmo com Smart Context.")
                return "VEREDICTO: APROVADO COM RESSALVAS (ERRO: Contexto excede limite máximo do modelo)"

        # Se chegou aqui, temos um prompt válido (Full ou Smart)
        print(f"🚀 Enviando para o Gemini usando {strategy_used}...")
        response = model.generate_content(prompt)

        # Log de uso final
        usage = response.usage_metadata
        print(f"📈 Consumo Final: {usage.total_token_count} tokens")

        # Adiciona a tag da estratégia usada no topo da resposta
        final_response = f"🔍 **Estratégia Utilizada:** {strategy_used}\n\n{response.text}"
        return final_response

    except Exception as e:
        print(f"💥 Erro no Pipeline: {e}")
        sys.exit(1)
    finally:
        if clone_dir and os.path.exists(clone_dir):
            try:
                shutil.rmtree(clone_dir)
                print("🧹 Pasta temporária removida.")
            except:
                pass


def create_prompt(project_context, diff):
    return f"""
    NÃO PRODUZA QUALQUER TEXTO DE INTRODUÇÃO, SAUDAÇÃO OU CONTEXTUALIZAÇÃO.
    NÃO EXPLIQUE O PAPEL. NÃO ELABORE PREFÁCIOS.
    NÃO RESUMA O PR. NÃO EXPLIQUE O QUE O CÓDIGO FAZ.
    INICIE A RESPOSTA DIRETAMENTE NO FORMATO EXIGIDO.
    
    Aja como um Arquiteto de Software Sênior, especialista em qualidade, arquitetura, segurança e aderência a padrões.
    
    CONTEXTO:
    Você tem acesso a:
    1) Todo o código-fonte do projeto (para entender padrões, modelos, utilitários e fluxos gerais).
    2) O DIFF do Pull Request (única parte a ser avaliada).
    
    Use o código completo apenas como referência contextual. Sua avaliação deve focar exclusivamente no DIFF.
    
    DIRETRIZES:
        1. NÃO GERE CÓDIGO. Apenas aponte o que falta.
        2. Oferaça soluções ou reescritas que julgar fazer sentido.
        3. Seja breve e direto (bullet points).
        4. A resposta deve começar diretamente pelos itens da análise, sem qualquer texto extra.
    
    CRITÉRIOS DE AVALIAÇÃO (ANALISAR *NO DIFF*):
        1. Segurança  
           - Riscos de injection, exposição indevida de dados, fluxos de autenticação/autorização fracos.  
        2. Bugs  
           - Lógicas inconsistentes, nulls inesperados, edge cases ignorados, loops desnecessários.  
        3. Testes  
           - A alteração possui testes adequados? Caso faltem, sugerir cenários essenciais.  
        4. Qualidade de Código  
           - Clareza, nomes adequados, complexidade ciclomática, duplicações, responsabilidades mal definidas.  
        5. Arquitetura  
           - A mudança segue padrões do restante do projeto?  
           - Viola princípios como coesão, separação de camadas, modularidade, SRP, LSP, etc.?
    
    SAÍDA OBRIGATÓRIA:
        - Lista clara, objetiva e detalhada dos problemas encontrados (caso existam), cada um com explicação.        
        - Informar métricas de tokens utilizados na análise.
        - Conclusão:
            • Se REPROVADO: VEREDICTO: REPROVADO como título. Explicar o motivo da reprovação.
            • Se APROVADO: VEREDICTO: REPROVADO como título. Sem explicação.
        - Finalizar **EXATAMENTE** com:  
          "VEREDICTO: APROVADO"  
          ou  
          "VEREDICTO: REPROVADO"
    
    --- CONTEXTO DO PROJETO (REFERÊNCIA) ---
    {project_context}
    
    --- DIFF DO PULL REQUEST (ALVO DA ANÁLISE) ---
    {diff}
    """


def post_comment_on_pr(comment, is_blocking):
    url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests/{PR_ID}/comments"
    title = "🚫 **BLOQUEIO DE IA Auditor**" if is_blocking else "✅ **IA Auditor**"

    payload = {"content": {"raw": f"{title}\n\n{comment}"}}
    requests.post(url, headers=get_headers(), json=payload)
    print("✅ Comentário postado.")


# --- Execução ---
if __name__ == "__main__":
    review_text = run_analysis_pipeline()

    if "VEREDICTO: REPROVADO" in review_text:
        print("❌ Resultado: REPROVADO.")
        post_comment_on_pr(review_text, is_blocking=True)
    else:
        print("✅ Resultado: APROVADO.")
        post_comment_on_pr(review_text, is_blocking=False)