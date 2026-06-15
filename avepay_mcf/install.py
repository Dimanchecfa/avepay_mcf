"""Auto-configuration des mappings (taxes / paiements) à l'installation et à la demande.

- after_install : tente de pré-remplir les mappings depuis les données ERPNext existantes.
- autodetect_mappings : whitelisted, rejouable (bouton « Auto-détecter les mappings »).
"""

import frappe

# Valeurs de Select (doivent matcher les options du DocType AvePay Tax Mapping).
GROUP_EXONERE = "A — Exonéré (0 %)"
GROUP_TVA18 = "B — TVA taxable (18 %)"
GROUP_TVA10 = "C — TVA taxable (10 %)"

# Heuristique nom du Mode of Payment -> méthode MCF (valeur de Select descriptive).
PAYMENT_RULES = [
    (("cash", "espèce", "especes", "comptant"), "E — Espèces"),
    (("virement", "transfer", "wire", "bank"), "V — Virement"),
    (("chèque", "cheque", "check"), "C — Chèque"),
    (("mobile", "momo", "orange money", "moov", "wave", "money"), "M — Mobile money"),
    (("carte", "card", "visa", "master"), "B — Carte bancaire"),
    (("crédit", "credit"), "A — À crédit"),
]
PAYMENT_DEFAULT = "E — Espèces"


def after_install():
    try:
        autodetect_mappings()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "AvePay MCF after_install")


def _template_rate(tpl):
    doc = frappe.get_doc("Item Tax Template", tpl)
    rates = [t.tax_rate for t in (doc.taxes or []) if t.tax_rate is not None]
    return max(rates) if rates else 0


def _group_for_rate(rate):
    if rate == 0:
        return GROUP_EXONERE, 0
    if 17 <= rate <= 19:
        return GROUP_TVA18, rate
    if 9 <= rate <= 11:
        return GROUP_TVA10, rate
    return None, rate  # taux non standard (régime spécial) -> à mapper manuellement


def _method_for_payment(name):
    low = (name or "").lower()
    for needles, method in PAYMENT_RULES:
        if any(n in low for n in needles):
            return method
    return PAYMENT_DEFAULT


@frappe.whitelist()
def autodetect_mappings():
    """Pré-remplit les mappings taxes/paiements manquants depuis ERPNext. Rejouable."""
    s = frappe.get_single("AvePay Settings")
    added_tax = added_pay = skipped_tax = 0

    seen_tpl = {m.item_tax_template for m in (s.tax_mappings or [])}
    for tpl in frappe.get_all("Item Tax Template", pluck="name"):
        if tpl in seen_tpl:
            continue
        group, rate = _group_for_rate(_template_rate(tpl))
        if not group:
            skipped_tax += 1  # taux non standard : à mapper manuellement
            continue
        s.append("tax_mappings", {"item_tax_template": tpl, "secef_group": group, "tax_rate": rate})
        added_tax += 1

    seen_pay = {m.mode_of_payment for m in (s.payment_mappings or [])}
    for mop in frappe.get_all("Mode of Payment", pluck="name"):
        if mop in seen_pay:
            continue
        s.append("payment_mappings", {"mode_of_payment": mop, "method": _method_for_payment(mop)})
        added_pay += 1

    s.save(ignore_permissions=True)
    frappe.db.commit()
    return {"added_tax": added_tax, "added_pay": added_pay, "skipped_tax": skipped_tax}
