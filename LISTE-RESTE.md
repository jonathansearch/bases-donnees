# LISTE — tout ce qui reste à ajouter au dépôt (pour l'autre agent)

Contexte : `/home/user/bases-donnees/` = le dépôt. Dedans : UN catalogue
léger (fiches + échantillons, voir `INDICE.md`) et les scripts
(`scripts/echantillonner_s1.py`, `scripts/sonder_s2.py`).

LOI DU DÉPÔT (respecte-la, sinon la session plante) : ici le plafond est
128 Mo. On ne garde JAMAIS de Go qui dorment. Méthode : clone → vérifie
(taille, comptage, 1 extrait) → échantillon + fiche → JETTE le brut.
Vitesse mesurée : ~60 Mo/s. Tout est re-clonable en minutes.

Outils : `pip install huggingface_hub pyarrow pandas` (à refaire à
chaque session, les paquets ne persistent pas).

---

## SECTION 1 — conversations (Ordre : du plus petit au plus grand)

### 1. discord-dialogues — 331 Mo — ✅ vérifié anonyme
- Source : https://huggingface.co/datasets/mookiezi/Discord-Dialogues
- Licence : Apache-2.0. Contenu : 7 300 966 lignes (1 parquet).
- Commande :
  snapshot_download("mookiezi/Discord-Dialogues", repo_type="dataset",
  local_dir="conversations/discord-dialogues", ignore_patterns=["assets/*"])

### 2. yield — 363 Mo — ✅ vérifié anonyme
- Source : https://huggingface.co/datasets/infosense/yield
- Licence : CC BY 4.0. Contenu : 105 735 blocs (2 281 dialogues),
  4 domaines, dossiers yield/ + yield-experimental/, train/test.
- Commande :
  snapshot_download("infosense/yield", repo_type="dataset",
  local_dir="conversations/yield")

### 3. ko-agent — 1,36 Go, 654 fichiers — ✅ vérifié anonyme
- Source : https://huggingface.co/datasets/taejoon89/Ko-Agent-Trajectories-1.0
- Licence : ? (noter celle de la carte). Contenu : jsonl + jsonl.gz
  (dpo/, cross_judge/, dpo_behavior/, ...), trajectoires avec outils.
- Commande :
  snapshot_download("taejoon89/Ko-Agent-Trajectories-1.0",
  repo_type="dataset", local_dir="conversations/ko-agent")

### 4. lmsys-chat-1m — 1,49 Go — 🔒 GATED (401 anonyme)
- Source : https://huggingface.co/datasets/lmsys/lmsys-chat-1m
- Contenu : 1M conversations (6 parquets). Bloqué sans compte HF :
  1 clic "accepter les conditions" sur la page, puis re-cloner avec
  token (`huggingface-cli login` ou HF_TOKEN=...).
- Commande (après acceptation) :
  snapshot_download("lmsys/lmsys-chat-1m", repo_type="dataset",
  local_dir="conversations/lmsys-chat-1m")

### 5. ultrachat-200k — 1,62 Go — ✅ vérifié anonyme
- Source : https://huggingface.co/datasets/HuggingFaceH4/ultrachat_200k
- Contenu : 515 311 lignes (train_sft + train_gen, parquets).
- Commande :
  snapshot_download("HuggingFaceH4/ultrachat_200k", repo_type="dataset",
  local_dir="conversations/ultrachat-200k")

