# -*- coding: utf-8 -*-
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

for section in doc.sections:
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(11)
style._element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")

for i in range(1, 4):
    hs = doc.styles[f"Heading {i}"]
    hs.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)
    hs.font.name = "Calibri"


def set_cell_shading(cell, hex_color):
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), hex_color)
    shading.set(qn("w:val"), "clear")
    cell._tc.get_or_add_tcPr().append(shading)


def add_table(headers, rows, header_color="1A365D"):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for p in cell.paragraphs:
            for r in p.runs:
                r.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
                r.font.size = Pt(10)
                r.font.name = "Calibri"
        set_cell_shading(cell, header_color)
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = table.rows[ri + 1].cells[ci]
            cell.text = str(val)
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(10)
                    r.font.name = "Calibri"
            if ri % 2 == 1:
                set_cell_shading(cell, "F0F4F8")
    doc.add_paragraph()
    return table


def add_para(text, bold=False, italic=False, size=11, space_after=8):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.name = "Calibri"
    p.paragraph_format.space_after = Pt(space_after)
    return p


def add_bullet(text):
    p = doc.add_paragraph(text, style="List Bullet")
    for r in p.runs:
        r.font.size = Pt(11)
        r.font.name = "Calibri"
    return p


# ========== COVER ==========
for _ in range(2):
    doc.add_paragraph()

title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title.add_run("CAHIER DES CHARGES")
r.bold = True
r.font.size = Pt(26)
r.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = subtitle.add_run(
    "Automatisation marketing, blog, veille prix,\ndevis WhatsApp & CRM emails"
)
r.font.size = Pt(14)
r.font.color.rgb = RGBColor(0x2C, 0x52, 0x82)

doc.add_paragraph()

add_table(
    ["Élément", "Valeur"],
    [
        ["Version", "1.1 — Version simplifiée"],
        ["Date", "23 novembre 2026"],
        ["Statut", "À valider avec le client"],
        ["Durée totale estimée", "5 à 7 mois"],
    ],
)

doc.add_page_break()

# ========== INTRO ==========
doc.add_heading("1. Présentation du projet", level=1)
add_para(
    "Ce projet vise à automatiser et moderniser plusieurs activités de l'entreprise : "
    "la création de contenus pour les réseaux sociaux, le blog et le référencement, "
    "le suivi des prix concurrents, la création de devis depuis WhatsApp, "
    "et l'envoi d'emails depuis le CRM (en remplacement de Mautic)."
)
add_para("Le projet est découpé en 5 parties indépendantes, qui peuvent être livrées progressivement.")

add_table(
    ["Partie", "Nom", "Durée estimée"],
    [
        ["1", "Affiches réseaux sociaux", "4 à 6 semaines"],
        ["2", "Blog intelligent SEO & GEO", "3 à 5 semaines"],
        ["3", "Veille concurrentielle & prix", "4 à 6 semaines"],
        ["4", "Devis automatiques via WhatsApp", "5 à 7 semaines"],
        ["6", "Remplacement de Mautic par le CRM", "4 à 6 semaines"],
    ],
)

# ========== PARTIE 1 ==========
doc.add_heading("2. Partie 1 — Affiches réseaux sociaux", level=1)

doc.add_heading("À quoi ça sert ?", level=2)
add_para(
    "Créer automatiquement des affiches (textes + images) pour Facebook, Instagram et TikTok, "
    "puis les publier sans tout faire à la main."
)

doc.add_heading("Ce que contient cette partie", level=2)
for b in [
    "Saisie d'un brief simple (produit, offre, ton, réseau).",
    "Génération du texte (accroche, hashtags) avec Claude.",
    "Génération du visuel (image ou vidéo courte) avec Higgsfield.ai.",
    "Prévisualisation et validation avant publication.",
    "Publication immédiate ou planifiée sur Facebook, Instagram et TikTok.",
    "Historique des publications.",
]:
    add_bullet(b)

