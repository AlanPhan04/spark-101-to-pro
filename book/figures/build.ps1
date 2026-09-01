<#
.SYNOPSIS
  Regenerate every figure PDF in book/images/ from its .drawio source.

  Each figure is <slug>.drawio (hand-authored) + <slug>_render.py (parses it,
  redraws with matplotlib). This runs every *_render.py. Requires Python with
  matplotlib on PATH.

.USAGE
  cd book
  .\figures\build.ps1
#>
Set-Location -Path $PSScriptRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "python not on PATH — cannot regenerate figures." -ForegroundColor Red
    exit 1
}

$renderers = Get-ChildItem -Filter "*_render.py" | Sort-Object Name
if (-not $renderers) {
    Write-Host "No *_render.py found in $PSScriptRoot"
    exit 0
}

$failed = 0
foreach ($r in $renderers) {
    Write-Host "-> $($r.Name)"
    & python $r.FullName
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   FAILED ($LASTEXITCODE)" -ForegroundColor Yellow
        $failed++
    }
}

if ($failed -gt 0) {
    Write-Host "$failed renderer(s) failed." -ForegroundColor Red
    exit 1
}
Write-Host "All figures regenerated -> ..\images\" -ForegroundColor Green
