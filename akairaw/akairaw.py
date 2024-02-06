from dataclasses import dataclass
from typing import ClassVar


_memoized_maps = {}

def map_u_to_cents(i: int):
    assert 0 <= i and i < 256 and int(i) == i
    s = a2psi(i)
    return map_s_to_cents(s)

def map_s_to_cents(i: int):
    if 'u2c' not in _memoized_maps:
        cents_distance = 50.0 - (- 50.0) # 100
        cents_step_count = 255
        cents_step_size = cents_distance / cents_step_count
        u2c = []
        for counter in range(cents_step_count):
            u2c.append(int(-50 + cents_step_size * counter))
        _memoized_maps['u2c'] = u2c
    assert -128 <= i and i < 128 and int(i) == i
    return _memoized_maps['u2c'][i + 128]

def a2psi_a(i: int):
    """Akai to Python signed int: 2's complement stuff"""
    # first verify that the passed number is short enough
    assert i & 0xff == i
    # then change its representation
    return i - int((i << 1) & 2 ** 8)

def a2psi(i: int):
    """Akai to Python signed int: 2's complement stuff"""
    # first verify that the passed number is short enough
    if (i & 0x80):
        return -((i ^ 0xFF) + 1)
    return i

@dataclass
class AkaiRawProgramHeaderData:
    data_length: ClassVar[int] = 48
    header_id: int
    keygroup_internal_offset_lsb: int 
    keygroup_internal_offset_msb: int
    program_name: bytearray(12)
    midi_program_number: int
    midi_channel: int
    polyphony: int
    priority: int
    play_range_low: int
    play_range_high: int
    play_octave_shift: int
    individual_output: int
    stereo_level: int
    stereo_pan: int
    loudness: int
    velocity_to_loudness: int
    key_to_loudness: int
    pressure_to_loudness: int
    pan_lfo_rate: int
    pan_depth: int
    pan_lfo_delay: int
    key_to_pan_position: int
    lfo_speed: int
    lfo_fixed_depth: int
    lfo_delay: int
    modwheel_to_depth: int
    pressure_to_depth: int
    velocity_to_depth: int
    bendwheel_to_pitch: int
    pressure_to_pitch: int
    keygroup_crossfade: int
    keygroup_count: int
    temporary_internal_program_number: int
    key_temperament_c: int
    key_temperament_cs: int
    key_temperament_d: int
    key_temperament_ds: int
    key_temperament_e: int
    key_temperament_f: int
    key_temperament_fs: int
    key_temperament_g: int
    key_temperament_gs: int
    key_temperament_a: int
    key_temperament_bb: int
    key_temperament_b: int
    echo_output_level: int
    modwheel_pan_amount: int
    sample_start_coherence: int
    lfo_desync: int
    pitch_law: int
    voice_assign_algorithm: int
    soft_pedal_loudness_reduction: int
    soft_pedal_attack_stretch: int
    soft_pedal_filter_close: int
    tune_offset: int
    key_to_lfo_rate: int
    key_to_lfo_depth: int
    key_to_lfo_delay: int
    voice_output_scale: int
    stereo_output_scale: int
    remainder: bytes

    @classmethod
    def from_bytes(cls, b: bytearray):
        return cls(b[0x00], *b[0x01:0x03], b[0x03:0x0f], *b[0x0f:0x47], b[0x47:])

