from __future__ import annotations

import importlib
import importlib.metadata
import shutil

CHECKS = ["flask", "pandas", "sklearn", "jieba", "pyspark"]


def main() -> None:
    for item in CHECKS:
        try:
            module = importlib.import_module(item)
            try:
                version = importlib.metadata.version(item)
            except importlib.metadata.PackageNotFoundError:
                version = getattr(module, "__version__", "ok")
            print(f"{item}: {version}")
        except Exception as exc:
            print(f"{item}: missing ({exc})")

    print("python: ok")
    print(f"java: {shutil.which('java') or 'missing'}")
    print(f"spark-submit: {shutil.which('spark-submit') or 'missing'}")


if __name__ == "__main__":
    main()
