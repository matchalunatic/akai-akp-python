"""AkaiAKP parser

The Akai AKP file format is a non-standard twist on the RIFF format.

This implementation goes from scratch so we consider these quirks as just plain.
"""

from collections import OrderedDict
import struct
from .data_maps import *


class AkaiAKPFile:
    @property
    def keygroups(self) -> iter:
        return iter(self._keygroups)

    @property
    def tune(self) -> TuneClass:
        return self._tune

    @property
    def out(self) -> OutClass:
        return self._out

    @property
    def prg(self) -> PrgClass:
        return self._prg

    @property
    def lfo_1(self) -> LFO1Class:
        return self._lfo[0]

    @property
    def lfo_2(self) -> LFO2Class:
        return self._lfo[1]

    @property
    def mods(self) -> ModsClass:
        return self._mods

    @property
    def envelopes(self):
        return self._envelopes

    def __init__(self, path):
        self._file = path
        self._mpn = None
        self._keygroups = []
        self._sections = {}
        self._as_bytes = bytearray(16384)
        self._akp_length = 0
        self._prg = OrderedDict(
            {"u_0": None, "midi_program_number": None, "num_keygroups": None}
        )
        self._tune = TuneClass()
        self._envelopes = []
        # OrderedDict(
        #    {
        #        "u_0": None,
        #        "semitone_tune": None,
        #        "fine_tune": None,
        #        "c_detune": None,
        #        "cs_detune": None,
        #        "d_detune": None,
        #        "ds_detune": None,
        #        "e_detune": None,
        #        "f_detune": None,
        #        "fs_detune": None,
        #        "g_detune": None,
        #        "gs_detune": None,
        #        "a_detune": None,
        #        "bb_detune": None,
        #        "b_detune": None,
        #        "pitchbend_up": None,
        #        "pitchbend_down": None,
        #        "bend_mode": None,
        #        "aftertouch": None,
        #        "u_19": None,
        #        "u_20": None,
        #        "u_21": None,
        #    }
        # )
        self._out = OrderedDict(
            {
                "u_0": None,
                "loudness": None,
                "amp_mod_1": None,
                "amp_mod_2": None,
                "pan_mod_1": None,
                "pan_mod_2": None,
                "pan_mod_3": None,
                "velocity_sens": None,
            }
        )
        lfo_template = OrderedDict(
            {
                "u_0": None,
                "waveform": None,
                "rate": None,
                "delay": None,
                "depth": None,
                "lfo_sync": None,
                "lfo_retrigger": None,
                "modwheel": None,
                "aftertouch": None,
                "rate_mod": None,
                "delay_mod": None,
                "depth_mod": None,
            }
        )

        self._lfo = [OrderedDict(**lfo_template), OrderedDict(**lfo_template)]
        self._mods = ModsClass()

        self.readbytes()

    def readbytes(self):
        """read the file"""
        with open(self._file, "rb") as fh:
            bs = fh.read()
            self._as_bytes[:] = bs
            self._akp_length = len(bs)

    def parse_prg(self, data: bytes):
        self._prg = PrgClass(*data)
 
    def parse_tune(self, data: bytes):
        up = {
            "u_0": data[0],
            "semitone_tune": data[1],
            "fine_tune": data[2],
            "c_detune": data[3],
            "cs_detune": data[4],
            "d_detune": data[5],
            "ds_detune": data[6],
            "e_detune": data[7],
            "f_detune": data[8],
            "fs_detune": data[9],
            "g_detune": data[10],
            "gs_detune": data[11],
            "a_detune": data[12],
            "bb_detune": data[13],
            "b_detune": data[14],
            "pitchbend_up": data[15],
            "pitchbend_down": data[16],
            "bend_mode": data[17],
            "aftertouch": data[18],
            "u_19": data[19],
            "u_20": data[20],
            "u_21": data[21],
            "u_22": data[22],
            "u_23": data[23],
        }
        for k, v in up.items():
            setattr(self._tune, k, v)

    def parse_kg_kloc(self, data: bytes):
        return OrderedDict(
            {
                "unused_0": data[0],
                "unused_1": data[1],
                "unused_2": data[2],
                "unused_3": data[3],
                "low_note": data[4],
                "high_note": data[5],
                "semitone_tune": data[6],
                "fine_tune": data[7],
                "override_fx": data[8],
                "fx_send_level": data[9],
                "pitch_mode_1": data[10],
                "pitch_mode_2": data[11],
                "amp_mode": data[12],
                "zone_xfade": data[13],
                "mute_group": data[14],
                "unused_15": data[15],
            }
        )

    def parse_kg_envelope(self, data: bytes, env: type) -> dict:
        # up = {
        #        "u_0": data[0],
        #        "rate_1": data[1],
        #        "rate_2": data[2],
        #        "rate_3": data[3],
        #        "rate_4": data[4],
        #        "level_1": data[5],
        #        "level_2": data[6],
        #        "level_3": data[7],
        #        "level_4": data[8],
        #        "u_9": data[9],
        #        "vel_rate_1": data[10],
        #        "u_11": data[11],
        #        "keyboard_r2_r4": data[12],
        #        "u_13": data[13],
        #        "vel_rate_4": data[14],
        #        "off_vel_rate_4": data[15],
        #        "vel_out_level_0": data[16],
        #        "u_17": data[17],
        #    }
        return env(*data)

    def parse_kg_zone(self, data: bytes) -> dict:
        len_sample_name = data[1]
        sample_name = data[2 : 2 + len_sample_name]
        parm_off = 1 + len_sample_name

        return ZoneClass(
            data[0], len_sample_name, sample_name, *data[parm_off : parm_off + 24]
        )

    def parse_kg_filter(self, data: bytes):
        return OrderedDict(
            {
                "u_0": data[0],
                "filter_mode": data[1],
                "cutoff_freq": data[2],
                "resonance": data[3],
                "keyboard_track": data[4],
                "mod_input_1": data[5],
                "mod_input_2": data[6],
                "mod_input_3": data[7],
                "headroom": data[8],
                "u_9": data[9],
            }
        )

    def parse_keygroup(self, data: bytes):
        # a keygroup is a nested collection of sections
        # keyboard location, amplitude envelope, filter envelope, auxiliary envelope, filter settings, zone 1, zone2, zone3, zone4
        envelope_counter = 0
        zone_counter = 0
        offset = 0
        keygroup = OrderedDict(
            {
                "kloc": OrderedDict({}),
                "amp_env": EnvelopeClass(),
                "fil_env": EnvelopeClass(),
                "aux_env": AuxEnvelopeClass(),
                "filter": OrderedDict({}),
                "zone1": OrderedDict({}),
                "zone2": OrderedDict({}),
                "zone3": OrderedDict({}),
                "zone4": OrderedDict({}),
            }
        )

        zones = [
            "zone1",
            "zone2",
            "zone3",
            "zone4",
        ]
        envelopes = ["amp_env", "fil_env", "aux_env"]
        while offset < len(data):
            section_name = data[offset : offset + 4].decode("ascii")
            section_length = struct.unpack_from("<I", data[offset + 4 : offset + 8])[0]
            sections = data[offset + 8 : offset + 8 + section_length]
            assert section_length % 2 == 0
            if section_name == "kloc":
                assert section_length == 16
                keygroup["kloc"].update(self.parse_kg_kloc(sections))
            elif section_name == "env ":
                assert section_length == 18
                keygroup[envelopes[envelope_counter]] = self.parse_kg_envelope(
                    sections,
                    EnvelopeClass if envelope_counter < 2 else AuxEnvelopeClass,
                )
                # envelopes[envelope_counter].update(self.parse_kg_envelope(sections))
                envelope_counter += 1
            elif section_name == "filt":
                assert section_length == 10
                keygroup["filter"].update(self.parse_kg_filter(sections))
            elif section_name == "zone":
                # print(f'zone len: {section_length}')
                keygroup[zones[zone_counter]] = self.parse_kg_zone(sections)
                zone_counter += 1
            offset += section_length + 8
        return keygroup

    def parse_out(self, data: bytes):
        self._out.update(
            {
                "u_0": data[0],
                "loudness": data[1],
                "amp_mod_1": data[2],
                "amp_mod_2": data[3],
                "pan_mod_1": data[4],
                "pan_mod_2": data[5],
                "pan_mod_3": data[6],
                "velocity_sens": data[7],
            }
        )

    def parse_lfo(self, data: bytes, lfoclass: type) -> object:
        return lfoclass(*data)

    def parse_mods(self, data: bytes):
        up = {
            "u_0": data[0],
            "u_1": data[1],
            "u_2": data[2],
            "u_3": data[3],
            "u_4": data[4],
            "amp_mod_1_src": data[5],
            "u_6": data[6],
            "amp_mod_2_src": data[7],
            "u_8": data[8],
            "pan_mod_1_src": data[9],
            "u_10": data[10],
            "pan_mod_2_src": data[11],
            "u_12": data[12],
            "pan_mod_3_src": data[13],
            "u_14": data[14],
            "lfo_1_rate_mod_src": data[15],
            "u_16": data[16],
            "lfo_1_delay_mod_src": data[17],
            "u_18": data[18],
            "lfo_1_depth_mod_src": data[19],
            "u_20": data[20],
            "lfo_2_rate_mod_src": data[21],
            "u_22": data[22],
            "lfo_2_delay_mod_src": data[23],
            "u_24": data[24],
            "lfo_2_depth_mod_src": data[25],
            "u_26": data[26],
        }
        for k, v in up.items():
            setattr(self._mods, k, v)
        self._mods.u_remainder = b"".join([data[27:]])

    def list_sections(self):
        offset = 0
        o_secname = 0
        l_secname = 4
        o_attrlen = 4
        l_attrlen = 4
        o_attribs = 8
        l_attribs = 1
        section_counter = 0
        keygroup_counter = 0
        lfo_counter = 0
        while offset < self._akp_length:
            ro_secname = offset + o_secname
            ro_attrlen = offset + o_attrlen
            ro_attribs = offset + o_attribs
            section_name = self._as_bytes[ro_secname : ro_secname + l_secname].decode(
                "ascii"
            )
            # little endian decoding of the integer
            section_length = struct.unpack_from(
                "<I", self._as_bytes[ro_attrlen : ro_attrlen + l_attrlen]
            )[0]
            sections = self._as_bytes[
                ro_attribs : ro_attribs + l_attribs * section_length
            ]
            print(f"Section: [{section_name}] (len: {section_length})")
            assert section_length % 2 == 0
            if section_name == "RIFF":
                # skip the garbage of the RIFF file for good hey
                sections = b"\0\0\0\0"
                section_length = 4
            elif section_name == "prg ":
                self.parse_prg(sections)
            elif section_name == "tune":
                assert section_length == 24
                self.parse_tune(sections)
            elif section_name == "lfo ":
                assert section_length == 14
                self._lfo[lfo_counter] = self.parse_lfo(sections, LFO1Class if lfo_counter == 0 else LFO2Class)
                lfo_counter += 1
            elif section_name == "mods":
                assert section_length == 38
                self.parse_mods(sections)
            elif section_name == "kgrp":
                kg = self.parse_keygroup(sections)
                self._keygroups.append(kg)
                keygroup_counter += 1
            elif section_name == "out ":
                assert section_length == 8
                self.parse_out(sections)
            else:
                raise ValueError(f"unknown section {section_name}")
            offset += o_attribs + l_attribs * section_length
            section_counter += 1
            print(f"Read {offset}/{self._akp_length}")
