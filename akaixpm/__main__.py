import sys
import logging
from . import AkaiXPMFile
import json
from dataclasses import asdict

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

filez = []
for item in sys.argv[1:]:
    filez.append(AkaiXPMFile(item))

for item in filez:
    #print("XPM to JSON -->", json.dumps(asdict(item._mpcvobj), indent=4))
    item.program.program_name += " m-edit"
    with open("test-out.xml", "w", encoding='utf-8') as fh:
        x = item.to_xml()
        fh.write(x)
        logger.info("wrote %s bytes to test-out.xml", len(x))
    with open("program.json", "w", encoding="utf-8") as fh:
        json.dump(item.program.program_pads, fh, indent=2)
