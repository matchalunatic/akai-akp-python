from dataclasses import dataclass, astuple


@dataclass
class TuneClass:
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

    def as_bytes(self) -> bytes:
        return b"".join(bytes(a) for a in astuple(self))


@dataclass
class OutClass:
    u_0: int = 1
    loudness: int = 0x55
    amp_mod_1: int = 0
    amp_mod_2: int = 0
    pan_mod_1: int = 0
    pan_mod_2: int = 0
    pan_mod_3: int = 0
    velocity_sens: int = 0x19

    def as_bytes(self) -> bytes:
        return b"".join(bytes(a) for a in astuple(self))


@dataclass
class PrgClass:
    u_0: int = 1
    midi_program_number: int = 0
    number_of_keygroups: int = 0x1
    u_3: int = 0
    u_4: int = 0
    u_5: int = 0

    def as_bytes(self) -> bytes:
        return b"".join(bytes(a) for a in astuple(self))


@dataclass
class ModsClass:
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


@dataclass
class LFO1Class:
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

    def as_bytes(self) -> bytes:
        return b"".join(bytes(a) for a in astuple(self))


@dataclass
class LFO2Class:
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

    def as_bytes(self) -> bytes:
        return b"".join(bytes(a) for a in astuple(self))

@dataclass
class EnvelopeClass:
    u_0: int = 1
    attack: int = 0
    u_2: int = 0
    decay: int = 0x32
    release: int = 0x0f
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

    def as_bytes(self) -> bytes:
        return b"".join(bytes(a) for a in astuple(self))


@dataclass
class AuxEnvelopeClass:
    u_0: int = 1
    rate_1: int = 0
    rate_2: int = 0x32
    rate_3: int = 0x32
    rate_4: int = 0x0f
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

    def as_bytes(self) -> bytes:
        return b"".join(bytes(a) for a in astuple(self))
