import subprocess, sys, re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SCR = "/tmp/claude-0/-home-user-Regula-o-da-gua/59c78df9-e290-55db-9332-1ed095ca28fc/scratchpad/"
BASE = "/home/user/Regula-o-da-gua/artigo/"
FONT = "Times New Roman"

# 1) reference doc com estilos
d = Document(SCR + "ref_default.docx")
def setfont(style, size=None, bold=None, italic=None, color=None, align=None, before=None, after=None, line=None):
    f = style.font; f.name = FONT
    rpr = style.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"): rf.set(qn(a), FONT)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rf.get(qn(a)) is not None: del rf.attrib[qn(a)]
    if size: f.size = Pt(size)
    if bold is not None: f.bold = bold
    if italic is not None: f.italic = italic
    f.color.rgb = RGBColor(0, 0, 0) if color is None else color
    pf = style.paragraph_format
    if align is not None: pf.alignment = align
    if before is not None: pf.space_before = Pt(before)
    if after is not None: pf.space_after = Pt(after)
    if line is not None: pf.line_spacing = line
names = {s.name: s for s in d.styles}
for n in ["Normal", "Body Text", "First Paragraph", "Compact", "Block Text"]:
    if n in names: setfont(names[n], 11, align=WD_ALIGN_PARAGRAPH.JUSTIFY, before=0, after=6, line=1.25)
if "Compact" in names: setfont(names["Compact"], 9, align=WD_ALIGN_PARAGRAPH.LEFT, before=1, after=1, line=1.0)
setfont(names["Title"], 17, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, before=0, after=14, line=1.15)
setfont(names["Heading 1"], 13.5, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, before=16, after=8, line=1.15)
setfont(names["Heading 2"], 12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, before=12, after=6, line=1.15)
setfont(names["Heading 3"], 11.5, bold=True, italic=True, align=WD_ALIGN_PARAGRAPH.LEFT, before=10, after=4, line=1.15)
for n in ["Image Caption", "Table Caption", "Captioned Figure"]:
    if n in names: setfont(names[n], 10, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, before=6, after=4, line=1.1)
for n in ["Hyperlink"]:
    if n in names: names[n].font.color.rgb = RGBColor(0x1F, 0x3A, 0x8A)
for s in d.sections:
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin, s.top_margin, s.right_margin, s.bottom_margin = Cm(3.0), Cm(3.0), Cm(2.0), Cm(2.0)
d.save(SCR + "ref_custom.docx")

# 2) pandoc
out = BASE + "Artigo_Restricoes_Hidraulicas_SIN_Belo_Monte.docx"
subprocess.run(["pandoc", BASE + "fonte/artigo_completo.md", "-f", "markdown+pipe_tables+superscript+subscript+smart-fancy_lists",
                "--reference-doc", SCR + "ref_custom.docx", "--resource-path", BASE + "fonte", "-o", out], check=True)

# 3) pós-processamento
doc = Document(out)
# tabelas
def set_cell_border(cell, **kw):
    tcPr = cell._tc.get_or_add_tcPr()
    b = tcPr.find(qn("w:tcBorders"))
    if b is None:
        b = OxmlElement("w:tcBorders"); tcPr.append(b)
    for edge, val in kw.items():
        e = b.find(qn("w:" + edge))
        if e is None:
            e = OxmlElement("w:" + edge); b.append(e)
        for k, v in val.items(): e.set(qn("w:" + k), str(v))
def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), fill); tcPr.append(sh)

usable = Cm(16.0)
for t in doc.tables:
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = t._tbl.tblPr
    # largura fixa
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tblPr.append(lay)
    ncol = len(t.columns)
    # pesos pelo comprimento do texto (limitados)
    w = [0.0] * ncol
    for i in range(ncol):
        cells = [r.cells[i].text for r in t.rows]
        longest_word = max((len(x) for c in cells for x in c.split()), default=1)
        mean_len = sum(len(c) for c in cells) / max(len(cells), 1)
        w[i] = max(longest_word * 1.5 + 3, min(mean_len, 42))
    tot = sum(w)
    widths = [int(usable * x / tot) for x in w]
    grid = t._tbl.find(qn("w:tblGrid"))
    for i, gc in enumerate(grid.findall(qn("w:gridCol"))): gc.set(qn("w:w"), str(int(widths[i] / 635)))
    for ri, r in enumerate(t.rows):
        for ci, c in enumerate(r.cells[:ncol]):
            c.width = widths[ci]
            for p in c.paragraphs:
                p.paragraph_format.space_after = Pt(1); p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.line_spacing = 1.0
                for run in p.runs:
                    run.font.size = Pt(8.5); run.font.name = FONT
                    if ri == 0: run.font.bold = True
            set_cell_border(c, bottom={"val": "single", "sz": 4, "color": "BFBFBF"})
            if ri == 0:
                shade(c, "E8EEF7")
                set_cell_border(c, top={"val": "single", "sz": 10, "color": "000000"}, bottom={"val": "single", "sz": 8, "color": "000000"})
            if ri == len(t.rows) - 1:
                set_cell_border(c, bottom={"val": "single", "sz": 10, "color": "000000"})
# imagens: centralizar
for p in doc.paragraphs:
    if p._p.xpath(".//w:drawing"):
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
# legendas "Fonte:" menores
for p in doc.paragraphs:
    if p.text.startswith("Fonte:") or p.text.startswith("Nota:"):
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p.runs: r.font.size = Pt(9)
        p.paragraph_format.space_after = Pt(10)
    if re.match(r"^Quadro \d+ –", p.text):
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT; p.paragraph_format.keep_with_next = True
        p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(3)
# referências: recuo deslocado, alinhamento à esquerda
in_ref = False
for p in doc.paragraphs:
    if p.style.name.startswith("Heading 1"):
        in_ref = p.text.strip() == "Referências"
        if p.text.strip().startswith("Anexos"): in_ref = False
        continue
    if in_ref and p.text and not p.text.startswith("Nota:"):
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.left_indent = Cm(0); p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.0
        for r in p.runs: r.font.size = Pt(10)
# rodapé com número de página
sec = doc.sections[0]
sec.left_margin, sec.top_margin, sec.right_margin, sec.bottom_margin = Cm(3.0), Cm(3.0), Cm(2.0), Cm(2.0)
fp = sec.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
def fld(par, instr):
    r = par.add_run(); r.font.size = Pt(10); r.font.name = FONT
    a = OxmlElement("w:fldChar"); a.set(qn("w:fldCharType"), "begin"); r._r.append(a)
    r2 = par.add_run(); i = OxmlElement("w:instrText"); i.set(qn("xml:space"), "preserve"); i.text = instr; r2._r.append(i)
    r3 = par.add_run(); b = OxmlElement("w:fldChar"); b.set(qn("w:fldCharType"), "end"); r3._r.append(b)
fld(fp, "PAGE")
# propriedades
doc.core_properties.title = "Restrições hidráulicas operativas no SIN e os hidrogramas da UHE Belo Monte"
doc.core_properties.language = "pt-BR"
doc.save(out)
print("salvo", out)
