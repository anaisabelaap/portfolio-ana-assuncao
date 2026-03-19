"""Extrai texto de um ou vários PDFs.

Uso:
  python -m src.extract_text <caminho_para_pdf_ou_diretorio> [-o saída]

Exemplos:
  python -m src.extract_text data/PEC_6x1.pdf
  python -m src.extract_text data/ -o extracted_texts/
"""

from pathlib import Path
import argparse
import sys

try:
    import pdfplumber
except ImportError:
    print(
        "Erro: o pacote 'pdfplumber' não está instalado.\n" \
        "Instale com: python -m pip install pdfplumber",
        file=sys.stderr,
    )
    sys.exit(1)


def extract_pdf_to_text(pdf_path: Path, out_path: Path | None = None) -> Path:
    """Extrai texto do `pdf_path` e grava em `out_path` (ou ao lado do PDF com extensão .txt).

    Retorna o caminho do arquivo gravado.
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")

    with pdfplumber.open(pdf_path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    full_text = "\n".join(pages)

    if out_path is None:
        out_path = pdf_path.with_suffix(".txt")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        f.write(full_text)
    return out_path


def main() -> int:
    p = argparse.ArgumentParser(
        prog="extract_text",
        description="Extrai texto de PDF(s) e grava arquivos .txt",
    )
    p.add_argument("input", help="caminho para um PDF ou para um diretório contendo PDFs")
    p.add_argument("-o", "--out-dir", help="diretório de saída (opcional)")
    p.add_argument("-r", "--recursive", action="store_true", help="procurar recursivamente em diretórios")
    args = p.parse_args()

    path = Path(args.input)
    out_dir = Path(args.out_dir) if args.out_dir else None

    pdfs: list[Path] = []
    if path.is_dir():
        if args.recursive:
            pdfs = sorted(path.rglob("*.pdf"))
        else:
            pdfs = sorted(path.glob("*.pdf"))
    elif path.is_file():
        pdfs = [path]
    else:
        print(f"Caminho não encontrado: {path}", file=sys.stderr)
        return 2

    if not pdfs:
        print("Nenhum PDF encontrado para processar.", file=sys.stderr)
        return 3

    for pdf in pdfs:
        target = (out_dir / pdf.name).with_suffix(".txt") if out_dir else None
        written = extract_pdf_to_text(pdf, target)
        print(f"Gerado: {written}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
