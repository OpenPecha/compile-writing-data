# Importing libraries
from pathlib import Path
from tqdm import tqdm

from tibcleaner.docx_to_txt import docx_to_txt
from tibcleaner.utils import _mkdir
from tibcleaner.checkpoint import load_checkpoints

output_dir = Path("data/txt/yigdrel")
files = list(Path("data/DOH").rglob("*.docx"))
_mkdir(output_dir)

checkpoints = load_checkpoints()

for file in tqdm(files, desc="Converting to txt"):
    if str(file) in checkpoints:
        continue
    docx_to_txt(file, output_dir)
