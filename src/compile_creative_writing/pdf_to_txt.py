"""importing libraries"""

import re
from multiprocessing import Pool
from pathlib import Path
from typing import List

from pdf2image import convert_from_path
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
    # Define a regex pattern for Tibetan characters (Unicode range from U+0F00 to U+0FFF)
    tibetan_pattern = re.compile(r"[\u0F00-\u0FFF]")

    # Search the text for the pattern
    return bool(tibetan_pattern.search(text))


"""Spliting pdfs to images (page by page)"""


def pdf_to_images(pdf_path: Path, images_path: Path):
    """In some cases, pypdf package can't extract text from a PDF file."""
    """so we convert the PDF file to images and then use OCR to extract the text."""

    """pdfinfo:tool that comes with Poppler,to get info about PDF file need to be installed."""
    try:
        pages = convert_from_path(pdf_path)
        for i, page in enumerate(pages, 1):
            image_path = images_path / f"{pdf_path.stem}_to_image_{i:06}.jpeg"
            page.save(image_path, "JPEG")
    except Exception as e:
        save_corrupted_files(pdf_path, str(e))
        return None


def process_pdf(args):
    pdf_file, output_dir_txt, output_dir_jpeg, checkpoints = args
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
            save_checkpoint(pdf_file)  # Adjusted to ensure correct format
            return
        images_path = output_dir_jpeg / f"{pdf_file.stem}_images"
        images_path.mkdir(parents=True, exist_ok=True)
        pdf_to_images(pdf_file, images_path)
        save_checkpoint(pdf_file)
    except Exception as e:
        print(f"[ERROR] Processing failed for {pdf_file}: {e}")
        save_corrupted_files(pdf_file, str(e))


def pdfs_to_txt_and_images(
    pdf_files: List[Path], output_dir_txt: Path, output_dir_jpeg: Path
):
    checkpoints = load_checkpoints()
    tasks = [
        (pdf_file, output_dir_txt, output_dir_jpeg, checkpoints)
        for pdf_file in pdf_files
    ]

    num_processes = 2  # Adjust based on your system capabilities

    # Use a Pool to manage multiple processes
    with Pool(processes=num_processes) as pool:
        # Note: tqdm might not directly work with pool.map or pool.starmap in Jupyter notebooks without some tweaks
        list(
            tqdm(
                pool.imap(process_pdf, tasks),
                total=len(tasks),
                desc="Converting PDF files to images",
            )
        )


if __name__ == "__main__":
    pdf_files = list(Path("data/DRC").rglob("*.pdf"))
    output_dir_txt = Path("data/DRC/txt")
    output_dir_jpeg = Path("data/jpeg")
    pdfs_to_txt_and_images(pdf_files, output_dir_txt, output_dir_jpeg)