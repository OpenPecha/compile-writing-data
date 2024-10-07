import re
from pathlib import Path


def contains_tibetan(text: str) -> bool:
    return bool(re.search(r'[\u0F00-\u0FFF]', text))


def clean_text(text: str) -> str:
    lines = text.splitlines()
    tibetan_lines = [line for line in lines if contains_tibetan(line)]
    cleaned_text = '\n'.join(tibetan_lines)

    match = re.search(r'༄༅།', cleaned_text)
    if match:
        return cleaned_text[match.start():].strip()

    return cleaned_text


def clean_tibetan_files(input_dir: Path, output_dir: Path):
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
