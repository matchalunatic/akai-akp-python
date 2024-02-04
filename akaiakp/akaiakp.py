"""AkaiAKP parser

The Akai AKP file format is a non-standard twist on the RIFF format.

This implementation goes from scratch so we consider these quirks as just plain.
"""

import struct
from .data_maps import *
import logging

logger = logging.getLogger(__name__)

class AkaiAKPFile:
    @property
    def file_name(self) -> str:
        return self._file
    @property
    def riff(self) -> RIFFClass:
        return self._riff
    @property
    def keygroups(self) -> list:
        return self._keygroups

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
        self._as_bytes = bytearray()
        self._akp_length = 0
        self._riff = RIFFClass()
        self._prg = PrgClass()
        self._tune = TuneClass()
        self._envelopes = []
        self._out = OutClass()

        self._lfo = [LFO1Class(), LFO2Class()]
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
        return KLocClass(*data)

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
        sample_name = bytes(data[2 : 22])
        parm_off = 22
        remainder = data[parm_off:]
        return ZoneClass(
            data[0], len_sample_name, sample_name, *remainder
        )

    def parse_kg_filter(self, data: bytes):
        return FilterClass(*data)

    def parse_keygroup(self, data: bytes):
        # a keygroup is a nested collection of sections
        # keyboard location, amplitude envelope, filter envelope, auxiliary envelope, filter settings, zone 1, zone2, zone3, zone4
        envelope_counter = 0
        zone_counter = 0
        offset = 0

        zones = [
            "zone1",
            "zone2",
            "zone3",
            "zone4",
        ]
        kloc = None
        filter = None
        zones = [None, None, None, None]
        envelopes = [None, None, None]
        while offset < len(data):
            section_name = data[offset : offset + 4].decode("ascii")
            section_length = struct.unpack_from("<I", data[offset + 4 : offset + 8])[0]
            sections = data[offset + 8 : offset + 8 + section_length]
            assert section_length % 2 == 0
            if section_name == "kloc":
                assert section_length == 16
                kloc = self.parse_kg_kloc(sections)
            elif section_name == "env ":
                assert section_length == 18
                envelopes[envelope_counter] = self.parse_kg_envelope(
                    sections,
                    EnvelopeClass if envelope_counter < 2 else AuxEnvelopeClass,
                )
                # envelopes[envelope_counter].update(self.parse_kg_envelope(sections))
                envelope_counter += 1
            elif section_name == "filt":
                assert section_length == 10
                filter = self.parse_kg_filter(sections)
            elif section_name == "zone":
                assert section_length == 48
                zones[zone_counter] = self.parse_kg_zone(sections)
                zone_counter += 1
            offset += section_length + 8
        return KeygroupClass(
            kloc=kloc,
            amp_envelope=envelopes[0],
            filter_envelope=envelopes[1],
            aux_envelope=envelopes[2],
            filter=filter,
            zone1=zones[0],
            zone2=zones[1],
            zone3=zones[2],
            zone4=zones[3],
        )

    def parse_out(self, data: bytes):
        self._out = OutClass(*data)

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
                self._lfo[lfo_counter] = self.parse_lfo(
                    sections, LFO1Class if lfo_counter == 0 else LFO2Class
                )
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
            logger.info(f"Read {offset}/{self._akp_length}")

    def to_bytes(self):
        b = bytearray()
        c = bytearray()
        c.extend(self.prg.as_riff_bytes())
        c.extend(self.out.as_riff_bytes())
        c.extend(self.tune.as_riff_bytes())
        c.extend(self.lfo_1.as_riff_bytes())
        c.extend(self.lfo_2.as_riff_bytes())
        c.extend(self.mods.as_riff_bytes())
        for k in self.keygroups:
            c.extend(k.as_riff_bytes())
        self.riff.LENGTH = len(c) + 4
        b.extend(self.riff.as_riff_bytes())
        b.extend(c)
        return b