@dataclass
class AkaiRawProgramKeygroupData:
    data_length: ClassVar[int] = 34
    keygroup_block_id: int
    next_keygroup_offset_lsb: int
    next_keygroup_offset_msb: int
    keyrange_low: int
    keyrange_high: int
    tune_offset_coarse: int
    tune_offset_cents: int
    filter_freq: int
    key_to_filter_freq: int
    velocity_to_filter_freq: int
    pressure_to_filter_freq: int
    envelope_to_filter_freq: int
    amp_attack: int
    amp_decay: int
    amp_sustain: int
    amp_release: int
    velocity_to_amp_attack: int
    velocity_to_amp_release: int
    off_velocity_to_amp_release: int
    key_to_amp_decay_and_release: int
    filter_attack: int
    filter_decay: int
    filter_sustain: int
    filter_release: int
    velocity_to_filter_attack: int
    velocity_to_filter_release: int
    off_velocity_to_filter_release: int
    key_to_filter_decay_and_release: int
    velocity_to_filter_envelope_output: int
    envelope_to_pitch: int
    velocity_zone_crossfade: int
    number_of_velocity_zones: int
    internal_a: int
    internal_b: int
    remainder: bytes

    def __str__(self):
        return f"""#{self.keygroup_block_id} k: {self.keyrange_low} K: {self.keyrange_high}
Filter: {self.filter_freq}
"""
    
    @property
    def velocity_zones(self):
        if not hasattr(self, '_vlzs'):
            self.remainder_to_velocity_zone_data()
        return self._vlzs
    @classmethod
    def from_bytes(cls, b: bytearray):
        return cls(*b[0:cls.data_length], b[cls.data_length:])

    def remainder_to_velocity_zone_data(self):
        vlz_length = 0x39 - 0x22 + 1
        vlzs = []
        total_rem = len(self.remainder)
        offset = 0
        num_vlz = self.number_of_velocity_zones
        while (offset < total_rem and num_vlz > 0):
            ds = self.remainder[offset : offset + vlz_length]
            vlzs.append(AkaiRawProgramKeygroupVelocityZoneData.from_bytes(ds))
            offset += vlz_length
            num_vlz -= 1
        self._vlzs = vlzs

@dataclass
class AkaiRawProgramKeygroupVelocityZoneData:
    sample_name: bytearray(12)
    velocity_range_low: int
    velocity_range_high: int
    tune_offset_fine: int
    tune_offset_coarse: int
    loudness_offset: int
    filter_freq_offset: int
    pan_offset: int
    playback_mode: int
    low_velocity_xfade_factor_lsb: int
    low_velocity_xfade_factor_msb: int
    sample_address_lsb: int
    sample_address_msb: int

    def __str__(self):
        return f"""v: {self.velocity_range_low} V: {self.velocity_range_high}
Sample: [{self.ascii_sample_name}] CTune:{a2psi(self.tune_offset_coarse)}/STune:{map_u_to_cents(self.tune_offset_fine)}
Loudness: {a2psi(self.loudness_offset)} Pan: {a2psi(self.pan_offset)} Playback Mode: {self.playback_mode}
"""
    
    @property
    def ascii_sample_name(self):
        return decode_akai_string(self.sample_name).decode('ascii')

    @classmethod
    def from_bytes(cls, b: bytearray):
        return cls(b[0:12], *b[12:])



FROM_STRING = b''.join(b'%c' % (a,) for a in range(10)) + b'\x0a' + b''.join(b'%c' % (a,) for a in range(11, 0x28))
TO_STRING = b'0123456789 ABCDEFGHIJKLMNOPQRSTUVWXYZ#+.'

trans_table = bytes.maketrans(FROM_STRING, TO_STRING)
def decode_akai_string(b: bytes):
    return b.translate(trans_table)

class AkaiRAWProgramFile:

    @property
    def keygroup_ranges(self) -> str:
        return "\n".join([f"Low: {k.keyrange_low} High: {k.keyrange_high}" for k in self.keygroups])
    @property
    def program_name(self) -> str:
        return decode_akai_string(self.header.program_name).decode('utf-8')

    @property
    def header(self) -> AkaiRawProgramHeaderData:
        return self._header

    @property
    def keygroups(self) -> list[AkaiRawProgramKeygroupData]:
        return self._keygroups

    def __init__(self, path):
        self._file = path
        self.asbytes = bytearray()
        self._program_len = 0
        self._header = None
        self._keygroups = []
        self.readbytes()

    def readbytes(self):
        with open(self._file, "rb") as fh:
            bh = fh.read()
            self.asbytes[:] = bh
            self._program_len = len(bh)

    def parse_program(self):
        first_keygroup_offset = 0xc0
        keygroup_length = 0x17f - 0x0c0
        # read the header
        hd = AkaiRawProgramHeaderData.from_bytes(self.asbytes[0x00:0xbf])
        self._header = hd
        # make sanity checks
        assert self.header.header_id == 1
        # now let's read the keygroups
        keygroup_offset = 0xc0
        keygroup_boundary = 0x180 - 0xc0
        keygroups = []
        while keygroup_offset < self._program_len:
            kg = AkaiRawProgramKeygroupData.from_bytes(self.asbytes[keygroup_offset:keygroup_offset + keygroup_boundary])
            keygroups.append(kg)
            keygroup_offset += keygroup_boundary
        self._keygroups = keygroups
