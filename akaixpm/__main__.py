import sys
import logging
from .akaixpm import AkaiXPMFile

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

filez = []
for item in sys.argv[1:]:
    filez.append(AkaiXPMFile(item))

for item in filez:
    print("hi", item)
