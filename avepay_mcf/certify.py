"""Certification des factures ERPNext au MCF via le SDK `avepay-mcf`.

Branché sur Sales Invoice (cf. hooks.py) :
  - validate  -> validate_certifiable (garde-fous, refuse une facture non certifiable)
  - on_submit -> certify_invoice (mappe -> mcf.certify() -> écrit codeSecef/QR/FVC)
"""

import frappe
from frappe import _

OFFLINE_BLOCK = "Bloquer la validation"

STATUS_CERTIFIED = "Certifiee"
STATUS_QUEUED = "En attente"
STATUS_ERROR = "Erreur"


def _settings():
    return frappe.get_single("AvePay Settings")


def _client(s):
    from avepay.mcf import AvePay
    return AvePay(api_key=s.get_password("api_key"), base_url=(s.base_url or None), isf=(s.isf or "1"))


# ---- mapping helpers --------------------------------------------------

def _customer_payload(doc):
    """Customer ERPNext -> {type CC/PP/PM, ifu, name}."""
    cust = frappe.get_doc("Customer", doc.customer) if doc.customer else None
    if not cust:
        return {"type": "CC"}
    ctype = "PM" if cust.customer_type == "Company" else "PP"
    payload = {"type": ctype, "name": doc.customer_name or cust.customer_name}
    if cust.tax_id:
        payload["ifu"] = cust.tax_id
    return payload


def code(value):
    """Extrait le code nu d'une valeur de Select descriptive (« B — TVA 18 % » -> « B »)."""
    v = (value or "").strip()
    return v.split(" ", 1)[0] if v else ""


def _tax_group(s, item_tax_template):
    for m in s.tax_mappings or []:
        if m.item_tax_template == item_tax_template:
            return code(m.secef_group), (m.tax_rate or 0)
    return None, None


def _payment_method(s, mode_of_payment):
    for m in s.payment_mappings or []:
        if m.mode_of_payment == mode_of_payment:
            return code(m.method)
    return None


def _items_payload(doc, s):
    items = []
    for it in doc.items:
        tpl = it.item_tax_template
        group, rate = _tax_group(s, tpl)
        if not group:
            frappe.throw(_("Ligne « {0} » : la taxe « {1} » n'est pas associée à un groupe SECEF "
                           "(à configurer dans AvePay Settings).").format(it.item_name, tpl or "—"))
        # ERPNext: prix HT par défaut -> TTC = HT * (1 + taux/100). priceMode TTC côté MCF.
        # abs() : les avoirs (is_return) portent des quantités/montants négatifs.
        ttc = int(round(abs(it.amount or 0) * (1 + (rate or 0) / 100.0)))
        qty = abs(it.qty or 1)
        line = {
            "name": (it.item_name or it.item_code)[:64],
            "taxGroup": group,
            "taxRate": rate,
            "unitPrice": int(round(ttc / qty)) if qty else ttc,
            "quantity": qty,
            "amountTtc": ttc,
        }
        # Taxe spécifique (TS) : TSR par unité -> specificTax = TSR × qté (règle firmware ELTRADE).
        tsr = abs(it.get("avepay_ts_rate") or 0)
        if tsr:
            line["specificTaxRate"] = tsr
            line["specificTax"] = int(round(tsr * qty))
            line["specificTaxDesc"] = it.get("avepay_ts_desc") or _("Taxe spécifique")
        items.append(line)
    return items


def _payments_payload(doc, s, total_ttc):
    """POS -> doc.payments ; sinon paiement unique au total (mode par défaut)."""
    pays = []
    if getattr(doc, "is_pos", 0) and doc.get("payments"):
        for p in doc.payments:
            method = _payment_method(s, p.mode_of_payment)
            if not method:
                frappe.throw(_("Mode de paiement « {0} » non mappé (AvePay Settings).").format(p.mode_of_payment))
            if p.amount:
                pays.append({"method": method, "amount": int(round(abs(p.amount)))})
    if not pays:
        # Facture non-POS : ERPNext ne porte pas le mode de paiement -> espèces (E) par convention.
        pays.append({"method": "E", "amount": total_ttc})
    return pays


def build_payload(doc, s, invoice_type="FV", credit_ref=None):
    items = _items_payload(doc, s)
    total = sum(i["amountTtc"] for i in items)
    payload = {
        "number": doc.name,
        "type": invoice_type,
        "operator": {"id": (frappe.session.user or "1"),
                     "name": frappe.utils.get_fullname(frappe.session.user) or "Operateur"},
        "customer": _customer_payload(doc),
        "items": items,
        "payments": _payments_payload(doc, s, total),
    }
    if credit_ref:
        payload["creditNoteRef"] = credit_ref
        payload["creditNoteNature"] = "COR"
    return payload


def _credit_ref(doc):
    """Référence MCF de l'avoir = {NIM}-{FVC} de la facture d'origine (déjà certifiée)."""
    if not doc.get("return_against"):
        frappe.throw(_("AvePay : un avoir doit référencer une facture d'origine (return_against)."))
    orig = frappe.db.get_value("Sales Invoice", doc.return_against,
                               ["avepay_nim", "avepay_fvc"], as_dict=True)
    if not orig or not orig.avepay_nim or not orig.avepay_fvc:
        frappe.throw(_("AvePay : la facture d'origine « {0} » n'est pas certifiée — "
                       "impossible d'émettre l'avoir.").format(doc.return_against))
    return "{0}-{1}".format(orig.avepay_nim, orig.avepay_fvc)


