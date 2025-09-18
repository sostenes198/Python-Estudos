# api.py
import logging
from log_context_manager import LogContextManager
from log_context_filter import LogContextFilter

log = logging.getLogger("app").getChild("api")  # "app.api"


async def handle_request(req):
    # nível "raiz" do request: id e usuário
    with LogContextManager.scoped_log(scope_name="api", req_id=req.id, user=req.user_name):
        log.info("request received", stacklevel=2)  # stacklevel p/ origem correta (3.8+)
        from service import run_use_case
        await run_use_case(customer_id=req.customer_id)

        log.info("finished request received")
