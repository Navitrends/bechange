# Bechange — Bricodari

Documentation du dépôt **Navitrends/bechange**.

Ce projet automatise et modernise plusieurs activités Bricodari. La partie livrée dans ce code est la **veille concurrentielle & prix** (plateforme *Bricodari Price Intelligence*).

Site concerné : [bricodari.tn](https://bricodari.tn)

---

## Contenu du dépôt

| Élément | Rôle |
|---------|------|
| [`bricodari-price-intelligence/`](bricodari-price-intelligence/) | Plateforme comparateur de prix (backend + frontend) |
| [`Cahier_des_charges.md`](Cahier_des_charges.md) | Cahier des charges global (version simplifiée) |
| [`Cahier_des_charges_Bricodari_Comparateur_Prix.md`](Cahier_des_charges_Bricodari_Comparateur_Prix.md) | CDC détaillé du comparateur |
| `generate_docx.py` | Génération des versions Word du CDC |

Documentation technique détaillée de la plateforme :  
→ [`bricodari-price-intelligence/README.md`](bricodari-price-intelligence/README.md)

---

## Plateforme Price Intelligence — en bref

Elle centralise **3 sources** et produit un **tableau de décision** :

1. **Catalogue site** — sync WooCommerce (bricodari.tn)
2. **Prix d’achat** — import Excel/CSV (ERP)
3. **Prix concurrents** — import Excel/CSV
4. **Comparateur** — écarts, marges, alertes, export CSV

**Règle métier :** la plateforme **n’écrit jamais** automatiquement les prix sur le site. Elle aide à décider.

```
WooCommerce (catalogue)
        │
        ▼
Prix d'achat (Excel) ──► Base ──► Comparateur ──► Alertes + export
        ▲
Prix concurrents (Excel)
```

### Workflow opérationnel

| Étape | Écran | Action |
|-------|--------|--------|
| 1 | Catalogue site | Sync manuelle ou auto (toutes les 6 h) |
| 2 | Prix d’achat | Upload fichier ERP (SKU, prix, fournisseur) |
| 3 | Concurrents | Gérer les sites + upload des prix marché |
| 4 | Comparateur | Recalculer, filtrer, exporter |

Alertes typiques :

- **Trop cher** — vente > concurrent min de plus de ~10 %
- **Moins cher** — vente < concurrent min de plus de ~5 %
- **Aligné** — dans la bande

---

## Architecture technique

```
bricodari-price-intelligence/
├── backend/          FastAPI + SQLAlchemy + sync WooCommerce
├── frontend/         React + Vite (interface métier)
├── docs/             Workflow, checklist, exemples CSV
├── scripts/          Outils de contrôle / démo
├── docker-compose.yml
└── .env.example
```

| Couche | Techno |
|--------|--------|
| API | FastAPI (port 8000) |
| UI | React 19 + Vite (port 5173) |
| Base locale | SQLite |
| Prod / Docker | PostgreSQL + Redis |
| Catalogue | WooCommerce REST API |

---

## Démarrage rapide

```powershell
cd bricodari-price-intelligence
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
copy .env.example .env
# Renseigner WOOCOMMERCE_CONSUMER_KEY / SECRET dans .env
```

**Terminal 1 — API**

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Interface**

```powershell
cd frontend
npm install
npm run dev
```

| URL | Usage |
|-----|--------|
| http://127.0.0.1:5173 | Interface métier |
| http://127.0.0.1:8000/docs | Documentation API (Swagger) |

Clés WooCommerce : WordPress → WooCommerce → Réglages → Avancé → API REST → clé **lecture**.

---

## Documentation liée

| Document | Contenu |
|----------|---------|
| [bricodari-price-intelligence/README.md](bricodari-price-intelligence/README.md) | Doc complète plateforme (écrans, API, Git) |
| [bricodari-price-intelligence/docs/WORKFLOW.md](bricodari-price-intelligence/docs/WORKFLOW.md) | Workflow métier court |
| [bricodari-price-intelligence/docs/CHECKLIST_DEMARRAGE.md](bricodari-price-intelligence/docs/CHECKLIST_DEMARRAGE.md) | Prérequis Phase 1–2 |
| [Cahier_des_charges.md](Cahier_des_charges.md) | Vue d’ensemble des 5 parties du projet Bechange |

---

## Périmètre Bechange (hors code actuel)

Le cahier des charges global prévoit aussi :

1. Affiches réseaux sociaux  
2. Blog intelligent SEO & GEO  
3. **Veille prix** ← ce dépôt  
4. Devis automatiques via WhatsApp  
5. Remplacement Mautic / CRM emails  

---

## Ce qui ne doit pas être committé

- `.env` (secrets WooCommerce)
- `.venv/`, `node_modules/`
- bases SQLite (`*.db`)
- fichiers uploadés / exports métier sensibles

Voir `.gitignore` dans `bricodari-price-intelligence/`.
