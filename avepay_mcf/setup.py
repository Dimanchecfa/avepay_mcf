"""One-shot helper to create the AvePay DocTypes (run via `bench execute`).

    bench --site <site> execute avepay_mcf.setup.create_doctypes

DocTypes are written to disk (developer_mode=1) so they are versioned in the app.
"""

import frappe

SECEF = "A\nB\nC\nD\nE\nF\nG\nH\nI\nJ\nK\nL\nM\nN"


def _mk(name, extra):
    if frappe.db.exists("DocType", name):
        print("exists:", name)
        return
    doc = {"doctype": "DocType", "name": name, "module": "AvePay MCF", "custom": 0}
    doc.update(extra)
    frappe.get_doc(doc).insert()
    print("created:", name)


def create_doctypes():
    if not frappe.db.exists("Module Def", "AvePay MCF"):
        frappe.get_doc({"doctype": "Module Def", "module_name": "AvePay MCF",
                        "app_name": "avepay_mcf"}).insert()
        print("created Module Def: AvePay MCF")
    # S'assurer que le mapping module->app connaît notre module (cache parfois non reconstruit).
    if getattr(frappe.local, "module_app", None) is not None:
        frappe.local.module_app["avepay_mcf"] = "avepay_mcf"
        frappe.local.app_modules.setdefault("avepay_mcf", []).append("avepay_mcf")
    _mk("AvePay Tax Mapping", {
        "istable": 1,
        "fields": [
            {"fieldname": "item_tax_template", "fieldtype": "Link", "options": "Item Tax Template",
             "label": "Item Tax Template", "in_list_view": 1, "reqd": 1},
            {"fieldname": "secef_group", "fieldtype": "Select", "options": SECEF,
             "label": "Groupe SECEF", "in_list_view": 1, "reqd": 1},
            {"fieldname": "tax_rate", "fieldtype": "Float", "label": "Taux (%)", "in_list_view": 1},
        ],
    })
    _mk("AvePay Payment Mapping", {
        "istable": 1,
        "fields": [
            {"fieldname": "mode_of_payment", "fieldtype": "Link", "options": "Mode of Payment",
             "label": "Mode of Payment", "in_list_view": 1, "reqd": 1},
            {"fieldname": "method", "fieldtype": "Select", "options": "E\nV\nC\nM\nB\nA",
             "label": "Methode MCF", "in_list_view": 1, "reqd": 1},
        ],
    })
    _mk("AvePay Settings", {
        "issingle": 1,
        "fields": [
            {"fieldname": "sec_api", "fieldtype": "Section Break", "label": "Connexion API"},
            {"fieldname": "base_url", "fieldtype": "Data", "label": "Base URL",
             "default": "https://api-mcf-orchestrator.toolsite.io"},
            {"fieldname": "nim", "fieldtype": "Data", "label": "NIM", "reqd": 1},
            {"fieldname": "col_api", "fieldtype": "Column Break"},
            {"fieldname": "isf", "fieldtype": "Data", "label": "ISF", "default": "1"},
            {"fieldname": "api_key", "fieldtype": "Password", "label": "Cle API (ak_live_...)", "reqd": 1},
            {"fieldname": "sec_behavior", "fieldtype": "Section Break", "label": "Comportement"},
            {"fieldname": "offline_behavior", "fieldtype": "Select",
             "options": "Bloquer la validation\nFile d'attente",
             "label": "Si MCF hors-ligne", "default": "Bloquer la validation"},
            {"fieldname": "sec_tax", "fieldtype": "Section Break", "label": "Mapping taxes -> groupes SECEF"},
            {"fieldname": "tax_mappings", "fieldtype": "Table", "options": "AvePay Tax Mapping", "label": "Taxes"},
            {"fieldname": "sec_pay", "fieldtype": "Section Break", "label": "Mapping modes de paiement"},
            {"fieldname": "payment_mappings", "fieldtype": "Table", "options": "AvePay Payment Mapping", "label": "Paiements"},
        ],
        "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1}],
    })
    frappe.db.commit()
    print("OK settings exists:", bool(frappe.db.exists("DocType", "AvePay Settings")))


