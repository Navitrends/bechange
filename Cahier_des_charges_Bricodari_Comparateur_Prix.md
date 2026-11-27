# Cahier des charges fonctionnel et technique

## Comparateur intelligent des prix d'achat et des prix du marché -- Bricodari.tn

**Version :** 1.0\
**Projet :** Bricodari Price Intelligence\
**Site cible :** https://bricodari.tn\
**Objectif :** centraliser les prix d'achat provenant de plusieurs
sources, les rapprocher du catalogue WooCommerce de Bricodari et
comparer les prix de vente avec ceux des concurrents afin d'aider la
direction à prendre des décisions commerciales.

------------------------------------------------------------------------

# 1. Présentation du projet

Bricodari souhaite mettre en place un système de veille et de
comparaison des prix permettant de rapprocher trois ensembles de données
:

1.  **Prix d'achat internes** : prix issus du logiciel de gestion/ERP,
    transmis par fichier Excel/CSV, récupérés depuis Google Drive ou
    obtenus directement via API ou autre connecteur.
2.  **Prix fournisseurs** : tarifs et offres transmis par les
    fournisseurs sous différents formats (Excel, CSV, PDF, documents,
    e-mails ou pièces jointes).
3.  **Prix de vente et catalogue Bricodari** : produits présents dans la
    boutique WooCommerce, avec leur code UGS/SKU, désignation, marque,
    catégorie et prix affiché.
4.  **Prix concurrents** : prix publics relevés sur une liste de sites
    concurrents fournie et autorisée par Bricodari.

Le système rapproche les produits, identifie les correspondances fiables
et les cas ambigus, puis produit une fiche comparative consolidée.

Le résultat attendu pour chaque produit est notamment :

-   Code UGS/SKU Bricodari.
-   Désignation et informations du produit.
-   Prix d'achat interne.
-   Prix fournisseur et fournisseur correspondant.
-   Prix de vente actuel sur Bricodari.tn.
-   Prix concurrents trouvés.
-   Concurrent le moins cher et son prix.
-   Concurrent le plus cher et son prix.
-   Écarts en valeur et en pourcentage.
-   Marge estimée, lorsque les données nécessaires sont disponibles.
-   Niveau de confiance du rapprochement.
-   Recommandation ou alerte à examiner par un responsable.

**Le système est un outil d'aide à la décision. Il ne doit pas modifier
automatiquement les prix de vente ou les prix d'achat sans validation
humaine explicite.**

# 2. Objectifs métier

## 2.1. Objectifs principaux

-   Centraliser plusieurs sources de prix dans une base unique.
-   Réduire les opérations manuelles de rapprochement des articles.
-   Utiliser le code UGS/SKU comme identifiant prioritaire pour relier
    les articles au catalogue Bricodari.
-   Importer les listes fournisseurs provenant de formats variés.
-   Comparer les produits Bricodari avec les produits équivalents des
    concurrents.
-   Identifier les écarts de prix et les opportunités commerciales.
-   Détecter les prix fournisseurs obsolètes ou incohérents.
-   Produire des rapports exploitables par la direction et les équipes
    commerciales.
-   Conserver l'historique des prix afin de suivre leur évolution dans
    le temps.

## 2.2. Périmètre fonctionnel

Le système couvre quatre familles de données :

  -----------------------------------------------------------------------
  Source                  Données principales     Mode d'intégration
  ----------------------- ----------------------- -----------------------
  Logiciel de gestion /   Code article,           Excel, CSV, Drive, API
  ERP                     désignation, prix       ou connecteur
                          d'achat                 

  Fournisseurs            Référence, désignation, Excel, CSV, PDF, e-mail
                          marque, prix, devise,   et pièces jointes
                          date, conditions        

  Bricodari WooCommerce   UGS, produit, marque,   WordPress / WooCommerce
                          catégorie, prix de      REST API
                          vente                   

  Sites concurrents       Produit, référence,     Connecteurs web et
                          marque, prix public,    extraction autorisée
                          URL, disponibilité      
  -----------------------------------------------------------------------

# 3. Architecture générale du système

Le système doit être modulaire. Chaque source possède son propre
connecteur et son propre processus d'importation. Les données sont
ensuite normalisées dans un référentiel commun.

``` text
       SOURCES DE DONNÉES
               |
   +-----------+------------+----------------+
   |           |            |                |
 ERP / Drive  Fournisseurs  WooCommerce   Concurrents
 XLS / CSV    XLS/PDF/Mail  API            Sites web
 API          Pièces jointes
   |           |            |                |
   +-----------+------------+----------------+
               |
               v
       MODULE D'IMPORTATION
               |
               v
       EXTRACTION ET NORMALISATION
               |
               v
       RÉFÉRENTIEL PRODUITS
               |
       +-------+--------------------+
       |                            |
       v                            v
 RAPPROCHEMENT UGS             RAPPROCHEMENT
 ET RÉFÉRENCES                 SÉMANTIQUE
       |                            |
       +-------------+--------------+
                     |
                     v
             VALIDATION DES MATCHS
                     |
                     v
             MOTEUR DE COMPARAISON
                     |
                     v
             ANALYSE DES ÉCARTS
                     |
                     v
             DASHBOARD / RAPPORTS
                     |
                     v
             AIDE À LA DÉCISION
```

