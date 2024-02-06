from .akptoxpm import AkaiAKPToXPM

import sys

def halp():
    print('Usage: akptoxpm <to_xpm|to_akp> <akp_file> <xpm_file>')

action = None
f = None
try:
    action = sys.argv[1]
    f = AkaiAKPToXPM(sys.argv[2], sys.argv[3])
except Exception:
    halp()
    sys.exit(1)
if action == 'to_xpm':
    f.parse_akp()
    f.write_xpm()
elif action == 'to_akp':
    f.parse_xpm()
    f.write_akp()
else:
    halp()
    sys.exit(1)
