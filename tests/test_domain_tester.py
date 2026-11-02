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
