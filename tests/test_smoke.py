import base64

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"ok": True}

def test_normalize_encoding_to_utf8_bom():
    # Include a Latin-1 character to force non-ASCII handling
    raw = "name,city\nPaul,Montréal\n".encode("latin-1")

    files = {"file": ("test.csv", raw, "text/csv")}
    r = client.post("/normalize", files=files)
    assert r.status_code == 200

    data = r.json()
    assert "normalized_csv" in data
    assert data["normalized_csv"]["encoding"] == "utf-8-sig"

    out_bytes = base64.b64decode(data["normalized_csv"]["content_b64"])
    # UTF-8 BOM bytes
    assert out_bytes.startswith(b"\xef\xbb\xbf")
    # Should decode cleanly as utf-8-sig
    out_text = out_bytes.decode("utf-8-sig")
    assert "Montréal" in out_text
