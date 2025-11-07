import json, logging, time

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # leva extras simples como atributos
        for k, v in record.__dict__.items():
            if k in ("args", "msg", "exc_info", "exc_text", "stack_info", "stack_text"):
                continue
            if isinstance(v, (str, int, float, bool)) or v is None:
                payload.setdefault(k, v)
        return json.dumps(payload, ensure_ascii=False)
