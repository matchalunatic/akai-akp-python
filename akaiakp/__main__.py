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
    b = bytearray()
    c = bytearray()
    c.extend(item.prg.as_riff_bytes())
    c.extend(item.out.as_riff_bytes())
    c.extend(item.tune.as_riff_bytes())
    c.extend(item.lfo_1.as_riff_bytes())
    c.extend(item.lfo_2.as_riff_bytes())
    c.extend(item.mods.as_riff_bytes())
    for k in item.keygroups:
        c.extend(k.as_riff_bytes())
    
    item.riff.LENGTH = len(c) + 4
    print("RIFF Len", item.riff.LENGTH)
    print(item.riff.as_riff_bytes())
    b.extend(item.riff.as_riff_bytes())
    b.extend(c)
    with open('test_out.akp', 'wb') as fh:
        fh.write(b)
