import contextvars
import contextlib
import uuid


class LogContextManager:
    def __new__(cls, *args, **kwargs):
        raise TypeError('Static classes cannot be instantiated')

    log_context: contextvars.ContextVar = contextvars.ContextVar(__name__, default={})

    @classmethod
    @contextlib.contextmanager
    def scoped_log(cls, scope_name: str, **kwargs):
        scope_id = cls.__generate_hash()
        merged = {f"scope-{scope_name}-{scope_id}": scope_id}

        parent = cls.log_context.get()
        merged = {**merged, **parent, **kwargs}

        token = cls.log_context.set(merged)

        try:
            yield
        finally:
            cls.log_context.reset(token)

    @staticmethod
    def __generate_hash() -> str:
        return uuid.uuid4().hex[:8]