doc.add_heading("Estimation de temps", level=2)
add_para("4 à 6 semaines", bold=True)
add_para(
    "Dépend surtout de l'accès aux comptes Facebook / Instagram / TikTok "
    "et de la validation de la charte graphique.",
    italic=True,
)

# ========== PARTIE 2 ==========
doc.add_heading("3. Partie 2 — Blog intelligent (SEO & GEO)", level=1)

doc.add_heading("À quoi ça sert ?", level=2)
add_para(
    "Mettre en place un blog qui attire des visiteurs grâce au référencement naturel (SEO) "
    "et qui est aussi bien compris par les intelligences artificielles (GEO), "
    "pour apparaître dans Google et dans les réponses type ChatGPT / Perplexity."
)

doc.add_heading("Ce que contient cette partie", level=2)
for b in [
    "Blog avec articles, catégories et auteurs.",
    "Aide à la rédaction par IA (brouillon, titres, meta, FAQ).",
    "Optimisation SEO classique (titres, structure, balises).",
    "Optimisation GEO (contenu clair, FAQ, sources, structure citable).",
    "Calendrier éditorial et validation avant publication.",
    "Suivi de base du trafic et du référencement.",
]:
    add_bullet(b)

doc.add_heading("Estimation de temps", level=2)
add_para("3 à 5 semaines", bold=True)
add_para(
    "Plus court si un site / CMS existe déjà ; plus long si tout est à créer.",
    italic=True,
)

# ========== PARTIE 3 ==========
doc.add_heading("4. Partie 3 — Veille concurrentielle & prix", level=1)

doc.add_heading("À quoi ça sert ?", level=2)
add_para(
    "Avoir chaque semaine un tableau clair qui compare vos prix, "
    "les prix des concurrents, les prix affichés sur votre site, "
    "et le dernier prix d'achat enregistré dans Sage."
)

doc.add_heading("Ce que contient cette partie", level=2)
for b in [
    "Liste des produits (références / SKU) alignée avec Sage.",
    "Liste des concurrents à surveiller.",
    "Récupération automatique des prix une fois par semaine.",
    "Prix actuels de vente (internes).",
    "Prix affichés sur le site du client.",
    "Dernier prix d'achat depuis Sage.",
    "Tableau comparatif avec écarts et marges.",
    "Historique des prix et export Excel.",
    "Alertes en cas d'écart important.",
]:
    add_bullet(b)

doc.add_heading("Estimation de temps", level=2)
add_para("4 à 6 semaines", bold=True)
add_para(
    "Dépend du nombre de produits, du nombre de concurrents, "
    "et de la facilité d'accès aux données Sage.",
    italic=True,
)

# ========== PARTIE 4 ==========
doc.add_heading("5. Partie 4 — Devis automatiques via WhatsApp", level=1)

doc.add_heading("À quoi ça sert ?", level=2)
add_para(
    "Quand un client demande un devis sur WhatsApp, le système prépare automatiquement "
    "un brouillon de devis en s'appuyant sur Sage, le site et les listes de prix fournisseurs. "
    "Un commercial valide, puis le devis est envoyé."
)

doc.add_heading("Ce que contient cette partie", level=2)
for b in [
    "Réception des messages WhatsApp Business.",
    "Compréhension de la demande (produits, quantités) assistée par IA.",
    "Recherche des prix dans Sage, sur le site et dans les listes fournisseurs.",
    "Création d'un brouillon de devis.",
    "Validation par un commercial avant envoi.",
    "Envoi du devis (PDF) au client via WhatsApp ou email.",
    "Enregistrement / synchronisation du devis dans Sage.",
    "Escalade humaine si la demande est trop floue.",
]:
    add_bullet(b)

doc.add_heading("Estimation de temps", level=2)
add_para("5 à 7 semaines", bold=True)
add_para(
    "C'est la partie la plus longue : elle touche WhatsApp, Sage, le site et les règles commerciales.",
    italic=True,
)

