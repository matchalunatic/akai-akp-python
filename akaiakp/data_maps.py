from dataclasses import dataclass, astuple
from typing import ClassVar
from struct import pack

class ToBytesAble:
    LENGTH: ClassVar[int]
    SECTION_NAME: ClassVar[bytes]
    SKIP_FIELDS: ClassVar[list[str]] = []
    def attrs_as_bytes(self) -> bytes:
        to_concat = []
        for el in astuple(self):
            if isinstance(el, bytes):
                to_concat.append(el)
            else:
                assert el & 0x000000ff == el # ensure you don't set non 0-255 numbers
                to_concat.append(bytes([el & 0x000000ff]))
        return b"".join(to_concat)

    def as_riff_bytes(self) -> bytes:
        attrs_len = self.LENGTH
        attrs_len_b = pack('<I', attrs_len)
        as_bytes = self.attrs_as_bytes()
        return b"".join([self.SECTION_NAME, attrs_len_b, as_bytes])

@dataclass
class RIFFClass(ToBytesAble):
    LENGTH: int = 0
    SECTION_NAME: ClassVar[bytes] = b'RIFF'
    def attrs_as_bytes(self):
        return b'APRG'

@dataclass
class KLocClass(ToBytesAble):
    LENGTH: ClassVar[int] = 16
    SECTION_NAME: ClassVar[bytes] = b'kloc'
    u_0: int = 0x01
    u_1: int = 0x03
    u_2: int = 0x01
    u_3: int = 0x04
    low_note: int = 0x15
    high_note: int = 0x7F
    semitone_tune: int = 0
    fine_tune: int = 0
    override_fx: int = 0
    fx_send_level: int = 0
    pitch_mod_1: int = 0x64
    pitch_mod_2: int = 0
    amp_mod: int = 0
    zone_xfade: int = 0
    mute_group: int = 0
    u_15: int = 0


@dataclass
class TuneClass(ToBytesAble):
    LENGTH: ClassVar[int] = 24
    SECTION_NAME: ClassVar[bytes] = b'tune'
    u_0: int = 1
    semitone_tune: int = 0
    fine_tune: int = 0
    c_detune: int = 0
    cs_detune: int = 0
    d_detune: int = 0
    ds_detune: int = 0
    e_detune: int = 0
    f_detune: int = 0
    fs_detune: int = 0
    g_detune: int = 0
    gs_detune: int = 0
    a_detune: int = 0
    bb_detune: int = 0
    b_detune: int = 0
    pitchbend_up: int = 0x2
    pitchbend_down: int = 0x2
    bend_mode: int = 0
    aftertouch: int = 0
    u_19: int = 0
    u_20: int = 0
    u_21: int = 0
    u_22: int = 0
    u_23: int = 0


@dataclass
class OutClass(ToBytesAble):
    LENGTH: ClassVar[int] = 8
    SECTION_NAME: ClassVar[bytes] = b'out '

    u_0: int = 1
    loudness: int = 0x55
    amp_mod_1: int = 0
    amp_mod_2: int = 0
    pan_mod_1: int = 0
    pan_mod_2: int = 0
    pan_mod_3: int = 0
    velocity_sens: int = 0x19

    def attrs_as_bytes(self) -> bytes:
        return b"".join(bytes([a]) for a in astuple(self))


@dataclass
class PrgClass(ToBytesAble):
    LENGTH: ClassVar[int] = 6
    SECTION_NAME: ClassVar[bytes] = b'prg '

    u_0: int = 1
    midi_program_number: int = 0
    number_of_keygroups: int = 0x1
    u_3: int = 0
    u_4: int = 0
    u_5: int = 0


@dataclass
class ModsClass(ToBytesAble):
    LENGTH: ClassVar[int] = 38
    SECTION_NAME: ClassVar[bytes] = b'mods'

    u_0: int = 0x1
    u_1: int = 0
    u_2: int = 0x11
    u_3: int = 0
    u_4: int = 0x02
    amp_mod_1_src: int = 0x06
    u_6: int = 0x02
    amp_mod_2_src: int = 0x03
    u_8: int = 0x01
    pan_mod_1_src: int = 0x08
    u_10: int = 0x01
    pan_mod_2_src: int = 0x06
    u_12: int = 0x01
    pan_mod_3_src: int = 0x01
    u_14: int = 0x04
    lfo_1_rate_mod_src: int = 0x06
    u_16: int = 0x05
    lfo_1_delay_mod_src: int = 0x06
    u_18: int = 0x03
    lfo_1_depth_mod_src: int = 0x06
    u_20: int = 0x07
    lfo_2_rate_mod_src: int = 0
    u_22: int = 0x08
    lfo_2_delay_mod_src: int = 0
    u_24: int = 0x06
    lfo_2_depth_mod_src: int = 0
    u_26: int = 0
    u_remainder: bytes = b"\00"

    def attrs_as_bytes(self):
        the_tup = astuple(self)
        res = b"".join(bytes([a]) for a in the_tup[0:-1])
        res = res + the_tup[-1]
        return res


