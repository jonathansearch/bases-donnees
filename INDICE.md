# INDICE du dépôt (un par un, selon nos besoins)

Loi du dépôt : ici les Go ne dorment pas (le snapshot les avale et la
session plante, prouvé 2 fois). UN seul dataset complet à la fois, le
reste attend sous forme de catalogue léger (fiches + échantillons Ko-Mo,
re-clonables en quelques minutes, vitesse mesurée ~60 Mo/s).

## LE dataset de travail (1 seul)

- AUCUN complet pour l'instant (budget) : le dépôt = catalogue.
  Le travail se fait à la demande : on clone, on s'en sert, on jette.
  (Précédents sortis : yield 363 Mo, accueil-ubs 745 Ko — fiches gardées.)

## Catalogue d'attente (fiches + échantillons, re-clonables)

Section `conversations/` (l'ordre du chef : du plus petit au plus grand) :

| # | Dataset | Taille | Contenu | Échantillon | Licence | Statut |
|---|---------|--------|---------|-------------|---------|--------|
| 1 | discord-dialogues | 331 Mo | 7 300 966 lignes | 200 | Apache-2.0 | ✅ clonable |
| 2 | yield | 363 Mo | 105 735 blocs | 200 | CC BY 4.0 | 📦 DANS LE REPO |
| 3 | ko-agent | 1,36 Go | 654 fichiers | 1000 | ? | ✅ clonable |
| 4 | lmsys-chat-1m | 1,49 Go | 1M conv. | — | ? | 🔒 gated (1 clic HF) |
| 5 | ultrachat-200k | 1,62 Go | 515 311 lignes | 200 | ? | ✅ clonable |
| 6 | escorpius-dialog | 2,98 Go | 26,9M dial. | — | CC BY-NC-ND | ✅ Zenodo 18466512 |
| 7 | wildchat-1m | 3,36 Go | 837 989 lignes | 200 | ? | ✅ clonable |

Section `francais/` (sources repérées, à cloner sur ordre) :

| Dataset | Source repérée | Note |
|---------|----------------|------|
| accueil-ubs | univ-tours ZIP | fiche seule (brut sorti, 3 s) |
| CFDD | OpenLLM-France/Claire-Dialogue-French-0.1 (HF) | ~160M mots, CC BY-NC-SA |
| ding-01 | GitLab Inria semagramme ding | dialogues Catan + AMR |
| FLEURON | apps.atilf.fr/fleuron | site concordancier, masse à vérifier |
| TCOF | cnrtl.fr/corpus/tcof | 200k mots transcrits (+20h audio) |
| Makxxx/french_CEFR | HF Makxxx/french_CEFR | phrases A1→C2 |
| iRead4Skills | Zenodo 10889888 | corpus FR par niveaux |
| CATIE-AQ prompts | org HF CATIE-AQ | collection 30 tâches |
| Zagreus-0.4B / Ilyana | modèles HF | RÉFÉRENCES, pas des données (pas de LLM dans le système) |

## Scripts

- `scripts/echantillonner_s1.py` : clone → échantillonne → jette le brut.
- `scripts/sonder_s2.py` : sonde les sources françaises.

## Règle de rotation

Quand le chef ordonne le suivant : on sort l'actuel (sa fiche reste),
on clone le suivant, on travaille. Jamais 2 complets ensemble.
