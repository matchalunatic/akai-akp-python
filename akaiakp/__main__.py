import sys
from pprint import pprint
from .akaiakp import AkaiAKPFile

flz = []

for item in sys.argv[1:]:
    flz.append(AkaiAKPFile(item))

for item in flz:
    item.list_sections()
    #pprint(list(item.keygroups))
    print("Tune")
    pprint(item.tune)
    print("tune as bytes", item.tune.as_bytes())
    print("Mods")
    pprint(item.mods)
    print("mods as bytes", item.mods.as_bytes())
