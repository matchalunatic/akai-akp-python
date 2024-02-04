import sys
from pprint import pprint
from .akaiakp import AkaiAKPFile

flz = []

for item in sys.argv[1:]:
    flz.append(AkaiAKPFile(item))

for item in flz:
    item.list_sections()
    #pprint(list(item.keygroups))
#    print("Tune")
#    pprint(item.tune)
#    print("tune as bytes", item.tune.attrs_as_bytes())
#    print("Mods")
#    pprint(item.mods)
#    print("mods as bytes", item.mods.attrs_as_bytes())
#    print("PRG")
#    pprint(item.prg)
#    print("prg as bytes", item.prg.attrs_as_bytes())
#    print("Keygroups")
#    pprint(item.keygroups[0])
#    print("mods len", len(item.mods.attrs_as_bytes()))
    as_bytes = item.to_bytes()
    with open('test_out.akp', 'wb') as fh:
        fh.write(as_bytes)
