from akaiakp import AkaiAKPFile
from akaixpm import AkaiXPMMPCVObject
from dataclasses import dataclass

@dataclass
class AkaiUnifiedRepresentation:
    """Unified representation for Akai sampler formats once parsed.
    
    Of course, samplers have different features and because of that the
    match is not perfect but we aim to get a good-enough fit
    """

class AkaiAKPToXPM:
    def __init__(self, akp_file=None, xpm_file=None):
        self._akp_file = akp_file
        self._xpm_file = xpm_file

    def parse_akp(self):
        """parse the AKP file to prepare for writing and set it to the unified representation"""

    def parse_xpm(self):
        """parse the XPM file to prepare for writing and set it to the unified representation"""

    def write_akp(self):
        """write the unified representation to the AKP file"""

    def write_xpm(self):
        """write the unified representation to the XPM file"""
