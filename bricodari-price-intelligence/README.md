# Bricodari Price Intelligence

Comparateur de prix pour [bricodari.tn](https://bricodari.tn). La plateforme rassemble le catalogue du site, les prix d'achat et les prix des concurrents, puis calcule écarts, marges et alertes.

Elle aide à décider. Elle n'écrit jamais les prix sur WooCommerce.

Ce dépôt couvre la veille prix (partie 3 du cahier des charges). Les autres parties (affiches, blog, devis WhatsApp, CRM) ne sont pas dans ce code.

## À quoi sert la plateforme

Quatre sources alimentent un tableau unique :

| Source | D'où ça vient | Ce qu'on en retient |
|---|---|---|
| Catalogue site | API WooCommerce de bricodari.tn | Produits, variantes, SKU, prix de vente, catégorie, URL |
| Prix d'achat | Fichier Excel ou CSV déposé dans l'interface | Dernier prix d'achat, fournisseur, historique |
| Prix concurrents | Fichier Excel ou CSV déposé dans l'interface | Prix observé, site, lien produit |
| Comparateur | Calcul interne | Écart vs le moins cher, marge estimée, alerte |

Le rapprochement se fait par **SKU** (UGS WooCommerce = code article). Les prix sont en **TND**.

## Workflow

```
bricodari.tn (WooCommerce)
        │  sync manuelle ou automatique (toutes les 6 h)
        ▼
   Catalogue local
        │
Prix d'achat (Excel/CSV) ──► Base ──► Comparateur ──► Tableau, alertes, export CSV
        │
Prix concurrents (Excel/CSV)
```

### 1. Catalogue site

- Source : API REST WooCommerce (`WOOCOMMERCE_URL`, clés lecture dans `.env`).
- Lancement manuel : écran **Catalogue site**, bouton de synchronisation. La sync tourne en arrière-plan.
- Lancement automatique : activé par défaut toutes les 6 heures. L'intervalle se règle dans le même écran (1 à 168 heures) et dans `.env` (`WOO_SYNC_ENABLED`, `WOO_SYNC_INTERVAL_HOURS`).
- Contenu importé : produits, variantes, prix affiché, catégories, URL, statut de stock.
- Un SKU déjà présent n'est pas écrasé par une valeur vide venue de WooCommerce.

### 2. Prix d'achat

- Dépôt d'un `.xlsx`, `.xls` ou `.csv` dans l'écran **Prix d'achat**.
- Colonnes reconnues (noms flexibles) : SKU / UGS / code, désignation, prix d'achat, fournisseur, marque, EAN, devise, unité.
- Chaque import est conservé. Le comparateur utilise la **dernière** ligne du SKU.
- Exemple : `docs/exemple_prix_erp.csv`.

### 3. Concurrents

- Liste des sites dans l'écran **Concurrents** (nom + URL).
- Dépôt d'un fichier avec au minimum : **SKU**, **Concurrent**, **Prix**. Colonnes optionnelles : nom produit, URL, devise.
- Le fichier crée ou met à jour le concurrent, le produit concurrent (référence = SKU) et une observation de prix datée.

### 4. Comparaison

- Bouton de recalcul dans **Comparateur** (`POST /api/comparisons/rebuild`).
- Périmètre : produits catalogue qui ont un SKU, hors variantes.
- Pour chaque produit :

| Indicateur | Règle |
|---|---|
| Prix de vente | Prix affiché WooCommerce |
| Prix d'achat | Dernier enregistrement ERP du même SKU |
| Prix concurrent min / max | Dernière observation, via correspondance validée ou référence fabricant = SKU |
| Écart | Prix de vente − prix concurrent minimum |
| Marge estimée | (vente − achat) / vente |
| Alerte **Trop cher** | Écart supérieur à +10 % |
| Alerte **Moins cher** | Écart inférieur à −5 % |
| Alerte **Aligné** | Entre −5 % et +10 % |

- Filtres par texte et par niveau d'alerte.
- Export direction : `GET /api/comparisons/export.csv`.
- L'écran **Alertes** reprend les lignes « trop cher » et « moins cher ».
- L'écran **Historique** liste les imports et synchronisations.

## Écrans

| Écran | Rôle |
|---|---|
| Tableau de bord | Compteurs des 4 étapes et état de santé |
| 1. Catalogue site | Recherche, sync manuelle, planning automatique |
| 2. Prix d'achat | Upload ERP et dernières lignes importées |
| 3. Concurrents | Fiches sites + upload des prix marché |
| 4. Comparateur | Tableau des écarts, recalcul, export |
| Alertes | Écarts hors bande |
| Historique | Jobs d'import et de sync |

Interface : [http://127.0.0.1:5173](http://127.0.0.1:5173)  
API et essai des routes : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Architecture

```
frontend/          React + Vite (port 5173, proxy /api vers le backend)
backend/app/
  api/             Routes FastAPI
  woo_commerce/    Client et sync catalogue
  imports/         Lecture Excel/CSV (achat et concurrents)
  pricing/         Calcul des comparaisons
  core/            Config, base, planificateur
  models/          Tables SQLAlchemy
docker-compose.yml PostgreSQL 16 + Redis 7 + API (quand Docker est installé)
docs/              Checklist, workflow court, exemple CSV
scripts/           Contrôles et jeux de démonstration
```

En local, la base par défaut est SQLite (`bricodari.db`, non versionnée). Docker bascule l'API sur PostgreSQL.

Principales tables : `products`, `erp_price_records`, `competitors`, `competitor_products`, `competitor_price_observations`, `price_comparisons`, `import_jobs`. Les modèles fournisseurs (`suppliers`, `supplier_offers`) sont prêts ; l'import des listes fournisseurs n'est pas encore branché à l'écran.

## Démarrage local (Windows)

Prérequis : Python 3.11 et Node.js.

```powershell
cd bricodari-price-intelligence
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
copy .env.example .env
```

Renseigner dans `.env` la Consumer Key et le Consumer Secret WooCommerce (lecture seule) :

WordPress → WooCommerce → Réglages → Avancé → API REST → Ajouter une clé.

Deux terminaux :

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

```powershell
cd frontend
npm install
npm run dev
```

Avec Docker Desktop, depuis la racine du projet : `docker compose up --build`. Le fichier `.env` doit exister ; Compose force `DATABASE_URL` vers PostgreSQL.

## API utile

| Méthode | URL | Action |
|---|---|---|
| GET | `/api/health` | Santé et présence des clés Woo |
| GET | `/api/dashboard` | Compteurs du tableau de bord |
| GET | `/api/woocommerce/test` | Test de connexion WooCommerce |
| POST | `/api/woocommerce/sync` | Sync catalogue en arrière-plan |
| GET | `/api/woocommerce/sync/status` | État et prochaine exécution |
| PUT | `/api/woocommerce/sync/schedule` | Activer / changer l'intervalle |
| GET | `/api/products` | Catalogue local (`q`, `limit`) |
| POST | `/api/imports/erp/upload` | Import prix d'achat |
| POST | `/api/imports/competitors/upload` | Import prix concurrents |
| GET/POST/DELETE | `/api/competitors` | Liste des sites |
| POST | `/api/comparisons/rebuild` | Recalculer les écarts |
| GET | `/api/comparisons` | Lignes comparatives |
| GET | `/api/comparisons/export.csv` | Export CSV |
| GET | `/api/jobs` | Historique des traitements |

`POST /api/woocommerce/sync?max_products=20` limite le volume pour un essai.

## Ce que Git contient

Versionné : code, `docker-compose.yml`, `.env.example`, documentation, exemple CSV.

Ignoré (voir `.gitignore`) :

- `.env` (clés WooCommerce et secret applicatif)
- `.venv/`, `node_modules/`
- `*.db` (base SQLite locale)
- `uploads/*` (fichiers déposés dans la plateforme)
- exports Excel de travail

Les fichiers déposés par les utilisateurs passent par l'interface. Ils ne remplacent pas le dépôt Git.

## Hors périmètre actuel

- Écriture des prix vers WooCommerce
- Crawl automatique des sites concurrents (les prix marché arrivent par fichier)
- Connexion directe à Sage ou Google Drive
- Import des listes fournisseurs PDF
