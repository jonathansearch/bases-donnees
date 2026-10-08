#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SECTION 1 (conversations) : clone -> échantillonne -> jette le brut.

Loi du dépôt : ici les Go ne dorment pas (le snapshot les avale et la
session plante). On télécharge, on prélève un échantillon + une fiche,
on jette le brut aussitôt. Les sources restent notées : on re-clone
en quelques minutes quand le chef lance la méthode.
"""
import os
import io
import json
import gzip
import hashlib
import shutil
import zipfile
import tarfile
from pathlib import Path

# Le dépôt peut être cloné n'importe où : ne pas dépendre de /home/user.
ROOT = Path(__file__).resolve().parents[1]
BASE = str(ROOT / "conversations")
TMP = str(ROOT / "_tmp")
N_LIGNES = 200
PLAFOND = 3_000_000  # ~3 Mo max par échantillon


def taille(d):
    t = 0
    for r, _, fs in os.walk(d):
        for f in fs:
            t += os.path.getsize(os.path.join(r, f))
    return t


def echantillonner(src, dst):
    """parquet / jsonl / json / autre -> echantillon + fiche (sans OOM)."""
    import pandas as pd
    import pyarrow.parquet as pq
    os.makedirs(dst, exist_ok=True)
    pars = []
    for r, _, fs in os.walk(src):
        for f in sorted(fs):
            if f.endswith(".parquet"):
                pars.append(os.path.join(r, f))
    info = {"fichiers_parquet": len(pars)}
    if pars:
        tot, morceaux, besoin = 0, [], N_LIGNES
        for p in pars:
            try:
                pf = pq.ParquetFile(p)
                tot += pf.metadata.num_rows
                if besoin > 0:
                    for lot in pf.iter_batches(batch_size=min(besoin, 500)):
                        morceaux.append(lot.to_pandas())
                        besoin -= len(lot)
                        if besoin <= 0:
                            break
            except Exception as e:
                info.setdefault("erreurs", []).append(
                    "%s: %s" % (os.path.basename(p), e))
        if morceaux:
            ech = pd.concat(morceaux, ignore_index=True).head(N_LIGNES)
            s = ech.to_json(orient="records", lines=True, force_ascii=False)
            while len(s.encode("utf-8")) > PLAFOND and len(ech) > 20:
                ech = ech.head(len(ech) // 2)
                s = ech.to_json(orient="records", lines=True, force_ascii=False)
            with open(os.path.join(dst, "echantillon.jsonl"), "w",
                      encoding="utf-8") as fh:
                fh.write(s)
            info.update({"lignes_echantillon": len(ech),
                         "lignes_totales": tot,
                         "colonnes": list(ech.columns)})
        return info
    jl = []
    for r, _, fs in os.walk(src):
        for f in sorted(fs):
            if f.endswith(".jsonl") or f.endswith(".jsonl.gz") \
                    or f.endswith(".json"):
                jl.append(os.path.join(r, f))
    info["fichiers_json"] = len(jl)
    if jl:
        lignes, prises = 0, []
        for j in jl[:5]:
            try:
                if j.endswith(".gz"):
                    fh = gzip.open(j, "rt", encoding="utf-8")
                else:
                    fh = open(j, encoding="utf-8")
                with fh:
                    for ln in fh:
                        lignes += 1
                        if len(prises) < N_LIGNES * 5:
                            prises.append(ln.rstrip("\n"))
            except Exception as e:
                info.setdefault("erreurs", []).append(
                    "%s: %s" % (os.path.basename(j), e))
        while prises:
            s = "\n".join(prises)
            if len(s.encode("utf-8")) <= PLAFOND or len(prises) <= 20:
                break
            prises = prises[:len(prises) // 2]
        if prises:
            with open(os.path.join(dst, "echantillon.jsonl"), "w",
                      encoding="utf-8") as fh:
                fh.write("\n".join(prises))
        info.update({"lignes_echantillon": len(prises),
                     "lignes_vues_5fichiers": lignes,
                     "note": "comptage sur les 5 premiers fichiers"})
        return info
    tout = []
    for r, _, fs in os.walk(src):
        for f in sorted(fs):
            tout.append(os.path.relpath(os.path.join(r, f), src))
    info["fichiers"] = len(tout)
    for t in tout[:3]:
        try:
            with open(os.path.join(src, t), "rb") as fh:
                head = fh.read(2000)
            with open(os.path.join(dst, "tete_" + os.path.basename(t)
                                   + ".txt"), "wb") as fh:
                fh.write(head)
        except Exception:
            pass
    return info


def fiche_license(inf):
    for t in (inf.tags or []):
        if t.startswith("license:"):
            return t.split(":", 1)[1]
    return "?"


def job_hf(api, repo, dossier):
    from huggingface_hub import snapshot_download
    try:
        inf = api.dataset_info(repo, files_metadata=True)
        annonce = sum(s.size or 0 for s in (inf.siblings or []) if s.size)
        lic = fiche_license(inf)
    except Exception as e:
        print("INFO %s: %s" % (dossier, e), flush=True)
        annonce, lic = 0, "?"
    src = os.path.join(TMP, dossier)
    try:
        print("--- %s (annonce %.2f Go) ---" % (repo, annonce / 1e9),
              flush=True)
        snapshot_download(repo, repo_type="dataset", local_dir=src)
        reel = taille(src)
        print("reçu %.2f Go, échantillonne..." % (reel / 1e9), flush=True)
        dst = os.path.join(BASE, dossier)
        res = echantillonner(src, dst)
        res.update({"source": "https://huggingface.co/datasets/" + repo,
                    "licence": lic, "taille_octets": reel})
        e = os.path.join(dst, "echantillon.jsonl")
        if os.path.exists(e):
            with open(e, "rb") as fh:
                res["sha_echantillon"] = hashlib.sha256(fh.read()
                                                       ).hexdigest()[:16]
        with open(os.path.join(dst, "FICHE.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, ensure_ascii=False)
        print("OK %s: %s lignes, échantillon %s" % (
            dossier, res.get("lignes_totales",
                             res.get("lignes_vues_5fichiers", "?")),
            res.get("lignes_echantillon", 0)), flush=True)
    except Exception as e:
        print("ECHEC %s: %s %s" % (dossier, type(e).__name__, str(e)[:150]),
              flush=True)
    finally:
        shutil.rmtree(src, ignore_errors=True)


def job_zenodo(escorpius_id=18466512):
    import requests
    dst = os.path.join(BASE, "escorpius-dialog")
    os.makedirs(dst, exist_ok=True)
    tmp = os.path.join(TMP, "escorpius")
    os.makedirs(tmp, exist_ok=True)
    rec = requests.get("https://zenodo.org/api/records/%d" % escorpius_id,
                       timeout=60).json()
    print("--- esCorpiusDialog v%s (%d fichiers) ---" % (
        rec.get("metadata", {}).get("version"), len(rec.get("files", []))),
        flush=True)
    fiche = {"source": "https://zenodo.org/records/%d" % escorpius_id,
             "licence": "CC BY-NC-ND 4.0", "fichiers": {}}
    tetes, budget = [], PLAFOND
    for f in rec.get("files", []):
        key, want = f["key"], f.get("size", 0)
        links = f.get("links", {})
        urls = []
        if links.get("download"):
            urls.append(links["download"])
        urls.append("https://zenodo.org/records/%d/files/%s?download=1"
                    % (escorpius_id, key))
        dest = os.path.join(tmp, key)
        got = 0
        for u in urls:
            try:
                with requests.get(u, stream=True, timeout=180) as d:
                    d.raise_for_status()
                    with open(dest, "wb") as fh:
                        for ch in d.iter_content(4 * 1024 * 1024):
                            fh.write(ch)
                got = os.path.getsize(dest)
                break
            except Exception as e:
                print("retry %s: %s" % (key, str(e)[:80]), flush=True)
        if not got:
            fiche["fichiers"][key] = {"statut": "ECHEC"}
            continue
        ent = {"octets": got, "membres": 0, "octets_membres": 0}
        try:
            if key.endswith(".zip"):
                with zipfile.ZipFile(dest) as z:
                    for m in z.infolist():
                        if m.is_dir():
                            continue
                        ent["membres"] += 1
                        ent["octets_membres"] += m.file_size
                        if budget > 0 and len(tetes) < 400:
                            with z.open(m) as fh:
                                morceau = fh.read(20000).decode(
                                    "utf-8", "replace")
                            tetes.append("===== %s :: %s =====\n%s"
                                         % (key, m.filename, morceau))
                            budget -= len(morceau)
            elif key.endswith(".tar.gz"):
                with tarfile.open(dest, "r:gz") as t:
                    for m in t.getmembers():
                        if not m.isfile():
                            continue
                        ent["membres"] += 1
                        ent["octets_membres"] += m.size
                        if budget > 0 and len(tetes) < 400:
                            fh = t.extractfile(m)
                            morceau = fh.read(20000).decode(
                                "utf-8", "replace") if fh else ""
                            tetes.append("===== %s :: %s =====\n%s"
                                         % (key, m.name, morceau))
                            budget -= len(morceau)
            else:
                with open(dest, "rb") as fh:
                    tetes.append("===== %s =====\n%s"
                                 % (key, fh.read(5000).decode(
                                     "utf-8", "replace")))
        except Exception as e:
            ent["erreur"] = "%s %s" % (type(e).__name__, str(e)[:100])
        fiche["fichiers"][key] = ent
        os.remove(dest)
        print("OK %s (%d membres)" % (key, ent["membres"]), flush=True)
    if tetes:
        with open(os.path.join(dst, "echantillon.txt"), "w",
                  encoding="utf-8") as fh:
            fh.write("\n\n".join(tetes))
    fiche["taille_octets"] = sum(
        v.get("octets", 0) for v in fiche["fichiers"].values())
    with open(os.path.join(dst, "FICHE.json"), "w",
              encoding="utf-8") as fh:
        json.dump(fiche, fh, indent=1, ensure_ascii=False)
    shutil.rmtree(tmp, ignore_errors=True)
    print("OK escorpius-dialog", flush=True)


def fiche_lmsys():
    dst = os.path.join(BASE, "lmsys-chat-1m")
    os.makedirs(dst, exist_ok=True)
    fiche = {"source": "https://huggingface.co/datasets/lmsys/lmsys-chat-1m",
             "licence": "à vérifier sur la carte",
             "taille_annoncee_octets": 1490000000,
             "statut": "gated-401-anonyme",
             "action": "1 clic 'accepter les conditions' sur HF, puis re-cloner"}
    with open(os.path.join(dst, "FICHE.json"), "w",
              encoding="utf-8") as fh:
        json.dump(fiche, fh, indent=1, ensure_ascii=False)
    print("NOTE lmsys-chat-1m: gated (1 clic requis)", flush=True)


def main():
    from huggingface_hub import HfApi
    os.makedirs(BASE, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    api = HfApi()
    for repo, dossier in [("mookiezi/Discord-Dialogues", "discord-dialogues"),
                          ("infosense/yield", "yield"),
                          ("taejoon89/Ko-Agent-Trajectories-1.0", "ko-agent"),
                          ("HuggingFaceH4/ultrachat_200k", "ultrachat-200k"),
                          ("allenai/WildChat-1M", "wildchat-1m")]:
        job_hf(api, repo, dossier)
    job_zenodo()
    fiche_lmsys()
    shutil.rmtree(TMP, ignore_errors=True)
    print("TERMINE S1", flush=True)


if __name__ == "__main__":
    main()