def create_custom_fields():
    """Custom Fields de certification sur Sales Invoice."""
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields as ccf
    ccf({
        "Sales Invoice": [
            {"fieldname": "avepay_sec", "fieldtype": "Section Break", "label": "Certification MCF (AvePay)",
             "insert_after": "taxes_and_charges", "collapsible": 1},
            {"fieldname": "avepay_invoice_type", "fieldtype": "Select", "label": "Type de facture MCF",
             "options": "FV\nEV\nET", "default": "FV", "insert_after": "avepay_sec",
             "description": "FV = vente locale, EV/ET = export"},
            {"fieldname": "avepay_status", "fieldtype": "Select", "label": "Statut MCF",
             "options": "\nNon certifiee\nEn attente\nCertifiee\nErreur", "default": "Non certifiee",
             "read_only": 1, "insert_after": "avepay_invoice_type", "allow_on_submit": 1, "no_copy": 1},
            {"fieldname": "avepay_codesecef", "fieldtype": "Data", "label": "Code SECEF",
             "read_only": 1, "insert_after": "avepay_status", "allow_on_submit": 1, "no_copy": 1},
            {"fieldname": "avepay_fvc", "fieldtype": "Int", "label": "Compteur FVC",
             "read_only": 1, "insert_after": "avepay_codesecef", "allow_on_submit": 1, "no_copy": 1},
            {"fieldname": "avepay_col", "fieldtype": "Column Break", "insert_after": "avepay_fvc"},
            {"fieldname": "avepay_nim", "fieldtype": "Data", "label": "NIM",
             "read_only": 1, "insert_after": "avepay_col", "allow_on_submit": 1, "no_copy": 1},
            {"fieldname": "avepay_datetime", "fieldtype": "Data", "label": "Date/heure MCF",
             "read_only": 1, "insert_after": "avepay_nim", "allow_on_submit": 1, "no_copy": 1},
            {"fieldname": "avepay_qr", "fieldtype": "Small Text", "label": "QR SECEF",
             "read_only": 1, "insert_after": "avepay_datetime", "allow_on_submit": 1, "no_copy": 1},
        ],
        "Sales Invoice Item": [
            {"fieldname": "avepay_ts_rate", "fieldtype": "Currency", "label": "Taxe spécifique / unité (TSR)",
             "insert_after": "item_tax_template",
             "description": "Montant de taxe spécifique par unité (XOF). TS = TSR × quantité."},
            {"fieldname": "avepay_ts_desc", "fieldtype": "Data", "label": "Libellé taxe spécifique",
             "insert_after": "avepay_ts_rate"},
        ],
    })
    frappe.db.commit()
    print("custom fields OK")


def configure_settings(nim, api_key, base_url="http://host.docker.internal:9080", isf="1"):
    """Configure AvePay Settings + mappings de test (Burkina Faso Tax - A -> B, Cash -> E)."""
    s = frappe.get_single("AvePay Settings")
    s.base_url = base_url
    s.nim = nim
    s.isf = isf
    s.api_key = api_key
    s.offline_behavior = "Bloquer la validation"
    s.set("tax_mappings", [])
    if frappe.db.exists("Item Tax Template", "Burkina Faso Tax - A"):
        s.append("tax_mappings", {"item_tax_template": "Burkina Faso Tax - A",
                                  "secef_group": "B — TVA taxable (18 %)", "tax_rate": 18})
    s.set("payment_mappings", [])
    if frappe.db.exists("Mode of Payment", "Cash"):
        s.append("payment_mappings", {"mode_of_payment": "Cash", "method": "E — Espèces"})
    s.save()
    frappe.db.commit()
    print("settings OK nim=", s.nim, "taxes=", len(s.tax_mappings), "pay=", len(s.payment_mappings))


def create_workspace():
    """Crée la tuile/Workspace « AvePay MCF » sur l'accueil (raccourcis Réglages + Factures)."""
    import json
    name = "AvePay MCF"
    if frappe.db.exists("Workspace", name):
        ws = frappe.get_doc("Workspace", name)
        ws.shortcuts = []
    else:
        ws = frappe.new_doc("Workspace")
        ws.name = name
    ws.label = name
    ws.title = name
    ws.module = "AvePay MCF"
    ws.public = 1
    ws.icon = "tax"
    ws.append("shortcuts", {"type": "DocType", "link_to": "AvePay Settings",
                            "label": "AvePay Settings", "color": "Grey"})
    ws.append("shortcuts", {"type": "DocType", "link_to": "Sales Invoice",
                            "label": "Factures", "color": "Blue"})
    ws.content = json.dumps([
        {"id": "hdr", "type": "header",
         "data": {"text": "<span class=\"h4\">AvePay MCF — Certification fiscale</span>", "col": 12}},
        {"id": "s1", "type": "shortcut", "data": {"shortcut_name": "AvePay Settings", "col": 3}},
        {"id": "s2", "type": "shortcut", "data": {"shortcut_name": "Factures", "col": 3}},
    ])
    ws.save(ignore_permissions=True)
    frappe.db.commit()
    print("workspace OK:", ws.name)


