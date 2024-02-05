import bs4
from typing import ClassVar
from dataclasses import dataclass, fields, asdict
import logging
import json
from html import escape
import xml.dom.minidom


logger = logging.getLogger(__name__)
PT_KEYGROUP = "Keygroup"
PT_DRUMS = "Drum"

PROGRAMPADS_TAG = "ProgramPads-v2.10"


class AkaiXPMFile:
    @property
    def program(self):
        return self._mpcvobj.program

    @property
    def version(self):
        return self._mpcvobj.version

    def __init__(self, path):
        self._file_path = path
        self._mpcvobj = None
        with open(self._file_path, "r", encoding="utf-8") as fh:
            self._xml_data = fh.read()
        self._xml_tree = bs4.BeautifulSoup(self._xml_data, "xml")
        self._parse()

    def _parse_version(self, elem: bs4.element.Tag):
        self._version = AkaiXPMVersion.from_xml_element(elem)

    def _parse_mpcvobject(self, elem: bs4.element.Tag):
        self._mpcvobj = AkaiXPMMPCVObject.from_xml_element(elem)

    def _parse(self):
        for tag in self._xml_tree.children:
            if tag.name == "MPCVObject":
                self._parse_mpcvobject(tag)

    def to_xml(self):
        newsoup = bs4.BeautifulSoup("<MPCVObject></MPCVObject>", "xml")
        xmlstr = str(self._mpcvobj.to_xml_element(newsoup))
        logger.info("xmlstr len %s", len(xmlstr))
        dom = xml.dom.minidom.parseString(xmlstr)
        # ewww
        return (
            dom.toprettyxml(indent="  ")
            .replace(
                '<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8"?>\n'
            )
            .replace("<SampleName/>", "<SampleName></SampleName>")
            .replace("<SampleFile/>", "<SampleFile></SampleFile>")
        )


class XMLLoadable:
    tag_name: ClassVar[str]
    collection_name: ClassVar[str] = None

    @classmethod
    def from_xml_element(cls, e: bs4.element.Tag):
        if e.name == cls.collection_name:
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

    def to_xml_element(self, soup: bs4.BeautifulSoup):
        tag = soup.new_tag(self.tag_name)
        properties = asdict(self)
        for k in fields(self):
            unjuice_tags(tag, k.name, getattr(self, k.name), soup)
        return tag


@dataclass
class AkaiXPMVersion(XMLLoadable):
    tag_name: ClassVar[str] = "Version"

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
class AkaiXPMDrumPadEffect(XMLLoadable):
    tag_name: ClassVar[str] = "DrumPadEffect"
    collection_name: ClassVar[str] = "DrumPadEffects"
    num: int
    parameter: float
    type: int

@dataclass
class AkaiXPMKeygroupInstrument(XMLLoadable):
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
    # pitch: int
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
    drum_pad_effects: list[AkaiXPMDrumPadEffect]
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
class AkaiXPMDrumInstrument(XMLLoadable):
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
    # pitch: int
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
    drum_pad_effects: list[AkaiXPMDrumPadEffect]
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
class AkaiXPMKeygroupProgram(XMLLoadable):
    """AkaiXPMKeygroupProgram represents the XML data in an XPM for the program.

    Offense intended, this is weaponized stupidity.
    """

    tag_name: ClassVar[str] = "Program"

    program_type: str
    program_name: str
    program_pads: str
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
    pitch: float
    tune_coarse: int
    tune_fine: int
    mono: bool
    program_polyphony: int
    portamento_time: float
    portamento_legato: bool
    portamento_quantized: bool
    program_xfader_route: int
    instruments: list[
        AkaiXPMKeygroupInstrument
    ]  # a 128-item list of instruments, how stupid can you get?
    pad_note_map: list[AkaiXPMPadNote]  # same, 128
    pad_group_map: list[AkaiXPMPadGroup]
    keygroup_master_transpose: float
    keygroup_num_keygroups: int
    keygroup_pitch_bend_range: float
    keygroup_wheel_to_lfo: float
    keygroup_aftertouch_to_filter: float

@dataclass
class AkaiXPMKDrumProgram(XMLLoadable):
    """AkaiXPMKeygroupProgram represents the XML data in an XPM for the program.

    Offense intended, this is weaponized stupidity.
    """

    tag_name: ClassVar[str] = "Program"

    program_type: str
    program_name: str
    program_pads: str
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
    pitch: float
    tune_coarse: int
    tune_fine: int
    mono: bool
    program_polyphony: int
    portamento_time: float
    portamento_legato: bool
    portamento_quantized: bool
    program_xfader_route: int
    instruments: list[
        AkaiXPMDrumInstrument
    ]  # a 128-item list of instruments, how stupid can you get?
    pad_note_map: list[AkaiXPMPadNote]  # same, 128
    pad_group_map: list[AkaiXPMPadGroup]
    keygroup_num_keygroups: int
    keygroup_pitch_bend_range: float
    keygroup_wheel_to_lfo: float
    keygroup_aftertouch_to_filter: float


