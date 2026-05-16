#!/usr/bin/env python3
"""Pull all templates from n8n public template library and save as JSON files."""

import json
import os
import time
import urllib.request

BASE_URL = "https://api.n8n.io/api/templates/search"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
ROWS = 50

os.makedirs(OUT_DIR, exist_ok=True)

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "cntxos-template-importer/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def pull_all():
    print("Fetching page 1...")
    first = fetch(f"{BASE_URL}?page=1&rows={ROWS}")
    total = first["totalWorkflows"]
    pages = (total + ROWS - 1) // ROWS
    print(f"Total: {total} templates, {pages} pages\n")

    saved = 0
    for page in range(1, pages + 1):
        try:
            if page == 1:
                data = first
            else:
                data = fetch(f"{BASE_URL}?page={page}&rows={ROWS}")

            for wf in data["workflows"]:
                wf_id = wf["id"]
                out_path = os.path.join(OUT_DIR, f"{wf_id}.json")
                if not os.path.exists(out_path):
                    with open(out_path, "w") as f:
                        json.dump(wf, f, indent=2)
                    saved += 1

            print(f"page {page}/{pages} — {saved} saved so far", flush=True)
            time.sleep(0.2)

        except Exception as e:
            print(f"page {page} error: {e}")
            time.sleep(2)

    print(f"\nDone. {saved} templates in {OUT_DIR}/")

if __name__ == "__main__":
    pull_all()
