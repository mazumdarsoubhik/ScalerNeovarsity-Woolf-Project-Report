from contextvars import ContextVar

current_username: ContextVar[str] = ContextVar("current_username", default="System")
current_ip: ContextVar[str] = ContextVar("current_ip", default="localhost")