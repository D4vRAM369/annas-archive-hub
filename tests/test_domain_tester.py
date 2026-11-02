"""Tests para classify() de core/domain_tester.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.domain_tester import classify


def test_annas_by_host():
    assert classify("https://annas-archive.gl/", "") == "annas_archive"

def test_annas_by_content_on_redirect():
    assert classify("https://otro.example/", "<html><title>Anna’s Archive</title></html>") == "annas_archive"

def test_libgen_not_annas():
    assert classify("https://libgen.la/", "<title>Library Genesis</title>") == "libgen"

def test_unknown_discarded():
    assert classify("https://titansearch.top/", "<html>buy now</html>") is None

def test_body_mention_is_not_enough():
    html = "<title>Library Genesis</title><a>Anna's Archive</a>"
    assert classify("https://libgen.la/", html) == "libgen"


def test_zlibrary_by_host():
    assert classify("https://z-lib.gd/", "") == "zlibrary"


def test_cid_v0_to_v1_known_pair():
    from core.ipfs_publisher import cid_v0_to_v1
    # par real (CID de Pinata -> link inbrowser.link verificado por el usuario)
    assert cid_v0_to_v1("QmYdbTjHZvZfDGY53ZmkPy89hYV1apP5KCWpKmoiPpv3Vh") == \
        "bafybeiey5qjbkc3km7zardukvolpsvvcerxpxw4sn5luhng4dbcoglpeaa"


def test_render_domains_groups_and_sorts():
    import run
    out = run.render_domains(
        {"annas_archive": ["https://annas-archive.pk/", "https://annas-archive.gl/"],
         "libgen": ["https://libgen.la/"], "zlibrary": ["https://welib.org/"]},
        ["z-lib.gl"], "es")
    assert out.index("annas-archive.gl") < out.index("annas-archive.pk") < out.index("libgen.la")
    assert "welib.org" in out and "z-lib.gl" in out and "Activo" in out


def test_render_domains_skips_empty_service():
    import run
    out = run.render_domains({"annas_archive": ["https://annas-archive.gl/"]}, ["z-lib.gl"], "en")
    assert "Libgen" not in out and "### Z-Library" not in out and "z-lib.gl" in out
