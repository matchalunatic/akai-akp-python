import bs4
from typing import ClassVar
from dataclasses import dataclass, fields, asdict, field
import logging
import json
from html import escape
import xml.dom.minidom

from akaixpm.constants import DEFAULT_PROGRAMPADS_JSON


logger = logging.getLogger(__name__)
PT_KEYGROUP = "Keygroup"
PT_DRUMS = "Drum"

PROGRAMPADS_TAG = "ProgramPads-v2.10"


class AkaiXPMFile:

    @property
    def program_type(self):
        return self.program.program_type

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
        newsoup = bs4.BeautifulSoup("", "xml")
        xmlstr = str(self._mpcvobj.to_xml_element(newsoup, self.program_type.lower()))
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

    def to_xml_element(self, soup: bs4.BeautifulSoup, context_hint: str = None):
        tag = soup.new_tag(self.tag_name)
        properties = asdict(self)
        for k in fields(self):
            unjuice_tags(tag, k.name, getattr(self, k.name), soup, context_hint)
        return tag


@dataclass
class AkaiXPMVersion(XMLLoadable):
    tag_name: ClassVar[str] = "Version"

    file_version: str = "2.1"
    application: str = "MPC-V"
    application_version: str = "3.3.0.0"
    platform: str = "Linux"


@dataclass
class AkaiXPMAudioRoute(XMLLoadable):
    tag_name: ClassVar[str] = "AudioRoute"
    audio_route: int
    audio_route_sub_index: int
    audio_route_channel_bitmap: int
    inserts_enabled: bool

    @classmethod
    def audioroute(
        cls,
        audio_route: int,
        audio_route_sub_index: int = 0,
        audio_route_channel_bitmap: int = 3,
        inserts_enabled: bool = True,
    ):
        return cls(
            audio_route=audio_route,
            audio_route_sub_index=audio_route_sub_index,
            audio_route_channel_bitmap=audio_route_channel_bitmap,
            inserts_enabled=inserts_enabled,
        )


@dataclass
class AkaiXPMLFO(XMLLoadable):
    tag_name: ClassVar[str] = "LFO"
    lfo_num: int
    type: str = "Sine"
    rate: float = 0.5
    sync: int = 0
    reset: bool = True
    lfo_pitch: float = 0.0
    lfo_cutoff: float = 0.0
    lfo_volume: float = 0.0
    lfo_pan: float = 0.0

    @classmethod
    def lfo(cls, lfo_num: int, **kwargs):
        return cls(lfo_num=lfo_num, **kwargs)


@dataclass
class AkaiXPMInstrumentLayer(XMLLoadable):
    tag_name: ClassVar[str] = "Layer"
    collection_name: ClassVar[str] = "Layers"

    number: int
    active: bool = True
    volume: float = 1.0
    pan: float = 0.5
    pitch: float = 0.0
    tune_coarse: int = 0
    tune_fine: int = 0
    vel_start: int = 0
    vel_end: int = 127
    sample_start: int = 0
    sample_end: int = 0
    loop_start: int = 0
    loop_end: int = 0
    loop_crossfade_length: int = 0
    loop_tune: int = 0
    root_note: int = 0
    key_track: bool = False
    sample_name: str = ""
    pitch_random: float = 0.0
    volume_random: float = 0.0
    pan_random: float = 0.0
    offset_random: float = 0.0
    sample_file: str = ""
    slice_index: int = 129
    direction: int = 0
    offset: int = 0
    slice_start: int = 0
    slice_end: int = 0
    slice_loop_start: int = 0
    slice_loop: int = 0
    slice_loop_cross_fade_length: int = 0
    slice_tail_position: float = 0.5
    slice_tail_length: float = 0.0

    @classmethod
    def default_layers(cls, num_layers: int = 4) -> list:
        return [cls(number=a + 1) for a in range(num_layers)]


@dataclass
class AkaiXPMDrumPadEffect(XMLLoadable):
    tag_name: ClassVar[str] = "DrumPadEffect"
    collection_name: ClassVar[str] = "DrumPadEffects"
    num: int
    parameter: float
    type: int

    @classmethod
    def drumpadeffect_default_list(cls):
        parm_map = [0, 9, 1, 2, 3, 7, 4, 13]
        return [cls(a, 0.0, b) for a, b in enumerate(parm_map)]


