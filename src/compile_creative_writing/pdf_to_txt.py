import re
from multiprocessing import Pool
from pathlib import Path
from typing import List

from pypdf import PdfReader
from tqdm import tqdm

from tibcleaner.checkpoint import (
    load_checkpoints,
    save_checkpoint,
    save_corrupted_files,
)
from tibcleaner.utils import _mkdir


def pdf_to_txt(file_path: Path, output_dir: Path, extracted_text: str):
    """Converts pdf file to a txt file"""
    _mkdir(output_dir)
    output_file = output_dir / f"{file_path.stem}.txt"
    text = ""
    file_type = file_path.suffix[1:]

    if file_type == "pdf":
        text = extracted_text
        if text:
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(text)
            return output_file


def read_pdf_file(pdf_file_path: Path) -> str:
    """Reads the content of a PDF file using pypdf."""
    text = ""
    try:
        with open(pdf_file_path, "rb") as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text += page.extract_text() if page.extract_text() else ""
        return text
    except Exception as e:
        print(f"pdf file {pdf_file_path} is corrupted")
        save_corrupted_files(pdf_file_path, str(e))
        return ""


def contains_tibetan_text(text: str):
    """Check if the text contains Tibetan characters."""
    tibetan_pattern = re.compile(r"[\u0F00-\u0FFF]")
    return bool(tibetan_pattern.search(text))


def process_pdf(args):
    pdf_file, output_dir_txt, checkpoints = args
    try:
        if f"{str(pdf_file)}" in checkpoints:
            return
        extracted_text = read_pdf_file(pdf_file)
        if extracted_text is None:
            print(f"[ERROR]: {str(pdf_file)} is corrupted file.")
            save_corrupted_files(pdf_file, "Corrupted file")
            return
        if contains_tibetan_text(extracted_text):
            pdf_to_txt(pdf_file, output_dir_txt, extracted_text)
            save_checkpoint(pdf_file)
    except Exception as e:
        print(f"[ERROR] Processing failed for {pdf_file}: {e}")
        save_corrupted_files(pdf_file, str(e))


def pdfs_to_txt(
    pdf_files: List[Path], output_dir_txt: Path
):
    checkpoints = load_checkpoints()
    tasks = [
        (pdf_file, output_dir_txt, checkpoints)
        for pdf_file in pdf_files
    ]

    num_processes = 2  # Adjust based on your system capabilities

    # Use a Pool to manage multiple processes
    with Pool(processes=num_processes) as pool:
        list(
            tqdm(
                pool.imap(process_pdf, tasks),
                total=len(tasks),
                desc="Converting PDF files to text",
            )
        )


if __name__ == "__main__":
    pdf_files = list(Path("data/cta_docs/DOE").rglob("*.pdf"))
    output_dir_txt = Path("data/converted_txt/yigdrel/doe")
    pdfs_to_txt(pdf_files, output_dir_txt)
