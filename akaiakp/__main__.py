import sys
import logging
from .akaiakp import AkaiAKPFile

logging.basicConfig(level=logging.INFO)
flz = []

for item in sys.argv[1:]:
    flz.append(AkaiAKPFile(item))

for item in flz:
    item.list_sections()
    item.out.velocity_sens = -100
    item.tune.semitone_tune = -30
    item.tune.fine_tune = -5
    item.tune.keyscale = 2
    item.keygroups[0].zone2.keyscale = 0
    item.keygroups[0].filter.cutoff_freq = 50
    item.keygroups[0].filter.resonance = 2
    as_bytes = item.to_bytes()

    with open('test_out.akp', 'wb') as fh:
        fh.write(as_bytes)
        logging.info("Wrote %s bytes to test_out.akp from %s", len(as_bytes), item.file_name)
