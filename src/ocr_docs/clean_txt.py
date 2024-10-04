import re
from pathlib import Path


def clean_text(text: str) -> str:
    """Removes text before the first occurrence of '༄༅།'."""
    match = re.search(r'༄༅།', text)
    if match:
        return text[match.start():].strip()
    return text


def clean_tibetan_files(input_dir: Path, output_dir: Path):
    """Cleans text in all txt files by removing text before '༄༅།' and preserving directory structure."""
    for txt_file in input_dir.rglob('*.txt'):
        with txt_file.open(encoding='utf-8') as file:
            text = file.read()
        cleaned_text = clean_text(text)

        relative_path = txt_file.relative_to(input_dir)
        output_file = output_dir / relative_path
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open('w', encoding='utf-8') as file:
            file.write(cleaned_text)

        print(f"Processed: {txt_file}")


if __name__ == "__main__":
    input_dir = Path("data/ocr_txt/DOE")
    output_dir = Path("data/cleaned_ocr_txt/DOE")

    clean_tibetan_files(input_dir, output_dir)