def test_mapping():
    """Valide le mapping facture->payload sans appeler le MCF (vraie Sales Invoice en mémoire)."""
    import json
    from avepay_mcf import certify
    inv = frappe.new_doc("Sales Invoice")
    inv.customer = "Client Comptant"
    inv.company = "AvePLUS"
    inv.currency = "XOF"
    inv.append("items", {"item_code": "ART-TEST", "qty": 1, "rate": 1000,
                         "item_tax_template": "Burkina Faso Tax - A"})
    inv.set_missing_values()
    inv.calculate_taxes_and_totals()
    inv.name = "TEST-INV-001"
    s = frappe.get_single("AvePay Settings")
    print("PAYLOAD", json.dumps(certify.build_payload(inv, s), default=str))


def test_me():
    """Vérifie l'auth + l'état MCF via le SDK (appel réseau réel)."""
    from avepay_mcf import certify
    s = certify._settings()
    cl = certify._client(s)
    try:
        print("ME OK", cl.me())
    except Exception as e:
        print("ME ERR", type(e).__name__, str(e)[:300])


def test_certify():
    """Certifie une vraie FV de bout en bout via le SDK (appel réseau réel)."""
    from avepay_mcf import certify
    inv = frappe.new_doc("Sales Invoice")
    inv.customer = "Client Comptant"
    inv.company = "AvePLUS"
    inv.currency = "XOF"
    inv.append("items", {"item_code": "ART-TEST", "qty": 1, "rate": 1000,
                         "item_tax_template": "Burkina Faso Tax - A"})
    inv.set_missing_values()
    inv.calculate_taxes_and_totals()
    inv.name = "ERP-TEST-CERTIFY-1"
    s = certify._settings()
    payload = certify.build_payload(inv, s)
    try:
        mcf = certify._client(s).mcf(s.nim)
        receipt = mcf.certify(payload, idempotency_key=inv.name)
        print("CERTIFY OK sig=", receipt.sig, "fvc=", receipt.counters.fvc, "nim=", receipt.nim)
    except Exception as e:
        print("CERTIFY ERR", type(e).__name__, str(e)[:300])


PRINT_FORMAT_NAME = "AvePay Facture Certifiee"