### 6. escorpius-dialog — 2,98 Go — ✅ Zenodo, à finir
- Source : https://zenodo.org/records/18466512 (v1.2)
- Licence : CC BY-NC-ND 4.0. 8 fichiers : usenet.zip (1,46 Go),
  open_subtitles.zip (1,38 Go), gutenberg.zip (3 Mo),
  meneame/mediavida/reddit dehydrated (IDs SEULS, pas de texte :
  rehydratation depuis les plateformes d'origine, à part),
  LICENSE.txt, README.txt.
- Déjà vérifié : meneame 221 747 membres OK, usenet 2 membres OK.
  RESTE : finir open_subtitles + reddit + mediavida + fiche.
- Commande : API https://zenodo.org/api/records/18466512 puis
  download fichier par fichier :
  https://zenodo.org/records/18466512/files/<nom>?download=1
  (GARDER les zips tels quels, ne pas tout dézipper : 10 Go+ !)

### 7. wildchat-1m — 3,36 Go — ✅ vérifié anonyme
- Source : https://huggingface.co/datasets/allenai/WildChat-1M
- Contenu : 837 989 lignes (15 parquets).
- Commande :
  snapshot_download("allenai/WildChat-1M", repo_type="dataset",
  local_dir="conversations/wildchat-1m")

---

## SECTION 2 — français (sonder d'abord : `python3 scripts/sonder_s2.py`)

### 8. accueil-ubs — 745 Ko — ✅ vérifié (déjà cloné 1 fois)
- Source : https://www.info.univ-tours.fr/~antoine/parole_publique/Accueil_UBS/DISTRIBUTION_ACCUEIL_UBS.zip
- Licence : CC BY-SA. Contenu : 40 dialogues téléphoniques réels,
  26 045 mots (TRANS_TXT + TRANS_XML + docs).
- Commande : télécharger le ZIP, dézipper dans
  `francais/accueil-ubs/brut/`, compter les mots, fiche.

### 9. CFDD — ~160M mots — source OK, taille à mesurer
- Source : https://huggingface.co/datasets/OpenLLM-France/Claire-Dialogue-French-0.1
- Licence : CC BY-NC-SA (annoncée). Théâtre + débats + oral.
- Commande : mesurer d'abord (`dataset_info(..., files_metadata=True)`),
  puis snapshot_download vers `francais/cfdd/`.

### 10. ding-01 — taille à mesurer
- Transcriptions : https://gitlab.inria.fr/semagramme-public-projects/resources/ding
  (API : /api/v4/projects/semagramme-public-projects%2Fresources%2Fding/repository/tree?per_page=100&recursive=true)
- Annotations AMR : papier arXiv 2508.12819 (trouver le dépôt du papier).
- Dialogues Catan spontanés. Vers `francais/ding-01/`.

### 11. FLEURON — ⚠️ masse NON TROUVÉE, à investiguer
- Site : https://apps.atilf.fr/fleuron/ (concordancier pédagogique).
- Chercher un téléchargement en masse (sinon : noter "site seul").
- Vers `francais/fleuron/` si masse trouvée.

### 12. TCOF — 200k mots (+20h audio) — liens à extraire
- Page : http://cnrtl.fr/corpus/tcof/
- Prendre les TRANSCRIPTIONS seules (.trs), PAS l'audio (Go inutiles).
- Vers `francais/tcof/`.

### 13. Makxxx/french_CEFR — taille à mesurer
- Source : https://huggingface.co/datasets/Makxxx/french_CEFR
- Phrases A1→C2. Mesurer puis snapshot_download vers `francais/cefr/`.

### 14. iRead4Skills — fichiers à lister
- Corpus : https://zenodo.org/api/records/10889888 (Dataset 1 FR/PT/SP,
  CC BY-NC-ND). Lexiques : https://zenodo.org/records/10889986 (544 Ko).
- Prendre le FR (+ lexiques, minuscules). Vers `francais/iread4skills/`.

### 15. CATIE-AQ prompts — ~30 datasets, liste à tirer
- API : https://huggingface.co/api/datasets?author=CATIE-AQ&limit=100
- Collection 30 tâches (déjà vus : frenchQA, french_books,
  orange_sum_fr, stsb, paws-x...). Cloner chaque dataset
  (petits, prompts). Vers `francais/catie-prompts/<nom>/`.

### 16. Zagreus-0.4B / Ilyana — MODÈLES, ne pas cloner
- Références d'inspiration seulement (poids de LLM).
- PAS de LLM dans le système : noter les liens, ne RIEN télécharger.

---

## Après chaque ajout (obligatoire)

1. Vérifier : taille réelle, comptage (lignes/membres/mots), 1 extrait.
2. Écrire `FICHE.json` (source, licence, taille, comptage, sha).
3. Garder UN échantillon ≤ 3 Mo si le dataset est gros.
4. JETER le brut si > 50 Mo (le snapshot ne le gardera pas de toute façon).
5. Mettre à jour `INDICE.md` (statut ✅ + chiffres).
