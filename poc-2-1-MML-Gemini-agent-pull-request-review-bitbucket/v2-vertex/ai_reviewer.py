import os
import sys
import logging
import requests
import vertexai
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel, Tool, SafetySetting, GenerationConfig
from vertexai import rag

# ==============================================================================
# CONFIGURAÇÃO Das credenciais
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SA_PATH = os.path.join(BASE_DIR, "service_account.json")

# Carrega credenciais do JSON
credentials = service_account.Credentials.from_service_account_file(
    SA_PATH,
    scopes=[
        "https://www.googleapis.com/auth/cloud-platform"
    ]
)

# ==============================================================================
# CONFIGURAÇÃO DE LOGS & MONITORAMENTO
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("AuditBot")

# ==============================================================================
# AMBIENTE
# ==============================================================================
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = "us-west4"  # Região fixa para RAG

BB_TOKEN = os.getenv("BB_TOKEN")
WORKSPACE = 'govoll'
REPO_SLUG = 'pay-bff'
PR_ID = '130'

if not all([PROJECT_ID, LOCATION, REPO_SLUG, BB_TOKEN, WORKSPACE, PR_ID]):
    logger.error("❌ Faltam variáveis de ambiente obrigatórias.")
    sys.exit(1)

SAFE_LIMIT = 1_500_000
GEN_MODEL_NAME = os.getenv("GEN_MODEL_NAME", "gemini-2.5-pro")
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "60000"))

GEN_CONFIG = GenerationConfig(
    temperature=0.1,
    top_p=0.95,
    top_k=5,
    max_output_tokens=MAX_OUTPUT_TOKENS,
    response_mime_type="text/plain",
    presence_penalty=0.0,
    frequency_penalty=0.0,
)

