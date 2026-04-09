"""Tests para core/domain_extractor.py"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.domain_extractor import extract_domains


def test_extracts_known_service_domain():
    text = "Use annas-archive.gl for books"
    result = extract_domains(text, require_context=False)
    assert "annas-archive.gl" in result


def test_extracts_url_with_lib_tld():
    text = "check out https://libgen.la for papers"
    result = extract_domains(text, require_context=False)
    assert any("libgen" in d for d in result)


def test_context_filter_blocks_unrelated_text():
    text = "visit example.gl for nothing"
    result = extract_domains(text, require_context=True)
    assert result == []


def test_context_filter_passes_with_keyword():
    text = "new anna archive mirror at annas-archive.pk"
    result = extract_domains(text, require_context=True)
    assert len(result) > 0


def test_no_duplicates():
    text = "annas-archive.gl and annas-archive.gl again"
    result = extract_domains(text, require_context=False)
    assert result.count("annas-archive.gl") == 1


def test_empty_string():
    result = extract_domains("", require_context=False)
    assert result == []


if __name__ == "__main__":
    passed = 0
    failed = 0
    tests = [
        test_extracts_known_service_domain,
        test_extracts_url_with_lib_tld,
        test_context_filter_blocks_unrelated_text,
        test_context_filter_passes_with_keyword,
        test_no_duplicates,
        test_empty_string,
    ]
    for test in tests:
        try:
            test()
            print(f"  ✅ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  ❌ {test.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
