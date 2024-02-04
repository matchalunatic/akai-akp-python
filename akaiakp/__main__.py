import sys
from pprint import pprint
from .akaiakp import AkaiAKPFile

flz = []

for item in sys.argv[1:]:
    flz.append(AkaiAKPFile(item))

for item in flz:
    print(item)
    item.list_sections()
    #pprint(list(item.keygroups))
    print("Tune")
    pprint(item.tune)
    pprint(next(item.keygroups))
