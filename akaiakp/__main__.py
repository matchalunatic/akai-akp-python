import sys
import logging
from .akaiakp import AkaiAKPFile

logging.basicConfig(level=logging.INFO)
flz = []

for item in sys.argv[1:]:
    flz.append(AkaiAKPFile(item))

for item in flz:
    item.list_sections()
    as_bytes = item.to_bytes()
    with open('test_out.akp', 'wb') as fh:
        fh.write(as_bytes)
        logging.info("Wrote %s bytes to test_out.akp from %s", len(as_bytes), item.file_name)