# ---- garde-fous (validate) -------------------------------------------

def validate_certifiable(doc, method=None):
    if doc.get("avepay_codesecef"):
        return  # déjà certifiée
    s = _settings()
    if not s.nim or not s.get_password("api_key"):
        frappe.throw(_("AvePay : NIM ou clé API manquant dans AvePay Settings."))
    if not doc.items:
        frappe.throw(_("AvePay : la facture doit comporter au moins une ligne."))
    if doc.get("is_return"):
        _credit_ref(doc)  # lève si la facture d'origine est absente ou non certifiée
    if doc.currency and doc.currency != "XOF":
        frappe.throw(_("AvePay : la devise doit être XOF (facture en {0}).").format(doc.currency))
    cust = frappe.get_doc("Customer", doc.customer) if doc.customer else None
    if cust and cust.customer_type == "Company" and not cust.tax_id:
        frappe.throw(_("AvePay : le client « {0} » est une personne morale — l'IFU (Tax ID) est obligatoire.")
                     .format(doc.customer_name or doc.customer))
    # chaque ligne doit avoir un groupe SECEF résolu
    for it in doc.items:
        group, _r = _tax_group(s, it.item_tax_template)
        if not group:
            frappe.throw(_("AvePay : ligne « {0} » — taxe « {1} » non mappée vers un groupe SECEF.")
                         .format(it.item_name, it.item_tax_template or "—"))
    # POS : chaque mode de paiement doit être mappé vers une méthode MCF
    if getattr(doc, "is_pos", 0) and doc.get("payments"):
        for p in doc.payments:
            if (p.amount or 0) and not _payment_method(s, p.mode_of_payment):
                frappe.throw(_("AvePay : mode de paiement « {0} » non mappé vers une méthode MCF "
                               "(AvePay Settings).").format(p.mode_of_payment))


# ---- certification (on_submit) ---------------------------------------

def certify_invoice(doc, method=None):
    if doc.get("avepay_codesecef"):
        return  # idempotent
    s = _settings()
    is_return = bool(doc.get("is_return"))
    if is_return:
        payload = build_payload(doc, s, invoice_type="FA", credit_ref=_credit_ref(doc))
    else:
        payload = build_payload(doc, s, invoice_type=(doc.get("avepay_invoice_type") or "FV"))
    try:
        from avepay.mcf import AvePayError
        mcf = _client(s).mcf(s.nim)
        if is_return:
            receipt = mcf.credit_note(payload, idempotency_key=doc.name)
        else:
            receipt = mcf.certify(payload, idempotency_key=doc.name)
    except AvePayError as e:
        msg = _("Certification MCF échouée : [{0}] {1}").format(e.code, e.message)
        if (s.offline_behavior or OFFLINE_BLOCK) == OFFLINE_BLOCK:
            frappe.throw(msg)
        # mode file d'attente : la facture est validée, certif différée (job retry_pending)
        doc.db_set("avepay_status", STATUS_QUEUED)
        frappe.log_error(msg, "AvePay MCF")
        return

    _write_receipt(doc, receipt)


def _write_receipt(doc, receipt):
    doc.db_set("avepay_codesecef", receipt.sig)
    doc.db_set("avepay_qr", receipt.qr)
    doc.db_set("avepay_fvc", receipt.counters.fvc)
    doc.db_set("avepay_nim", receipt.nim)
    doc.db_set("avepay_datetime", _receipt_datetime(receipt))
    doc.db_set("avepay_status", STATUS_CERTIFIED)


def retry_pending():
    """Job planifié (mode file d'attente) : re-certifie les factures soumises non encore certifiées."""
    s = _settings()
    if (s.offline_behavior or OFFLINE_BLOCK) == OFFLINE_BLOCK:
        return  # mode bloquant : rien à rattraper
    names = frappe.get_all(
        "Sales Invoice",
        filters={"docstatus": 1, "avepay_codesecef": ["in", [None, ""]],
                 "avepay_status": ["in", [STATUS_QUEUED, STATUS_ERROR]]},
        pluck="name",
    )
    for name in names:
        try:
            certify_invoice(frappe.get_doc("Sales Invoice", name))
        except Exception:
            frappe.log_error(frappe.get_traceback(), "AvePay MCF retry_pending")


def _receipt_datetime(receipt):
    """Date/heure de certification : champ du reçu, sinon dernier segment du QR (YYYYMMDDHHMMSS)."""
    dt = getattr(receipt, "dateTime", None)
    if dt is not None:
        return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)
    qr = getattr(receipt, "qr", None) or ""
    raw = qr.split(";")[-1] if ";" in qr else ""
    if len(raw) == 14 and raw.isdigit():
        return "{0}-{1}-{2} {3}:{4}:{5}".format(raw[0:4], raw[4:6], raw[6:8], raw[8:10], raw[10:12], raw[12:14])
    return raw or None