# 4. Module 1 -- Importation des prix internes depuis le logiciel de gestion

Ce module récupère les prix d'achat et les informations articles
provenant du logiciel de gestion utilisé par Bricodari.

## 4.1. Source A : fichier Excel ou CSV

Le système doit accepter les fichiers `.xlsx`, `.xls` et `.csv`.

Le fichier peut être déposé manuellement ou récupéré depuis un dossier
Google Drive autorisé.

Champs attendus, selon disponibilité :

-   Code UGS / SKU / code article.
-   Désignation.
-   Référence fabricant.
-   Code-barres / EAN.
-   Marque.
-   Catégorie.
-   Prix d'achat.
-   Devise.
-   Unité de mesure.
-   Fournisseur associé.
-   Date du prix.
-   Date de mise à jour.

L'utilisateur doit pouvoir associer les colonnes du fichier aux champs
internes lors du premier import. Le mapping pourra ensuite être
enregistré comme modèle réutilisable.

## 4.2. Source B : récupération depuis Google Drive

Fonctionnalités :

-   Connexion sécurisée à Google Drive.
-   Sélection du compte, du dossier et du fichier source.
-   Détection des nouveaux fichiers ou fichiers modifiés.
-   Import manuel ou planifié.
-   Conservation du nom du fichier, de son identifiant et de sa date
    d'import.
-   Historique des imports et possibilité de réimporter un fichier.

Le système ne doit traiter que les dossiers explicitement autorisés par
Bricodari.

## 4.3. Source C : connexion directe au logiciel

Prévoir une architecture de connecteurs interchangeables :

-   API REST ou SOAP, si disponible.
-   Accès base de données en lecture seule, si autorisé et techniquement
    sûr.
-   Export automatique programmé.
-   Dépôt de fichiers sur un dossier SFTP.
-   Autre mécanisme validé avec l'éditeur du logiciel.

Le connecteur doit permettre de récupérer les articles et leurs prix
sans modifier les données de gestion.

**À confirmer pendant l'audit :** nom et version du logiciel,
disponibilité de son API, méthode d'authentification, champs disponibles
et fréquence de synchronisation.

## 4.4. Gestion des mises à jour

Le système doit distinguer :

-   Nouvel article.
-   Article existant avec prix modifié.
-   Article existant sans changement.
-   Article supprimé ou absent de la nouvelle extraction.
-   Article avec code UGS manquant ou dupliqué.

Une absence dans un nouvel import ne doit pas entraîner automatiquement
la suppression d'un article du référentiel.

# 5. Module 2 -- Importation et traitement des listes fournisseurs

Ce module doit accepter des documents fournisseurs de formats variés.

## 5.1. Formats acceptés

  Format       Méthode de traitement
  ------------ -------------------------------------------------------
  XLSX / XLS   Extraction des feuilles et cellules
  CSV          Lecture et détection du séparateur
  PDF texte    Extraction des tableaux et du texte
  PDF scanné   OCR puis extraction et contrôle
  DOCX         Extraction des tableaux et paragraphes
  E-mail       Lecture du corps et des pièces jointes via connecteur
  Image        OCR, sous réserve de qualité suffisante

Les formats supplémentaires pourront être ajoutés ultérieurement selon
les besoins.

## 5.2. Sources d'arrivée des documents

-   Import manuel dans le dashboard.
-   Dossier Google Drive dédié.
-   Boîte e-mail fournisseur dédiée ou boîte connectée avec
    autorisation.
-   Dépôt SFTP.
-   API fournisseur, lorsqu'elle existe.

Pour les e-mails, le système devra identifier le fournisseur, la date,
l'objet, les pièces jointes et les éventuelles conditions commerciales.

## 5.3. Extraction des données fournisseurs

Pour chaque ligne ou produit détecté, extraire autant que possible :

-   Nom du fournisseur.
-   Référence fournisseur.
-   Code fabricant.
-   Code-barres.
-   Désignation.
-   Marque.
-   Catégorie.
-   Prix unitaire.
-   Devise.
-   Taux de TVA ou mention HT/TTC.
-   Remise.
-   Quantité minimale.
-   Conditionnement.
-   Unité.
-   Frais ou conditions de livraison, si présents.
-   Date de validité de l'offre.
-   Date du document.
-   Numéro du document.
-   Source et page/ligne d'origine.

Les informations absentes doivent rester inconnues et ne doivent pas
être inventées.

## 5.4. Contrôle des documents

Le système doit détecter :

-   Prix manquants.
-   Devises non identifiées.
-   Prix HT et TTC mélangés.
-   Unités différentes.
-   Remises non interprétées.
-   Dates de validité dépassées.
-   Références dupliquées.
-   Quantités minimales.
-   Prix manifestement aberrants.

Les lignes douteuses doivent être placées dans une file de contrôle
manuel.

## 5.5. Gestion des différentes offres

Un même produit peut avoir plusieurs prix fournisseurs. Il faut
conserver toutes les offres, sans écraser l'historique.

Le système doit permettre de comparer :

