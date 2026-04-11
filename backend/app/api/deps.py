from fastapi import Header


def get_user_id(x_user_id: str | None = Header(default=None)) -> str:
    # Keeps local development friction low; production auth middleware can replace this.
    return (x_user_id or "demo-user").strip()
