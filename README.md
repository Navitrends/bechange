# Bricodari — Guide d’utilisation

**Comparateur de prix & veille concurrentielle**

Ce guide s’adresse aux équipes Bricodari (achats, pricing, direction).  
Il explique **comment utiliser la plateforme au quotidien**, pas comment elle est construite.

Site concerné : [bricodari.tn](https://bricodari.tn)

---

## À quoi sert l’outil ?

En quelques minutes, vous voyez pour chaque produit :

- le **prix affiché sur votre site**
- votre **dernier prix d’achat**
- les **prix des concurrents**
- si vous êtes **trop cher**, **moins cher** ou **aligné**

La plateforme **aide à décider**.  
Elle **ne change jamais automatiquement** les prix sur le site.

---

## Parcours en 4 étapes

Suivez toujours cet ordre :

```
1. Catalogue site  →  2. Prix d’achat  →  3. Concurrents  →  4. Comparateur
```

| Étape | Menu | Ce que vous faites |
|-------|------|--------------------|
| 1 | **Catalogue site** | Récupérer les produits et prix de vente du site |
| 2 | **Prix d’achat** | Déposer le fichier Excel des prix d’achat |
| 3 | **Concurrents** | Ajouter les sites concurrents + déposer leurs prix |
| 4 | **Comparateur** | Lire les écarts, alertes, et exporter pour la direction |

---

## Étape 1 — Catalogue site

**But :** avoir la liste à jour des produits vendus sur bricodari.tn.

1. Ouvrez le menu **1. Catalogue site**
2. Cliquez sur **Synchroniser maintenant**
3. Attendez la fin de la synchronisation (elle tourne en arrière-plan)
4. Vérifiez que le nombre de produits augmente

**Astuce :** une synchronisation automatique peut tourner régulièrement (par défaut toutes les 6 heures). Vous pouvez l’activer, la désactiver ou changer la fréquence dans le même écran.

---

## Étape 2 — Prix d’achat

**But :** indiquer à la plateforme votre dernier coût d’achat.

1. Ouvrez **2. Prix d’achat**
2. Préparez un fichier Excel (ou CSV) avec au minimum :

| Colonne | Exemple |
|---------|---------|
| SKU (code article) | `AB-12345` |
| Désignation | Perceuse 18V |
| Prix achat | `45.500` |
| Fournisseur | Nom du fournisseur |

3. Déposez / importez le fichier dans l’écran
4. Vérifiez le message de confirmation (lignes importées)

**Important :** le code article (**SKU**) doit être le **même** que sur le site. Sinon le produit ne sera pas rapproché.

Chaque import est conservé. Le comparateur utilise toujours le **dernier** prix d’achat connu pour un SKU.

---

## Étape 3 — Concurrents

**But :** renseigner les prix observés chez les concurrents.

### A. Enregistrer un concurrent

1. Ouvrez **3. Concurrents**
2. Saisissez le **nom** du concurrent et l’**adresse du site**
3. Validez l’ajout

### B. Importer les prix

Préparez un fichier Excel (ou CSV) avec au minimum :

| Colonne | Exemple |
|---------|---------|
| SKU | `AB-12345` |
| Concurrent | Nom du site |
| Prix | `59.900` |
| URL (optionnel) | Lien vers la fiche produit |

Puis importez le fichier dans le même écran.

---

## Étape 4 — Comparateur

**But :** voir qui est plus cher / moins cher, et décider.

1. Ouvrez **4. Comparateur**
2. Cliquez sur **Lancer comparaison** (ou le bouton équivalent dans la barre latérale)
3. Parcourez le tableau :

| Colonne | Signification |
|---------|----------------|
| Prix site | Votre prix de vente |
| Prix d’achat | Votre dernier coût |
| Concurrent min | Prix le plus bas observé |
| Écart | Différence vs le concurrent le moins cher |
| Marge | Estimation de marge |
| Alerte | Statut prix |

### Comprendre les alertes

| Alerte | Signification | Action typique |
|--------|---------------|----------------|
| **Trop cher** | Vous êtes nettement au-dessus du marché | Revoir le prix de vente |
| **Moins cher** | Vous êtes nettement en dessous | Vérifier la marge / opportunité |
| **Aligné** | Vous êtes dans une zone correcte | Pas d’action urgente |

### Filtrer et exporter

- Filtrez par texte (nom, SKU, catégorie) ou par type d’alerte
- Menu **Alertes** : vue concentrée sur les écarts importants
- Bouton **Export CSV** : fichier pour la direction / Excel

---

## Routine recommandée (chaque semaine)

1. Vérifier que le **catalogue** est à jour (sync si besoin)
2. Importer le **dernier fichier de prix d’achat**
3. Importer / mettre à jour les **prix concurrents**
4. Lancer la **comparaison**
5. Traiter d’abord les alertes **Trop cher**
6. Exporter le CSV pour la réunion pricing / direction

---

## Les autres écrans

| Écran | Utilité |
|-------|---------|
| **Tableau de bord** | Vue d’ensemble : combien de produits, imports, alertes |
| **Alertes** | Uniquement les produits hors zone |
| **Historique** | Suivi des imports et synchronisations déjà faits |

---

## Points d’attention

- Le **SKU** est la clé de tout. Sans SKU commun entre site, achat et concurrent, pas de comparaison fiable.
- Un fichier mal formaté (colonnes manquantes, mauvais séparateur) peut importer 0 ligne : vérifiez le message après upload.
- La plateforme **ne publie pas** les nouveaux prix sur le site : la décision et la mise à jour restent humaines.
- Plus besoin de déposer les fichiers “quelque part sur OneDrive” : **tout se dépose dans la plateforme**.

---

## En cas de problème

| Situation | Que faire |
|-----------|-----------|
| “Site non configuré” | Demander à l’équipe technique de brancher l’accès au site |
| Aucun produit après sync | Relancer la sync ; sinon contacter le support |
| Import à 0 ligne | Vérifier les noms de colonnes (SKU, prix…) |
| Produit absent du comparateur | Vérifier que le SKU existe côté site **et** dans vos fichiers |
| Écarts bizarres | Vérifier que le fichier concurrents utilise le bon SKU |

---

## Pour aller plus loin (équipe technique)

La documentation technique (installation, API, architecture) est dans :

- [`bricodari-price-intelligence/README.md`](bricodari-price-intelligence/README.md)
- [`bricodari-price-intelligence/docs/`](bricodari-price-intelligence/docs/)