-   Le prix fournisseur le plus bas.
-   Le prix fournisseur le plus récent.
-   Le prix fournisseur le plus avantageux après remise.
-   Le prix selon les conditions de quantité.
-   Le prix rendu, si les frais de livraison et autres coûts sont
    disponibles.

Ne pas considérer automatiquement le prix le plus bas comme le meilleur
prix d'achat : les conditions, la disponibilité, le délai, la quantité
minimale et la qualité doivent être pris en compte.

# 6. Module 3 -- Connexion au catalogue Bricodari WooCommerce

Le catalogue WooCommerce constitue le référentiel commercial principal.

## 6.1. Données à récupérer

Pour chaque produit :

-   Identifiant WooCommerce.
-   UGS / SKU.
-   Nom du produit.
-   Description courte.
-   Description complète.
-   Marque.
-   Catégorie(s).
-   Référence fabricant, si disponible.
-   EAN / code-barres, si disponible.
-   Prix normal.
-   Prix promotionnel.
-   Prix affiché.
-   Statut de publication.
-   URL publique.
-   Disponibilité / stock, si exposé.
-   Variantes et attributs.
-   Date de dernière modification.

## 6.2. Produits variables

Le système doit distinguer le produit parent de ses variantes.

Exemple : un robinet disponible en plusieurs finitions ou dimensions
peut avoir plusieurs références et plusieurs prix. La comparaison doit
se faire au niveau de la variante lorsque les caractéristiques
influencent le prix.

## 6.3. Correspondance par UGS

La première règle de rapprochement est l'UGS/SKU.

Exemple :

  Source        Code UGS   Désignation
  ------------- ---------- ------------------------
  ERP           ROB-001    Robinet lavabo chromé
  WooCommerce   ROB-001    Robinet de lavabo
  Fournisseur   ROB-001    Mitigeur lavabo chromé

Si le code est strictement identique et fiable, le rapprochement peut
être proposé avec un niveau de confiance élevé.

Toutefois, le système doit vérifier les incohérences de marque,
référence fabricant, variante et unité. Un code identique ne doit pas
masquer une erreur de référentiel.

## 6.4. Cas des codes UGS absents

Si le fournisseur ne transmet pas le code UGS Bricodari, le système doit
rechercher une correspondance à partir de plusieurs critères :

-   Référence fabricant.
-   EAN / code-barres.
-   Marque.
-   Désignation.
-   Caractéristiques techniques.
-   Catégorie.
-   Dimensions, puissance, capacité, couleur ou modèle.

Le rapprochement sémantique doit être utilisé comme mécanisme de
proposition, pas comme preuve définitive.

# 7. Module 4 -- Collecte des prix concurrents

Ce module compare les produits Bricodari avec les produits équivalents
vendus sur les sites concurrents.

## 7.1. Gestion des concurrents

Le dashboard doit permettre d'ajouter, modifier, désactiver et supprimer
des concurrents.

Pour chaque concurrent :

-   Nom commercial.
-   URL du site.
-   Pays et devise.
-   Langue.
-   Type de site.
-   URL du catalogue ou des catégories à surveiller.
-   Fréquence de collecte.
-   Méthode de collecte.
-   Statut du connecteur.
-   Date de dernière collecte.

La liste des concurrents sera fournie par Bricodari.

## 7.2. Méthodes de collecte

Prévoir plusieurs méthodes selon les capacités du site concurrent :

1.  API publique ou partenaire, si disponible.
2.  Flux produits XML/CSV.
3.  Sitemap et pages produits publiques.
4.  Extraction HTML des pages accessibles.
5.  Connecteur spécifique à un concurrent.

Le système doit respecter les conditions d'utilisation des sites, les
règles d'accès, les limites de fréquence et les mesures de protection
applicables. Il ne doit pas contourner des authentifications ou
protections techniques.

## 7.3. Informations à collecter

-   Nom du concurrent.
-   URL exacte du produit.
-   Désignation.
-   Marque.
-   Référence fabricant.
-   EAN, si disponible.
-   Catégorie.
-   Description.
-   Caractéristiques techniques.
-   Prix affiché.
-   Prix promotionnel.
-   Devise.
-   Disponibilité annoncée.
-   Frais de livraison, si disponibles.
-   Date et heure de collecte.
-   État de la page et source.

Chaque prix concurrent doit être conservé avec sa date de collecte. Un
prix n'est jamais considéré comme actuel sans date de vérification.

## 7.4. Fréquence de collecte

La fréquence doit être paramétrable par concurrent ou catégorie :

-   Quotidienne.
-   Hebdomadaire.
-   À la demande.
-   Selon une autre fréquence définie.

Le système doit éviter les collectes excessives et enregistrer les
erreurs de connexion ou les changements de structure des sites.

# 8. Module 5 -- Moteur intelligent de rapprochement des produits

**C'est le module le plus stratégique du projet.**

Il doit déterminer si deux désignations différentes correspondent
réellement au même produit.

## 8.1. Ordre de priorité du rapprochement

  Priorité   Critère                               Fiabilité attendue
  ---------- ------------------------------------- --------------------
  1          EAN / code-barres identique           Très élevée
  2          Référence fabricant identique         Très élevée
  3          UGS Bricodari identique et vérifiée   Très élevée
  4          Marque + modèle exact                 Élevée
  5          Désignation + caractéristiques        Moyenne à élevée
  6          Similarité sémantique                 À confirmer

