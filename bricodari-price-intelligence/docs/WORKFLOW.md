# Workflow plateforme Bricodari Price Intelligence

## Principe

Plus de dépôt OneDrive obligatoire. Tout passe par la plateforme.

```
1. Catalogue site (WooCommerce)  → sync automatique depuis bricodari.tn
2. Prix d'achat                  → upload Excel/CSV dans la plateforme
3. Prix concurrents              → upload Excel/CSV dans la plateforme
4. Comparateur                   → calcul écarts / marges / alertes
```

## Détail

### Étape 1 — Catalogue site
- Source : API WooCommerce (bricodari.tn)
- Sync manuelle : bouton "Synchroniser maintenant" (arrière-plan)
- Sync automatique : activée par défaut toutes les 6 h (réglable dans Catalogue)
- Contenu : produits, variantes, prix vente, catégories, URL
- Les SKU déjà renseignés ne sont pas écrasés s'ils sont vides côté WooCommerce

### Étape 2 — Prix d'achat
- Source : fichier Excel/CSV déposé dans la plateforme
- Colonnes : SKU, Désignation, Prix achat, Fournisseur
- Historique conservé dans la base

### Étape 3 — Concurrents
- Source : fichier Excel/CSV déposé dans la plateforme
- Colonnes : SKU, Concurrent, Prix, URL
- Gestion de la liste des concurrents dans l’écran dédié

### Étape 4 — Comparaison
- Rapprochement par SKU (puis nom si besoin)
- Calcul : écart vs concurrent min, marge, alerte
- Export CSV pour la direction

## Règle métier
La plateforme **n’écrit jamais** automatiquement les prix sur le site.
Elle aide à décider.
