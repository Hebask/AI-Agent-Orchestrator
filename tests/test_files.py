import io
from pypdf import PdfWriter


def _make_valid_pdf_bytes() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_upload_file(client):
    pdf_bytes = _make_valid_pdf_bytes()

    files = {
        "file": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf")
    }

    response = client.post("/files/upload", files=files)
    assert response.status_code == 200

    data = response.json()
    # Your UploadResponse schema shows these:
    assert "ok" in data
    assert data["ok"] is True
    assert "file_id" in data
    assert "filename" in data
    assert data["filename"] == "test.pdf"
    assert "chunks" in data
    assert isinstance(data["chunks"], int)