La similarité de texte seule ne suffit jamais pour conclure qu'il s'agit
du même produit.

## 8.2. Analyse des désignations

Le système doit être capable de reconnaître les différences de
rédaction.

Exemple fictif :

  Source         Désignation
  -------------- -----------------------------------------
  Bricodari      Perceuse à percussion 750 W marque X
  Fournisseur    Perceuse percussion X 750 watts
  Concurrent A   Perceuse filaire à percussion 750W -- X

Ces lignes peuvent être proposées comme correspondance, sous réserve de
vérifier le modèle, la référence et les caractéristiques.

En revanche, une perceuse de 500 W ne doit pas être assimilée
automatiquement à une perceuse de 750 W, même si les désignations sont
proches.

## 8.3. Comparaison des caractéristiques

Le moteur doit pouvoir comparer les attributs structurés :

-   Marque.
-   Modèle.
-   Puissance.
-   Dimensions.
-   Capacité.
-   Matière.
-   Couleur.
-   Tension.
-   Pression.
-   Débit.
-   Volume.
-   Quantité par emballage.
-   Type de produit.

Les caractéristiques pertinentes dépendent de la catégorie.

## 8.4. Score de confiance du rapprochement

Prévoir un score distinct du score SEO du projet précédent.

Exemple de grille :

  Critère                         Pondération
  ----------------------------- -------------
  EAN / référence exacte                   30
  Marque                                   15
  Modèle                                   20
  Désignation                              15
  Caractéristiques techniques              15
  Catégorie                                 5
  Total                                   100

La pondération doit être adaptée selon les données disponibles. Les
identifiants exacts doivent avoir priorité sur les similarités
textuelles.

## 8.5. Trois niveaux de décision

-   **90 à 100 : correspondance forte** -- rapprochement proposé
    automatiquement, sous réserve de l'absence de contradiction.
-   **70 à 89 : correspondance probable** -- validation humaine requise.
-   **Moins de 70 : correspondance faible** -- ne pas associer
    automatiquement.

Une contradiction majeure (marque différente, modèle incompatible,
dimension ou puissance incompatible, conditionnement différent) doit
bloquer la correspondance automatique, même si le score est élevé.

## 8.6. Interface de validation des correspondances

Lorsqu'un doute existe, afficher les produits côte à côte :

  Critère           Produit Bricodari   Produit candidat
  ----------------- ------------------- ------------------
  Désignation       Produit A           Produit B
  Marque            Marque X            Marque X
  Référence         REF-001             REF-001
  Catégorie         Outillage           Outillage
  Caractéristique   750 W               750 W
  Score             ---                 94/100

Actions disponibles :

-   Confirmer la correspondance.
-   Rejeter.
-   Choisir un autre produit.
-   Demander une analyse complémentaire.
-   Enregistrer une règle de correspondance pour les prochains imports.

Les validations humaines doivent enrichir progressivement le référentiel
de correspondances.

# 9. Module 6 -- Normalisation des prix et des conditions commerciales

Avant toute comparaison, les prix doivent être ramenés à une base
homogène.

## 9.1. Règles de normalisation

Le système doit distinguer :

-   Prix hors taxes.
-   Prix toutes taxes comprises.
-   Devise.
-   Taux de TVA.
-   Remise.
-   Quantité minimale.
-   Unité de vente.
-   Conditionnement.
-   Frais de transport.
-   Validité du tarif.

Il faut éviter de comparer directement un prix fournisseur HT à un prix
concurrent TTC.

## 9.2. Prix de référence

Pour chaque offre, conserver le prix original et calculer, lorsque les
données sont disponibles :

-   Prix net après remise.
-   Prix unitaire normalisé.
-   Prix HT.
-   Prix TTC.
-   Coût rendu estimé.
-   Devise d'origine.
-   Taux de conversion et date du taux, si conversion nécessaire.

Aucune conversion ou taxe ne doit être appliquée sans règle
explicitement configurée.

## 9.3. Prix concurrent

Le comparateur doit présenter séparément :

-   Prix affiché.
-   Prix promotionnel.
-   Prix TTC ou HT lorsque connu.
-   Frais de livraison connus.
-   Prix total estimé pour le client, si calculable.

Les prix dont le régime fiscal ou les conditions sont inconnus doivent
être signalés comme non directement comparables.

# 10. Module 7 -- Moteur de comparaison et indicateurs

Pour chaque produit Bricodari, construire une fiche consolidée.

## 10.1. Exemple de tableau comparatif

Données entièrement fictives pour illustrer le fonctionnement :

  Information                                       Valeur
  -------------------------- -----------------------------
  Code UGS                                         PER-001
  Désignation                  Perceuse à percussion 750 W
  Prix achat ERP                                 82,000 DT
  Prix fournisseur A                             79,500 DT
  Prix fournisseur B                             85,000 DT
  Prix vente Bricodari                          119,000 DT
  Concurrent A                                  109,000 DT
  Concurrent B                                  125,000 DT
  Concurrent le moins cher                      109,000 DT
  Concurrent le plus cher                       125,000 DT