@dataclass
class AkaiXPMBaseInstrument(XMLLoadable):
    tag_name: ClassVar[str] = "Instrument"
    collection_name: ClassVar[str] = "Instruments"


@dataclass
class AkaiXPMKeygroupInstrument(AkaiXPMBaseInstrument):
    number: int
    cue_bus_enable: bool = False
    audio_route: AkaiXPMAudioRoute = field(
        default_factory=lambda: AkaiXPMAudioRoute.audioroute(0)
    )
    send1: float = 0.0
    send2: float = 0.0
    send3: float = 0.0
    send4: float = 0.0
    volume: float = 0.707946
    mute: bool = False
    solo: bool = False
    pan: float = 0.5
    automation_filter: int = 1
    filter_keytrack: float = 0.0
    filter_type: int = 29
    cutoff: float = 1.0
    resonance: float = 0.0
    filter_env_amt: float = 0.0
    after_touch_to_filter: float = 0.0
    velocity_to_filter: float = 0.0
    velocity_to_filter_envelope: float = 0.0
    velocity_to_start: float = 0.0
    velocity_to_filter_attack: float = 0.0
    filter_attack: float = 0.0
    filter_decay: float = 0.047244
    filter_sustain: float = 1.0
    filter_release: float = 0.0
    filter_attack_curve: float = 0.375
    filter_decay_curve: float = 0.375
    filter_release_curve: float = 0.375
    filter_hold: float = 0.0
    filter_decay_type: bool = True
    filter_a_d_envelope: bool = False
    volume_hold: float = 0.0
    volume_decay_type: bool = True
    volume_a_d_envelope: bool = False
    volume_attack: float = 0.0
    volume_decay: float = 0.047244
    volume_sustain: float = 1.0
    volume_release: float = 0.0
    volume_attack_curve: float = 0.375
    volume_decay_curve: float = 0.375
    volume_release_curve: float = 0.375
    pitch_hold: float = 0.0
    pitch_decay_type: bool = True
    pitch_a_d_envelope: bool = False
    pitch_attack: float = 0.0
    pitch_decay: float = 0.047244
    pitch_sustain: float = 1.0
    pitch_release: float = 0.0
    pitch_attack_curve: float = 0.375
    pitch_decay_curve: float = 0.375
    pitch_release_curve: float = 0.375
    pitch_env_amount: float = 0.5
    velocity_to_pitch: float = 0.0
    velocity_to_volume_attack: float = 0.0
    velocity_sensitivity: float = 1.0
    velocity_to_pan: float = 0.0
    randomization_scale: float = 1.0
    attack_random: float = 0.0
    decay_random: float = 0.0
    cutoff_random: float = 0.0
    resonance_random: float = 0.0
    lfo: AkaiXPMLFO = field(default_factory=lambda: AkaiXPMLFO.lfo(0))
    # drum_pad_effects: list[AkaiXPMDrumPadEffect] =
    tune_coarse: int = 0
    tune_fine: int = 0
    mono: bool = False
    polyphony: int = 16
    low_note: int = 0
    high_note: int = 127
    ignore_base_note: bool = False
    zone_play: int = 1
    mute_group: int = 0
    mute_target1: int = 0
    mute_target2: int = 0
    mute_target3: int = 0
    mute_target4: int = 0
    simult_target1: int = 0
    simult_target2: int = 0
    simult_target3: int = 0
    simult_target4: int = 0
    trigger_mode: int = 2
    layers: list[AkaiXPMInstrumentLayer] = field(
        default_factory=lambda: AkaiXPMInstrumentLayer.default_layers(4)
    )  # 4 layers

    @classmethod
    def default_list(cls, num=1):
        return [cls(number=a + 1) for a in range(num)]


