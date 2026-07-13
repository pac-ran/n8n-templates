#!/usr/bin/env python3
"""Pull full workflow JSON for all n8n community templates."""

import json
import os
import time
import urllib.request

SEARCH_URL = "https://api.n8n.io/api/templates/search"
DETAIL_URL = "https://api.n8n.io/api/templates/workflows"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
ROWS = 50

os.makedirs(OUT_DIR, exist_ok=True)

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "cntxos-template-importer/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def pull_all():
    print("Fetching index page 1...")
    first = fetch(f"{SEARCH_URL}?page=1&rows={ROWS}")
    total = first["totalWorkflows"]
    pages = (total + ROWS - 1) // ROWS
    print(f"Total: {total} templates, {pages} pages\n")

    # collect all IDs from index
    all_ids = []
    for wf in first["workflows"]:
        all_ids.append(wf["id"])

    for page in range(2, pages + 1):
        try:
            data = fetch(f"{SEARCH_URL}?page={page}&rows={ROWS}")
            for wf in data["workflows"]:
                all_ids.append(wf["id"])
            print(f"index page {page}/{pages} — {len(all_ids)} ids collected", flush=True)
            time.sleep(0.15)
        except Exception as e:
            print(f"index page {page} error: {e}")
            time.sleep(2)

    print(f"\nFetching full workflow JSON for {len(all_ids)} templates...\n")
    saved = 0
    errors = 0
    for wf_id in all_ids:
        out_path = os.path.join(OUT_DIR, f"{wf_id}.json")
        if os.path.exists(out_path):
            saved += 1
            continue
        try:
            detail = fetch(f"{DETAIL_URL}/{wf_id}")
            with open(out_path, "w") as f:
                json.dump(detail, f, indent=2)
            saved += 1
            if saved % 100 == 0:
                print(f"  {saved}/{len(all_ids)} saved ({errors} errors)", flush=True)
            time.sleep(0.15)
        except Exception as e:
            errors += 1
            print(f"  id {wf_id} error: {e}")
            time.sleep(1)

    print(f"\nDone. {saved} templates saved, {errors} errors.")

if __name__ == "__main__":
    pull_all()