## 10.2. Indicateurs calculés

-   Prix d'achat interne.
-   Meilleur prix fournisseur comparable.
-   Écart entre prix ERP et prix fournisseur.
-   Prix de vente Bricodari.
-   Prix concurrent minimum.
-   Prix concurrent maximum.
-   Nombre de concurrents ayant une correspondance validée.
-   Écart Bricodari / concurrent le moins cher.
-   Écart Bricodari / concurrent le plus cher.
-   Positionnement de Bricodari sur le marché.
-   Marge brute estimée et taux de marge, lorsque les données sont
    suffisantes.

## 10.3. Formules

**Écart avec le concurrent le moins cher :**

`Prix Bricodari - Prix concurrent minimum`

**Écart en pourcentage :**

`(Prix Bricodari - Prix concurrent minimum) / Prix concurrent minimum × 100`

**Marge brute unitaire simplifiée :**

`Prix de vente HT - Coût d'achat HT`

**Taux de marque :**

`Marge brute / Prix de vente HT × 100`

**Taux de marge :**

`Marge brute / Coût d'achat HT × 100`

Ces indicateurs ne sont fiables que si les prix sont exprimés sur la
même base fiscale, dans la même devise et avec des unités comparables.
La marge calculée ne constitue pas nécessairement la marge nette : les
coûts logistiques, frais de paiement, retours et autres charges peuvent
ne pas être inclus.

## 10.4. Alertes commerciales

Le système doit pouvoir identifier :

-   Bricodari plus cher que tous les concurrents.
-   Bricodari moins cher que tous les concurrents.
-   Prix de vente inférieur au coût d'achat.
-   Prix fournisseur en hausse.
-   Écart important entre deux fournisseurs.
-   Prix concurrent anormalement bas.
-   Produit sans prix concurrent récent.
-   Produit sans correspondance fiable.
-   Prix promotionnel concurrent.
-   Offre fournisseur expirée.

Les seuils d'alerte doivent être configurables.

# 11. Module 8 -- Dashboard et rapports de décision

## 11.1. Tableau de bord général

Indicateurs proposés :

-   Nombre de produits WooCommerce.
-   Nombre d'articles ERP rapprochés.
-   Nombre d'offres fournisseurs importées.
-   Nombre de produits concurrents collectés.
-   Nombre de correspondances automatiques.
-   Nombre de correspondances en attente.
-   Nombre de produits sans correspondance.
-   Nombre d'alertes tarifaires.
-   Date de dernière synchronisation par source.

## 11.2. Filtres

-   Catégorie.
-   Marque.
-   Fournisseur.
-   Concurrent.
-   Produit.
-   Code UGS.
-   Écart de prix.
-   Niveau de confiance.
-   Date de collecte.
-   Disponibilité.
-   Statut de validation.

## 11.3. Fiche détaillée d'un produit

La fiche doit présenter quatre blocs :

**A. Informations produit** - UGS. - Désignation. - Marque. -
Catégorie. - Référence fabricant. - Lien vers la fiche WooCommerce.

**B. Prix d'achat** - Prix ERP. - Prix de chaque fournisseur. -
Conditions d'achat. - Date de validité. - Historique.

**C. Prix concurrents** - Concurrent. - Désignation trouvée. - Prix. -
URL source. - Disponibilité. - Date de vérification. - Score de
correspondance.

**D. Analyse** - Prix Bricodari. - Prix minimum du marché observé. -
Prix maximum du marché observé. - Écarts. - Marge estimée. - Alertes. -
Recommandations indicatives.

## 11.4. Exports

Le système doit permettre d'exporter les résultats :

-   Excel `.xlsx`.
-   CSV.
-   PDF de synthèse.
-   Rapport par catégorie.
-   Rapport par fournisseur.
-   Rapport par concurrent.
-   Rapport des produits à revoir.

Les exports doivent conserver les références des sources et les dates de
collecte.

# 12. Module 9 -- Historique et suivi des prix

Ne jamais écraser les anciennes observations de prix.

Chaque prix doit être historisé avec :

-   Produit associé.
-   Source.
-   Fournisseur ou concurrent.
-   Prix.
-   Devise.
-   Base HT/TTC/inconnue.
-   Date d'observation.
-   Date de validité.
-   Document ou URL source.
-   Statut de validation.

Fonctionnalités :

-   Courbe d'évolution des prix.
-   Comparaison entre périodes.
-   Historique des prix fournisseurs.
-   Historique des prix concurrents.
-   Détection des hausses et baisses.
-   Identification des données obsolètes.

Le dashboard doit clairement distinguer le prix courant du dernier prix
observé.

# 13. Architecture technique recommandée

Le projet doit réutiliser les principes d'architecture modulaire du
projet SEO, mais rester un système indépendant.

