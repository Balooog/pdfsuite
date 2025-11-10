from pathlib import Path
import subprocess, sys, shlex
import typer
from rich import print
from pdfsuite import __version__

app = typer.Typer(add_completion=False, help="All‑FOSS Acrobat‑grade PDF toolkit")

# subcommand groups
merge_app = typer.Typer(help="Merge/split/reorder")
forms_app = typer.Typer(help="Forms operations")
redact_app = typer.Typer(help="Redaction helpers")

app.add_typer(merge_app, name="merge")
app.add_typer(forms_app, name="forms")
app.add_typer(redact_app, name="redact")


def run(cmd: str) -> int:
    print(f"[dim]$ {cmd}[/dim]")
    return subprocess.call(cmd, shell=True)


@app.command()
def version():
    """Show version."""
    print(f"pdfsuite {__version__}")


@app.command()
def doctor():
    """Check external tool availability."""
    from pathlib import Path as _P; _sp = (_P(__file__).resolve().parent.parent / "scripts" / "doctor.py"); sys.exit(subprocess.call([sys.executable, str(_sp)]))


@app.command()
def ocr(input: Path, output: Path = typer.Option(..., "-o", help="Output PDF")):
    """Add searchable text layer using OCRmyPDF."""
    sys.exit(run(f"ocrmypdf {shlex.quote(str(input))} {shlex.quote(str(output))}"))


@merge_app.callback(invoke_without_command=True)
def merge_main(ctx: typer.Context, inputs: list[Path] = typer.Argument(None), output: Path = typer.Option(None, "-o")):
    """Merge PDFs with qpdf.  Example: pdfsuite merge in1.pdf in2.pdf -o out.pdf"""
    if ctx.invoked_subcommand is not None:
        return
    if not inputs or not output:
        raise typer.Exit(code=2)
    files = " ".join(shlex.quote(str(p)) + " 1-z" for p in inputs)
    cmd = f"qpdf --empty --pages {files} -- {shlex.quote(str(output))}"
    sys.exit(run(cmd))


@app.command()
def optimize(input: Path, output: Path = typer.Option(..., "-o")):
    """Optimize/compress via Ghostscript."""
    cmd = (
        f"gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.6 -dPDFSETTINGS=/printer "
        f"-dDetectDuplicateImages=true -dDownsampleColorImages=true -dColorImageResolution=150 "
        f"-o {shlex.quote(str(output))} {shlex.quote(str(input))}"
    )
    sys.exit(run(cmd))


@app.command()
def stamp(input: Path, output: Path = typer.Option(..., "-o"), bates: str = typer.Option(None, "--bates"), start: int = 1):
    """Stamp/watermark/Bates using pdfcpu."""
    if bates:
        cmd = f"pdfcpu stamp add -mode text '{bates}:%04d' -p 1- -s {start} -o {shlex.quote(str(output))} {shlex.quote(str(input))}"
    else:
        cmd = f"pdfcpu stamp add 'CONFIDENTIAL' -p 1- -o {shlex.quote(str(output))} {shlex.quote(str(input))}"
    sys.exit(run(cmd))


@forms_app.command("fill")
def forms_fill(form: Path, fdf: Path, output: Path = typer.Option(..., "-o")):
    """Fill forms with pdftk-java (FDF/XFDF)."""
    cmd = f"pdftk {shlex.quote(str(form))} fill_form {shlex.quote(str(fdf))} output {shlex.quote(str(output))}"
    sys.exit(run(cmd))


@forms_app.command("flatten")
def forms_flatten(input: Path, output: Path = typer.Option(..., "-o")):
    cmd = f"pdftk {shlex.quote(str(input))} output {shlex.quote(str(output))} flatten"
    sys.exit(run(cmd))


@redact_app.command("safe")
def redact_safe(input: Path, output: Path = typer.Option(..., "-o")):
    """Rasterize+sanitize redaction using pdf-redact-tools (requires WSL on Windows)."""
    cmd = f"pdf-redact-tools --sanitize -i {shlex.quote(str(input))} -o {shlex.quote(str(output))}"
    sys.exit(run(cmd))


@app.command()
def sign(input: Path, output: Path = typer.Option(..., "-o"), p12: Path = typer.Option(..., "--p12"), alias: str = typer.Option(..., "--alias"), visible: str = typer.Option(None, "--visible", help="p=<page>,x=,y=,w=,h=")):
    """Digitally sign via jSignPdf."""
    vis = ""
    if visible:
        vis = " --visible " + shlex.quote(visible)
    cmd = f"jsignpdf -ks {shlex.quote(str(p12))} -ksPass ask -a {shlex.quote(str(alias))}{vis} -o {shlex.quote(str(output))} {shlex.quote(str(input))}"
    sys.exit(run(cmd))


@app.command()
def verify(input: Path):
    """Verify signatures via pdfsig."""
    sys.exit(run(f"pdfsig {shlex.quote(str(input))}"))


@app.command()
def metadata_scrub(input: Path, output: Path = typer.Option(..., "-o")):
    """Remove metadata using MAT2."""
    sys.exit(run(f"mat2 --inplace=false -o {shlex.quote(str(output))} {shlex.quote(str(input))}"))


if __name__ == "__main__":
    app()