SYSTEM_INSTRUCTION = """
DO NOT PRODUCE ANY INTRODUCTORY TEXT, GREETINGS, OR CONTEXTUALIZATION.
DO NOT EXPLAIN YOUR ROLE.
DO NOT ELABORATE PREFACES.

Act as a Senior Software Architect, specializing in quality, architecture, security, performance, testing, and standards.

IMPORTANT:
THE FINAL OUTPUT MUST BE WRITTEN IN PORTUGUESE (PT-BR).
ONLY THE ANALYSIS IS PERFORMED IN ENGLISH/CODE CONTEXT, BUT THE VERDICT AND FINDINGS MUST BE IN PORTUGUESE.

AVAILABLE CONTEXT:
    1. Project Source Code CHUNKS (reference, retrieved from Vector Store via RAG).
    2. Pull Request DIFF (sole target of analysis).

ABSOLUTE RULE ABOUT CONTEXT AVAILABILITY:
    • If the retrieved RAG context is insufficient to understand:
        – architecture, 
        – layering,
        – patterns used in the project,        
        – conventions,
        – or the implications of the changes in the DIFF,

      THEN:
        – DO NOT attempt to guess the architecture,
        – DO NOT assume non-existent conventions,
        – DO NOT fabricate patterns,
        – DO NOT block the PR.

      IN THIS CASE:
        → You MUST APPROVE the PR.
        → Output a clear message stating that the PR could not be fully analyzed due to insufficient context obtained from the project index.
        → Still summarize the DIFF in Portuguese, but without inventing architectural observations.

GLOBAL RESPONSIBILITIES:
    • Use the RAG SEARCH TOOL to:
        – Understand existing architecture and layering (domain, application, infra, UI, etc.).
        – Inspect existing patterns of logging, error handling, validation, DTOs, services, repositories, etc.
        – Understand how tests are structured (naming conventions, helpers, fixtures, mocks, etc.).
        – Confirm how similar logic is implemented elsewhere.
    • Compare the DIFF strictly against:
        – Existing standards and conventions visible in retrieved context.
        – Existing layering constraints.
        – Existing patterns for tests and quality.

    • NEVER invent conventions that do not appear in the retrieved context.
    • NEVER penalize the PR if the project context does not provide enough clues.
    • ALWAYS prefer alignment with patterns already observable in the project.

GENERAL REVIEW RULES:
    • DO NOT GENERATE CODE.
    • Evaluate EXCLUSIVELY the DIFF.
    • Project context is for reference only. Do NOT comment on files outside the DIFF unless the DIFF depends on them.
    • All findings must be objective, based in what is visible in the DIFF and supported by retrieved context.
    • For each identified problem:
        – Descrição (PT-BR)
        – Impacto (PT-BR)
        – Sugestão (PT-BR)

ARCHITECTURE & DESIGN PRIORITY CHECKLIST:
    • Does the new code respect module/layer boundaries?
    • Are business rules kept in the correct layer (domain/application)?
    • Are there cross-module references that violate project direction?
    • Is there duplication of logic visible elsewhere in the project (use RAG)?
    • Does naming and folder placement match existing conventions?
    • Are service, repository, DTO, controller and validator structures aligned with existing ones?

TEST QUALITY RULES:
    • Check if the DIFF adds or removes tests where needed.
    • Compare the test style with existing tests retrieved via RAG.
    • If a change affects behavior and tests were not updated:
        → Mark as a quality problem (unless project context is insufficient).
    • When changes affect important behaviors or flows but NO tests are added or updated:
        → Mark this as a problem under “Tests”.
        → Suggest explicitly what kind of tests should be added (unit, integration, e2e) and what scenarios should be covered.

EVALUATION CRITERIA (ONLY WHAT APPEARS IN THE DIFF):
    1. Security
    2. Bugs
    3. Tests
    4. Code Quality
    5. Architecture & Design
    6. Performance
    7. Code Duplication
    8. Complexity & Maintainability
    9. Readability & Conventions

MANDATORY OUTPUT FORMAT (IN PORTUGUESE):
    • Breve resumo do PR (baseado SOMENTE no DIFF).
    • Lista objetiva de problemas identificados.
        – Para cada problema: Descrição + Impacto + Sugestão.
    • Se não houver problemas → não invente críticas artificiais.

MANDATORY BEHAVIOR WHEN CONTEXT IS INSUFFICIENT:
    • If the model cannot determine project architecture, conventions, patterns or dependencies due to limited retrieved context:
        → Output: “A análise não pôde ser completada devido à falta de contexto suficiente no índice do projeto.”
        → VEREDICTO: APROVADO.
        → DO NOT invent issues or block the PR.

FINAL VERDICT (IN PORTUGUESE):
    • If any CRITICAL problem exists → VEREDICTO: REPROVADO (+ justificativa).
    • If only minor problems → VEREDICTO: APROVADO.
    • If no relevant problems → VEREDICTO: APROVADO.
    • If insufficient context → VEREDICTO: APROVADO (explicit reason).

"""

SAFETY_SETTINGS = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
    ),
]


# ==============================================================================
# LÓGICA RAG
# ==============================================================================
def find_corpus_dynamic():
    target = f"corpus-{REPO_SLUG}"
    logger.info(f"🔍 Buscando base de conhecimento: {target}")

    try:
        corpora = rag.list_corpora()
        for c in corpora:
            if c.display_name == target:
                logger.info(f"   -> Conectado ao Corpus: {c.name}")
                return c.name
    except Exception as e:
        logger.warning(f"⚠️ Erro ao listar corpora: {e}")

    logger.warning("⚠️ Corpus não encontrado. Rodando em modo 'Zero-Context'.")
    return None


# ==============================================================================
# BITBUCKET
# ==============================================================================
def get_diff():
    logger.info(f"📥 Baixando Diff PR #{PR_ID} ({REPO_SLUG})...")
    url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests/{PR_ID}/diff"
    r = requests.get(url, headers={"Authorization": f"Bearer {BB_TOKEN}"})
    if r.status_code != 200:
        raise Exception(f"Bitbucket API Error: {r.text}")
    return r.text


