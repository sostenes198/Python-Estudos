import os
import shutil
import subprocess
import uuid
import time
import logging
import json
from datetime import timezone

from google.cloud import storage
import vertexai
from google.oauth2 import service_account
from vertexai.preview import rag
from vertexai.rag.utils.resources import TransformationConfig
from google.api_core.exceptions import PreconditionFailed, NotFound

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
# CONFIGURAÇÃO DE LOGS (PADRÃO PRODUÇÃO)
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("IndexerBot")

# ==============================================================================
# VARIÁVEIS DE AMBIENTE
# ==============================================================================
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = "us-west4"  # Região fixa para RAG
BUCKET_NAME = os.getenv("GCP_BUCKET_NAME", "estudos-codebase-source")

BB_TOKEN = os.getenv("BB_TOKEN")
WORKSPACE = 'govoll'
REPO_SLUG = 'pay-bff'
PR_ID = '126'

# Validação Crítica
if not all([PROJECT_ID, REPO_SLUG, BB_TOKEN, WORKSPACE, PR_ID]):
    logger.error("❌ Variáveis GCP_PROJECT_ID e REPO_SLUG, BB_TOKEN, WORKSPACE, PR_ID são obrigatórias.")
    exit(1)

CORPUS_DISPLAY_NAME = f"corpus-{REPO_SLUG}"
SOURCE_PATH = "./"

# Directory Configuration
BASE_CLONE_DIR = SOURCE_PATH + "CLONED_REPOS"

# Filtros
ALLOWED_EXTENSIONS = {
    '.ts', '.js', '.tsx', '.jsx',
    '.go', '.py', '.java', '.json',
    '.md', '.yml', '.yaml', '.cs'
}

IGNORED_DIRS = {
    '.git', 'node_modules', 'dist', 'build', 'coverage', 'venv',
    '__pycache__', '.idea', '.vscode', '.husky', 'bin',
    'obj', 'terraform', 'scripts'
}

# Extensões que já são "nativas" para o RAG (não precisam ser renomeadas)
NATIVE_EXTENSIONS = {'.txt', '.md', '.html', '.htm', '.xml', '.pdf'}

# Lock config
LOCK_BLOB_NAME = f"tmp/rag-lock/{REPO_SLUG}.lock"
LOCK_MAX_AGE_SECONDS = 20 * 60   # 20 minutos
LOCK_POLL_INTERVAL = 5           # segundos entre tentativas
LOCK_MAX_WAIT_SECONDS = 20 * 60  # máximo que um processo espera pelo lock


# ==============================================================================
# FUNÇÕES DE LOCK VIA GCS
# ==============================================================================

def get_storage_client() -> storage.Client:
    return storage.Client(project=PROJECT_ID, credentials=credentials)


def acquire_lock(bucket_name: str) -> str:
    """
    Tenta adquirir um lock no GCS.
    - Cria um blob LOCK_BLOB_NAME se não existir (if_generation_match=0).
    - Se já existir:
        - Se tiver menos de LOCK_MAX_AGE_SECONDS -> espera.
        - Se tiver mais -> considera stale, tenta remover e assumir.
    - Tempo máximo de espera: LOCK_MAX_WAIT_SECONDS.

    Retorna o execution_id do lock adquirido (string).
    Lança TimeoutError se não conseguir em tempo hábil.
    """
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    execution_id = uuid.uuid4().hex[:8]
    start_time = time.time()

    logger.info(f"🔐 Tentando adquirir lock para execução {execution_id}...")

    while True:
        blob = bucket.blob(LOCK_BLOB_NAME)

        lock_payload = {
            "execution_id": execution_id,
            "created_at": time.time(),
        }

        try:
            # Tenta criar o lock *somente se não existir ainda*
            blob.upload_from_string(
                data=json.dumps(lock_payload),
                content_type="application/json",
                if_generation_match=0  # Só cria se o objeto NÃO existir
            )
            logger.info(f"✅ Lock adquirido com sucesso. execution_id={execution_id}")
            return execution_id

        except PreconditionFailed:
            # Já existe um lock. Vamos ver se está fresco ou stale.
            try:
                blob.reload()
            except NotFound:
                # Foi removido entre o erro e o reload → tenta de novo
                continue

            if not blob.time_created:
                # Sem time_created por algum motivo estranho → assume que é velho
                logger.warning("⚠️ Lock sem time_created. Tentando assumir o lock...")
                try:
                    blob.delete(if_generation_match=blob.generation)
                except Exception:
                    # Se falhar, alguém mexeu. Só espera e tenta de novo.
                    time.sleep(LOCK_POLL_INTERVAL)
                    continue
                # Na próxima iteração vamos tentar criar de novo.
                continue

            lock_age = time.time() - blob.time_created.replace(tzinfo=timezone.utc).timestamp()

            if lock_age > LOCK_MAX_AGE_SECONDS:
                logger.warning(
                    f"⚠️ Lock encontrado, mas está stale (idade={lock_age:.1f}s). "
                    f"Tentando assumir o lock..."
                )
                try:
                    # Tenta remover o lock stale com controle de geração
                    blob.delete(if_generation_match=blob.generation)
                except PreconditionFailed:
                    # Outro processo limpou/assumiu primeiro
                    logger.info("Outro processo atualizou o lock enquanto tentávamos assumir. Re-tentando...")
                    time.sleep(LOCK_POLL_INTERVAL)
                    continue
                except NotFound:
                    # Já removeram, beleza
                    pass
                # Agora voltamos ao loop e tentamos criar o lock de novo
                continue

            # Lock ativo e recente → esperar
            waited = time.time() - start_time
            if waited > LOCK_MAX_WAIT_SECONDS:
                raise TimeoutError(
                    f"Não foi possível adquirir o lock em {LOCK_MAX_WAIT_SECONDS}s. "
                    f"Outro processo pode estar travado."
                )

            logger.info(
                f"🔒 Lock já está em uso (idade={lock_age:.1f}s). "
                f"Aguardando {LOCK_POLL_INTERVAL}s..."
            )
            time.sleep(LOCK_POLL_INTERVAL)