PRINT_FORMAT_HTML = """
<div class="avepay-invoice" style="font-size: 9pt;">
  <div style="display:flex; justify-content:space-between; border-bottom:2px solid #222; padding-bottom:6px;">
    <div>
      <div style="font-size:13pt; font-weight:bold;">{{ doc.company }}</div>
      <div>NIM : <b>{{ doc.avepay_nim or "—" }}</b></div>
      {% set comp = frappe.get_doc("Company", doc.company) %}
      {% if comp.tax_id %}<div>IFU : {{ comp.tax_id }}</div>{% endif %}
    </div>
    <div style="text-align:right;">
      <div style="font-size:12pt; font-weight:bold;">FACTURE NORMALISÉE</div>
      <div>N° {{ doc.name }}</div>
      <div>Date : {{ frappe.utils.format_date(doc.posting_date) }}</div>
    </div>
  </div>

  <div style="margin:8px 0;">
    <b>Client :</b> {{ doc.customer_name }}
    {% set cust = frappe.get_doc("Customer", doc.customer) %}
    {% if cust.tax_id %}— IFU : {{ cust.tax_id }}{% endif %}
  </div>

  <table class="table table-bordered" style="width:100%; border-collapse:collapse;">
    <thead>
      <tr style="background:#f0f0f0;">
        <th style="text-align:left; padding:4px;">Désignation</th>
        <th style="text-align:right; padding:4px;">Qté</th>
        <th style="text-align:right; padding:4px;">P.U. HT</th>
        <th style="text-align:center; padding:4px;">TVA</th>
        <th style="text-align:right; padding:4px;">Montant HT</th>
      </tr>
    </thead>
    <tbody>
      {% for it in doc.items %}
      <tr>
        <td style="padding:4px;">{{ it.item_name }}</td>
        <td style="text-align:right; padding:4px;">{{ it.qty }}</td>
        <td style="text-align:right; padding:4px;">{{ frappe.utils.fmt_money(it.rate, currency=doc.currency) }}</td>
        <td style="text-align:center; padding:4px;">{{ secef_tax_label(it.item_tax_template) }}</td>
        <td style="text-align:right; padding:4px;">{{ frappe.utils.fmt_money(it.amount, currency=doc.currency) }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <div style="display:flex; justify-content:flex-end; margin-top:6px;">
    <table style="min-width:240px;">
      <tr><td style="padding:2px 8px;">Total HT</td><td style="text-align:right; padding:2px 8px;">{{ frappe.utils.fmt_money(doc.net_total, currency=doc.currency) }}</td></tr>
      <tr><td style="padding:2px 8px;">TVA</td><td style="text-align:right; padding:2px 8px;">{{ frappe.utils.fmt_money(doc.total_taxes_and_charges, currency=doc.currency) }}</td></tr>
      <tr style="font-weight:bold; border-top:1px solid #222;"><td style="padding:2px 8px;">Total TTC</td><td style="text-align:right; padding:2px 8px;">{{ frappe.utils.fmt_money(doc.grand_total, currency=doc.currency) }}</td></tr>
    </table>
  </div>

  {% if doc.avepay_codesecef %}
  <div style="margin-top:14px; border:1px solid #222; padding:8px; display:flex; gap:12px; align-items:center;">
    <img src="{{ qr_data_uri(doc.avepay_qr) }}" style="width:110px; height:110px;" />
    <div style="font-size:8.5pt; line-height:1.5;">
      <div style="font-weight:bold; font-size:10pt;">Facture certifiée — SECEF / DGI Burkina Faso</div>
      <div>Code SECEF (signature) : <b>{{ doc.avepay_codesecef }}</b></div>
      <div>Compteur FVC : {{ doc.avepay_fvc }} &nbsp;|&nbsp; NIM : {{ doc.avepay_nim }}</div>
      {% set dt = doc.avepay_datetime or (doc.avepay_qr.split(';')[-1] if doc.avepay_qr else '') %}
      <div>Date/heure de certification : {{ dt }}</div>
      <div style="margin-top:4px; font-style:italic;">Facture normalisée conforme à la réglementation en vigueur (Module de Contrôle Fiscal).</div>
    </div>
  </div>
  {% else %}
  <div style="margin-top:14px; color:#b00; font-weight:bold;">⚠ Facture NON certifiée par le SECEF.</div>
  {% endif %}
</div>
"""


def create_print_format():
    """Crée/MAJ le Print Format 'AvePay Facture Certifiee' pour Sales Invoice."""
    if frappe.db.exists("Print Format", PRINT_FORMAT_NAME):
        pf = frappe.get_doc("Print Format", PRINT_FORMAT_NAME)
    else:
        pf = frappe.new_doc("Print Format")
        pf.name = PRINT_FORMAT_NAME
    pf.doc_type = "Sales Invoice"
    pf.module = "AvePay MCF"
    pf.standard = "No"
    pf.custom_format = 1
    pf.print_format_type = "Jinja"
    pf.html = PRINT_FORMAT_HTML
    pf.save(ignore_permissions=True)
    frappe.db.commit()
    print("print format OK:", pf.name)


def test_render_print(invoice=None):
    """Rend la facture avec le Print Format et vérifie la présence du QR + codeSecef."""
    if not invoice:
        invoice = frappe.get_last_doc("Sales Invoice").name
    html = frappe.get_print("Sales Invoice", invoice, print_format=PRINT_FORMAT_NAME)
    print("RENDER OK invoice=", invoice, "len=", len(html),
          "has_qr=", ("data:image/svg+xml" in html),
          "has_sec=", ("Code SECEF" in html))


def cancel_pending():
    """Annule une transaction MCF pendante (facture ouverte qui bloque les suivantes)."""
    from avepay_mcf import certify
    s = certify._settings()
    res = certify._client(s).mcf(s.nim).cancel_pending()
    print("CANCEL", res)


