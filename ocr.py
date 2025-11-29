# Script which runs OCR on images, returning
# the text that's been detected. This script
# runs within the Docker container.

import json
import os
import hashlib
import easyocr

# Load metadata about which images have been processed.
with open("/images/meta.json") as f:
    meta = json.loads(f.read())

reader = easyocr.Reader(["en"])
for filename in os.listdir("/images"):
    if filename == "meta.json":
        continue
    filepath = os.path.join("/images", filename)

    # Skip images we've already processed.
    with open(filepath, "rb") as f:
        fileid = hashlib.md5(f.read(), usedforsecurity=False).hexdigest()
    if fileid in meta["processed"]:
        continue

    result = reader.readtext(filepath, detail=0)
    print(json.dumps({"id": fileid, "result": result}))
