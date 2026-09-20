<#
.SYNOPSIS
  Build book/main.tex on Windows (XeLaTeX + biber). The fontspec Times New
  Roman font and the biblatex bibliography require this combo; plain
  pdflatex/bibtex will not compile this document.

  Every run (including -Quick) sweeps .aux/.log/.bbl/... afterwards, keeping
  only the source and main.pdf; the error/undefined-reference summary is
  still printed to the console before that happens.

.USAGE
  cd book
  .\build.ps1            # full build: xelatex -> biber -> xelatex x2 (default)
  .\build.ps1 -Quick      # one xelatex pass, for text-only edits
  .\build.ps1 -Clean      # remove build artifacts, keep main.pdf
  .\build.ps1 -Distclean  # also remove main.pdf

  If PowerShell refuses to run the script ("running scripts is disabled"),
  either right-click build.ps1 -> Run with PowerShell, or run once:
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#>

param(
    [switch]$Quick,
    [switch]$Clean,
    [switch]$Distclean
)

$Name = "main"
Set-Location -Path $PSScriptRoot

function Test-Tool($cmd, $installHint) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "Missing '$cmd' on PATH. $installHint" -ForegroundColor Red
        exit 1
    }
}

function Remove-BuildArtifacts {
    Remove-Item -ErrorAction SilentlyContinue -Force `
        "$Name.bbl", "$Name.bcf", "$Name.blg", "$Name.run.xml", "$Name.fls", "$Name.fdb_latexmk", `
        "$Name.log", "$Name.lof", "$Name.lot", "$Name.out", "$Name.toc", "$Name.synctex.gz", "comment.cut"
    Get-ChildItem -Recurse -Filter *.aux | Remove-Item -Force -ErrorAction SilentlyContinue
}

if ($Clean -or $Distclean) {
    Write-Host "Cleaning build artifacts..."
    Remove-BuildArtifacts
    if ($Distclean) {
        Remove-Item -ErrorAction SilentlyContinue -Force "$Name.pdf"
    }
    Write-Host "Done."
    exit 0
}

Test-Tool "xelatex" "Install a LaTeX distribution first, e.g.:  winget install MiKTeX.MiKTeX   (then restart your terminal)"
if (-not $Quick) {
    Test-Tool "biber" "biber ships with MiKTeX/TeX Live; if it's still missing, open the MiKTeX Console and install the 'biber' package, then restart your terminal."
}

function Invoke-XeLaTeX {
    & xelatex -interaction=nonstopmode -file-line-error $Name
    if ($LASTEXITCODE -ne 0) {
        Write-Host "xelatex exited with code $LASTEXITCODE - see $Name.log for details." -ForegroundColor Yellow
    }
}

if ($Quick) {
    Invoke-XeLaTeX
} else {
    Invoke-XeLaTeX
    & biber $Name
    if ($LASTEXITCODE -ne 0) {
        Write-Host "biber exited with code $LASTEXITCODE - see $Name.blg for details." -ForegroundColor Yellow
    }
    Invoke-XeLaTeX
    Invoke-XeLaTeX
}

# --- report errors / undefined refs ----------------------------------------
$log = "$Name.log"
$hadProblems = $false
if (Test-Path $log) {
    $logText = Get-Content $log -Raw
    # "ignored error" lines are XeTeX's own non-fatal box-splitting diagnostics
    # (observed with longtable spanning a page break); XeTeX recovers from them
    # itself, so they are not counted as build errors.
    $errCount = ([regex]::Matches($logText, '(?m)^(\./)?[^\r\n ]*:[0-9]+: (?!ignored error)|^! ')).Count
    $undCount = ([regex]::Matches($logText, 'Citation .* undefined|Reference .* undefined')).Count
    Write-Host ""
    Write-Host "errors: $errCount   undefined refs/cites: $undCount"
    if ($errCount -gt 0 -or $undCount -gt 0) {
        $hadProblems = $true
        Write-Host "--- first 20 problem lines ---" -ForegroundColor Yellow
        $logText -split "`r?`n" |
            Select-String -Pattern '^(\./)?[^ ]*:[0-9]+: |^! |Citation .* undefined|Reference .* undefined' |
            Select-Object -First 20 |
            ForEach-Object { Write-Host $_.Line }
    }
}

if (Test-Path "$Name.pdf") {
    Write-Host "Build OK -> $PSScriptRoot\$Name.pdf" -ForegroundColor Green
}

Remove-BuildArtifacts

if ($hadProblems) {
    exit 1
}