@dataclass
class AkaiXPMDrumInstrument(AkaiXPMBaseInstrument):
    number: int
    cue_bus_enable: bool = False
    audio_route: AkaiXPMAudioRoute = field(
        default_factory=lambda: AkaiXPMAudioRoute.audioroute(0)
    )
    send1: float = 0.0
    send2: float = 0.0
    send3: float = 0.0
    send4: float = 0.0
    volume: float = 0.707946
    mute: bool = False
    solo: bool = False
    pan: float = 0.5
    automation_filter: int = 1
    filter_keytrack: float = 0.0
    filter_type: int = 0
    cutoff: float = 1.0
    resonance: float = 0.0
    filter_env_amt: float = 0.0
    after_touch_to_filter: float = 0.0
    velocity_to_filter: float = 0.0
    velocity_to_filter_envelope: float = 0.0
    velocity_to_start: float = 0.0
    velocity_to_filter_attack: float = 0.0
    filter_attack: float = 0.0
    filter_decay: float = 0.047244
    filter_sustain: float = 1.0
    filter_release: float = 0.0
    filter_attack_curve: float = 0.375
    filter_decay_curve: float = 0.375
    filter_release_curve: float = 0.375
    filter_hold: float = 0.0
    filter_decay_type: bool = True
    filter_a_d_envelope: bool = True
    volume_hold: float = 0.0
    volume_decay_type: bool = True
    volume_a_d_envelope: bool = True
    volume_attack: float = 0.0
    volume_decay: float = 0.047244
    volume_sustain: float = 1.0
    volume_release: float = 0.0
    volume_attack_curve: float = 0.375
    volume_decay_curve: float = 0.375
    volume_release_curve: float = 0.375
    pitch_hold: float = 0.0
    pitch_decay_type: bool = True
    pitch_a_d_envelope: bool = True
    pitch_attack: float = 0.0
    pitch_decay: float = 0.047244
    pitch_sustain: float = 1.0
    pitch_release: float = 0.0
    pitch_attack_curve: float = 0.375
    pitch_decay_curve: float = 0.375
    pitch_release_curve: float = 0.375
    pitch_env_amount: float = 0.5
    velocity_to_pitch: float = 0.0
    velocity_to_volume_attack: float = 0.0
    velocity_sensitivity: float = 1.0
    velocity_to_pan: float = 0.0
    randomization_scale: float = 1.0
    attack_random: float = 0.0
    decay_random: float = 0.0
    cutoff_random: float = 0.0
    resonance_random: float = 0.0
    lfo: AkaiXPMLFO = field(default_factory=lambda: AkaiXPMLFO.lfo(0))
    drum_pad_effects: list[AkaiXPMDrumPadEffect] = field(
        default_factory=AkaiXPMDrumPadEffect.drumpadeffect_default_list
    )
    tune_coarse: int = 0
    tune_fine: int = 0
    mono: bool = True
    polyphony: int = 1
    low_note: int = 0
    high_note: int = 127
    ignore_base_note: bool = False
    zone_play: int = 1
    mute_group: int = 0
    mute_target1: int = 0
    mute_target2: int = 0
    mute_target3: int = 0
    mute_target4: int = 0
    simult_target1: int = 0
    simult_target2: int = 0
    simult_target3: int = 0
    simult_target4: int = 0
    trigger_mode: int = 0
    warp_tempo: float = 120.0
    bpm_lock: bool = True
    warp_enable: bool = False
    stretch_percentage: int = 100
    layers: list[AkaiXPMInstrumentLayer] = field(
        default_factory=lambda: AkaiXPMInstrumentLayer.default_layers(4)
    )  # 4 layers

    @classmethod
    def default_list(cls, num=128):
        return [cls(number=a + 1) for a in range(num)]


@dataclass
class AkaiXPMPadNote(XMLLoadable):
    tag_name: ClassVar[str] = "PadNote"
    collection_name: ClassVar[str] = "PadNoteMap"

    number: int
    note: int

    @classmethod
    def default_keygroup_list(cls):
        return [cls(number=a + 1, note=a) for a in range(128)]

    @classmethod
    def default_drum_list(cls):
        first_chunk = [cls(number=a-35, note=a) for a in range(36,128)]
        second_chunk = [cls(number=a+93, note=a) for a in range(0, 36)]
        return first_chunk + second_chunk
@dataclass
class AkaiXPMPadGroup(XMLLoadable):
    tag_name: ClassVar[str] = "PadGroup"
    collection_name: ClassVar[str] = "PadGroupMap"

    number: int
    group: int

    @classmethod
    def default_list(cls):
        return [cls(number=a + 1, group=0) for a in range(128)]

