import json
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOG_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "../specification/v1_0/catalogs/basic/catalog.json"))
INSTRUCTIONS_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "../specification/v1_0/catalogs/basic/instructions.md"))

with open(INSTRUCTIONS_PATH, "r") as f:
    instructions_text = f.read().strip()

with open(CATALOG_PATH, "r") as f:
    catalog = json.load(f)

catalog["instructions"] = instructions_text

with open(CATALOG_PATH, "w") as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print("Successfully injected instructions.md content into catalog.json instructions property!")
