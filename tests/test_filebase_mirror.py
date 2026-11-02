"""Tests para la copia de respaldo en Filebase (sin red: se simula `http`)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import ipfs_publisher as ip


class R:
    def __init__(self, code=200, data=None): self.status_code, self._d, self.text = code, data or {}, ""
    def json(self): return self._d


def make(monkeypatch, token="tok", keep=2, existing=None, results=None):
    calls = []
    def get(url, **kw):
        calls.append(("get", kw.get("params")))
        if kw["params"].get("cid"):
            return R(200, {"count": 1 if existing else 0})
        return R(200, {"results": results or []})
    monkeypatch.setattr(ip.http, "get", get)
    monkeypatch.setattr(ip.http, "post", lambda url, **kw: calls.append(("post", kw["json"])) or R(202))
    monkeypatch.setattr(ip.http, "delete", lambda url, **kw: calls.append(("delete", url)) or R(202))
    monkeypatch.setenv("FILEBASE_TOKEN", token)
    p = ip.IPFSPublisher(); p.keep_last = keep
    return p, calls


def test_no_token_skips(monkeypatch):
    p, calls = make(monkeypatch, token="")
    assert p._mirror_to_filebase("Qmabc") is False and calls == []


def test_pins_new_cid(monkeypatch):
    p, calls = make(monkeypatch)
    assert p._mirror_to_filebase("QmNEW12345") is True
    assert any(c[0] == "post" and c[1]["cid"] == "QmNEW12345" for c in calls)


def test_skips_duplicate(monkeypatch):
    p, calls = make(monkeypatch, existing=True)
    p._mirror_to_filebase("Qmdup")
    assert not any(c[0] == "post" for c in calls)


def test_rotation_keeps_newest(monkeypatch):
    rows = [{"requestid": f"r{i}", "created": f"2026-11-0{i}", "pin": {"cid": f"c{i}"}} for i in range(1, 6)]
    p, calls = make(monkeypatch, keep=2, results=rows)
    p._rotate_filebase()
    deleted = [c[1].rsplit("/", 1)[1] for c in calls if c[0] == "delete"]
    assert sorted(deleted) == ["r1", "r2", "r3"]   # quedan r5 y r4


def test_error_does_not_raise(monkeypatch):
    p, _ = make(monkeypatch)
    monkeypatch.setattr(ip.http, "get", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("red caída")))
    assert p._mirror_to_filebase("Qmx") is False
