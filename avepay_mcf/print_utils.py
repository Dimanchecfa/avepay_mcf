"""Utilitaires d'impression : génère le QR SECEF pour les Print Formats.

Appelable depuis Jinja (print format) :
    {{ avepay_mcf.print_utils.qr_data_uri(doc.avepay_qr) }}

Le QR est rendu en PNG (data-URI) : wkhtmltopdf gère mal les SVG en <img>.
"""

import base64
import io

import frappe


@frappe.whitelist()
def secef_tax_label(item_tax_template):
    """Libellé fiscal d'une ligne : « 18 % (B) » d'après le mapping AvePay Settings."""
    if not item_tax_template:
        return "—"
    s = frappe.get_single("AvePay Settings")
    for m in s.tax_mappings or []:
        if m.item_tax_template == item_tax_template:
            rate = m.tax_rate or 0
            group = (m.secef_group or "").strip().split(" ", 1)[0]
            return "{0:g} % ({1})".format(rate, group)
    return item_tax_template


@frappe.whitelist()
def qr_data_uri(content, scale=6, quiet=4):
    """Retourne un data-URI PNG du QR encodant `content` (vide si pas de contenu)."""
    if not content:
        return ""
    import pyqrcode
    from PIL import Image

    qr = pyqrcode.create(content, error="M")
    matrix = qr.code  # liste de lignes de 0/1
    n = len(matrix)
    scale = int(scale)
    quiet = int(quiet)

    img = Image.new("1", (n, n), 1)  # 1 = blanc
    px = img.load()
    for y, row in enumerate(matrix):
        for x, val in enumerate(row):
            if val:
                px[x, y] = 0  # noir

    side = n + 2 * quiet
    canvas = Image.new("1", (side, side), 1)
    canvas.paste(img, (quiet, quiet))
    canvas = canvas.resize((side * scale, side * scale), Image.NEAREST)

    buf = io.BytesIO()
    canvas.convert("L").save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