def release_lock(bucket_name: str, execution_id: str):
    """
    Libera o lock no GCS *somente se* o execution_id for o dono.
    Isso evita que uma outra execução apague o lock de alguém.
    """
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(LOCK_BLOB_NAME)

    try:
        data = blob.download_as_text()
    except NotFound:
        logger.info("🔓 Lock já não existe mais no GCS.")
        return

    try:
        payload = json.loads(data)
    except json.JSONDecodeError:
        payload = {}

    owner_id = payload.get("execution_id")

    if owner_id != execution_id:
        logger.warning(
            f"⚠️ Tentativa de liberar lock com execution_id={execution_id}, "
            f"mas o dono atual é {owner_id}. Não será removido."
        )
        return

    try:
        blob.delete()
        logger.info(f"🔓 Lock liberado com sucesso. execution_id={execution_id}")
    except NotFound:
        logger.info("🔓 Lock já não existe mais no momento da liberação.")


# ==============================================================================
# PIPELINE
# ==============================================================================

def clone_repo():
    execution_id = str(uuid.uuid4())[:8]
    clone_dir = os.path.join(BASE_CLONE_DIR, f"{REPO_SLUG}_{execution_id}")

    logger.info(f"🔄 Cloning repo into '{clone_dir}'...")
    os.makedirs(BASE_CLONE_DIR, exist_ok=True)
    git_url = f"https://x-token-auth:{BB_TOKEN}@bitbucket.org/{WORKSPACE}/{REPO_SLUG}.git"

    subprocess.check_call(
        [
            "git", "clone", "--depth", "1",
            git_url,
            clone_dir
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return clone_dir


def init_vertex():
    """Inicializa conexão e define o bucket de staging se necessário"""
    vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)
    logger.info(f"🔧 Vertex AI conectado: {PROJECT_ID} ({LOCATION})")


def upload_repo_to_gcs(source_dir: str, bucket_name: str) -> str:
    """
    Envia todos os arquivos permitidos do repositório para o GCS,
    convertendo código para .txt para o RAG conseguir ingerir.

    Retorna o prefixo GCS no formato:
        gs://{bucket_name}/{base_prefix}
    """
    storage_client = get_storage_client()
    bucket = storage_client.bucket(bucket_name)

    base_prefix = f"tmp/rag/{REPO_SLUG}"

    logger.info(f"☁️  Enviando arquivos individuais para Storage: gs://{bucket_name}/{base_prefix}")

    file_count = 0

    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for file in files:
            _, ext = os.path.splitext(file)
            if ext in ALLOWED_EXTENSIONS or ext in NATIVE_EXTENSIONS:
                local_path = os.path.join(root, file)
                rel_path = os.path.relpath(local_path, source_dir)

                if ext not in NATIVE_EXTENSIONS:
                    rel_path = rel_path + ".txt"

                gcs_blob_path = f"{base_prefix}/{rel_path}"

                blob = bucket.blob(gcs_blob_path)
                blob.upload_from_filename(local_path)

                file_count += 1

    logger.info(f"   -> {file_count} arquivos enviados individualmente para o GCS.")

    if file_count == 0:
        logger.warning("⚠️ Nenhum arquivo elegível foi enviado para o GCS. Verifique os filtros de extensão.")

    return f"gs://{bucket_name}/{base_prefix}"


def delete_gcs_prefix(bucket_name: str, gcs_prefix_uri: str):
    if not gcs_prefix_uri.startswith("gs://"):
        logger.warning(f"Prefixo GCS inválido: {gcs_prefix_uri}")
        return

    _, rest = gcs_prefix_uri.split("gs://", 1)
    bucket_name_from_uri, prefix = rest.split("/", 1)

    if bucket_name_from_uri != bucket_name:
        logger.warning(
            f"Bucket do prefixo ({bucket_name_from_uri}) "
            f"não bate com BUCKET_NAME ({bucket_name}). Limpando mesmo assim."
        )

    logger.info(f"🧽 Limpando prefixo temporário no GCS: gs://{bucket_name_from_uri}/{prefix}")

    storage_client = get_storage_client()
    bucket = storage_client.bucket(bucket_name_from_uri)

    blobs = list(bucket.list_blobs(prefix=prefix))

    if not blobs:
        logger.info("🧽 Nenhum blob encontrado para remoção.")
        return

    logger.info(f"🧽 Removendo {len(blobs)} blobs em gs://{bucket_name_from_uri}/{prefix} ...")

    bucket.delete_blobs(blobs)  # a lib faz o loop internamente

    logger.info(f"🧽  -> arquivos removidos do GCS.")


def reset_corpus():
    """
    ESTRATÉGIA 'NUKE':
    Procura o Corpus antigo e o deleta inteiro.
    Depois cria um novo zerado.
    Evita erro de cota (ResourceExhausted) ao deletar arquivos um por um.
    """
    logger.info(f"☢️  Verificando existência do Corpus: '{CORPUS_DISPLAY_NAME}'")

    # 1. Procura e Deleta
    corpora = rag.list_corpora()
    for c in corpora:
        if c.display_name == CORPUS_DISPLAY_NAME:
            logger.info(f"   -> Encontrado (ID: {c.name}). Deletando inteiro...")
            try:
                # force=True garante que delete mesmo se tiver arquivos dentro
                rag.delete_corpus(name=c.name)
                logger.info("   -> Corpus deletado com sucesso.")
            except Exception as e:
                logger.error(f"   -> Erro ao deletar corpus: {e}")
                # Se falhar a deleção, tentamos seguir, mas vai dar erro na criação se o nome for duplicado
            break  # Só existe um com esse nome, podemos sair

    # 2. Cria Novo
    logger.info("✨ Criando novo Corpus limpo...")
    # DICA: Adicionando description para auditoria futura
    new_corpus = rag.create_corpus(
        display_name=CORPUS_DISPLAY_NAME,
        description=f"Índice para o repo {REPO_SLUG}. Criado automaticamente"
    )
    logger.info(f"   -> Corpus criado: {new_corpus.name}")
    return new_corpus


def update_index_full_context(corpus_name: str, gcs_prefix_uri: str):
    logger.info("🚀 Iniciando Importação (Modo Full-Context)...")

    transformation_config = TransformationConfig(
        chunking_config=rag.ChunkingConfig(
            chunk_size=2048,
            chunk_overlap=200
        )
    )

    response = rag.import_files(
        corpus_name=corpus_name,
        paths=[gcs_prefix_uri],
        transformation_config=transformation_config,
        max_embedding_requests_per_min=900
    )

    logger.info(
        f"✅ IMPORT CONCLUÍDO: imported={response.imported_rag_files_count} | "
        f"skipped={response.skipped_rag_files_count}"
    )

    if response.skipped_rag_files_count > 0:
        logger.warning("⚠️ Alguns arquivos foram ignorados pelo RAG. Verifique formatos e logs de detalhe.")


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
if __name__ == "__main__":
    start_time = time.time()
    clone_dir = None
    gcs_prefix_uri = None
    execution_id = None

    try:
        # 0. Tenta adquirir lock global
        execution_id = acquire_lock(BUCKET_NAME)

        init_vertex()

        # 1. Clonar repositório
        clone_dir = clone_repo()

        # 2. Upload da codebase completa (sem ZIP) para GCS (temporário)
        gcs_prefix_uri = upload_repo_to_gcs(clone_dir, BUCKET_NAME)

        # 3. Gestão do RAG
        corpus = reset_corpus()

        # 4. Atualização do índice usando o prefixo no GCS
        update_index_full_context(corpus.name, gcs_prefix_uri)

    except TimeoutError as e:
        logger.error(f"❌ Não foi possível adquirir o lock: {e}")
        exit(1)
    except Exception as e:
        logger.critical(f"❌ FALHA FATAL: {e}", exc_info=True)
        exit(1)
    finally:
        # Limpa o clone local
        if clone_dir and os.path.exists(clone_dir):
            try:
                shutil.rmtree(clone_dir)
            except Exception:
                pass

        # Limpa o prefixo temporário no GCS depois da importação
        try:
            if gcs_prefix_uri:
                delete_gcs_prefix(BUCKET_NAME, gcs_prefix_uri)
        except Exception as e:
            logger.warning(f"⚠️ Falha ao limpar prefixo temporário no GCS: {e}")

        # Libera o lock, se foi adquirido
        if execution_id:
            try:
                release_lock(BUCKET_NAME, execution_id)
            except Exception as e:
                logger.warning(f"⚠️ Falha ao liberar lock no GCS: {e}")

        logger.info(f"⏱️ Tempo Total: {round(time.time() - start_time, 2)}s")
