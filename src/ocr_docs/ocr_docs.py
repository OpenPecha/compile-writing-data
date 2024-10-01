import os
import io
import json
import logging
import gzip
from pathlib import Path
from google.cloud import vision
from google.cloud.vision import AnnotateImageResponse

vision_client = vision.ImageAnnotatorClient()

def check_google_credentials():
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        raise EnvironmentError("Set the GOOGLE_APPLICATION_CREDENTIALS environment variable.")

def load_image(image_path):
    with io.open(image_path, "rb") as image_file:
        return image_file.read()

def perform_ocr(image_content, lang_hint=None):
    ocr_image = vision.Image(content=image_content)

    features = [
        {"type_": vision.Feature.Type.DOCUMENT_TEXT_DETECTION, "model": "builtin/weekly"},
    ]
    
    image_context = {"language_hints": [lang_hint]} if lang_hint else {}

    response = vision_client.annotate_image({
        "image": ocr_image,
        "features": features,
        "image_context": image_context,
    })

    response_json = AnnotateImageResponse.to_json(response)
    return json.loads(response_json)

def gzip_string(string_):
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="w") as fo:
        fo.write(string_.encode())
    return out.getvalue()

def save_results(result, json_path, txt_path):
    result_json = json.dumps(result)
    gzip_result = gzip_string(result_json)
    json_path.write_bytes(gzip_result)

    full_text = result.get("fullTextAnnotation", {}).get("text", "")
    if full_text:
        txt_path.write_text(full_text, encoding="utf-8")
        print(f"OCR completed and saved as: {json_path} and {txt_path}.")
    else:
        logging.warning(f"No text detected for the image.")

def process_image(image_path, OCR_json_dir, OCR_txt_dir, lang=None):
    image_name = image_path.stem
    result_json_fn = OCR_json_dir / f"{image_name}.json.gz"
    result_txt_fn = OCR_txt_dir / f"{image_name}.txt"

    if result_json_fn.is_file() and result_txt_fn.is_file():
        print(f"Skipping already processed image: {image_name}")
        return

    try:
        image_content = load_image(image_path)
        result = perform_ocr(image_content, lang)
        save_results(result, result_json_fn, result_txt_fn)
    except Exception as e:
        logging.exception(f"Error processing {image_path}: {e}")

def process_images_in_directory(images_dir, OCR_json_root, OCR_txt_root):
    for sub_dir in images_dir.iterdir():
        if not sub_dir.is_dir():
            continue

        OCR_json_path = OCR_json_root / sub_dir.name
        OCR_txt_path = OCR_txt_root / sub_dir.name

        OCR_json_path.mkdir(parents=True, exist_ok=True)
        OCR_txt_path.mkdir(parents=True, exist_ok=True)

        for img_fn in sub_dir.iterdir():
            if img_fn.is_file() and img_fn.suffix.lower() in {".tiff", ".tif", ".jpg", ".jpeg"}:
                lang = img_fn.suffix.lower()[1:]
                process_image(img_fn, OCR_json_path, OCR_txt_path, lang)
            else:
                logging.warning(f"Unsupported file or directory: {img_fn.name}")

def main():
    check_google_credentials()
    images_dir = Path("data/scanned_docs/DOH")
    OCR_json_root = Path("data/ocr_json/DOH")
    OCR_txt_root = Path("data/ocr_txt/DOH")

    OCR_json_root.mkdir(parents=True, exist_ok=True)
    OCR_txt_root.mkdir(parents=True, exist_ok=True)

    process_images_in_directory(images_dir, OCR_json_root, OCR_txt_root)

if __name__ == "__main__":
    main()
