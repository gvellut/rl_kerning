import sys

from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import uharfbuzz as hb


class RLKerningError(Exception):
    pass


def drawStringHB(pdf_canvas, x, y, text, mode=None, direction=None):
    """Draws a string in the current text styles."""
    if sys.version_info[0] == 3 and not isinstance(text, str):
        text = text.decode("utf-8")

    font = pdfmetrics.getFont(pdf_canvas._fontname)
    if not isinstance(font, TTFont):
        # TODO make valid for all types of fonts
        raise RLKerningError("Not a TTF font")
    font_size = pdf_canvas._fontsize

    fontdata = font.face._ttf_data
    face = hb.Face(fontdata)
    font = hb.Font(face)

    font.scale = (font_size, font_size)
    hb.ot_font_set_funcs(font)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf)

    t = pdf_canvas.beginText(x, y, direction=direction)
    if mode is not None:
        t.setTextRenderMode(mode)

    x_advance = 0
    y_advance = 0
    for i, pos in enumerate(buf.glyph_positions):
        xchar = x + x_advance + pos.x_offset
        if pdf_canvas.bottomup:
            # TODO verify if y_advance / offset is always be 0 for horizontal languages
            ychar = y + y_advance + pos.y_offset
        else:
            ychar = y - y_advance - pos.y_offset

        t.setTextOrigin(xchar, ychar)
        t.textOut(text[i])
        x_advance += pos.x_advance
        y_advance += pos.y_advance

    if mode is not None:
        t.setTextRenderMode(0)
    pdf_canvas.drawText(t)


if __name__ == "__main__":
    from reportlab.pdfgen import canvas  # isort:skip

    # fonts = ["FiraCode-Regular"]
    pdfmetrics.registerFont(TTFont("cmunrm", "tests/cmunrm.ttf"))

    pdf_canvas = canvas.Canvas("test.pdf", pagesize=(8.5 * inch, 8.5 * inch))
    pdf_canvas.saveState()
    pdf_canvas.setFont("cmunrm", 26)
    text = "Guilhem Vellut"
    drawStringHB(pdf_canvas, 1.5 * inch, 1.7 * inch, "Guilhem Vellut")
    pdf_canvas.drawString(1.5 * inch, 2 * inch, text)
    pdf_canvas.restoreState()
    pdf_canvas.showPage()
    pdf_canvas.save()
