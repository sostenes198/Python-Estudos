# service.py
import logging
from log_context_manager import LogContextManager

log = logging.getLogger("app").getChild("service")  # "app.service"


async def run_use_case(customer_id: str):
    # "child scope" (herda req_id/user da API e adiciona scope/hash)
    with LogContextManager.scoped_log(scope_name="service", prop1="prop_1", prop2="prop_2"):
        log.info("starting use case", extra={"customer_id": customer_id})
        # ... sua lógica
        log.info("finished use case")
