import bs4
from typing import ClassVar
from dataclasses import dataclass, fields
import logging
import json

logger = logging.getLogger(__name__)
PT_KEYGROUP = "Keygroup"
PT_DRUMS = "Drum"

PROGRAMPADS_TAG = "ProgramPads-v2.10"




class AkaiXPMFile:
    def __init__(self, path):
        self._file_path = path
        self._version = None
        with open(self._file_path, "r", encoding="utf-8") as fh:
            self._xml_data = fh.read()
        self._xml_tree = bs4.BeautifulSoup(self._xml_data, "xml")
        self._parse()

    def _parse_version(self, elem: bs4.element.Tag):
        self._version = XPMVersion.from_xml_element(elem)
        logger.info("version: %s", self._version)

    def _parse_drum_program(self, elem: bs4.element.Tag):
        i = AkaiXPMProgram.from_xml_element(elem)

    def _parse_keygroup_program(self, elem: bs4.element.Tag):
        i = AkaiXPMProgram.from_xml_element(elem)

    def _parse_mpcvobject(self, elem: bs4.element.Tag):
        logger.info("Got MPCVObject")
        for tag in elem.children:
            if not tag.name:
                continue
            n = tag.name
            if tag.name == "Version":
                self._parse_version(tag)
            elif tag.name == "Program":
                if tag["type"] == "Drum":
                    self._parse_drum_program(tag)
                elif tag["type"] == "Keygroup":
                    self._parse_keygroup_program(tag)
                else:
                    raise ValueError(f"Incorrect tag type {tag['type']}")

    def _parse(self):
        for tag in self._xml_tree.children:
            if tag.name == "MPCVObject":
                self._parse_mpcvobject(tag)


class XMLLoadable:
    tag_name: ClassVar[str]
    collection_name: ClassVar[str] = None

    @classmethod
    def from_xml_element(cls, e: bs4.element.Tag):
        if (e.name == cls.collection_name):
            # this is a collection, let's make a list
            r = []
            for elm in e.children:
                if elm.name is None:
                    continue
                assert elm.name == cls.tag_name
                r.append(cls.from_xml_element(elm))
            return r
        else:
            assert e.name == cls.tag_name
            parms = {}
            for tn in fields(cls):
                t = juice_tags(e, tn.name)
                parms[tn.name] = t
        return cls(**parms)

@dataclass
class XPMVersion(XMLLoadable):
    tag_name: ClassVar[str] = 'Version'

    file_version: str
    application: str
    application_version: str
    platform: str


@dataclass
class AkaiXPMAudioRoute(XMLLoadable):
    tag_name: ClassVar[str] = "AudioRoute"
    audio_route: int
    audio_route_sub_index: int
    audio_route_channel_bitmap: int
    inserts_enabled: bool


@dataclass
class AkaiXPMLFO(XMLLoadable):
    tag_name: ClassVar[str] = "LFO"
    lfo_num: int
    type: str
    rate: float
    sync: int
    reset: bool
    lfo_pitch: float
    lfo_cutoff: float
    lfo_volume: float
    lfo_pan: float


@dataclass
class AkaiXPMInstrumentLayer(XMLLoadable):
    tag_name: ClassVar[str] = "Layer"
    collection_name: ClassVar[str] = "Layers"

    number: int
    active: bool
    volume: float
    pan: float
    pitch: float
    tune_coarse: int
    tune_fine: int
    vel_start: int
    vel_end: int
    sample_start: int
    sample_end: int
    loop_start: int
    loop_end: int
    loop_crossfade_length: int
    loop_tune: int
    root_note: int
    key_track: bool
    sample_name: str
    pitch_random: float
    volume_random: float
    pan_random: float
    offset_random: float
    sample_file: str
    slice_index: int
    direction: int
    offset: int
    slice_start: int
    slice_end: int
    slice_loop_start: int
    slice_loop: int
    slice_loop_cross_fade_length: int
    slice_tail_position: float
    slice_tail_length: float


