$ErrorActionPreference = 'Stop'
$src = 'C:\Users\lenovo\OneDrive\Desktop\毕业设计_4\杨浦区\thesis\lida_thesis_workspace\deliverables\潘哲-毕业论文-终稿.docx'
$dst = 'C:\Users\lenovo\OneDrive\Desktop\毕业设计_4\杨浦区\thesis\lida_thesis_workspace\deliverables\潘哲-毕业论文-终稿-排版.docx'
if (Test-Path $dst) { Remove-Item $dst -Force }
function Replace-All($doc, $findText, $replaceText) {
  $find = $doc.Content.Find
  $find.ClearFormatting()
  $find.Replacement.ClearFormatting()
  $find.Text = $findText
  $find.Replacement.Text = $replaceText
  $find.Forward = $true
  $find.Wrap = 1
  $null = $find.Execute($findText, $false, $false, $false, $false, $false, $true, 1, $false, $replaceText, 2)
}
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
  $doc = $word.Documents.Open($src)
  Replace-All $doc '202109423' '202209517'
  Replace-All $doc 'Candidate：潘哲' 'Candidate: Pan Zhe'
  Replace-All $doc 'Supervisor：马利平' 'Supervisor: Ma Liping'
  Replace-All $doc '年  月  日（手填时间）' '2026年3月20日'
  Replace-All $doc '图5.1展示' '如图5.1所示'
  Replace-All $doc '图6.1说明' '如图6.1所示'
  Replace-All $doc '表3.1反映' '由表3.1可知'
  Replace-All $doc '可以说明该系统已具备' '可认为该系统已经形成'
  foreach ($toc in $doc.TablesOfContents) { $toc.Update() | Out-Null }
  $doc.Fields.Update() | Out-Null
  $doc.Content.Font.Color = 0
  $doc.SaveAs([ref]$dst, [ref]16)
  Write-Output 'ok'
}
catch {
  Write-Output $_.Exception.Message
  throw
}
finally {
  if ($doc) { $doc.Close([ref]0) | Out-Null }
  $word.Quit() | Out-Null
}
