#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ajoute la section française sans conserver de corpus volumineux.

La politique du dépôt est appliquée ici : API et HEAD pour les métadonnées,
extraits limités à 3 Mo, et suppression immédiate des archives temporaires.
Les corpus massifs restent re-clonables depuis leur source.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import quote

import requests

ROOT = Path(__file__).resolve().parents[1]
FR = ROOT / "francais"
MAX_SAMPLE = 3_000_000
N_LINES = 200
S = requests.Session()
S.headers.update({"User-Agent": "bases-donnees-catalogue/1.0"})


def get_json(url: str):
    r = S.get(url, timeout=60)
    r.raise_for_status()
    return r.json()


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()[:16]


def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def hf_info(repo: str) -> dict:
    return get_json(f"https://huggingface.co/api/datasets/{repo}")


def hf_sample(repo: str, filename: str, out: Path):
    url = f"https://huggingface.co/datasets/{repo}/resolve/main/{quote(filename, safe='/')}?download=true"
    out.parent.mkdir(parents=True, exist_ok=True)
    lines, size = [], 0
    with S.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        for raw in r.iter_lines(decode_unicode=True):
            if raw is None:
                continue
            line = raw if isinstance(raw, str) else raw.decode("utf-8", "replace")
            encoded = (line + "\n").encode("utf-8")
            if size + len(encoded) > MAX_SAMPLE or len(lines) >= N_LINES:
                break
            lines.append(line)
            size += len(encoded)
    out.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return len(lines), size


def add_cefr():
    repo = "Makxxx/french_CEFR"
    info = hf_info(repo)
    dst = FR / "cefr"
    sample = dst / "echantillon_train.csv.txt"
    n, size = hf_sample(repo, "train.csv.txt", sample)
    write_json(dst / "FICHE.json", {
        "nom": "french_CEFR",
        "source": f"https://huggingface.co/datasets/{repo}",
        "licence": "non indiquée par la carte HF",
        "taille_octets_annoncee": info.get("usedStorage"),
        "fichiers": [x.get("rfilename") for x in info.get("siblings", [])],
        "lignes_echantillon": n,
        "octets_echantillon": size,
        "sha_echantillon": sha(sample),
        "contenu": "phrases françaises classées A1 à C2",
    })


def add_cfdd():
    repo = "OpenLLM-France/Claire-Dialogue-French-0.1"
    info = hf_info(repo)
    dst = FR / "cfdd"
    # Un petit extrait du premier fichier public, sans snapshot.
    first = next((x["rfilename"] for x in info.get("siblings", []) if x.get("rfilename", "").endswith("train.txt")), None)
    sample_info = {}
    if first:
        try:
            n, size = hf_sample(repo, first, dst / "echantillon.txt")
            sample_info = {"fichier_source": first, "lignes_echantillon": n, "octets_echantillon": size,
                           "sha_echantillon": sha(dst / "echantillon.txt")}
        except requests.RequestException as e:
            sample_info = {"erreur_extrait": str(e)[:160]}
    write_json(dst / "FICHE.json", {
        "nom": "Claire French Dialogue Dataset (CFDD)",
        "source": f"https://huggingface.co/datasets/{repo}",
        "licence": "CC BY-NC-SA 4.0",
        "taille_octets_annoncee": info.get("usedStorage"),
        "statut": "catalogué; brut non conservé",
        "contenu": "théâtre et transcriptions de dialogues français",
        **sample_info,
    })


def add_ding():
    project = "https://gitlab.inria.fr/semagramme-public-projects/resources/ding"
    api = project.replace("https://gitlab.inria.fr/", "https://gitlab.inria.fr/api/v4/projects/")
    # L'identifiant URL-encodé est nécessaire pour l'API GitLab.
    api = "https://gitlab.inria.fr/api/v4/projects/semagramme-public-projects%2Fresources%2Fding/repository/tree?per_page=100&recursive=true"
    entries = get_json(api)
    files = [x["path"] for x in entries if x.get("type") == "blob"]
    dst = FR / "ding-01"
    samples = []
    for name in [x for x in files if x.endswith(".txt")][:2]:
        for branch in ("master", "main"):
            url = f"{project}/-/raw/{branch}/{quote(name, safe='/')}"
            try:
                r = S.get(url, timeout=60)
                if r.status_code == 200:
                    data = r.content[:MAX_SAMPLE]
                    out = dst / (Path(name).stem + ".txt")
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(data)
                    samples.append({"source": name, "octets": len(data), "sha256_16": sha(out)})
                    break
            except requests.RequestException:
                pass
    license_url = f"{project}/-/raw/master/LICENSE"
    license_status = S.get(license_url, timeout=30).status_code
    write_json(dst / "FICHE.json", {
        "nom": "DING",
        "source": project,
        "licence": "voir LICENSE du dépôt Inria" if license_status == 200 else "à vérifier",
        "fichiers_source": len(files),
        "fichiers_transcriptions": len([x for x in files if x.endswith(".txt")]),
        "fichiers_annotations": len([x for x in files if x.endswith(".conllu")]),
        "contenu": "dialogues spontanés Catan et annotations CoNLL-U",
        "samples": samples,
        "statut": "échantillon ajouté; source complète re-clonable",
    })