def post_comment(body, is_blocking, params):
    logger.info("💬 Postando feedback no Bitbucket...")
    url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests/{PR_ID}/comments"

    icon = "🚫 **BLOQUEIO DE IA**" if is_blocking else "✅ **IA Auditor**"

    # Adiciona rodapé com métricas de consumo (Opcional, bom para gestão)
    footer = (
        f"\n\n---\n"
        f"*Tokens: Input {params.get('input_tokens')} | Output {params.get('output_tokens')}*\n\n\n"
        f"Modelo: {params.get('model')}"
    )

    payload = {"content": {"raw": f"{icon}\n\n{body}{footer}"}}
    requests.post(url, headers={"Authorization": f"Bearer {BB_TOKEN}"}, json=payload)


# ==============================================================================
# MODELO & EXPERIMENTO
# ==============================================================================
def run_audit():
    # 1. Inicializa Vertex com Rastreamento de Experimento
    # Isso habilita os gráficos no console do GCP
    vertexai.init(
        project=PROJECT_ID,
        credentials=credentials,
        location=LOCATION,
    )

    # 2. Configura Ferramentas
    corpus_id = find_corpus_dynamic()
    tools = []
    if corpus_id:
        # Define quais recursos RAG esse modelo pode consultar
        rag_store = rag.VertexRagStore(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=corpus_id,
                    rag_file_ids=[]  # vazio = qualquer arquivo do corpus
                )
            ],
            rag_retrieval_config=rag.RagRetrievalConfig(
                top_k=5,  # quantidade de trechos retornados
                # você pode adicionar filtros aqui se quiser
            ),
        )

        rag_tool = Tool.from_retrieval(
            retrieval=rag.Retrieval(
                source=rag_store,
            )
        )

        tools.append(rag_tool)

    # 3. Define Modelo
    model = GenerativeModel(
        GEN_MODEL_NAME,
        system_instruction=[SYSTEM_INSTRUCTION],
        tools=tools
    )

    # 4. Prompt Engenheirado
    diff_text = get_diff()
    if not diff_text.strip():
        logger.info("Diff vazio. Encerrando.")
        return

    prompt = f"""
    Analyze the DIFF below.
    If there are calls to methods you don’t recognize, USE THE SEARCH TOOL to view their definition.

    --- DIFF ---
    {diff_text}
    """

    # 5. Safety Check (Tokens)
    token_check = model.count_tokens(prompt)
    logger.info(f"ℹ️  Estimativa de Tokens: {token_check.total_tokens}")

    if token_check.total_tokens > SAFE_LIMIT:
        logger.error("❌ Diff muito grande para processar.")
        post_comment("O PR é muito grande para análise automática (>1.5M tokens).", False, token_check)
        return

    # 6. Geração com Rastreamento
    logger.info("🚀 Enviando para Gemini (Reasoning)...")

    # Iniciando 'Run' do experimento para logar essa execução específica
    # with vertexai.start_run(f"pr-{REPO_SLUG}-{PR_ID}") as run:
    response = model.generate_content(
        prompt,
        generation_config=GEN_CONFIG,
        safety_settings=SAFETY_SETTINGS
    )

    # Loga parâmetros para auditoria futura
    params = {
        "repo": REPO_SLUG,
        "pr_id": PR_ID,
        "model": GEN_MODEL_NAME,
        "input_tokens": response.usage_metadata.prompt_token_count,
        "output_tokens": response.usage_metadata.candidates_token_count
    }
        # run.log_params(params)

    logger.info("✅ Análise concluída.")
    logger.info(f"📊 Consumo: {response.usage_metadata}")

    # 7. Postagem
    verdict_text = response.text
    is_fail = "VEREDICTO: REPROVADO" in verdict_text.upper()

    post_comment(verdict_text, is_fail, params)


if __name__ == "__main__":
    try:
        run_audit()
    except Exception as e:
        logger.critical(f"💥 Erro Fatal: {e}", exc_info=True)
        sys.exit(1)
