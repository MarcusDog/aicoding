from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Post-process thesis docx with Word COM.")
    parser.add_argument("--input", required=True, help="Input DOCX path")
    parser.add_argument("--output", required=True, help="Output DOCX path")
    parser.add_argument("--pdf", help="Optional output PDF path")
    return parser.parse_args()


def build_powershell(input_docx: Path, output_docx: Path, pdf_path: Path | None) -> str:
    pdf_block = ""
    if pdf_path is not None:
        pdf_escaped = str(pdf_path).replace("'", "''")
        pdf_block = f"$doc.ExportAsFixedFormat('{pdf_escaped}', 17)\n"
    return f"""
$ErrorActionPreference = 'Stop'
$input = [System.IO.Path]::GetFullPath('{str(input_docx).replace("'", "''")}')
$output = [System.IO.Path]::GetFullPath('{str(output_docx).replace("'", "''")}')
$word = $null
$doc = $null
try {{
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.Open($input, $false, $false)
    foreach ($section in $doc.Sections) {{
        foreach ($header in $section.Headers) {{
            try {{ $header.LinkToPrevious = $false }} catch {{}}
        }}
        foreach ($footer in $section.Footers) {{
            try {{ $footer.LinkToPrevious = $false }} catch {{}}
        }}
    }}
    $sectionCount = $doc.Sections.Count
    for ($i = 1; $i -le [Math]::Min(2, $sectionCount); $i++) {{
        $section = $doc.Sections.Item($i)
        $section.PageSetup.DifferentFirstPageHeaderFooter = $true
        foreach ($footer in $section.Footers) {{
            $footer.Range.Text = ''
        }}
    }}
    if ($sectionCount -ge 3) {{
        $front = $doc.Sections.Item(3)
        $front.PageSetup.DifferentFirstPageHeaderFooter = $false
        foreach ($footer in $front.Footers) {{
            if ($footer.PageNumbers.Count -gt 0) {{
                $footer.PageNumbers.RestartNumberingAtSection = $true
                $footer.PageNumbers.StartingNumber = 1
                $footer.PageNumbers.NumberStyle = 2
            }}
        }}
    }}
    if ($sectionCount -ge 4) {{
        $body = $doc.Sections.Item(4)
        $body.PageSetup.DifferentFirstPageHeaderFooter = $false
        foreach ($footer in $body.Footers) {{
            if ($footer.PageNumbers.Count -gt 0) {{
                $footer.PageNumbers.RestartNumberingAtSection = $true
                $footer.PageNumbers.StartingNumber = 1
                $footer.PageNumbers.NumberStyle = 0
            }}
        }}
    }}
    $doc.Fields.Update() | Out-Null
    foreach ($toc in $doc.TablesOfContents) {{
        $toc.Update() | Out-Null
    }}
    $equations = @(
        @('{{EQ:Precision=\\frac{{TP}}{{TP+FP}}}}', 'Precision=TP/(TP+FP)'),
        @('{{EQ:Recall=\\frac{{TP}}{{TP+FN}}}}', 'Recall=TP/(TP+FN)'),
        @('{{EQ:FPR=\\frac{{FP}}{{FP+TN}}}}', 'FPR=FP/(FP+TN)')
    )
    foreach ($eq in $equations) {{
        $word.Selection.HomeKey(6) | Out-Null
        $find = $word.Selection.Find
        $find.Text = $eq[0]
        if ($find.Execute()) {{
            $range = $word.Selection.Range
            $range.Text = $eq[1]
            $doc.OMaths.Add($range) | Out-Null
            $range.OMaths.Item(1).BuildUp()
        }}
    }}
    $doc.Fields.Update() | Out-Null
    foreach ($toc in $doc.TablesOfContents) {{
        $toc.Update() | Out-Null
    }}
    $doc.SaveAs([ref]$output, [ref]16)
    {pdf_block}
}} finally {{
    if ($doc -ne $null) {{
        $doc.Close([ref]0) | Out-Null
    }}
    if ($word -ne $null) {{
        $word.Quit() | Out-Null
    }}
}}
"""


def main() -> None:
    args = parse_args()
    input_docx = Path(args.input).expanduser().resolve()
    output_docx = Path(args.output).expanduser().resolve()
    pdf_path = Path(args.pdf).expanduser().resolve() if args.pdf else None
    output_docx.parent.mkdir(parents=True, exist_ok=True)
    if pdf_path is not None:
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
    ps_script = build_powershell(input_docx, output_docx, pdf_path)
    subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps_script], check=True, capture_output=True, text=True)
    print(f"Post-processed DOCX: {output_docx}")
    if pdf_path is not None:
        print(f"PDF preview: {pdf_path}")


if __name__ == "__main__":
    main()
