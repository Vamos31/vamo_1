from fastapi.testclient import TestClient

from app.core.config import settings
from main import app

client = TestClient(app)


def test_unknown_path_returns_common_error_format():
    res = client.get("/no-such-path")
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "NOT_FOUND"


def test_write_request_from_other_origin_is_rejected():
    res = client.post("/teams", headers={"Origin": "http://evil.example"})
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "CSRF_ORIGIN_MISMATCH"


def test_write_request_from_frontend_origin_passes_origin_check():
    # ルートがまだないので 404 / 405 になるが、403 (Origin 不一致) ではないことを確認する
    res = client.post("/teams", headers={"Origin": settings.frontend_origin})
    assert res.status_code != 403
