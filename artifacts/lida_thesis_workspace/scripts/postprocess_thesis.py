from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Post-process thesis DOCX with Word COM.")
    parser.add_argument("--docx", required=True, help="Target DOCX file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    docx_path = Path(args.docx).expanduser().resolve()
    if not docx_path.exists():
        raise FileNotFoundError(docx_path)

    ps_script = f"""
$ErrorActionPreference = 'Stop'
$path = [System.IO.Path]::GetFullPath('{str(docx_path).replace("'", "''")}')
$word = $null
$doc = $null
try {{
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.Open($path)

    foreach ($paragraph in @($doc.Paragraphs)) {{
        $raw = $paragraph.Range.Text
        $clean = $raw.Replace("`r","").Replace("`a","").Trim()
        if ($clean.StartsWith("OMATH::")) {{
            $formula = $clean.Substring(7)
            $range = $paragraph.Range
            $range.Text = $formula
            $range.ParagraphFormat.Alignment = 1
            $range.Font.Name = 'Cambria Math'
            $range.Font.Color = 0
            $null = $doc.OMaths.Add($range)
        }}
    }}

    if ($doc.OMaths.Count -gt 0) {{
        $doc.OMaths.BuildUp()
    }}

    foreach ($toc in @($doc.TablesOfContents)) {{
        $toc.Update()
    }}

    $null = $doc.Fields.Update()
    $doc.Save()
}} finally {{
    if ($doc -ne $null) {{
        $doc.Close([ref]0) | Out-Null
    }}
    if ($word -ne $null) {{
        $word.Quit() | Out-Null
    }}
}}
"""

    subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", ps_script],
        check=True,
        capture_output=True,
        text=True,
    )
    print(f"Post-processed thesis DOCX: {docx_path}")


if __name__ == "__main__":
    main()
