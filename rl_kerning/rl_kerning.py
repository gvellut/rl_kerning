import sys
from typing import Dict

from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import uharfbuzz as hb


class RLKerningError(Exception):
    pass


# TODO drop the text arg once drawGlyphs has been implemented
def canvas_drawStringHB(
    pdf_canvas, x, y, text, cached_shape=None, mode=None, direction=None
):
    """Draws a string in the current text styles."""

    if sys.version_info[0] == 3 and not isinstance(text, str):
        text = text.decode("utf-8")

    t = pdf_canvas.beginText(x, y, direction=direction)
    if mode is not None:
        t.setTextRenderMode(mode)

    x_advance = 0
    y_advance = 0

    # assumes the cached_shape buffer corresponds to the current text and style
    # of the canvas
    for i, pos in enumerate(cached_shape.glyph_positions):
        xchar = x + x_advance + pos.x_offset
        print(f"offset {pos.x_offset}")
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


def canvas_stringWidthHB(pdf_canvas, text, features=None):
    buf = canvas_shape(pdf_canvas, text, features)
    return stringWidthHB(buf)


def stringWidthHB(cached_shape):
    x_advance = 0
    for pos in cached_shape.glyph_positions:
        x_advance += pos.x_advance
    return x_advance


def canvas_shape(pdf_canvas, text, features: Dict[str, bool] = None):
    font_name = pdf_canvas._fontname
    font_size = pdf_canvas._fontsize
    return shape(text, font_name, font_size, features)


def shape(text, font_name, font_size, features: Dict[str, bool] = None):
    font = pdfmetrics.getFont(font_name)
    if not isinstance(font, TTFont):
        # TODO make valid for all types of fonts
        raise RLKerningError("Not a TTF font")

    fontdata = font.face._ttf_data
    face = hb.Face(fontdata)
    font = hb.Font(face)

    font.scale = (font_size, font_size)
    hb.ot_font_set_funcs(font)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, features)

    return buf


if __name__ == "__main__":
    from reportlab.pdfgen import canvas  # isort:skip
    from reportlab.lib.colors import red  # isort:skip

    # fonts = ["FiraCode-Regular"]
    pdfmetrics.registerFont(TTFont("tnr", "tests/times-new-roman.ttf"))

    pdf_canvas = canvas.Canvas("test.pdf", pagesize=(8.5 * inch, 8.5 * inch))
    pdf_canvas.saveState()
    font = ("tnr", 26)
    pdf_canvas.setFont(*font)
    text = "Guilhem Ve"
    cached_shape = canvas_shape(pdf_canvas, text)
    canvas_drawStringHB(pdf_canvas, 1.5 * inch, 1.7 * inch, text, cached_shape)
    pdf_canvas.drawString(1.5 * inch, 2 * inch, text)

    # draw bbox
    def draw_bbox(size, pos):
        pdf_canvas.saveState()
        pdf_canvas.setStrokeColor(red)
        pdf_canvas.setLineWidth(1)
        p = pdf_canvas.beginPath()
        p.rect(*size, *pos)
        pdf_canvas.drawPath(p, stroke=True, fill=False)
        pdf_canvas.restoreState()

    asc, desc = pdfmetrics.getAscentDescent(*font)
    width = stringWidthHB(cached_shape)
    draw_bbox((1.5 * inch, 1.7 * inch + desc), (width, asc - desc))

    width = pdfmetrics.stringWidth(text, *font)
    draw_bbox((1.5 * inch, 2 * inch + desc), (width, asc - desc))

    pdf_canvas.restoreState()
    pdf_canvas.showPage()
    pdf_canvas.save()