## 13.1. Technologies

  Couche                 Technologie recommandée
  ---------------------- ---------------------------------------
  Backend                Python / FastAPI
  Import Excel/CSV       Pandas / OpenPyXL
  PDF et tableaux        PyMuPDF / pdfplumber
  OCR                    Tesseract ou service OCR
  E-mails                Gmail API ou IMAP selon autorisations
  Google Drive           Google Drive API
  ERP                    API spécifique / connecteur
  Crawling concurrents   Scrapy / httpx / BeautifulSoup
  Pages JavaScript       Playwright si nécessaire
  Similarité             RapidFuzz + embeddings / modèle IA
  Base de données        PostgreSQL
  Tâches asynchrones     Redis + Celery ou RQ
  Orchestration          n8n
  Dashboard              React / Next.js
  Déploiement            Docker Compose
  CMS catalogue          WooCommerce REST API

Le modèle IA peut aider à interpréter des désignations, documents et
caractéristiques. Les calculs de prix, conversions et marges doivent
être réalisés par du code déterministe et testé.

## 13.2. Arborescence proposée

``` text
bricodari-price-intelligence/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── imports/
│   │   │   ├── erp/
│   │   │   ├── suppliers/
│   │   │   ├── email/
│   │   │   └── drive/
│   │   ├── woo_commerce/
│   │   ├── competitors/
│   │   ├── matching/
│   │   ├── pricing/
│   │   ├── normalization/
│   │   ├── reports/
│   │   └── main.py
│   └── tests/
│
├── frontend/
│   └── src/
│
├── n8n/
│   └── workflows/
│
├── database/
│   └── migrations/
│
├── docs/
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

# 14. Modèle de données principal

Tables recommandées :

  Table                             Rôle
  --------------------------------- ---------------------------------
  `products`                        Référentiel produit central
  `product_identifiers`             UGS, EAN, références fabricant
  `product_attributes`              Caractéristiques techniques
  `erp_sources`                     Sources ERP
  `erp_price_records`               Prix d'achat internes
  `suppliers`                       Référentiel fournisseurs
  `supplier_documents`              Documents reçus
  `supplier_offers`                 Offres et lignes tarifaires
  `competitors`                     Sites concurrents
  `competitor_products`             Produits trouvés
  `competitor_price_observations`   Historique des prix concurrents
  `product_matches`                 Correspondances entre produits
  `match_reviews`                   Validations humaines
  `price_comparisons`               Résultats consolidés
  `import_jobs`                     Historique des imports
  `crawl_jobs`                      Historique des collectes
  `system_logs`                     Logs et erreurs

Chaque enregistrement de prix doit conserver sa source d'origine, sa
date et ses conditions. Il faut aussi conserver le document ou l'URL
d'origine lorsque cela est possible.

# 15. Workflows n8n

Créer des workflows indépendants.

## WF-01 -- Import des prix ERP

``` text
Schedule / Manual Trigger
        |
        v
Google Drive / API ERP
        |
        v
Python Import API
        |
        v
Validation des données
        |
        v
Normalisation
        |
        v
PostgreSQL
        |
        v
Rapport d'import
```

## WF-02 -- Import des listes fournisseurs

``` text
E-mail / Drive / Upload
        |
        v
Identification du fournisseur
        |
        v
Extraction XLS / PDF / OCR
        |
        v
Normalisation des lignes
        |
        v
Détection des anomalies
        |
        v
Rapprochement produit
        |
        v
Validation si nécessaire
        |
        v
Enregistrement des offres
```

## WF-03 -- Synchronisation WooCommerce

``` text
Schedule Trigger
        |
        v
WooCommerce REST API
        |
        v
Récupération produits / variantes
        |
        v
Mise à jour du référentiel
        |
        v
Détection des modifications
        |
        v
Rapport
```

## WF-04 -- Veille concurrentielle

``` text
Schedule Trigger
        |
        v
Liste des concurrents actifs
        |
        v
Connecteurs spécifiques
        |
        v
Collecte des pages produits
        |
        v
Extraction des prix
        |
        v
Normalisation
        |
        v
Rapprochement produits
        |
        v
Historisation
```

## WF-05 -- Comparaison et alertes

``` text
Nouvelle donnée de prix
        |
        v
Récupération des autres sources
        |
        v
Vérification de la fraîcheur
        |
        v
Calcul des écarts
        |
        v
Détection des anomalies
        |
        v
Mise à jour dashboard
        |
        v