def test_ts_raw():
    """Payload TS exact connu-bon (live), en direct via SDK, pour isoler MCF vs mapping ERPNext."""
    from avepay_mcf import certify
    s = certify._settings()
    mcf = certify._client(s).mcf(s.nim)
    try:
        mcf.cancel_pending()
    except Exception:
        pass
    payload = {
        "number": "ERP-TSRAW-1", "type": "FV",
        "operator": {"id": "1", "name": "TS"}, "customer": {"type": "CC"},
        "items": [{"name": "Boisson", "taxGroup": "B", "unitPrice": 1050, "quantity": 1,
                   "amountTtc": 1050, "specificTax": 50, "specificTaxRate": 50, "specificTaxDesc": "TS"}],
        "payments": [{"method": "E", "amount": 1050}],
    }
    try:
        r = mcf.certify(payload, idempotency_key="ERP-TSRAW-3")
        print("TS RAW OK sig=", r.sig, "fvc=", r.counters.fvc)
    except Exception as e:
        print("TS RAW ERR", type(e).__name__, str(e)[:200])


def test_export_ts_build():
    """Contrôle offline : type EV + ligne avec taxe spécifique -> payload."""
    import json
    from avepay_mcf import certify
    inv = frappe.new_doc("Sales Invoice")
    inv.customer = "Client Comptant"
    inv.company = "AvePLUS"
    inv.currency = "XOF"
    inv.avepay_invoice_type = "EV"
    inv.append("items", {"item_code": "ART-TEST", "qty": 2, "rate": 1000,
                         "item_tax_template": "Burkina Faso Tax - A",
                         "avepay_ts_rate": 50, "avepay_ts_desc": "Taxe boisson"})
    inv.set_missing_values()
    inv.calculate_taxes_and_totals()
    inv.name = "TEST-EXPORT-TS"
    s = certify._settings()
    payload = certify.build_payload(inv, s, invoice_type=inv.avepay_invoice_type)
    print("BUILD", json.dumps(payload, default=str))


def test_submit_ts():
    """Certif réelle d'une FV avec taxe spécifique (firmware : TSR × qté = TS)."""
    inv = frappe.new_doc("Sales Invoice")
    inv.customer = "Client Comptant"
    inv.company = "AvePLUS"
    inv.currency = "XOF"
    inv.due_date = frappe.utils.nowdate()
    inv.debit_to = "4111 - Clients - A"
    inv.append("items", {"item_code": "ART-TEST", "qty": 2, "rate": 1000,
                         "item_tax_template": "Burkina Faso Tax - A",
                         "income_account": "7011 - Dans la Région - A",
                         "avepay_ts_rate": 50, "avepay_ts_desc": "Taxe boisson"})
    inv.insert(ignore_permissions=True)
    inv.submit()
    inv.reload()
    print("TS SUBMIT name=", inv.name, "status=", inv.get("avepay_status"),
          "sec=", inv.get("avepay_codesecef"), "fvc=", inv.get("avepay_fvc"))
    frappe.db.commit()


def test_credit_note(original=None):
    """Crée un avoir (return) lié à une facture certifiée -> mcf.credit_note (FA)."""
    from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_sales_return
    if not original:
        original = frappe.db.get_value(
            "Sales Invoice",
            {"docstatus": 1, "is_return": 0, "avepay_codesecef": ["not in", [None, ""]]},
            "name", order_by="creation desc")
    print("ORIG=", original)
    ret = make_sales_return(original)
    ret.insert(ignore_permissions=True)
    ret.submit()
    ret.reload()
    print("CREDIT OK name=", ret.name, "status=", ret.get("avepay_status"),
          "sec=", ret.get("avepay_codesecef"), "fvc=", ret.get("avepay_fvc"),
          "return_against=", ret.return_against)
    frappe.db.commit()


def test_guard():
    """Vérifie qu'un garde-fou refuse une facture non conforme (devise != XOF)."""
    inv = frappe.new_doc("Sales Invoice")
    inv.customer = "Client Comptant"
    inv.company = "AvePLUS"
    inv.currency = "USD"
    inv.conversion_rate = 600
    inv.append("items", {"item_code": "ART-TEST", "qty": 1, "rate": 1000,
                         "item_tax_template": "Burkina Faso Tax - A"})
    inv.set_missing_values()
    inv.calculate_taxes_and_totals()
    try:
        from avepay_mcf import certify
        certify.validate_certifiable(inv)
        print("GUARD FAIL : aucune exception levée")
    except frappe.ValidationError as e:
        print("GUARD OK : facture USD refusée ->", str(e)[:80])


def _set_setting(field, value):
    frappe.db.set_value("AvePay Settings", "AvePay Settings", field, value)
    frappe.clear_document_cache("AvePay Settings", "AvePay Settings")


