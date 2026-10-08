import math
from pathlib import Path
from typing import Optional, Dict, Any
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors


class CertificateGenerator:
    """Generates professional, high-resolution vector PDF certificates

    using ReportLab.
    """

    WIDTH, HEIGHT = landscape(A4)  # 841.89 x 595.27 points

    # Curated color palette
    NAVY_DEEP = colors.HexColor("#0F172A")
    NAVY_PRIMARY = colors.HexColor("#1E3A8A")
    GOLD_PRIMARY = colors.HexColor("#D97706")
    GOLD_LIGHT = colors.HexColor("#FDE68A")
    SLATE_MUTED = colors.HexColor("#64748B")
    BG_CREAM = colors.HexColor("#FAFAFA")
    LINE_BORDER = colors.HexColor("#CBD5E1")

    @classmethod
    def generate_pdf(
        cls,
        output_path: Path,
        recipient_name: str,
        event_name: str,
        issuer_name: str,
        issue_date: str,
        certificate_code: str,
        template_title: str = "Certificate of Completion",
        custom_attributes: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Renders the certificate and writes it to output_path.

        Returns the resolved Path.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        c = canvas.Canvas(str(output_path), pagesize=landscape(A4))
        w, h = cls.WIDTH, cls.HEIGHT

        # 1. Background Fill
        c.setFillColor(cls.BG_CREAM)
        c.rect(0, 0, w, h, fill=1, stroke=0)

        # 2. Outer Decorative Borders
        cls._draw_borders_and_accents(c, w, h)

        # 3. Top Decorative Emblem / Rosette
        cls._draw_emblem(c, w / 2, h - 85)

        # 4. Certificate Title
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(cls.NAVY_DEEP)
        c.drawCentredString(w / 2, h - 135, template_title.upper())

        # 5. Subtitle
        c.setFont("Helvetica", 11)
        c.setFillColor(cls.SLATE_MUTED)
        c.drawCentredString(w / 2, h - 165, "THIS IS PROUDLY PRESENTED TO")

        # 6. Recipient Name
        c.setFont("Helvetica-Bold", 30)
        c.setFillColor(cls.NAVY_PRIMARY)
        c.drawCentredString(w / 2, h - 215, recipient_name)

        # Underline accent for recipient name
        name_width = min(c.stringWidth(recipient_name, "Helvetica-Bold", 30) + 40, 500)
        c.setStrokeColor(cls.GOLD_PRIMARY)
        c.setLineWidth(1.5)
        c.line((w - name_width) / 2, h - 225, (w + name_width) / 2, h - 225)

        # 7. Presentation context
        c.setFont("Helvetica", 11)
        c.setFillColor(cls.SLATE_MUTED)
        c.drawCentredString(w / 2, h - 260, "for successfully completing and fulfilling all requirements of")

        # 8. Event / Course Name
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(cls.NAVY_DEEP)
        c.drawCentredString(w / 2, h - 295, f'"{event_name}"')

        # 9. Custom Attributes (e.g. Grade, Honors, Hours) if provided
        if custom_attributes:
            attr_strings = [f"{k.capitalize()}: {v}" for k, v in custom_attributes.items()]
            attr_text = " • ".join(attr_strings)
            c.setFont("Helvetica-Oblique", 10)
            c.setFillColor(cls.SLATE_MUTED)
            c.drawCentredString(w / 2, h - 325, attr_text)

        # 10. Bottom Sections: Left (Metadata), Center (Seal), Right (Signature)
        cls._draw_footer(c, w, h, issue_date, certificate_code, issuer_name)

        # Finalize and save
        c.showPage()
        c.save()
        return output_path

    @classmethod
    def _draw_borders_and_accents(cls, c: canvas.Canvas, w: float, h: float):
        """Draws multi-layered borders and corner motifs."""
        # Outer heavy border
        c.setStrokeColor(cls.NAVY_DEEP)
        c.setLineWidth(4)
        c.rect(24, 24, w - 48, h - 48, fill=0, stroke=1)

        # Inner gold border
        c.setStrokeColor(cls.GOLD_PRIMARY)
        c.setLineWidth(1.5)
        c.rect(32, 32, w - 64, h - 64, fill=0, stroke=1)

        # Delicate thin inner border
        c.setStrokeColor(cls.LINE_BORDER)
        c.setLineWidth(0.5)
        c.rect(36, 36, w - 72, h - 72, fill=0, stroke=1)

        # Corner geometric diamond accents
        corners = [(32, 32), (w - 32, 32), (32, h - 32), (w - 32, h - 32)]
        for cx, cy in corners:
            c.setFillColor(cls.GOLD_PRIMARY)
            c.setStrokeColor(cls.NAVY_DEEP)
            c.setLineWidth(1)
            p = c.beginPath()
            p.moveTo(cx, cy - 8)
            p.lineTo(cx + 8, cy)
            p.lineTo(cx, cy + 8)
            p.lineTo(cx - 8, cy)
            p.close()
            c.drawPath(p, fill=1, stroke=1)

    @classmethod
    def _draw_emblem(cls, c: canvas.Canvas, cx: float, cy: float):
        """Draws a vector rosette/star emblem at the top."""
        # Outer gold circle
        c.setFillColor(cls.GOLD_LIGHT)
        c.setStrokeColor(cls.GOLD_PRIMARY)
        c.setLineWidth(2)
        c.circle(cx, cy, 22, fill=1, stroke=1)

        # Inner navy circle
        c.setFillColor(cls.NAVY_PRIMARY)
        c.circle(cx, cy, 16, fill=1, stroke=0)

        # Center gold star icon
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(cx, cy - 5, "★")

    @classmethod
    def _draw_footer(
        cls,
        c: canvas.Canvas,
        w: float,
        h: float,
        issue_date: str,
        certificate_code: str,
        issuer_name: str,
    ):
        """Draws the bottom metadata, seal, and signature line."""
        base_y = 110

        # Left Column: Date & Certificate ID
        c.setStrokeColor(cls.LINE_BORDER)
        c.setLineWidth(1)
        c.line(80, base_y + 10, 240, base_y + 10)

        c.setFont("Helvetica", 9)
        c.setFillColor(cls.SLATE_MUTED)
        c.drawString(80, base_y - 8, f"Issue Date: {issue_date}")
        c.drawString(80, base_y - 22, f"Certificate ID: {certificate_code}")

        # Center: Authenticity Seal
        seal_x = w / 2
        seal_y = base_y - 10
        c.setStrokeColor(cls.GOLD_PRIMARY)
        c.setFillColor(cls.GOLD_LIGHT)
        c.setLineWidth(1.5)
        c.circle(seal_x, seal_y, 28, fill=0, stroke=1)
        c.circle(seal_x, seal_y, 24, fill=0, stroke=1)

        c.setFont("Helvetica-Bold", 7)
        c.setFillColor(cls.GOLD_PRIMARY)
        c.drawCentredString(seal_x, seal_y + 5, "OFFICIAL")
        c.drawCentredString(seal_x, seal_y - 5, "CERTIFIED")
        c.drawCentredString(seal_x, seal_y - 14, "★ ★ ★")

        # Right Column: Authorized Signature
        right_x_start = w - 240
        right_x_end = w - 80
        c.setStrokeColor(cls.LINE_BORDER)
        c.setLineWidth(1)
        c.line(right_x_start, base_y + 10, right_x_end, base_y + 10)

        # Decorative cursive-like signature representation
        c.setFont("Times-Italic", 16)
        c.setFillColor(cls.NAVY_PRIMARY)
        c.drawCentredString((right_x_start + right_x_end) / 2, base_y + 18, issuer_name)

        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(cls.NAVY_DEEP)
        c.drawCentredString((right_x_start + right_x_end) / 2, base_y - 8, issuer_name)

        c.setFont("Helvetica", 8)
        c.setFillColor(cls.SLATE_MUTED)
        c.drawCentredString((right_x_start + right_x_end) / 2, base_y - 20, "Authorized Signatory")

        # Verification tagline at page bottom
        c.setFont("Helvetica", 7)
        c.setFillColor(cls.SLATE_MUTED)
        c.drawCentredString(w / 2, 45, f"Secure Digital Credential Verification Code: {certificate_code}")
