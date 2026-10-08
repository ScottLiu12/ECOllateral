"""Export course Markdown and the explicit system diagram using bundled ReportLab.

Run with the Codex bundled Python. Build slides first to include their PDF export.
Intermediate renders stay in the ignored data directory; outputs stay in docs/a2.
"""

import argparse
import re
from pathlib import Path
from xml.sax.saxutils import escape

import pypdfium2 as pdfium
from reportlab.graphics import renderPDF, renderSVG
from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = ROOT / "data/processed/a2-build"
NAVY = colors.HexColor("#142D42")
TEAL = colors.HexColor("#167D8D")
PALE = colors.HexColor("#EFF5F7")


def system_map():
    drawing = Drawing(1200, 530)

    def label(x, y, text, size=20, color=NAVY, bold=False):
        drawing.add(
            String(
                x,
                530 - y,
                text,
                fontName="Helvetica-Bold" if bold else "Helvetica",
                fontSize=size,
                fillColor=color,
            )
        )

    def node(x, top, heading, lines):
        drawing.add(
            Rect(x, 530 - top - 100, 190, 100, fillColor=PALE, strokeColor=TEAL, strokeWidth=1.5)
        )
        label(x + 12, top + 27, heading, 20, bold=True)
        for i, line in enumerate(lines):
            label(x + 12, top + 54 + 22 * i, line, 18)

    def arrow(x1, y1, x2, y2):
        drawing.add(Line(x1, 530 - y1, x2, 530 - y2, strokeColor=TEAL, strokeWidth=2))
        if y1 == y2:
            points = [x2, 530 - y2, x2 - 9, 530 - y2 + 5, x2 - 9, 530 - y2 - 5]
        else:
            points = [x2, 530 - y2, x2 - 5, 530 - y2 - 9, x2 + 5, 530 - y2 - 9]
        drawing.add(Polygon(points, fillColor=TEAL, strokeColor=TEAL))

    label(45, 34, "ECOllateral: predict water use and find permit quotations", 28, bold=True)
    label(
        45,
        69,
        "Enter IT size (MW), cooling type, watershed (HUC8), month; coordinates optional",
        20,
    )
    label(45, 99, "Number path", 20, TEAL, True)
    top_nodes = [
        ("Public data", ["USGS / NOAA", "values + units"]),
        ("Six inputs", ["size / weather / flow", "drought / season"]),
        ("AI model", ["RF / XGBoost", "predict a number"]),
        ("Heat rules", ["capacity + weather", "adjust + warn"]),
        ("Response (JSON)", ["MGD + range", "limits + warnings"]),
    ]
    bottom_nodes = [
        ("Permit text", ["document + section", "original words"]),
        ("Document info", ["text + identifiers", "HUC or radius"]),
        ("Word search", ["TF-IDF / FAISS", "rank word matches"]),
        ("Location check", ["HUC / coordinates", "eligible top-k"]),
        ("Quotes", ["source + section", "exact quotations"]),
    ]
    for i, ((heading, lines), (lower, lower_lines)) in enumerate(
        zip(top_nodes, bottom_nodes, strict=True)
    ):
        x = 45 + 230 * i
        node(x, 120, heading, lines)
        node(x, 310, lower, lower_lines)
        if i < 4:
            arrow(x + 190, 170, x + 230, 170)
            arrow(x + 190, 360, x + 230, 360)
    arrow(1060, 310, 1060, 220)
    label(45, 287, "Permit path", 20, TEAL, True)
    label(
        45,
        465,
        "Before use: made-up water targets -> train / choose + set ranges / test -> saved models",
        20,
    )
    label(
        45,
        499,
        "Rules depend on assumptions. A permit quotation does not prove legal compliance.",
        20,
    )
    renderSVG.drawToFile(drawing, str(HERE / "semantic-system-map.svg"))
    map_pdf = BUILD / "system-map-preview.pdf"
    renderPDF.drawToFile(drawing, str(map_pdf))
    doc = pdfium.PdfDocument(str(map_pdf))
    doc[0].render(scale=1.5).to_pil().save(HERE / "semantic-system-map.png")


def inline(text):
    text = text.replace("[x]", "Complete:").replace("[ ]", "Pending:")
    text = text.replace("\u2019", "'").replace("\u2013", "-").replace("\u2014", "-")
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r'<font face="Courier" size="8.5">\1</font>', text)
    text = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    return text


