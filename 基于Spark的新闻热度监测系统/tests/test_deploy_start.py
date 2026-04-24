from __future__ import annotations

from pathlib import Path

import deploy_start


def test_project_root_points_to_repo_root():
    assert (deploy_start.PROJECT_ROOT / "backend" / "requirements.txt").exists()
    assert (deploy_start.PROJECT_ROOT / "frontend" / "package.json").exists()


def test_filter_runtime_requirements_can_skip_pyspark(tmp_path):
    source = tmp_path / "requirements.txt"
    target = tmp_path / "runtime.txt"
    source.write_text("Flask==3.1.0\npyspark==4.0.1\npandas==2.2.3\n", encoding="utf-8")

    deploy_start.write_runtime_requirements(source, target, skip_pyspark=True)

    assert target.read_text(encoding="utf-8") == "Flask==3.1.0\npandas==2.2.3\n"


def test_backend_venv_python_path_is_platform_specific(monkeypatch):
    monkeypatch.setattr(deploy_start.platform, "system", lambda: "Windows")
    assert deploy_start.venv_python(Path("backend/.venv")).as_posix().endswith("Scripts/python.exe")

    monkeypatch.setattr(deploy_start.platform, "system", lambda: "Darwin")
    assert deploy_start.venv_python(Path("backend/.venv")).as_posix().endswith("bin/python")
