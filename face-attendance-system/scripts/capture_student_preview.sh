#!/usr/bin/env bash
set -euo pipefail

ROOT="/Volumes/Users/Public/work/face_anyls"
PREVIEW_DIR="$ROOT/face-attendance-system/docs/thesis_preview/student"
OUT_DIR="${1:-$ROOT/tmp/docs/runtime_screenshots}"
NODE_BIN="${NODE_BIN:-/Users/li/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node}"
NODE_PATH="${NODE_PATH:-/Users/li/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules}"

mkdir -p "$OUT_DIR"

export NODE_PATH
"$NODE_BIN" - "$PREVIEW_DIR" "$OUT_DIR" <<'JS'
const { chromium } = require("playwright");
const path = require("path");

const previewDir = process.argv[2];
const outDir = process.argv[3];
const pages = [
  ["profile.html", "student_profile.png"],
  ["face-register.html", "student_face_register.png"],
  ["check-in.html", "student_check_in.png"],
  ["records.html", "student_records.png"],
];

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: 560, height: 980 },
    deviceScaleFactor: 1.5,
  });

  for (const [pageFile, outputFile] of pages) {
    await page.goto(`file://${path.join(previewDir, pageFile)}`);
    await page.screenshot({
      path: path.join(outDir, outputFile),
      fullPage: true,
    });
  }

  await browser.close();
})();
JS

ls -1 "$OUT_DIR"/student_*.png