Notification responsable
```

# 16. API interne

Endpoints proposés :

  Méthode   Endpoint                             Fonction
  --------- ------------------------------------ ---------------------------
  POST      `/api/import/erp`                    Import ERP
  POST      `/api/import/supplier`               Import fournisseur
  POST      `/api/import/email`                  Traitement e-mail
  GET       `/api/import/jobs/{id}`              Statut import
  POST      `/api/woocommerce/sync`              Synchronisation catalogue
  GET       `/api/products`                      Référentiel produits
  GET       `/api/suppliers`                     Fournisseurs
  POST      `/api/competitors`                   Ajouter concurrent
  POST      `/api/competitors/{id}/crawl`        Lancer collecte
  GET       `/api/matches/pending`               Correspondances à valider
  POST      `/api/matches/{id}/confirm`          Confirmer correspondance
  POST      `/api/matches/{id}/reject`           Rejeter correspondance
  GET       `/api/comparisons`                   Comparaisons
  GET       `/api/products/{id}/price-history`   Historique des prix
  GET       `/api/dashboard/stats`               Indicateurs
  GET       `/api/reports/export`                Exporter rapport

Les opérations longues doivent être asynchrones, avec identifiant de
tâche, statut, progression et gestion des erreurs.

# 17. Sécurité, qualité et gouvernance des données

Exigences obligatoires :

-   Connexions API sécurisées.
-   Secrets stockés hors du dépôt Git.
-   Comptes en lecture seule lorsque possible.
-   Accès Google Drive limité aux dossiers autorisés.
-   Accès e-mail limité aux boîtes nécessaires.
-   Protection des pièces jointes.
-   Analyse des fichiers importés.
-   Sauvegarde PostgreSQL.
-   Journalisation des imports et validations.
-   Traçabilité des modifications.
-   Gestion des rôles et permissions.
-   Respect des conditions d'accès des sites concurrents.
-   Aucune modification automatique des prix WooCommerce.

Prévoir les rôles suivants :

-   Administrateur : configuration et gestion complète.
-   Responsable achats : prix ERP et fournisseurs.
-   Responsable commercial : analyse des prix et concurrence.
-   Validateur : validation des correspondances.
-   Lecteur : consultation et exports.

# 18. Découpage du développement en phases

Le développement doit être progressif. Chaque phase doit être livrée,
testée et validée avant la suivante.

## Phase 0 -- Audit des sources

-   Identifier le logiciel de gestion.
-   Examiner les fichiers d'achat existants.
-   Identifier le format des UGS.
-   Examiner WooCommerce.
-   Recenser les concurrents.
-   Identifier les fournisseurs et leurs formats.
-   Vérifier les possibilités API et Drive.

**Livrable :** rapport d'audit et dictionnaire des données.

## Phase 1 -- Infrastructure et base de données

-   Initialisation du dépôt GitHub.
-   Docker Compose.
-   FastAPI.
-   PostgreSQL.
-   Redis.
-   Worker.
-   n8n.
-   Authentification dashboard.

**Livrable :** environnement fonctionnel.

## Phase 2 -- Référentiel WooCommerce

-   Connexion API.
-   Import des produits.
-   Import des variantes.
-   Import des catégories.
-   Import des UGS et références.
-   Synchronisation incrémentale.

**Livrable :** catalogue Bricodari centralisé.

## Phase 3 -- Import des prix ERP

-   Import Excel.
-   Import CSV.
-   Mapping des colonnes.
-   Connexion Drive.
-   Historisation.
-   Détection des modifications.

**Livrable :** prix d'achat internes intégrés.

## Phase 4 -- Import fournisseurs

-   Import Excel/CSV.
-   Extraction PDF.
-   OCR pour les documents scannés.
-   Traitement des e-mails.
-   Identification du fournisseur.
-   Extraction des prix et conditions.
-   Contrôle des anomalies.

**Livrable :** base des offres fournisseurs.

## Phase 5 -- Rapprochement des produits

-   Rapprochement par UGS.
-   Rapprochement EAN.
-   Références fabricants.
-   Normalisation des désignations.
-   Analyse marque/catégorie/caractéristiques.
-   Score de confiance.
-   Interface de validation.
-   Apprentissage à partir des validations.

**Livrable :** moteur de rapprochement.

## Phase 6 -- Collecte concurrentielle

-   Configuration des concurrents.
-   Analyse de faisabilité par site.
-   Connecteurs.
-   Extraction des fiches produits.
-   Collecte des prix.
-   Historisation.
-   Contrôle de fraîcheur.

**Livrable :** base des prix concurrents.

## Phase 7 -- Normalisation et comparaison

-   Harmonisation des unités.
-   Gestion HT/TTC.
-   Gestion des devises.
-   Calcul des prix comparables.
-   Comparaison fournisseur.
-   Comparaison concurrent.
-   Calcul des écarts.
-   Indicateurs de marge.

**Livrable :** moteur de comparaison.

## Phase 8 -- Dashboard

-   Vue générale.
-   Catalogue.
-   Fournisseurs.
-   Concurrents.
-   Correspondances à valider.
-   Comparateur.
-   Historique.
-   Exports.
-   Alertes.

**Livrable :** interface opérationnelle.

## Phase 9 -- Automatisation n8n

-   Import programmé.
-   Synchronisation WooCommerce.
-   Réception des documents.
-   Collecte concurrentielle.
-   Comparaison.
-   Alertes.
-   Rapports périodiques.

**Livrable :** automatisation des opérations.

## Phase 10 -- Recette et mise en production

-   Tests fonctionnels.
-   Tests de charge raisonnables.
-   Tests de sécurité.
-   Contrôle des correspondances.
-   Vérification des calculs.
-   Sauvegardes.
-   Formation des utilisateurs.
-   Déploiement progressif.

**Livrable :** système de comparaison opérationnel.

# 19. Critères de recette

Le système sera accepté lorsque les tests suivants seront validés.

  Test                          Résultat attendu
  ----------------------------- -------------------------------------------------
  Import Excel ERP              Articles et prix correctement importés
  Import CSV                    Colonnes correctement interprétées
  Drive                         Détection des nouveaux fichiers
  API ERP                       Lecture sans modification des données
  Import PDF fournisseur        Extraction vérifiable
  Import e-mail                 Identification et traitement des pièces jointes
  WooCommerce                   Catalogue et variantes synchronisés
  Rapprochement UGS             Correspondances exactes détectées
  Rapprochement ambigu          Proposition soumise à validation
  Correspondance incompatible   Association automatique bloquée
  Collecte concurrent           Prix et URL enregistrés
  Normalisation                 HT/TTC et unités distingués
  Comparaison                   Minimum, maximum et écarts corrects
  Historique                    Anciennes observations conservées
  Export                        Fichier exploitable et traçable
  Alertes                       Seuils configurables fonctionnels
  Sécurité                      Aucun changement automatique des prix

## Scénario de recette de bout en bout

Utiliser un échantillon contrôlé de 50 produits :

1.  Importer 50 produits depuis le fichier ERP.
2.  Synchroniser les mêmes produits depuis WooCommerce.
3.  Importer deux listes fournisseurs.
4.  Importer un document PDF fournisseur.
5.  Ajouter trois concurrents.
6.  Collecter les prix de produits équivalents.
7.  Lancer le rapprochement.
8.  Valider les correspondances douteuses.
9.  Générer le comparatif.
10. Exporter le rapport Excel.

Les résultats doivent pouvoir être vérifiés à partir des documents et
URLs sources.

# 20. Planning indicatif

  Lot                               Estimation
  ------------------------------ -------------
  Audit des sources                 2--4 jours
  Infrastructure                    2--3 jours
  Référentiel WooCommerce           2--4 jours
  Import ERP                        3--5 jours
  Import fournisseurs               4--7 jours
  Rapprochement intelligent         5--8 jours
  Collecte concurrents             5--10 jours
  Normalisation et comparaison      3--5 jours
  Dashboard                         5--8 jours
  Workflows n8n                     3--5 jours
  Tests et déploiement              3--5 jours

**Estimation indicative globale : 37 à 64 jours de travail**, selon la
diversité des documents fournisseurs, la disponibilité de l'API ERP et
la complexité des sites concurrents. Les développements peuvent être
partiellement parallélisés.

# 21. Évolutions futures

Prévoir une architecture permettant d'ajouter :

-   Analyse automatique des tendances de prix.
-   Prévision des hausses fournisseurs.
-   Historique comparatif sur 6 ou 12 mois.
-   Détection des produits sous-évalués ou surévalués.
-   Simulation de prix de vente.
-   Simulation de marges par catégorie.
-   Analyse de compétitivité par marque.
-   Alertes sur les promotions concurrentes.
-   Recommandations de négociation fournisseurs.
-   Scoring de fiabilité des fournisseurs.
-   Analyse de disponibilité et délais.
-   Intégration de nouveaux ERP et nouvelles marketplaces.

# 22. Points à confirmer avant le développement

Les informations suivantes conditionnent les choix techniques et le
périmètre réel.

1.  **Logiciel de gestion/ERP :** nom, version, possibilité d'API et
    structure des exports.
2.  **Identifiant produit :** l'UGS présent dans l'ERP est-il
    strictement identique au SKU WooCommerce ?
3.  **Prix d'achat :** les prix ERP sont-ils HT ou TTC ? S'agit-il du
    dernier prix, du prix moyen pondéré ou d'un autre indicateur ?
4.  **Fournisseurs :** combien de fournisseurs et combien de formats de
    documents différents ?
5.  **E-mails :** Gmail, Microsoft 365 ou serveur IMAP ?
6.  **Concurrents :** combien de sites doivent être surveillés et quels
    sont leurs noms ?
7.  **Périmètre géographique :** concurrents tunisiens uniquement ou
    également internationaux ?
8.  **Comparaison :** faut-il comparer uniquement les produits
    strictement identiques ou aussi les produits équivalents ?
9.  **Prix de vente :** faut-il comparer le prix affiché TTC, le prix
    promotionnel ou les deux ?
10. **Décision commerciale :** le système doit-il seulement informer ou
    également proposer des prix de vente cibles ?

Ces paramètres devront être configurables autant que possible, afin
d'éviter de figer des règles métier dans le code.

# 23. Recommandations de pilotage

Trois règles doivent guider le développement :

**1. Le rapprochement exact avant l'intelligence artificielle.**\
Toujours exploiter UGS, EAN et références fabricants avant de recourir à
la similarité sémantique. L'IA doit résoudre les ambiguïtés, pas
remplacer les identifiants fiables.

**2. La comparabilité avant le calcul.**\
Un prix HT ne doit pas être comparé directement à un prix TTC. Un lot de
10 unités ne doit pas être comparé au prix d'une unité sans
normalisation. Un produit de caractéristiques différentes ne doit pas
être considéré comme identique.

**3. La traçabilité avant la recommandation.**\
Chaque prix doit être accompagné de sa source, de sa date et de ses
conditions. Chaque rapprochement doit être explicable. Chaque
recommandation doit pouvoir être vérifiée.

L'objectif final est de disposer d'un véritable outil de Price
Intelligence pour Bricodari : un référentiel unique reliant achats,
fournisseurs, catalogue e-commerce et marché concurrentiel, afin de
donner à la direction une vision fiable des prix et des marges avant
toute décision commerciale.
