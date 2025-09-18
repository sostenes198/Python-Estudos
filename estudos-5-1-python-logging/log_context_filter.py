import json
import logging
from log_context_manager import LogContextManager


class LogContextFilter(logging.Filter):

    def __init__(self):
        super().__init__()

    def filter(self, record: logging.LogRecord) -> bool:
        ctx = LogContextManager.log_context.get() or {}

        # pega atributos que vieram no extra (só os que não são built-ins)
        extra_attrs = {
            k: v
            for k, v in record.__dict__.items()
            if k not in logging.LogRecord('', 0, '', 0, '', (), None).__dict__
        }

        # ⬇️ injeta CADA campo no LogRecord → NR vai enviar como attributes
        merged_ctx = {**ctx, **extra_attrs}

        # # injeta no record para ficar disponível no formatter
        # for k, v in merged_ctx.items():
        #     setattr(record, k, v)

        # (opcional) manter um campo "ctx" só para debug humano no console
        record.ctx = json.dumps(merged_ctx, ensure_ascii=False, separators=(",", ":"))

        return True
