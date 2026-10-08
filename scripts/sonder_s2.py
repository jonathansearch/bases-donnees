#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sonde les sources françaises avec leurs API HTTP publiques.

Ce script ne dépend pas de huggingface_hub : il reste exécutable après un
clone frais et ne télécharge aucun corpus complet.
"""
import json
import requests

S = requests.Session()
S.headers.update({"User-Agent": "bases-donnees-sondage/1.0"})


def get_json(url, timeout=60):
    r = S.get(url, timeout=timeout)
    r.raise_for_status()
    return r.json()


def hf(repo):
    d = get_json("https://huggingface.co/api/datasets/" + repo)
    files = [x.get("rfilename") for x in d.get("siblings", [])]
    return {
        "repo": repo,
        "taille_octets": d.get("usedStorage"),
        "fichiers": len(files),
        "licences": [x for x in d.get("tags", []) if "license" in x],
        "exemples": files[:8],
    }


def main():
    print("== HF français ==", flush=True)
    for repo in [
        "Makxxx/french_CEFR",
        "OpenLLM-France/Claire-Dialogue-French-0.1",
    ]:
        try:
            print(json.dumps(hf(repo), ensure_ascii=False), flush=True)
        except Exception as e:
            print("ERR", repo, type(e).__name__, str(e)[:160], flush=True)

    print("== CATIE-AQ ==", flush=True)
    try:
        ds = get_json("https://huggingface.co/api/datasets?author=CATIE-AQ&limit=100")
        print(json.dumps({"datasets": len(ds), "premiers": [x.get("id") for x in ds[:10]]}, ensure_ascii=False), flush=True)
    except Exception as e:
        print("ERR CATIE", type(e).__name__, str(e)[:160], flush=True)

    print("== GitLab DING ==", flush=True)
    try:
        url = ("https://gitlab.inria.fr/api/v4/projects/"
               "semagramme-public-projects%2Fresources%2Fding/repository/tree"
               "?per_page=100&recursive=true")
        tree = get_json(url)
        files = [x.get("path") for x in tree if x.get("type") == "blob"]
        print(json.dumps({"fichiers": len(files), "txt": len([x for x in files if x.endswith('.txt')]), "conllu": len([x for x in files if x.endswith('.conllu')])}), flush=True)
    except Exception as e:
        print("ERR DING", type(e).__name__, str(e)[:160], flush=True)

    print("== Zenodo iRead4Skills ==", flush=True)
    for rid in [10889888, 13768477, 10889986]:
        try:
            d = get_json(f"https://zenodo.org/api/records/{rid}")
            print(json.dumps({"id": rid, "titre": d.get("metadata", {}).get("title"), "version": d.get("metadata", {}).get("version"), "fichiers": len(d.get("files", [])), "acces": d.get("metadata", {}).get("access_right")}, ensure_ascii=False), flush=True)
        except Exception as e:
            print("ERR Zenodo", rid, type(e).__name__, str(e)[:160], flush=True)

    print("== Sites ==", flush=True)
    for name, url in [
        ("FLEURON", "https://apps.atilf.fr/fleuron/"),
        ("TCOF", "http://cnrtl.fr/corpus/tcof/"),
    ]:
        try:
            r = S.get(url, timeout=60)
            print(name, r.status_code, len(r.content), r.url, flush=True)
        except Exception as e:
            print("ERR", name, type(e).__name__, str(e)[:160], flush=True)


if __name__ == "__main__":
    main()
