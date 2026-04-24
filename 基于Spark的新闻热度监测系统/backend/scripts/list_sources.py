from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.collectors import flatten_source_catalog, list_collectable_sources, load_source_catalog


def main() -> None:
    catalog = load_source_catalog()
    flattened = flatten_source_catalog(catalog)
    summary = {
        "metadata": catalog.get("metadata", {}),
        "total_sources": len(flattened),
        "collectable_sources": len(list_collectable_sources(catalog)),
        "sections": {key: len(catalog.get(key, [])) for key in catalog.keys() if key != "metadata"},
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print()
    for item in flattened:
        print(
            f"[{item['catalog_section']}] {item['name']} | {item.get('adapter')} | "
            f"enabled={item.get('enabled')} | status={item.get('status')}"
        )


if __name__ == "__main__":
    main()