@dataclass
class AkaiXPMBaseProgram(XMLLoadable):
    """AkaiXPMBaseProgram is the parent for all <Program> entries in an Akai XPM file.

    Offense intended, this is weaponized stupidity.
    """

    tag_name: ClassVar[str] = "Program"

    @staticmethod
    def factory(e: bs4.element.Tag) -> object:
        """return a AkaiXPMabcProgram of the right type based on the passed tag"""
        assert e["type"] in ("Drum", "Keygroup", "MIDI", "Plugin")
        if e["type"] == "Drum":
            return AkaiXPMDrumProgram.from_xml_element(e)
        elif e["type"] == "Keygroup":
            return AkaiXPMKeygroupProgram.from_xml_element(e)
        else:
            raise NotImplementedError(
                f"programs of type {e['type']} are not (yet) supported"
            )


@dataclass
class AkaiXPMKeygroupProgram(AkaiXPMBaseProgram):
    """AkaiXPMKeygroupProgram represents the XML data in an XPM for the program.

    Offense intended, this is weaponized stupidity.
    """

    program_type: str = "Keygroup"
    program_name: str = "EmptyKGName-ChangeMe"
    program_pads: str = DEFAULT_PROGRAMPADS_JSON
    cue_bus_enable: bool = False
    audio_route: AkaiXPMAudioRoute = field(
        default_factory=lambda: AkaiXPMAudioRoute.audioroute(2)
    )
    send1: float = 0.0
    send2: float = 0.0
    send3: float = 0.0
    send4: float = 0.0
    volume: float = 0.707946
    mute: bool = False
    solo: bool = False
    pan: float = 0.5
    automation_filter: int = 1
    pitch: float = 0.0
    tune_coarse: int = 0
    tune_fine: int = 0
    mono: bool = False
    program_polyphony: int = 16
    portamento_time: float = 0.0
    portamento_legato: bool = False
    portamento_quantized: bool = False
    program_xfader_route: int = 0
    instruments: list[AkaiXPMKeygroupInstrument] = field(
        default_factory=lambda: AkaiXPMKeygroupInstrument.default_list(1)
    )  # a 128-item list of instruments, how stupid can you get?
    pad_note_map: list[AkaiXPMPadNote] = field(default_factory=lambda: AkaiXPMPadNote.default_keygroup_list()) # same, 128
    pad_group_map: list[AkaiXPMPadGroup] = field(default_factory=lambda: AkaiXPMPadGroup.default_list())
    keygroup_master_transpose: float = 0.5
    keygroup_num_keygroups: int = 1
    keygroup_pitch_bend_range: float = 0.0
    keygroup_wheel_to_lfo: float = 0.0
    keygroup_aftertouch_to_filter: float = 0.0


@dataclass
class AkaiXPMDrumProgram(AkaiXPMBaseProgram):
    tag_name: ClassVar[str] = "Program"

    program_type: str = "Drum"
    program_name: str = "DefaultProgramName-ChangeMe"
    program_pads: str = DEFAULT_PROGRAMPADS_JSON
    cue_bus_enable: bool = False
    audio_route: AkaiXPMAudioRoute = field(
        default_factory=lambda: AkaiXPMAudioRoute.audioroute(2)
    )
    send1: float = 0.0
    send2: float = 0.0
    send3: float = 0.0
    send4: float = 0.0
    volume: float = 0.707946
    mute: bool = False
    solo: bool = False
    pan: float = 0.5
    automation_filter: int = 1
    pitch: float = 0.0
    tune_coarse: int = 0
    tune_fine: int = 0
    mono: bool = False
    program_polyphony: int = 1
    portamento_time: float = 0.0
    portamento_legato: bool = False
    portamento_quantized: bool = False
    program_xfader_route: int = 0
    instruments: list[AkaiXPMDrumInstrument] = field(
        default_factory=lambda: AkaiXPMDrumInstrument.default_list(128)
    )  # a 128-item list of instruments, how stupid can you get?
    pad_note_map: list[AkaiXPMPadNote] = field(default_factory=AkaiXPMPadNote.default_drum_list) # same, 128
    pad_group_map: list[AkaiXPMPadGroup] = field(default_factory=AkaiXPMPadGroup.default_list)
    # warp_tempo: float = 120.0
    # bpm_lock: bool = True
    # warp_enable: bool = False
    # stretch_percentage: int = 100


