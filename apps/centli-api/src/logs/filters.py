import logging
from contextvars import ContextVar

trace_id_ctx: ContextVar[str] = ContextVar("trace_id", default="-")


class TraceIdFilter(logging.Filter):
    """Attach trace_id to every record; respect an explicit one from `extra=`."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Attach trace id to the log message."""
        if not getattr(record, "trace_id", None):
            record.trace_id = trace_id_ctx.get()
        return True