@dataclass
class LFO1Class(ToBytesAble):
    LENGTH: ClassVar[int] = 14
    SECTION_NAME: ClassVar[bytes] = b'lfo '

    u_0: int = 1
    waveform: int = 0x1
    rate: int = 0x2B
    delay: int = 0
    depth: int = 0
    lfo_sync: int = 0
    u_6: int = 0
    modwheel: int = 0x0F
    aftertouch: int = 0
    rate_mod: int = 0
    delay_mod: int = 0
    depth_mod: int = 0
    u_12: int = 0
    u_13: int = 0


@dataclass
class LFO2Class(ToBytesAble):
    LENGTH: ClassVar[int] = 14
    SECTION_NAME: ClassVar[bytes] = b'lfo '

    u_0: int = 1
    waveform: int = 0x1
    rate: int = 0x2B
    delay: int = 0
    depth: int = 0
    u_5: int = 0
    lfo_retrigger: int = 0
    u_7: int = 0
    u_8: int = 0
    rate_mod: int = 0
    delay_mod: int = 0
    depth_mod: int = 0
    u_12: int = 0
    u_13: int = 0


@dataclass
class EnvelopeClass(ToBytesAble):
    LENGTH: ClassVar[int] = 18
    SECTION_NAME: ClassVar[bytes] = b'env '

    u_0: int = 1
    attack: int = 0
    u_2: int = 0
    decay: int = 0x32
    release: int = 0x0F
    u_5: int = 0
    u_6: int = 0
    sustain: int = 0x64
    u_8: int = 0
    u_9: int = 0
    vel_attack: int = 0
    u_11: int = 0
    keyscale: int = 0
    u_13: int = 0
    on_vel_release: int = 0
    off_vel_release: int = 0
    u_16: int = 0
    u_17: int = 1


@dataclass
class AuxEnvelopeClass(ToBytesAble):
    LENGTH: ClassVar[int] = 18
    SECTION_NAME: ClassVar[bytes] = b'env '

    u_0: int = 1
    rate_1: int = 0
    rate_2: int = 0x32
    rate_3: int = 0x32
    rate_4: int = 0x0F
    level_1: int = 0x64
    level_2: int = 0x64
    level_3: int = 0x64
    level_4: int = 0
    u_9: int = 0
    vel_rate_1: int = 0
    u_11: int = 0
    keyboard_r2_r4: int = 0
    u_13: int = 0
    on_vel_rate_4: int = 0
    off_vel_rate_4: int = 0
    vel_out_level: int = 0
    u_17: int = 0x85


@dataclass
class ZoneClass(ToBytesAble):
    LENGTH: ClassVar[int] = 48
    SECTION_NAME: ClassVar[bytes] = b'zone'

    u_0: int = 1
    sample_char_len: int = 20
    sample_name: bytes = b"\0" * 20
    u_1: int = 0
    u_2: int = 0
    u_3: int = 0
    u_4: int = 0
    u_5: int = 0
    u_6: int = 0
    u_7: int = 0
    u_8: int = 0
    u_9: int = 0
    u_10: int = 0
    u_11: int = 0
    u_12: int = 0
    u_13: int = 0
    low_velocity: int = 0
    high_velocity: int = 0x7F
    fine_tune: int = 0
    semitone_tune: int = 0
    filter: int = 0
    pan_balance: int = 0
    playback: int = 0x4
    output: int = 0
    zone_level: int = 0
    keyboard_track: int = 1
    velocity_start_lsb: int = 0
    velocity_start_msb: int = 0
    u_46: int = 0

@dataclass
class FilterClass(ToBytesAble):
    LENGTH: ClassVar[int] = 10
    SECTION_NAME: ClassVar[bytes] = b'filt'

    u_0: int = 1
    filter_mode: int = 0
    cutoff_freq: int = 0x64
    resonance: int = 0x0
    keyboard_track: int = 0
    mod_input_1: int = 0
    mod_input_2: int = 0
    mod_input_3: int = 0
    headroom: int = 0
    u_9: int = 0


@dataclass
class KeygroupClass(ToBytesAble):
    @property
    def LENGTH(self):
        return 999
    SECTION_NAME: ClassVar[bytes] = b'kgrp'

    kloc: KLocClass
    amp_envelope: EnvelopeClass
    filter_envelope: EnvelopeClass
    aux_envelope: AuxEnvelopeClass
    filter: FilterClass
    zone1: ZoneClass
    zone2: ZoneClass
    zone3: ZoneClass
    zone4: ZoneClass

    @property
    def zones(self):
        return [
            self.zone1,
            self.zone2,
            self.zone3,
            self.zone4,
        ]

    def as_riff_bytes(self) -> bytes:
        sections = bytearray()
        sections.extend(self.kloc.as_riff_bytes())
        sections.extend(self.amp_envelope.as_riff_bytes())
        sections.extend(self.filter_envelope.as_riff_bytes())
        sections.extend(self.aux_envelope.as_riff_bytes())
        sections.extend(self.filter.as_riff_bytes())
        sections.extend(self.zone1.as_riff_bytes())
        sections.extend(self.zone2.as_riff_bytes())
        sections.extend(self.zone3.as_riff_bytes())
        sections.extend(self.zone4.as_riff_bytes())
        len_sections = pack('<I', len(sections))
        return self.SECTION_NAME + len_sections + sections
