from src.ocr.extract import extract_document_text


def test_extract_document_text_reads_text_files(tmp_path):
    document_path = tmp_path / "notice.txt"
    document_path.write_text("Emergency variation approved for urgent works", encoding="utf-8")

    extracted = extract_document_text(str(document_path))

    assert "Emergency variation approved" in extracted


def test_extract_document_text_falls_back_to_printable_pdf_chunks(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 Procurement extension for urgent deviation notice")

    extracted = extract_document_text(str(pdf_path))

    assert "urgent deviation notice" in extracted