import httpx

from client.session import session

BASE_URL = "http://localhost:8000"


class ApiError(Exception):
    pass


def _auth_headers() -> dict:
    if session.token:
        return {"Authorization": f"Bearer {session.token}"}
    return {}


def post(path: str, json: dict, auth: bool = False) -> dict:
    headers = _auth_headers() if auth else {}
    try:
        resp = httpx.post(f"{BASE_URL}{path}", json=json, headers=headers, timeout=10)
    except httpx.ConnectError as exc:
        raise ApiError("Cannot reach the server. Is it running on localhost:8000?") from exc
    return _handle(resp)


def get(path: str, auth: bool = True) -> dict:
    headers = _auth_headers() if auth else {}
    try:
        resp = httpx.get(f"{BASE_URL}{path}", headers=headers, timeout=10)
    except httpx.ConnectError as exc:
        raise ApiError("Cannot reach the server. Is it running on localhost:8000?") from exc
    return _handle(resp)


def put(path: str, json: dict, auth: bool = True) -> dict:
    headers = _auth_headers() if auth else {}
    try:
        resp = httpx.put(f"{BASE_URL}{path}", json=json, headers=headers, timeout=10)
    except httpx.ConnectError as exc:
        raise ApiError("Cannot reach the server. Is it running on localhost:8000?") from exc
    return _handle(resp)


def _handle(resp: httpx.Response) -> dict:
    if resp.status_code >= 400:
        detail = resp.text
        if resp.content:
            try:
                detail = resp.json().get("detail", detail)
            except ValueError:
                pass
        raise ApiError(str(detail))
    return resp.json() if resp.content else {}
