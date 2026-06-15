# AvePay MCF — certification fiscale pour ERPNext

App Frappe/ERPNext qui certifie **automatiquement** les factures de vente au MCF
(DGI Burkina Faso / SECEF) via l'API AvePay, en réutilisant le SDK Python
[`avepay-mcf`](https://pypi.org/project/avepay-mcf/).

Le caissier valide sa facture comme d'habitude → la certification est transparente →
le **code SECEF**, le **QR** et le compteur **FVC** sont écrits sur la facture et son PDF.

## Fonctionnalités

- **Factures de vente (FV)** : certifiées à la validation (`on_submit`).
- **Avoirs (FA)** : un retour ERPNext (`is_return`) est certifié comme avoir, lié au
  `{NIM}-{FVC}` de la facture d'origine.
- **Export (EV/ET)** : champ *Type de facture MCF* sur la facture.
- **Taxe spécifique (TS)** : champs par ligne *Taxe spécifique / unité (TSR)* + libellé
  (la TS envoyée = TSR × quantité). ⚠️ voir *Limitations*.
- **Print Format** « AvePay Facture Certifiee » : facture normalisée + QR + mentions DGI.
- **Garde-fous** bloquants à la validation (devise XOF, IFU obligatoire pour les
  personnes morales, groupe SECEF résolu par ligne, etc.).
- **Hors-ligne** : au choix *bloquer la validation* ou *file d'attente* (certif différée
  par un job planifié toutes les 10 min).

## Pré-requis

- ERPNext / Frappe (testé sur **v16**).
- Accès à un orchestrateur AvePay MCF (cloud ou local) + une **clé API** `ak_live_…`
  scopée sur le **NIM** du marchand.

## Installation

```bash
# 1. récupérer l'app dans le bench
bench get-app avepay_mcf <url-du-repo>

# 2. installer le SDK dans l'environnement bench
./env/bin/pip install avepay-mcf

# 3. installer l'app sur le site
bench --site <site> install-app avepay_mcf
bench --site <site> migrate
```

> Les **Custom Fields** et le **Print Format** sont livrés en *fixtures* : ils sont créés
> automatiquement à l'installation.

## Configuration (AvePay Settings)

Ouvrir **AvePay Settings** (`/app/avepay-settings`) :

| Champ | Description |
|---|---|
| Base URL | URL de l'orchestrateur (défaut prod : `https://api-mcf-orchestrator.toolsite.io`). Vide ⇒ défaut SDK / env `AVEPAY_BASE_URL`. |
| NIM | Numéro d'identification de la machine (boîtier MCF). |
| ISF | Identifiant système de facturation (défaut `1`). |
| Clé API | Clé `ak_live_…` (stockée chiffrée). |
| Si MCF hors-ligne | *Bloquer la validation* ou *File d'attente*. |
| Mapping taxes | Item Tax Template → groupe SECEF (A..N) + taux. |
| Mapping paiements | Mode of Payment → méthode MCF (E/V/C/M/B/A). |

### Mapping de référence

- **Taxes** : chaque *Item Tax Template* utilisé doit être mappé vers un **groupe SECEF**
  (ex. TVA 18 % → **B**, exonéré → **A**). Une ligne dont la taxe n'est pas mappée
  bloque la validation.
- **Client** : *Individual* → **PP**, *Company* → **PM** (IFU/Tax ID **obligatoire**),
  pas de client → **CC** (comptant).
- **Paiement** : *Mode of Payment* → **E** espèces, **V** virement, **C** chèque,
  **M** mobile money, **B** carte bancaire, **A** à crédit.

## Utilisation

1. Créer une **Sales Invoice** normalement (client, articles avec leur Item Tax Template,
   devise XOF).
2. (Optionnel) *Type de facture MCF* = EV/ET pour un export ; renseigner *TSR* sur une
   ligne pour une taxe spécifique.
3. **Valider** (Submit) : la facture est certifiée. Les champs *Statut MCF*, *Code SECEF*,
   *Compteur FVC*, *NIM*, *Date/heure*, *QR SECEF* se remplissent.
4. **Imprimer** avec le format *AvePay Facture Certifiee*.

Pour un **avoir** : créer un retour (*Create > Return / Credit Note*) depuis une facture
certifiée puis valider — il est certifié comme avoir lié à l'original.

## Limitations connues

- **Taxe spécifique (TS) en production** : le mapping est correct (TS = TSR × qté), mais la
  certification *live* d'une ligne TS est actuellement rejetée par le firmware
  (`E: No amount!`). Le problème se reproduit avec le SDK brut → il est **côté
  orchestrateur/firmware**, pas côté plugin. À lever avant d'activer la TS en prod.

## Génération du PDF (wkhtmltopdf)

Le QR est rendu en **PNG** (wkhtmltopdf gère mal le SVG). En déploiement Docker, si la
génération PDF échoue (`ContentNotFoundError` / *broken image links*), pointer le
`host_name` du site vers le service servant les assets :

```bash
bench --site <site> set-config host_name http://<frontend-nginx>:8080
```

## Développement

`avepay_mcf/setup.py` contient des helpers (`bench --site <site> execute …`) :
`create_doctypes`, `create_custom_fields`, `create_print_format`, `configure_settings`,
`fix_company_accounting`, et des tests manuels `test_mapping`, `test_me`,
`test_submit_invoice`, `test_render_pdf`, `test_guard`, `test_queue_mode`,
`test_credit_note`, `cancel_pending`.

### Licence

MIT
