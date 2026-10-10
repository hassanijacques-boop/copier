#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Publie les descriptions du jour sur la page "A COPIER".
Utilise par les jobs cron Foot en Bref et Human Matrix.

Usage :
  python3 publier_description.py foot "Titre" "date" "texte complet"
  python3 publier_description.py humanmatrix "Titre" "date" "texte complet"

Met a jour /workspace/copier/descriptions.json puis pousse sur GitHub Pages
(repo hassanijacques-boop/copier).
"""
import sys, json, pathlib, subprocess, datetime, re

BASE = pathlib.Path("/workspace/copier")
JSON = BASE / "descriptions.json"
REPO = "copier"
OWNER = "hassanijacques-boop"

JOURS = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]
MOIS = ["janvier","février","mars","avril","mai","juin","juillet","août",
        "septembre","octobre","novembre","décembre"]

def maintenant():
    d = datetime.datetime.utcnow() + datetime.timedelta(hours=3)   # Mayotte
    return f"{JOURS[d.weekday()]} {d.day} {MOIS[d.month-1]} à {d.hour}h{d.minute:02d}"

def charger():
    if JSON.exists():
        try:
            return json.loads(JSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"maj": "", "blocs": {}}

def token():
    for p in ["/tmp/ghtoken"]:
        f = pathlib.Path(p)
        if f.exists() and f.read_text().strip():
            return f.read_text().strip()
    cfg = pathlib.Path("/workspace/protocole30j/.git/config")
    if cfg.exists():
        m = re.search(r"https://[^@]*:([^@]+)@github\.com", cfg.read_text())
        if m:
            return m.group(1)
    return None

def main():
    if len(sys.argv) < 5:
        print("usage : publier_description.py <cle> <titre> <date> <texte>")
        return 1
    cle, titre, date, texte = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    d = charger()
    d["blocs"][cle] = {"titre": titre, "date": date, "texte": texte}
    d["maj"] = maintenant()
    BASE.mkdir(parents=True, exist_ok=True)
    JSON.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  OK descriptions.json mis a jour (bloc « {cle} »)")

    tk = token()
    if not tk:
        print("  (pas de token GitHub -> pas de publication en ligne)")
        return 0
    git = ["git", "-C", str(BASE)]
    subprocess.run(git + ["init", "-q", "-b", "main"], capture_output=True)
    subprocess.run(git + ["config", "user.email", "hassanijacques@gmail.com"], capture_output=True)
    subprocess.run(git + ["config", "user.name", OWNER], capture_output=True)
    subprocess.run(git + ["add", "-A"], capture_output=True)
    subprocess.run(git + ["commit", "-q", "-m", f"MAJ {cle}"], capture_output=True)
    subprocess.run(git + ["remote", "remove", "origin"], capture_output=True)
    subprocess.run(git + ["remote", "add", "origin",
                          f"https://{OWNER}:{tk}@github.com/{OWNER}/{REPO}.git"], capture_output=True)
    r = subprocess.run(git + ["push", "-q", "-u", "origin", "main", "--force"],
                       capture_output=True, text=True)
    if r.returncode == 0:
        print(f"  OK publie -> https://{OWNER}.github.io/{REPO}/")
    else:
        print(f"  ERREUR push : {(r.stderr or '')[:200]}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