# ========== PARTIE 6 ==========
doc.add_heading("6. Partie 6 — Remplacement de Mautic par le CRM", level=1)

doc.add_heading("À quoi ça sert ?", level=2)
add_para(
    "Arrêter Mautic et envoyer les emails (campagnes, relances, newsletters) "
    "depuis votre CRM, pour tout centraliser au même endroit."
)

doc.add_heading("Ce que contient cette partie", level=2)
for b in [
    "Inventaire de ce qui existe dans Mautic (contacts, campagnes, scénarios).",
    "Migration des contacts et listes vers le CRM.",
    "Recréation des modèles d'emails.",
    "Envoi des emails depuis le CRM.",
    "Segments et automatisations essentielles.",
    "Respect du RGPD (désinscription, consentements).",
    "Période de transition, puis arrêt de Mautic.",
]:
    add_bullet(b)

doc.add_heading("Estimation de temps", level=2)
add_para("4 à 6 semaines", bold=True)
add_para(
    "Dépend de la complexité de Mautic actuel et du CRM choisi pour le remplacer.",
    italic=True,
)

# ========== RECAP TEMPS ==========
doc.add_heading("7. Récapitulatif des délais", level=1)

add_table(
    ["Partie", "Contenu en résumé", "Durée"],
    [
        [
            "1 — Affiches sociales",
            "Textes + images IA, publication FB / IG / TikTok",
            "4–6 semaines",
        ],
        [
            "2 — Blog SEO & GEO",
            "Blog + aide rédaction + référencement",
            "3–5 semaines",
        ],
        [
            "3 — Veille prix",
            "Tableau comparatif, extraction hebdo, Sage",
            "4–6 semaines",
        ],
        [
            "4 — Devis WhatsApp",
            "Devis auto depuis WhatsApp + Sage",
            "5–7 semaines",
        ],
        [
            "6 — CRM emails",
            "Remplacement Mautic par le CRM",
            "4–6 semaines",
        ],
        [
            "Cadrage + mise en prod",
            "Ateliers, tests, formation",
            "3–4 semaines",
        ],
    ],
)

add_para("Durée totale estimée : 5 à 7 mois", bold=True, size=12)
add_para(
    "Les parties peuvent être faites en parallèle (par exemple Partie 1 et Partie 2 en même temps). "
    "L'ordre recommandé : cadrage → Partie 1 & 2 → Partie 3 → Partie 4 → Partie 6 "
    "(la Partie 6 peut aussi démarrer tôt si l'audit Mautic est prêt)."
)

# ========== POINTS A VALIDER ==========
doc.add_heading("8. Points à valider avec le client", level=1)
for i, q in enumerate(
    [
        "Quelle version de Sage utilisez-vous ?",
        "Quel CRM remplacera Mautic ?",
        "Combien de produits et de concurrents pour la veille prix ?",
        "Combien de demandes devis WhatsApp par mois environ ?",
        "Avez-vous déjà un site / blog ?",
        "Souhaitez-vous définir une Partie 5 (non précisée pour l'instant) ?",
    ],
    1,
):
    add_para(f"{i}. {q}", space_after=4)

# ========== APPROBATION ==========
doc.add_heading("9. Validation", level=1)
add_table(
    ["Rôle", "Nom", "Date", "Signature"],
    [
        ["Client", "", "", ""],
        ["Chef de projet", "", "", ""],
    ],
)

doc.add_paragraph()
footer = doc.add_paragraph()
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = footer.add_run(
    "Cahier des charges simplifié — Version 1.1 — Novembre 2026"
)
r.italic = True
r.font.size = Pt(9)
r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

out = r"c:\Users\ThinkPad\Desktop\Nv_bechanged\Cahier_des_charges_simplifie.docx"
doc.save(out)
print("OK:", out)
