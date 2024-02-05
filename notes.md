## Map properties between formats

We want to sort of map the AKP format to the XPM format. The goal is quite clear: import Akai CD samples to more recent machines and software, like the MPC X, the Akai Force, and the MPC software.

## How this is done

For AKP: Using [refs.md](./refs.md), testing it as it goes, changing from the spec as it goes. My AKP files are built with Extreme Sample Converter, that I highly recommend.

For XPM: I'm using XPM files generated on my MPC X and Akai Force machines (I traded the MPC X for an Akai Force and am very happy with the Force).

## XPM

Drum programs seem to have no matter what 127 full instruments per drum. Each pad is mapped to one instrument.

Keygroup programs on the other hand may have a single Instrument.

No matter what, instruments have a low note and a high note set to 0 - 127 both in Drum programs and Keygroup programs.

Drum Programs seem to have a DrumPadEffects section that is absent from Keygroup programs. Guess we will have to figure that when converting AKP keygroups to Drum programs directly.


## Healthy criticism of XPM

Apparently, the XPM format was introduced with the MPC renaissance. I'm really surprised that they did not choose to compress these XML files. 

See:

- Compressed:   14895   SPACESTATION.xpm.gz
- Uncompressed: 1280561 SPACESTATION.xpm

There's like a hundredfold gain when compressing them.
