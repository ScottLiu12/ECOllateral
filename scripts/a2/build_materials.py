"""Export course Markdown and the system diagram using ReportLab.

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
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "docs/a2"
SOURCE = HERE / "source"
BUILD = ROOT / "data/processed/a2-build"


def system_map():
    drawing = Drawing(1200, 320)
    drawing.add(String(45, 278, "How the prototype works", fontName="Helvetica-Bold", fontSize=28))
    drawing.add(
        String(
            45,
            240,
            "Current tool: cooling water use. Area-wide water assessment is still planned.",
            fontName="Helvetica",
            fontSize=20,
        )
    )
    steps = [
        ("1. Inputs", "Six numeric features", "Method + location"),
        ("2. Estimate", "XGBoost learned trees", "Daily water use (MGD)"),
        ("3. Check", "Symbolic energy rules", "Constrain + flag (E3)"),
        ("4. Result", "Gallons/day + range", "Warnings + sources"),
    ]
    for i, (heading, first, second) in enumerate(steps):
        x = 45 + i * 285
        drawing.add(Rect(x, 90, 240, 115, fillColor=colors.white, strokeColor=colors.black))
        drawing.add(String(x + 14, 174, heading, fontName="Helvetica-Bold", fontSize=22))
        drawing.add(String(x + 14, 142, first, fontName="Helvetica", fontSize=18))
        drawing.add(String(x + 14, 114, second, fontName="Helvetica", fontSize=18))
        if i < len(steps) - 1:
            drawing.add(Line(x + 240, 148, x + 275, 148, strokeColor=colors.black))
            drawing.add(Polygon([x + 282, 148, x + 273, 153, x + 273, 143], fillColor=colors.black))
    for y, label in [
        (
            66,
            "Features: MW, air/wet-bulb temperature, river flow, PDSI drought, month.",
        ),
        (
            42,
            "Permit path: text -> TF-IDF vectors + HUC/location metadata -> exact quotes (E4).",
        ),
        (18, "Tests use generated examples. Next: measured water use at separate sites."),
    ]:
        drawing.add(String(45, y, label, fontName="Helvetica", fontSize=18))
    renderSVG.drawToFile(drawing, str(HERE / "semantic-system-map.svg"))
    map_pdf = BUILD / "system-map-preview.pdf"
    renderPDF.drawToFile(drawing, str(map_pdf))
    with pdfium.PdfDocument(str(map_pdf)) as doc:
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
    styles["Normal"].fontSize = 10
    styles["Normal"].leading = 14
    styles["Normal"].spaceAfter = 8
    styles["Title"].fontSize = 18
    styles["Title"].leading = 22
    styles["Title"].alignment = 0
    styles["Heading2"].fontSize = 13
    styles["Heading3"].keepWithNext = True
    styles.add(ParagraphStyle("Cell", parent=styles["Normal"], fontSize=8.5, leading=11.5))
    if source.stem == "dossier":
        styles["Normal"].fontSize = 9.5
        styles["Normal"].leading = 12
        styles["Normal"].spaceAfter = 5
        styles["Cell"].leading = 10.5
        for heading in ("Heading2", "Heading3"):
            styles[heading].spaceBefore = 8
            styles[heading].spaceAfter = 4
    styles.add(
        ParagraphStyle(
            "ListItem", parent=styles["Normal"], leftIndent=12, firstLineIndent=-8, spaceAfter=6
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
        if line.startswith("!["):
            path = re.search(r"\(([^)]+)\)", line).group(1)
            image = Image(str(source.parent / path))
            width, height = image.imageWidth, image.imageHeight
            image.drawWidth = 516
            image.drawHeight = height * 516 / width
            story.extend([image, Spacer(1, 10)])
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [item.strip() for item in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"[-: ]+", cell) for cell in cells):
                    rows.append([Paragraph(inline(cell), styles["Cell"]) for cell in cells])
                i += 1
            count = len(rows[0])
            widths = [145, 95, 276] if count == 3 else [516 / count] * count
            if source.stem == "dossier" and count == 3:
                widths = [145, 165, 206]
            table = Table(rows, colWidths=widths, hAlign="LEFT", splitByRow=False)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 7),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.black),
                    ]
                )
            )
            story.extend([table, Spacer(1, 12)])
            continue
        elif line.startswith("#"):
            depth = len(line) - len(line.lstrip("#"))
            style = {1: "Title", 2: "Heading2"}.get(depth, "Heading3")
            story.append(Paragraph(inline(line[depth:].strip()), styles[style]))
        elif line.startswith("- "):
            paragraph = line[2:]
            while i + 1 < len(lines) and lines[i + 1].startswith("  "):
                i += 1
                paragraph += " " + lines[i].strip()
            story.append(Paragraph("- " + inline(paragraph), styles["ListItem"]))
        else:
            paragraph = line
            while (
                i + 1 < len(lines)
                and lines[i + 1].strip()
                and not lines[i + 1].startswith(("#", "|", "- ", "!["))
            ):
                i += 1
                paragraph += " " + lines[i].strip()
            story.append(Paragraph(inline(paragraph), styles["Normal"]))
        i += 1

    def page_number(canv, doc):
        canv.setFont("Helvetica", 8)
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
    document.build(story, onFirstPage=page_number, onLaterPages=page_number)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--map-only", action="store_true")
    args = parser.parse_args()
    BUILD.mkdir(parents=True, exist_ok=True)
    system_map()
    if not args.map_only:
        for name in ("dossier", "project-checkoff"):
            markdown_pdf(SOURCE / f"{name}.md", HERE / f"{name}.pdf")
        markdown_pdf(HERE / "team-contributions.md", HERE / "team-contributions.pdf")
    print("Course materials exported to", HERE)


if __name__ == "__main__":
    main()