@dataclass
class AkaiXPMMPCVObject(XMLLoadable):
    tag_name: ClassVar[str] = "MPCVObject"

    version: AkaiXPMVersion = field(default_factory=AkaiXPMVersion)
    program: AkaiXPMBaseProgram = field(default_factory=AkaiXPMDrumProgram)


MAP_TAGS_CLASSES = {
    "PadNoteMap": AkaiXPMPadNote,
    "PadNote": AkaiXPMPadNote,
    "PadGroupMap": AkaiXPMPadGroup,
    "PadGroup": AkaiXPMPadGroup,
#    "Instruments": AkaiXPMKeygroupInstrument,
#    "Instrument": AkaiXPMKeygroupInstrument,
    "Layers": AkaiXPMInstrumentLayer,
    "Layer": AkaiXPMInstrumentLayer,
    "AudioRoute": AkaiXPMAudioRoute,
    "LFO": AkaiXPMLFO,
 #   "Program": AkaiXPMKeygroupProgram,
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

POLYMORPHIC_TAGS = [
    'Program',
    'Instrument',
    'Instruments',
]

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
        assert wanted_field in ("num", "parameter", "type")
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
    # special case: programs because they're highly polymorphic (why though? >.<)
    elif wanted_field == "program":
        prog_item = e.find("Program")
        logger.info("loading program %s", prog_item["type"])
        return AkaiXPMBaseProgram.factory(prog_item)
    # general case: all the rest
    elm = e.find(name=pascal_case_name)
    if elm is None:
        logging.error("Cannot find %s in %s", pascal_case_name, e.name)
        raise ValueError(f"Ouch, failed for {pascal_case_name}")

    elm_c = elm.findChildren()
    if len(elm_c) == 0:
        return elm.text
    else:
        # special case for polymorphic stuff
        if elm.name in POLYMORPHIC_TAGS:
            if elm.name == 'Program':
                return AkaiXPMBaseProgram.factory(elm)
            elif elm.name == 'Instruments':
                assert e.name == 'Program'
                assert e['type'] in ('Drum', 'Keygroup')
                if e['type'] == 'Drum':
                    return AkaiXPMDrumInstrument.from_xml_element(elm)
                elif e['type'] == 'Keygroup':
                    return AkaiXPMKeygroupInstrument.from_xml_element(elm)
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


def unjuice_tags(e: bs4.element.Tag, wanted_field: str, value, soup: bs4.BeautifulSoup, context_hint: str = None):
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
        assert wanted_field in ("num", "parameter", "type")
        e[wanted_field.capitalize()] = value
    else:
        pascal_case_name = "".join(f.capitalize() for f in wanted_field.split("_"))
        if wanted_field in PROPER_TAG_NAMES:
            pascal_case_name = PROPER_TAG_NAMES[wanted_field]
        if pascal_case_name in MAP_TAGS_CLASSES or pascal_case_name in POLYMORPHIC_TAGS:
            tgtcls = None
            # special case: programs, we gotta do some guess work
            if context_hint == "drum" and pascal_case_name == "Program":
                tgtcls = AkaiXPMDrumProgram
            elif context_hint == "keygroup" and pascal_case_name == "Program":
                tgtcls = AkaiXPMKeygroupProgram
            # special case: AudioRoute.AudioRoute
            elif pascal_case_name == "AudioRoute" and e.name == "AudioRoute":
                return unjuice_normal_tag(e, "AudioRoute", value, soup)
            elif context_hint == "drum" and pascal_case_name == "Instruments":
                tgtcls = AkaiXPMDrumInstrument
            elif context_hint == "keygroup" and pascal_case_name == "Instruments":
                tgtcls = AkaiXPMKeygroupInstrument
            else:
                assert pascal_case_name in MAP_TAGS_CLASSES
                tgtcls = MAP_TAGS_CLASSES[pascal_case_name]
            if tgtcls.collection_name is not None:
                # create a collection tag
                coll = soup.new_tag(tgtcls.collection_name)
                assert isinstance(value, list)
                for item in value:
                    coll.append(item.to_xml_element(soup, context_hint))
                e.append(coll)
            else:
                # create the complex object is all
                assert isinstance(value, XMLLoadable)
                e.append(value.to_xml_element(soup, context_hint))
        else:
            return unjuice_normal_tag(e, pascal_case_name, value, soup)
