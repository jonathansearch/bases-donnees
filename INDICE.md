# INDICE du dépôt

Le dépôt est un **catalogue léger** : fiches JSON, extraits et scripts
reproductibles. Les archives brutes ne sont jamais conservées. Le plafond
opérationnel est de 128 Mo et un échantillon ne dépasse pas 3 Mo.

## Dataset de travail

Aucun snapshot complet n'est conservé. Les corpus sont re-clonables à la
demande, puis supprimés après comptage et prélèvement.

## Conversations

| # | Dataset | Taille annoncée | Contenu / vérification | Statut |
|---|---|---:|---|---|
| 1 | discord-dialogues | 347 729 144 o | 7 300 966 lignes, 1 parquet, 200 lignes échantillonnées | ✅ fiche + extrait |
| 2 | yield | 362 440 161 o | 105 735 blocs, 2 281 dialogues, 4 domaines | ✅ fiche + extrait |
| 3 | ko-agent | 1 358 916 399 o | 600 fichiers JSON, 1 000 lignes échantillonnées | ✅ fiche + extrait |
| 4 | lmsys-chat-1m | ~1,49 Go | 1M conversations, 6 parquets | 🔒 gated HF, fiche ajoutée |
| 5 | ultrachat-200k | 1 624 060 272 o | 515 311 lignes, 8 parquets | ✅ fiche + extrait |
| 6 | escorpius-dialog v1.2 | 2 979 959 806 o | 8 fichiers Zenodo; archives dehydrated = identifiants | ✅ métadonnées + fiche, brut jeté |
| 7 | wildchat-1m | 3 360 876 486 o | 837 989 lignes, 14 parquets | ✅ fiche + extrait |

Les fichiers complets sont volontairement absents de Git et peuvent être
récupérés avec les sources listées dans `LISTE-RESTE.md`.

## Français

| Dataset | Taille / comptage | Statut |
|---|---:|---|
| accueil-ubs | 41 dialogues, 1062 tours, 6295 mots appris | ✅ BU 4 passages, réservoir vide (cerveau +101 neurones, +2166 liens) |
| CFDD / Claire | 15 089 356 633 o selon l'API HF | ✅ fiche + statut 401 documenté; brut non conservé |
| ding-01 | 10 dialogues, 14834 tours, 70274 mots appris | ✅ BU 4 passages, réservoir vide (+531 neurones, +12102 liens) |
| FLEURON | site ATILF, masse non trouvée; URL renvoie actuellement 404 | ⚠️ site seul documenté |
| TCOF | environ 200k mots annoncés | ⚠️ page actuelle 404; transcription `.trs` à obtenir ailleurs, pas d'audio |
| french_CEFR | 6000 phrases A1..C2, 109486 mots appris | ✅ BU 4 passages, réservoir vide (+5571 neurones, +38332 liens, MA1..MC2) |
| frenchQA | 204715 Q&R, 2398744 mots appris | ✅ BU leçon 41, brut jeté (+32903 neurones, +92673 liens, Q&R) |
| piaf | 3835 Q&R natif, 52658 mots appris | ✅ BU leçon 42, brut jeté (+48 neurones, +9536 liens, Q&R natif) |
| fquad2 | 1000 Q&R natif, 11700 mots appris | ✅ BU leçon 43, brut jeté (+214 neurones, +2866 liens, Q&R natif) |
| iRead4Skills | 2 199 textes FR / 530 298 tokens annoncés; dataset 1 restreint | ✅ versions et accès documentés; lexique public 544 270 o |
| CATIE-AQ | 100 datasets catalogués par l'API | ✅ `CATALOGUE.json` + extrait frenchQA |
| Zagreus-0.4B / Ilyana | modèles, pas corpus | ✅ références seulement, aucun poids téléchargé |

## Scripts

- `scripts/echantillonner_s1.py` : clone temporaire → échantillon → suppression
  du brut; chemin calculé depuis le dépôt, sans `/home/user` en dur.
- `scripts/sonder_s2.py` : sondage HTTP sans dépendance `huggingface_hub`.
- `scripts/ajouter_s2.py` : ajoute les fiches et extraits français via API,
  sans snapshot massif.

## Validation

```bash
python3 -m py_compile scripts/*.py
python3 scripts/sonder_s2.py
python3 scripts/ajouter_s2.py
```

Le dépôt ne conserve actuellement aucun fichier de données supérieur à 3 Mo.