def add_iread():
    # La version demandée est devenue restreinte; la version publique active est 2.1.
    rec = get_json("https://zenodo.org/api/records/13768477")
    lex = get_json("https://zenodo.org/api/records/10889986")
    dst = FR / "iread4skills"
    write_json(dst / "FICHE.json", {
        "nom": "iRead4Skills Dataset 1",
        "source_demandee": "https://zenodo.org/records/10889888",
        "source_publique_active": "https://zenodo.org/records/13768477",
        "source_lexiques": "https://zenodo.org/records/10889986",
        "licence": "CC BY-NC-ND 4.0 (dataset 1, selon la notice); CC BY 4.0 (lexiques)",
        "statut": "dataset 1 restreint (API sans fichier); lexique public catalogué",
        "comptage_notice": {"fr_textes": 2199, "fr_tokens": 530298},
        "fichiers_lexiques": [{"nom": x.get("key"), "octets": x.get("size")} for x in lex.get("files", [])],
        "version": rec.get("metadata", {}).get("version"),
    })


def add_catie():
    data = get_json("https://huggingface.co/api/datasets?author=CATIE-AQ&limit=100")
    dst = FR / "catie-prompts"
    catalogue = []
    for item in data:
        catalogue.append({
            "id": item.get("id"), "url": "https://huggingface.co/datasets/" + item.get("id", ""),
            "licences": [x for x in item.get("tags", []) if "license" in x],
            "langues": [x for x in item.get("tags", []) if x.startswith("language")],
            "taches": [x for x in item.get("tags", []) if x.startswith("task_")],
            "taille": next((x for x in item.get("tags", []) if x.startswith("size_categories")), None),
        })
    (dst / "CATALOGUE.json").parent.mkdir(parents=True, exist_ok=True)
    (dst / "CATALOGUE.json").write_text(json.dumps(catalogue, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    sample_repo = "CATIE-AQ/frenchQA"
    info = hf_info(sample_repo)
    sample_file = next((x["rfilename"] for x in info.get("siblings", []) if not x["rfilename"].startswith(".")), None)
    sample = {}
    if sample_file:
        try:
            n, size = hf_sample(sample_repo, sample_file, dst / "echantillon_frenchQA.txt")
            sample = {"dataset": sample_repo, "fichier": sample_file, "lignes": n, "octets": size,
                      "sha_echantillon": sha(dst / "echantillon_frenchQA.txt")}
        except requests.RequestException as e:
            sample = {"dataset": sample_repo, "erreur": str(e)[:160]}
    write_json(dst / "FICHE.json", {
        "source": "https://huggingface.co/CATIE-AQ",
        "licence": "variable selon dataset; voir CATALOGUE.json",
        "datasets_catalogues": len(catalogue),
        "statut": "catalogue complet API; un échantillon représentatif, pas de snapshots massifs",
        "echantillon": sample,
    })


def add_site_only():
    write_json(FR / "fleuron" / "FICHE.json", {
        "nom": "FLEURON", "source": "https://apps.atilf.fr/fleuron/",
        "statut": "site/concordancier accessible; téléchargement en masse non trouvé",
        "action": "utiliser le site ou obtenir une autorisation d'export",
    })
    write_json(FR / "tcof" / "FICHE.json", {
        "nom": "TCOF", "source": "http://cnrtl.fr/corpus/tcof/",
        "statut": "transcriptions à extraire; liens directs non publiés par la page sondée",
        "regle": "ne prendre que les .trs, jamais l'audio",
    })


def main():
    for fn in (add_cefr, add_cfdd, add_ding, add_iread, add_catie, add_site_only):
        print("==", fn.__name__, flush=True)
        try:
            fn()
            print("OK", flush=True)
        except Exception as e:
            print("ECHEC", type(e).__name__, str(e)[:200], flush=True)
    print("TERMINE S2", flush=True)


if __name__ == "__main__":
    main()
