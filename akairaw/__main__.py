import sys
from . import AkaiRAWProgramFile

p_file = sys.argv[1]

f = AkaiRAWProgramFile(p_file)
f.parse_program()
print("Program:", f.program_name)
print(f"Overall Tuning: {f.header.tune_offset}")
for keygroup in f.keygroups:
    print(keygroup)
    for vlz in keygroup.velocity_zones:
        if vlz.ascii_sample_name == "":
            continue
        if vlz.velocity_range_high == 0:
            continue
        print(vlz)

