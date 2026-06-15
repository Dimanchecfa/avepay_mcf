frappe.ui.form.on("AvePay Settings", {
	refresh(frm) {
		frm.add_custom_button(__("Auto-détecter les mappings"), () => {
			frappe.call({
				method: "avepay_mcf.install.autodetect_mappings",
				freeze: true,
				freeze_message: __("Détection des taxes et modes de paiement…"),
				callback(r) {
					const m = r.message || {};
					frappe.show_alert({
						message: __("Ajoutés : {0} taxe(s), {1} paiement(s). Ignorés (taux non standard) : {2}.", [
							m.added_tax || 0,
							m.added_pay || 0,
							m.skipped_tax || 0,
						]),
						indicator: "green",
					});
					frm.reload_doc();
				},
			});
		});
	},
});
