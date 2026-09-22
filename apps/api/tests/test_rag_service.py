import pytest
from app.services.rag_service import chunk_document_text, extract_keywords, clean_text


def test_extract_keywords():
    text = "The quick brown fox jumped over the lazy dog and required procurement authorization."
    keywords = extract_keywords(text)
    assert "procurement" in keywords
    assert "authorization" in keywords
    assert "the" not in keywords  # stopword check


def test_chunk_document_text():
    sample_policy = (
        "# General Procurement Policy\n"
        "All purchases above fifty thousand rupees require managerial sign-off.\n"
        "The purchase order must be approved before vendor commitments.\n\n"
        "# Approval Thresholds and Limits\n"
        "Department managers have authorization up to five lakh rupees.\n"
        "Vice presidents must approve any capital expenditure above twenty lakh rupees."
    )
    chunks = chunk_document_text(sample_policy, chunk_size_words=20)
    assert len(chunks) >= 2
    
    # Check section title preservation
    section_titles = [c["section_title"] for c in chunks]
    assert any("General Procurement Policy" in s for s in section_titles)
    assert any("Approval Thresholds and Limits" in s for s in section_titles)
    
    # Verify keywords and token count presence
    for chk in chunks:
        assert chk["token_count"] > 0
        assert "keywords" in chk
        assert isinstance(chk["keywords"], list)


def test_clean_text():
    raw = "  Hello   world \n\n this is \t clean. "
    cleaned = clean_text(raw)
    assert cleaned == "Hello world this is clean."