def markdown_pdf(source, output):
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "ReviewBody",
            fontName="Helvetica",
            fontSize=10.2,
            leading=14.8,
            textColor=NAVY,
            spaceAfter=9,
        )
    )
    styles.add(
        ParagraphStyle(
            "ReviewTitle",
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=27,
            textColor=NAVY,
            spaceAfter=16,
        )
    )
    styles.add(
        ParagraphStyle(
            "ReviewHeading",
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=20,
            textColor=TEAL,
            spaceBefore=9,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            "ReviewSubhead",
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            "ReviewCell", fontName="Helvetica", fontSize=8.5, leading=11.5, textColor=NAVY
        )
    )
    styles.add(
        ParagraphStyle(
            "ReviewBullet",
            parent=styles["ReviewBody"],
            leftIndent=12,
            firstLineIndent=-8,
            spaceAfter=6,
        )
    )
    lines = source.read_text(encoding="utf-8").splitlines()
    story = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line == "<!-- pagebreak -->":
            story.append(PageBreak())
        elif line.startswith("!["):
            path = re.search(r"\(([^)]+)\)", line).group(1)
            story.extend([Image(str(HERE / path), width=516, height=228), Spacer(1, 10)])
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [item.strip() for item in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"[-: ]+", cell) for cell in cells):
                    rows.append([Paragraph(inline(cell), styles["ReviewCell"]) for cell in cells])
                i += 1
            count = len(rows[0])
            widths = [145, 95, 276] if count == 3 else [516 / count] * count
            table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCEBF0")),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 7),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                        ("LINEBELOW", (0, 0), (-1, 0), 1, TEAL),
                    ]
                )
            )
            story.extend([table, Spacer(1, 12)])
            continue
        elif line.startswith("#"):
            depth = len(line) - len(line.lstrip("#"))
            if source.stem == "project-checkoff" and line.startswith(
                ("## System Architecture", "## Presentation Preparation")
            ):
                story.append(PageBreak())
            style = {1: "ReviewTitle", 2: "ReviewHeading"}.get(depth, "ReviewSubhead")
            story.append(Paragraph(inline(line[depth:].strip()), styles[style]))
        elif line.startswith("- "):
            paragraph = line[2:]
            while i + 1 < len(lines) and lines[i + 1].startswith("  "):
                i += 1
                paragraph += " " + lines[i].strip()
            story.append(Paragraph("- " + inline(paragraph), styles["ReviewBullet"]))
        else:
            paragraph = line
            while (
                i + 1 < len(lines)
                and lines[i + 1].strip()
                and not lines[i + 1].startswith(("#", "|", "- ", "<!--", "!["))
            ):
                i += 1
                paragraph += " " + lines[i].strip()
            story.append(Paragraph(inline(paragraph), styles["ReviewBody"]))
        i += 1

    def furniture(canv, doc):
        canv.setStrokeColor(colors.HexColor("#D0DFE5"))
        canv.line(48, 755, 564, 755)
        canv.setFont("Helvetica", 8)
        canv.setFillColor(TEAL)
        canv.drawString(48, 764, "ECOllateral | CSCI 4150 A2 | October 7, 2026 snapshot")
        canv.drawString(48, 26, "Synthetic benchmark evidence; field validation pending")
        canv.drawRightString(564, 26, str(doc.page))

    document = SimpleDocTemplate(
        str(output),
        pagesize=(612, 792),
        rightMargin=48,
        leftMargin=48,
        topMargin=50,
        bottomMargin=48,
        title=source.stem.replace("-", " "),
        author="ECOllateral team",
    )
    document.build(story, onFirstPage=furniture, onLaterPages=furniture)


def slides_pdf():
    images = sorted((BUILD / "slides/final-render").glob("slide-*.png"))
    if not images:
        return
    target = canvas.Canvas(str(HERE / "review-slides.pdf"), pagesize=(960, 540))
    target.setTitle("ECOllateral mid-semester evidence review")
    for path in images:
        target.drawImage(ImageReader(str(path)), 0, 0, width=960, height=540)
        target.showPage()
    target.save()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--map-only", action="store_true")
    args = parser.parse_args()
    BUILD.mkdir(parents=True, exist_ok=True)
    system_map()
    if not args.map_only:
        for name in ("dossier", "project-checkoff"):
            markdown_pdf(HERE / f"{name}.md", HERE / f"{name}.pdf")
        slides_pdf()
    print("Course materials exported to", HERE)


if __name__ == "__main__":
    main()
