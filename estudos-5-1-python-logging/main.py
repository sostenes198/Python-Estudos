# from log_context_manager import LogContextManager
import asyncio

from log_context_filter import LogContextFilter

#
# log_context = LogContextManager()
log_filter = LogContextFilter()

from types import SimpleNamespace
from api import handle_request
import logging.config


def filter_factory():
    return log_filter  # sempre retorna a MESMA instância


logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"ctx": {"()": filter_factory}},
    "formatters": {
        "default": {"format": "%(message)s | ctx=%(ctx)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["ctx"],
            "formatter": "default"
        }
    },
    "loggers": {
        # raiz da sua app
        "app": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        }
    }
})


async def main():
    await asyncio.gather(
        handle_request(SimpleNamespace(id=111, user_name="soso", customer_id="Jurema")),
        handle_request(SimpleNamespace(id=222, user_name="raquel", customer_id="Joaquim")),
        handle_request(SimpleNamespace(id=333, user_name="ed junior", customer_id="Jose")),
    )



if __name__ == '__main__':
    asyncio.run(main())
