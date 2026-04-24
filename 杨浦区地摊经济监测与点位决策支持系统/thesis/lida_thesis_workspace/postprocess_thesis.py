from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from docx import Document


WORKSPACE = Path(__file__).resolve().parent
DELIVERABLES = WORKSPACE / "deliverables"


def newest_docx(pattern: str, exclude: str | None = None) -> Path | None:
    matches = sorted(DELIVERABLES.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in matches:
        if exclude and exclude in path.name:
            continue
        return path
    return None


def default_docx() -> Path:
    path = newest_docx("*终稿*.docx", exclude="排版")
    if path is None:
        raise FileNotFoundError("No source thesis DOCX found in deliverables/")
    return path


def default_out(src: Path) -> Path:
    stem = src.stem
    if "排版" in stem:
        stem = stem.replace("-排版", "")
    return src.with_name(f"{stem}-排版-v3.docx")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Postprocess thesis DOCX with text repair and Word COM formatting.")
    parser.add_argument("--docx", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--pdf", action="store_true", help="Also export a PDF beside the output DOCX.")
    return parser.parse_args()


def set_plain_paragraph_text(paragraph, text: str) -> None:
    if paragraph.runs:
        paragraph.runs[0].text = text
        for run in paragraph.runs[1:]:
            run.text = ""
    else:
        paragraph.text = text


def clean_chinese_spacing(src: Path, dst: Path) -> None:
    doc = Document(str(src))
    spacing_re = re.compile(r"([。；：，、！？）】》”’]) +(?=[\u4e00-\u9fff“‘（【《])")
    double_space_re = re.compile(r"(?<=[\u4e00-\u9fff]) {2,}(?=[\u4e00-\u9fff])")

    for paragraph in doc.paragraphs:
        if not paragraph.text.strip():
            continue
        if paragraph._element.xpath(".//w:drawing"):
            continue
        if paragraph._element.xpath(".//w:fldChar"):
            continue
        if paragraph.style.name.lower().startswith("toc"):
            continue
        text = paragraph.text
        repaired = spacing_re.sub(r"\1", text)
        repaired = double_space_re.sub(" ", repaired)
        if repaired != text:
            set_plain_paragraph_text(paragraph, repaired)

    doc.save(str(dst))


def ps_string(path: Path) -> str:
    return str(path).replace("'", "''")


def build_ps_script(src: Path, dst: Path, pdf_path: Path | None) -> str:
    pdf_block = ""
    if pdf_path is not None:
        pdf_block = f"$doc.ExportAsFixedFormat('{ps_string(pdf_path)}', 17)\n"

    return f"""
$ErrorActionPreference = 'Stop'
$src = [System.IO.Path]::GetFullPath('{ps_string(src)}')
$dst = [System.IO.Path]::GetFullPath('{ps_string(dst)}')
if (Test-Path $dst) {{
    Remove-Item $dst -Force
}}

function Replace-All($doc, $findText, $replaceText) {{
    $find = $doc.Content.Find
    $find.ClearFormatting()
    $find.Replacement.ClearFormatting()
    $find.Text = $findText
    $find.Replacement.Text = $replaceText
    $find.Forward = $true
    $find.Wrap = 1
    $null = $find.Execute($findText, $false, $false, $false, $false, $false, $true, 1, $false, $replaceText, 2)
}}

function Set-RangeFont($range, $eastAsia, $asciiFont, $size, $bold) {{
    try {{ $range.Font.NameFarEast = $eastAsia }} catch {{}}
    try {{ $range.Font.NameAscii = $asciiFont }} catch {{}}
    try {{ $range.Font.NameOther = $asciiFont }} catch {{}}
    try {{ $range.Font.Name = $asciiFont }} catch {{}}
    $range.Font.Size = $size
    $range.Font.Bold = $bold
    $range.Font.Color = 0
}}

function Format-Paragraph($para, $eastAsia, $asciiFont, $size, $bold, $align) {{
    $range = $para.Range
    Set-RangeFont $range $eastAsia $asciiFont $size $bold
    $para.Alignment = $align
    $para.FirstLineIndent = 0
}}

$word = $null
$doc = $null
try {{
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.Open($src)

    Replace-All $doc '202109423' '202209517'
    Replace-All $doc 'Candidate：潘哲' 'Candidate: Pan Zhe'
    Replace-All $doc 'Supervisor：马利平' 'Supervisor: Ma Liping'
    Replace-All $doc '年  月  日（手填时间）' '2026年3月20日'
    Replace-All $doc '图5.1展示' '如图5.1所示'
    Replace-All $doc '图6.1说明' '如图6.1所示'
    Replace-All $doc '表3.1反映' '由表3.1可知'
    Replace-All $doc '可以说明该系统已具备' '可认为该系统已经形成'

    foreach ($para in $doc.Paragraphs) {{
        $text = $para.Range.Text.Trim()
        if ($text.StartsWith('EQ::')) {{
            $expr = $text.Substring(4)
            $para.Range.Text = $expr
            $para.Alignment = 1
            $mathRange = $para.Range
            $mathRange.End = $mathRange.End - 1
            $doc.OMaths.Add($mathRange) | Out-Null
            $doc.OMaths.Item($doc.OMaths.Count).BuildUp() | Out-Null
        }}
    }}

    $doc.Content.Font.Color = 0

    foreach ($para in $doc.Paragraphs) {{
        $text = $para.Range.Text.Trim()

        if ($para.Range.InlineShapes.Count -gt 0) {{
            $para.Alignment = 1
            $para.FirstLineIndent = 0
            $para.KeepWithNext = $true
        }}

        if ($text -eq '摘　要' -or $text -eq '目　录' -or $text -eq '郑重声明') {{
            Format-Paragraph $para '黑体' 'Times New Roman' 18 $true 1
        }}
        elseif ($text -eq 'ABSTRACT') {{
            Format-Paragraph $para 'Times New Roman' 'Times New Roman' 18 $true 1
        }}
        elseif ($text -match '^图\\d+\\.\\d+') {{
            Format-Paragraph $para '黑体' 'Times New Roman' 12 $true 1
            $para.KeepTogether = $true
        }}
        elseif ($text -match '^表\\d+\\.\\d+') {{
            Format-Paragraph $para '黑体' 'Times New Roman' 12 $true 1
            $para.KeepWithNext = $true
            $para.KeepTogether = $true
        }}
        elseif ($text -match '^代码\\d+\\.\\d+') {{
            Format-Paragraph $para '黑体' 'Times New Roman' 12 $true 1
            $para.KeepWithNext = $true
            $para.KeepTogether = $true
        }}
    }}

    $frontMatterStyles = @(
        @{{ Index = 6; East = '黑体'; Ascii = 'Times New Roman'; Size = 22; Bold = $true; Align = 1 }},
        @{{ Index = 8; East = '黑体'; Ascii = 'Times New Roman'; Size = 22; Bold = $true; Align = 1 }},
        @{{ Index = 19; East = 'Times New Roman'; Ascii = 'Times New Roman'; Size = 16; Bold = $true; Align = 1 }},
        @{{ Index = 22; East = 'Times New Roman'; Ascii = 'Times New Roman'; Size = 16; Bold = $true; Align = 1 }},
        @{{ Index = 26; East = 'Times New Roman'; Ascii = 'Times New Roman'; Size = 12; Bold = $false; Align = 1 }},
        @{{ Index = 27; East = 'Times New Roman'; Ascii = 'Times New Roman'; Size = 12; Bold = $false; Align = 1 }},
        @{{ Index = 32; East = 'Times New Roman'; Ascii = 'Times New Roman'; Size = 12; Bold = $false; Align = 1 }},
        @{{ Index = 37; East = '黑体'; Ascii = 'Times New Roman'; Size = 18; Bold = $true; Align = 1 }},
        @{{ Index = 55; East = '黑体'; Ascii = 'Times New Roman'; Size = 18; Bold = $true; Align = 1 }},
        @{{ Index = 57; East = '黑体'; Ascii = 'Times New Roman'; Size = 18; Bold = $true; Align = 1 }},
        @{{ Index = 74; East = 'Times New Roman'; Ascii = 'Times New Roman'; Size = 16; Bold = $true; Align = 1 }},
        @{{ Index = 76; East = 'Times New Roman'; Ascii = 'Times New Roman'; Size = 18; Bold = $true; Align = 1 }},
        @{{ Index = 81; East = '黑体'; Ascii = 'Times New Roman'; Size = 18; Bold = $true; Align = 1 }}
    )
    foreach ($item in $frontMatterStyles) {{
        $idx = [int]$item.Index
        if ($idx -lt $doc.Paragraphs.Count) {{
            Format-Paragraph $doc.Paragraphs.Item($idx + 1) $item.East $item.Ascii $item.Size $item.Bold $item.Align
        }}
    }}

    try {{
        $toc1 = $doc.Styles.Item('TOC 1')
        $toc1.Font.NameFarEast = '黑体'
        $toc1.Font.NameAscii = 'Times New Roman'
        $toc1.Font.NameOther = 'Times New Roman'
        $toc1.Font.Size = 14
        $toc1.Font.Bold = $true
        $toc1.Font.Color = 0
    }} catch {{}}
    try {{
        $toc2 = $doc.Styles.Item('TOC 2')
        $toc2.Font.NameFarEast = '宋体'
        $toc2.Font.NameAscii = 'Times New Roman'
        $toc2.Font.NameOther = 'Times New Roman'
        $toc2.Font.Size = 12
        $toc2.Font.Bold = $false
        $toc2.Font.Color = 0
    }} catch {{}}
    try {{
        $toc3 = $doc.Styles.Item('TOC 3')
        $toc3.Font.NameFarEast = '宋体'
        $toc3.Font.NameAscii = 'Times New Roman'
        $toc3.Font.NameOther = 'Times New Roman'
        $toc3.Font.Size = 12
        $toc3.Font.Bold = $false
        $toc3.Font.Color = 0
    }} catch {{}}

    foreach ($toc in $doc.TablesOfContents) {{
        $toc.Update() | Out-Null
    }}
    $doc.Fields.Update() | Out-Null

    $sectionCount = $doc.Sections.Count
    for ($i = 1; $i -le $sectionCount; $i++) {{
        $footer = $doc.Sections.Item($i).Footers.Item(1)
        foreach ($para in $footer.Range.Paragraphs) {{
            $para.Alignment = 1
            try {{ $para.Range.Font.NameAscii = 'Times New Roman' }} catch {{}}
            try {{ $para.Range.Font.NameOther = 'Times New Roman' }} catch {{}}
            try {{ $para.Range.Font.NameFarEast = 'Times New Roman' }} catch {{}}
            $para.Range.Font.Size = 10.5
            $para.Range.Font.Color = 0
        }}
    }}
    if ($sectionCount -ge 2) {{
        for ($i = 1; $i -lt $sectionCount; $i++) {{
            $pn = $doc.Sections.Item($i).Footers.Item(1).PageNumbers
            $pn.NumberStyle = 1
            $pn.RestartNumberingAtSection = $false
        }}
        $mainPn = $doc.Sections.Item($sectionCount).Footers.Item(1).PageNumbers
        $mainPn.NumberStyle = 0
        $mainPn.RestartNumberingAtSection = $true
        $mainPn.StartingNumber = 1
    }}

    if ($sectionCount -ge 1) {{
        $header = $doc.Sections.Item($sectionCount).Headers.Item(1).Range
        $header.Text = '上海立达学院本科毕业论文（设计）'
        $header.ParagraphFormat.Alignment = 1
        Set-RangeFont $header '宋体' 'Times New Roman' 9 $false
    }}

    $doc.SaveAs([ref]$dst, [ref]16)
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


def run_word_postprocess(src: Path, dst: Path, pdf_path: Path | None) -> None:
    ps_path = WORKSPACE / "tmp_postprocess.ps1"
    ps_path.write_text(build_ps_script(src, dst, pdf_path), encoding="utf-8-sig")
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps_path)],
            capture_output=True,
        )
        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="ignore").strip()
            stdout = result.stdout.decode("utf-8", errors="ignore").strip()
            message = stderr or stdout or f"Word postprocess failed with exit code {result.returncode}"
            raise RuntimeError(message)
    finally:
        if ps_path.exists():
            ps_path.unlink()


def main() -> None:
    args = parse_args()
    src = (args.docx or default_docx()).resolve()
    dst = (args.out or default_out(src)).resolve()
    pdf_path = dst.with_suffix(".pdf") if args.pdf else None
    dst.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="thesis-postprocess-") as tmp_dir:
        tmp_src = Path(tmp_dir) / "source.docx"
        shutil.copy2(src, tmp_src)
        clean_src = Path(tmp_dir) / "clean.docx"
        clean_chinese_spacing(tmp_src, clean_src)
        run_word_postprocess(clean_src, dst, pdf_path)

    print(dst)
    if pdf_path is not None:
        print(pdf_path)


if __name__ == "__main__":
    main()