@dataclass
class AkaiXPMMPCVObject(XMLLoadable):
    tag_name: ClassVar[str] = "MPCVObject"

    version: AkaiXPMVersion
    program: AkaiXPMKeygroupProgram


MAP_TAGS_CLASSES = {
    "PadNoteMap": AkaiXPMPadNote,
    "PadNote": AkaiXPMPadNote,
    "PadGroupMap": AkaiXPMPadGroup,
    "PadGroup": AkaiXPMPadGroup,
    "Instruments": AkaiXPMKeygroupInstrument,
    "Instrument": AkaiXPMKeygroupInstrument,
    "Layers": AkaiXPMInstrumentLayer,
    "Layer": AkaiXPMInstrumentLayer,
    "AudioRoute": AkaiXPMAudioRoute,
    "LFO": AkaiXPMLFO,
    "Program": AkaiXPMKeygroupProgram,
    "Version": AkaiXPMVersion,
    "DrumPadEffects": AkaiXPMDrumPadEffect,
    "DrumPadEffect": AkaiXPMDrumPadEffect,
}

PROPER_TAG_NAMES = {
    "program_polyphony": "Program_Polyphony",
    "program_xfader_route": "Program.Xfader.Route",
    "lfo": "LFO",
    "file_version": "File_Version",
    "application_version": "Application_Version",
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
        return e["LfoNum"]
    elif e.name == "DrumPadEffect":
        assert wanted_field in ('num', 'parameter', 'type')
        return e[pascal_case_name]
        # if wanted_field == "num":
        #     return e["Num"]
        # elif wanted_field == "parameter":
        #     return e["Parameter"]
        # elif wanted_field == "type":
        #     return e["Type"]

    elif wanted_field == "program_pads":
        return json.loads(e.find(PROGRAMPADS_TAG).text)
    elif wanted_field in PROPER_TAG_NAMES:
        pascal_case_name = PROPER_TAG_NAMES[wanted_field]
    #    elif wanted_field == "program_polyphony":
    #        assert e.name == "Program"
    #        pascal_case_name = 'Program_Polyphony'
    #    elif wanted_field == "program_xfader_route":
    #        assert e.name == "Program"
    #        pascal_case_name = "Program.Xfader.Route"
    #    elif wanted_field == 'lfo':
    #        pascal_case_name = 'LFO'
    #    elif wanted_field == 'file_version':
    #        pascal_case_name = 'File_Version'
    #    elif wanted_field == 'application_version':
    #        pascal_case_name = 'Application_Version'
    elm = e.find(name=pascal_case_name)
    if elm is None:
        logging.error("Cannot find %s in %s", pascal_case_name, e.name)
        raise ValueError(f"Ouch, failed for {pascal_case_name}")
    elm_c = elm.findChildren()
    if len(elm_c) == 0:
        return elm.text
    else:
        assert elm.name in MAP_TAGS_CLASSES
        return MAP_TAGS_CLASSES[elm.name].from_xml_element(elm)


def unjuice_normal_tag(
    e: bs4.element.Tag, field_name: str, value: str, soup: bs4.BeautifulSoup
):
    """simply set a value for a tag"""
    t = soup.new_tag(field_name)
    t.string = value
    e.append(t)
    return


def unjuice_tags(e: bs4.element.Tag, wanted_field: str, value, soup: bs4.BeautifulSoup):
    if value is None:
        value = ""
    if wanted_field == "program_type":
        assert e.name == "Program"
        e["type"] = value
    elif wanted_field == "number":
        e["number"] = value
    elif wanted_field == "program_pads":
        f = soup.new_tag(PROGRAMPADS_TAG)
        f.string = json.dumps(value, indent=4)
        e.append(f)
    elif wanted_field == "lfo_num":
        assert e.name == "LFO"
        e["LfoNum"] = value
    elif e.name == "DrumPadEffect":
        assert wanted_field in ('num', 'parameter', 'type')
    else:
        pascal_case_name = "".join(f.capitalize() for f in wanted_field.split("_"))
        if wanted_field in PROPER_TAG_NAMES:
            pascal_case_name = PROPER_TAG_NAMES[wanted_field]
        if pascal_case_name in MAP_TAGS_CLASSES:
            tgtcls = MAP_TAGS_CLASSES[pascal_case_name]
            # special case: AudioRoute.AudioRoute
            if pascal_case_name == "AudioRoute" and e.name == "AudioRoute":
                return unjuice_normal_tag(e, "AudioRoute", value, soup)
            if tgtcls.collection_name is not None:
                # create a collection tag
                coll = soup.new_tag(tgtcls.collection_name)
                assert isinstance(value, list)
                for item in value:
                    coll.append(item.to_xml_element(soup))
                e.append(coll)
            else:
                # create the complex object is all
                assert isinstance(value, XMLLoadable)
                e.append(value.to_xml_element(soup))
        else:
            return unjuice_normal_tag(e, pascal_case_name, value, soup)
