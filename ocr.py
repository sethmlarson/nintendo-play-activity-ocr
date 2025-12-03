# Script which runs OCR on images, returning
# the text that's been detected. This script
# runs within the Docker container.

import json
import os
import sys
import hashlib
import easyocr

# Determine which checksums to skip, if any.
if "--skip-checksums" in sys.argv:
    skip_checksums = sys.argv[sys.argv.index("--skip-checksums") + 1 :]
else:
    skip_checksums = []

reader = easyocr.Reader(["en"])
for filename in os.listdir("/images"):
    if filename == "meta.json":
        continue
    filepath = os.path.join("/images", filename)

    # Skip images we've already processed.
    with open(filepath, "rb") as f:
        file_checksum = hashlib.md5(f.read(), usedforsecurity=False).hexdigest()
    if file_checksum in skip_checksums:
        continue

    result = reader.readtext(filepath, detail=0)
    print(json.dumps({"checksum": file_checksum, "result": result}))
