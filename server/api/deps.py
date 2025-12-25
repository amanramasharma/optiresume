from fastapi import Request


def current_email(request: Request):
    return request.session.get("user_email")
