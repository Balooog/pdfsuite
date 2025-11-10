# Install core tools via winget/choco (run in elevated PowerShell)
$ErrorActionPreference = 'Stop'
winget install GnuWin32.QPDF -e --id GnuWin32.QPDF || choco install qpdf -y
winget install GnuWin32.Ghostscript -e --id ArtifexSoftware.Ghostscript || choco install ghostscript -y
winget install TesseractOCR.Tesseract -e --id TesseractOCR.Tesseract
# pdfcpu: download from https://github.com/pdfcpu/pdfcpu/releases and add to PATH
# pdftk-java + Java
choco install openjdk -y
choco install pdftk-java -y