@dataclass
class AkaiXPMInstrument(XMLLoadable):
    tag_name: ClassVar[str] = "Instrument"
    collection_name: ClassVar[str] = "Instruments"

    number: int
    cue_bus_enable: bool
    audio_route: AkaiXPMAudioRoute
    send1: float
    send2: float
    send3: float
    send4: float
    volume: float
    mute: bool
    solo: bool
    pan: float
    automation_filter: int
    filter_keytrack: float
    filter_type: int
    cutoff: float
    resonance: float
    filter_env_amt: float
    after_touch_to_filter: float
    velocity_to_filter: float
    velocity_to_filter_envelope: float
    velocity_to_start: float
    velocity_to_filter_attack: float
    filter_attack: float
    filter_decay: float
    filter_sustain: float
    filter_release: float
    filter_attack_curve: float
    filter_decay_curve: float
    filter_release_curve: float
    filter_hold: float
    filter_decay_type: bool
    filter_a_d_envelope: bool
    volume_hold: float
    volume_decay_type: bool
    volume_a_d_envelope: bool
    volume_attack: float
    volume_decay: float
    volume_sustain: float
    volume_release: float
    volume_attack_curve: float
    volume_decay_curve: float
    volume_release_curve: float
    pitch_hold: float
    pitch_decay_type: bool
    pitch_a_d_envelope: bool
    pitch_attack: float
    pitch_decay: float
    pitch_sustain: float
    pitch_release: float
    pitch_attack_curve: float
    pitch_decay_curve: float
    pitch_release_curve: float
    pitch_env_amount: float
    velocity_to_pitch: float
    velocity_to_volume_attack: float
    velocity_sensitivity: float
    velocity_to_pan: float
    randomization_scale: float
    attack_random: float
    decay_random: float
    cutoff_random: float
    resonance_random: float
    lfo: AkaiXPMLFO
    tune_coarse: int
    tune_fine: int
    mono: bool
    polyphony: int
    low_note: int
    high_note: int
    ignore_base_note: bool
    zone_play: int
    mute_group: int
    mute_target1: int
    mute_target2: int
    mute_target3: int
    mute_target4: int
    simult_target1: int
    simult_target2: int
    simult_target3: int
    simult_target4: int
    trigger_mode: int
    layers: list[AkaiXPMInstrumentLayer]  # 4 layers


@dataclass
class AkaiXPMPadNote(XMLLoadable):
    tag_name: ClassVar[str] = "PadNote"
    collection_name: ClassVar[str] = "PadNoteMap"

    number: int
    note: int


@dataclass
class AkaiXPMPadGroup(XMLLoadable):
    tag_name: ClassVar[str] = "PadGroup"
    collection_name: ClassVar[str] = "PadGroupMap"

    number: int
    group: int


@dataclass
class AkaiXPMProgram(XMLLoadable):
    """AkaiXPMProgram represents the XML data in an XPM for the program.

    Offense intended, this is weaponized stupidity.
    """

    tag_name: ClassVar[str] = "Program"

    program_type: str
    program_name: str
    program_pads: str
    cue_bus_enable: bool
    send1: float
    send2: float
    send3: float
    send4: float
    volume: float
    mute: bool
    solo: bool
    pan: float
    automation_filter: int
    tune_coarse: int
    tune_fine: int
    mono: bool
    program_polyphony: int
    portamento_time: float
    portamento_legato: bool
    portamento_quantized: bool
    program_xfader_route: int
    instruments: list[
        AkaiXPMInstrument
    ]  # a 128-item list of instruments, how stupid can you get?
    pad_note_map: list[AkaiXPMPadNote]  # same, 128
    pad_group_map: list[AkaiXPMPadGroup]
    keygroup_master_transpose: float
    keygroup_num_keygroups: int
    keygroup_pitch_bend_range: float
    keygroup_wheel_to_lfo: float
    keygroup_aftertouch_to_filter: float


MAP_TAGS_CLASSES = {
    'PadNoteMap': AkaiXPMPadNote,
    'PadNote': AkaiXPMPadNote,
    'PadGroupMap': AkaiXPMPadGroup,
    'PadGroup': AkaiXPMPadGroup,
    'Instruments': AkaiXPMInstrument,
    'Instrument': AkaiXPMInstrument,
    'Layers': AkaiXPMInstrumentLayer,
    'Layer': AkaiXPMInstrumentLayer,
    'AudioRoute': AkaiXPMAudioRoute,
    'LFO': AkaiXPMLFO,
}

def juice_tags(e: bs4.element.Tag, wanted_field: str):
    """find the right field from the tag, handling special cases, like you would juice a bad orange"""
    pascal_case_name = "".join(f.capitalize() for f in wanted_field.split("_"))
    if wanted_field == "program_type":
        assert e.name == "Program"
        return e["type"]
    elif wanted_field == "number":
        return e["number"]
    elif wanted_field == "lfo_num":
        assert e.name == "LFO"
        return e[pascal_case_name]
    elif wanted_field == "program_pads":
        return json.loads(e.find(PROGRAMPADS_TAG).text)
    elif wanted_field == "program_polyphony":
        assert e.name == "Program"
        return e.find("Program_Polyphony").text
    elif wanted_field == "program_xfader_route":
        assert e.name == "Program"
        return e.find("Program.Xfader.Route").text
    elif wanted_field == 'lfo':
        pascal_case_name = 'LFO'
    elif wanted_field == 'file_version':
        pascal_case_name = 'File_Version'
    elif wanted_field == 'application_version':
        pascal_case_name = 'Application_Version'
    elm = e.find(name=pascal_case_name)
    if elm is None:
        logging.error("Cannot find %s", pascal_case_name)
        raise ValueError(f"Ouch, failed for {pascal_case_name}")
    elm_c = elm.findChildren()
    if len(elm_c) == 0:
        return elm.text
    else:
        assert elm.name in MAP_TAGS_CLASSES
        return MAP_TAGS_CLASSES[elm.name].from_xml_element(elm)
