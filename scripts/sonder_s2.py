#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SECTION 2 (français) : sonde les sources (tailles, liens directs)."""
import json
import requests

S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0"


def get(u, timeout=30):
    try:
        r = S.get(u, timeout=timeout)
        return r.status_code, r.text
    except Exception as e:
        return -1, str(e)[:100]


def liens_href(page, mots):
    """Tous les href contenant un des mots (sans regex)."""
    trouves, i = [], 0
    while True:
        j = page.find("href", i)
        if j < 0:
            break
        k = page.find('"', j)
        if k < 0:
            break
        fin = page.find('"', k + 1)
        if fin < 0:
            break
        url = page[k + 1:fin]
        bas = url.lower()
        if any(m in bas for m in mots):
            if url not in trouves:
                trouves.append(url)
        i = fin + 1
    return trouves


def main():
    print("== 1. CEFR ==", flush=True)
    from huggingface_hub import HfApi
    try:
        inf = HfApi().dataset_info("Makxxx/french_CEFR", files_metadata=True)
        tot = sum(s.size or 0 for s in (inf.siblings or []) if s.size)
        print("  taille: %.1f Mo" % (tot / 1e6))
        for s in (inf.siblings or [])[:8]:
            print("  ", s.rfilename, (s.size or 0) // 1024, "Ko")
        print("  licence:", [t for t in (inf.tags or []) if "license" in t])
    except Exception as e:
        print("  ERR", e)
    print("== 2. CFDD ==", flush=True)
    try:
        inf = HfApi().dataset_info("OpenLLM-France/Claire-Dialogue-French-0.1",
                                   files_metadata=True)
        tot = sum(s.size or 0 for s in (inf.siblings or []) if s.size)
        print("  taille: %.2f Go, fichiers: %d"
              % (tot / 1e9, len(inf.siblings or [])))
        print("  licence:", [t for t in (inf.tags or []) if "license" in t])
    except Exception as e:
        print("  ERR", e)
    print("== 3. CATIE-AQ org ==", flush=True)
    try:
        ds = S.get("https://huggingface.co/api/datasets?author=CATIE-AQ"
                   "&limit=100&sort=downloads&direction=-1",
                   timeout=30).json()
        print("  nb datasets:", len(ds))
        for d in ds[:40]:
            print("  -", d.get("id"), d.get("downloads"))
    except Exception as e:
        print("  ERR", e)
    print("== 4. ORTOLANG ANCOR ==", flush=True)
    c, t = get("https://www.ortolang.fr/market/item/ortolang-000903/v3")
    print("  page:", c, len(t), "octets")
    for m in liens_href(t, ["download", "content", "zip"])[:10]:
        print("  lien:", m[:120])
    print("== 5. univ-tours Accueil ==", flush=True)
    c, t = get("https://www.info.univ-tours.fr/~antoine/parole_publique/"
               "Accueil_UBS/index.html")
    print("  page:", c, len(t), "octets")
    for m in liens_href(t, [".zip"])[:6]:
        print("  zip:", m[:150])
    print("== 6. GitLab ding ==", flush=True)
    c, t = get("https://gitlab.inria.fr/api/v4/projects/"
               "semagramme-public-projects%2Fresources%2Fding/"
               "repository/tree?per_page=100&recursive=true")
    print("  api:", c)
    if c == 200:
        for e in json.loads(t)[:25]:
            print("  ", e.get("type"), e.get("path"))
    print("== 7. FLEURON ==", flush=True)
    c, t = get("https://apps.atilf.fr/fleuron/")
    print("  site:", c, len(t), "octets")
    for m in liens_href(t, ["zip", "download", "corpus", "telecharg"])[:6]:
        print("  lien:", m[:120])
    print("== 8. TCOF CNRTL ==", flush=True)
    c, t = get("http://cnrtl.fr/corpus/tcof/")
    print("  page:", c, len(t), "octets")
    for m in liens_href(t, ["zip", "trs", "wav", "mp3", "download"])[:10]:
        print("  lien:", m[:130])
    print("== 9. iRead Zenodo 10889888 ==", flush=True)
    try:
        r = S.get("https://zenodo.org/api/records/10889888",
                  timeout=30).json()
        print("  titre:", (r.get("metadata", {}).get("title") or "?")[:70])
        for f in r.get("files", []):
            print("   %.1f Mo  %s" % (f.get("size", 0) / 1e6, f.get("key")))
    except Exception as e:
        print("  ERR", e)


if __name__ == "__main__":
    main()
