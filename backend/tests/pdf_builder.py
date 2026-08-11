"""
Builds a minimal, spec-valid single-page PDF containing the given lines of
text — entirely by hand (no PyMuPDF/reportlab/etc needed to GENERATE test
fixtures, even though the app under test uses PyMuPDF/pdfplumber to READ
them). Useful so parsing-pipeline tests don't depend on any PDF-authoring
library being installed, only a PDF-reading one.
"""


def _escape_pdf_string(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_test_pdf(lines: list[str]) -> bytes:
    content_lines = ["BT", "/F1 11 Tf", "50 750 Td", "14 TL"]
    for i, line in enumerate(lines):
        escaped = _escape_pdf_string(line)
        if i > 0:
            content_lines.append("T*")
        content_lines.append(f"({escaped}) Tj")
    content_lines.append("ET")
    content_stream = "\n".join(content_lines).encode("latin-1", errors="replace")

    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 5 0 R >> >> "
        b"/MediaBox [0 0 612 792] /Contents 4 0 R >>",
        b"<< /Length %d >>\nstream\n" % len(content_stream) + content_stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    pdf = b"%PDF-1.4\n"
    offsets = [0]
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"

    xref_offset = len(pdf)
    pdf += f"xref\n0 {len(objects) + 1}\n".encode()
    pdf += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        pdf += f"{off:010d} 00000 n \n".encode()
    pdf += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF"
    ).encode()

    return pdf
