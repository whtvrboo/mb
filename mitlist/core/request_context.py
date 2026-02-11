"""Request context variables for trace_id, user_id, group_id."""

from contextvars import ContextVar

# Context variables for request-scoped data
trace_id_var: ContextVar[str | None] = ContextVar("trace_id", default=None)
user_id_var: ContextVar[int | None] = ContextVar("user_id", default=None)
group_id_var: ContextVar[int | None] = ContextVar("group_id", default=None)


def get_trace_id() -> str | None:
    """Get the current request trace ID."""
    return trace_id_var.get()


def set_trace_id(trace_id: str) -> None:
    """Set the current request trace ID."""
    trace_id_var.set(trace_id)


def get_user_id() -> int | None:
    """Get the current request user ID."""
    return user_id_var.get()


def set_user_id(user_id: int) -> None:
    """Set the current request user ID."""
    user_id_var.set(user_id)


def get_group_id() -> int | None:
    """Get the current request group ID."""
    return group_id_var.get()


def set_group_id(group_id: int) -> None:
    """Set the current request group ID."""
    group_id_var.set(group_id)