def test_queue_mode():
    """E2E mode file d'attente : MCF injoignable au submit -> 'En attente' -> retry_pending certifie."""
    from avepay_mcf import certify
    good_url = "http://host.docker.internal:9080"
    _set_setting("offline_behavior", "File d'attente")
    _set_setting("base_url", "http://127.0.0.1:9999")  # port mort -> NETWORK_ERROR
    try:
        inv = frappe.new_doc("Sales Invoice")
        inv.customer = "Client Comptant"
        inv.company = "AvePLUS"
        inv.currency = "XOF"
        inv.due_date = frappe.utils.nowdate()
        inv.debit_to = "4111 - Clients - A"
        inv.append("items", {"item_code": "ART-TEST", "qty": 1, "rate": 1000,
                             "item_tax_template": "Burkina Faso Tax - A",
                             "income_account": "7011 - Dans la Région - A"})
        inv.insert(ignore_permissions=True)
        inv.submit()
        inv.reload()
        print("QUEUE step1 submit -> status=", inv.get("avepay_status"),
              "sec=", inv.get("avepay_codesecef"))
        # rétablir la connexion et lancer le rattrapage
        _set_setting("base_url", good_url)
        certify.retry_pending()
        inv.reload()
        print("QUEUE step2 retry -> status=", inv.get("avepay_status"),
              "sec=", inv.get("avepay_codesecef"), "fvc=", inv.get("avepay_fvc"))
    finally:
        _set_setting("base_url", good_url)
        _set_setting("offline_behavior", "Bloquer la validation")
        frappe.db.commit()


def test_render_pdf(invoice=None):
    """Génère le PDF de la facture certifiée dans /tmp/avepay-facture.pdf (conteneur)."""
    if not invoice:
        invoice = frappe.get_last_doc("Sales Invoice").name
    pdf = frappe.get_print("Sales Invoice", invoice, print_format=PRINT_FORMAT_NAME, as_pdf=True)
    with open("/tmp/avepay-facture.pdf", "wb") as f:
        f.write(pdf)
    print("PDF OK invoice=", invoice, "bytes=", len(pdf))


def fix_company_accounting():
    """Complète la config comptable d'AvePLUS pour permettre la soumission de factures (test-data)."""
    c = frappe.get_doc("Company", "AvePLUS")
    if not c.round_off_account:
        c.round_off_account = "657 - Pénalités et amendes pénales - A"
    if not c.round_off_cost_center:
        c.round_off_cost_center = "Main - A"
    if not c.default_income_account:
        c.default_income_account = "7011 - Dans la Région - A"
    if not c.default_receivable_account:
        c.default_receivable_account = "4111 - Clients - A"
    c.save(ignore_permissions=True)
    frappe.db.commit()
    print("company OK round_off=", c.round_off_account, "income=", c.default_income_account)


def test_submit_invoice():
    """Crée + soumet une vraie Sales Invoice -> les hooks validate/on_submit certifient."""
    inv = frappe.new_doc("Sales Invoice")
    inv.customer = "Client Comptant"
    inv.company = "AvePLUS"
    inv.currency = "XOF"
    inv.due_date = frappe.utils.nowdate()
    inv.debit_to = "4111 - Clients - A"
    inv.append("items", {"item_code": "ART-TEST", "qty": 1, "rate": 1000,
                         "item_tax_template": "Burkina Faso Tax - A",
                         "income_account": "7011 - Dans la Région - A"})
    inv.insert(ignore_permissions=True)
    inv.submit()
    inv.reload()
    print("SUBMIT OK name=", inv.name, "status=", inv.get("avepay_status"),
          "sec=", inv.get("avepay_codesecef"), "fvc=", inv.get("avepay_fvc"),
          "nim=", inv.get("avepay_nim"))
    frappe.db.commit()


def reset_and_create():
    """Repart propre : fixe le mapping module->app, supprime les 3 DocTypes puis recrée."""
    if getattr(frappe.local, "module_app", None) is not None:
        frappe.local.module_app["avepay_mcf"] = "avepay_mcf"
        frappe.local.app_modules.setdefault("avepay_mcf", []).append("avepay_mcf")
    for n in ["AvePay Settings", "AvePay Tax Mapping", "AvePay Payment Mapping"]:
        if frappe.db.exists("DocType", n):
            frappe.delete_doc("DocType", n, force=1, ignore_permissions=True)
    frappe.db.commit()
    create_doctypes()
