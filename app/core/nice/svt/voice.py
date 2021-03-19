from ....config import Settings
from ....schemas.common import Region
from ....schemas.gameenums import (
    COND_TYPE_NAME,
    VOICE_COND_NAME,
    VOICE_TYPE_NAME,
    SvtVoiceType,
    VoiceCondType,
)
from ....schemas.nice import (
    AssetURL,
    NiceVoiceCond,
    NiceVoiceGroup,
    NiceVoiceLine,
    NiceVoicePlayCond,
)
from ....schemas.raw import (
    MstSvtGroup,
    MstSvtVoice,
    MstVoice,
    MstVoicePlayCond,
    ScriptJson,
    ScriptJsonCond,
    ServantEntity,
)
from ...utils import nullable_to_string


settings = Settings()


def get_voice_folder(voice_type: int) -> str:
    if voice_type == SvtVoiceType.BATTLE:
        return "Servants_"
    elif voice_type == SvtVoiceType.TREASURE_DEVICE:
        return "NoblePhantasm_"
    else:
        return "ChrVoice_"


def get_voice_url(region: Region, svt_id: int, voice_type: int, voice_id: str) -> str:
    folder = get_voice_folder(voice_type) + str(svt_id)
    return AssetURL.audio.format(
        base_url=settings.asset_url, region=region, folder=folder, id=voice_id
    )


def get_nice_play_cond(playCond: MstVoicePlayCond) -> NiceVoicePlayCond:
    return NiceVoicePlayCond(
        condGroup=playCond.condGroup,
        condType=COND_TYPE_NAME[playCond.condType],
        targetId=playCond.targetId,
        condValue=playCond.condValues[0],
        condValues=playCond.condValues,
    )


def get_nice_voice_cond(
    cond: ScriptJsonCond, costume_ids: dict[int, int], mstSvtGroups: list[MstSvtGroup]
) -> NiceVoiceCond:
    cond_value = (
        costume_ids[cond.value]
        if cond.condType == VoiceCondType.COSTUME
        else cond.value
    )

    cond_value_list = (
        [group.svtId for group in mstSvtGroups if group.id == cond.value]
        if cond.condType == VoiceCondType.SVT_GROUP
        else []
    )

    voice_cond = NiceVoiceCond(
        condType=VOICE_COND_NAME[cond.condType],
        eventId=cond.eventId,
        value=cond_value,
        valueList=cond_value_list,
    )

    return voice_cond


def get_nice_voice_line(
    region: Region,
    script: ScriptJson,
    svt_id: int,
    voice_prefix: int,
    voice_type: int,
    costume_ids: dict[int, int],
    subtitle_ids: dict[str, str],
    play_conds: list[MstVoicePlayCond],
    mstVoices: dict[str, MstVoice],
    mstSvtGroups: list[MstSvtGroup],
) -> NiceVoiceLine:
    first_voice = script.infos[0]
    voice_id = first_voice.get_voice_id()

    voice_line = NiceVoiceLine(
        overwriteName=nullable_to_string(script.overwriteName),
        id=(info.id for info in script.infos),
        audioAssets=(
            get_voice_url(region, svt_id, voice_type, info.id) for info in script.infos
        ),
        delay=(info.delay for info in script.infos),
        face=(info.face for info in script.infos),
        form=(info.form for info in script.infos),
        text=(nullable_to_string(info.text) for info in script.infos),
        conds=(
            get_nice_voice_cond(info, costume_ids, mstSvtGroups)
            for info in script.conds
        ),
        playConds=(
            get_nice_play_cond(play_cond)
            for play_cond in play_conds
            if play_cond.svtId == svt_id
            and play_cond.voiceId == voice_id
            and (play_cond.voicePrefix == -1 or play_cond.voicePrefix == voice_prefix)
        ),
        subtitle=subtitle_ids.get(str(svt_id) + "_" + first_voice.id, ""),
    )

    if voice_id in mstVoices:
        mstVoice = mstVoices[voice_id]
        voice_line.name = mstVoice.name
        voice_line.condType = COND_TYPE_NAME[mstVoice.condType]
        voice_line.condValue = mstVoice.condValue
        voice_line.priority = mstVoice.priority
        voice_line.svtVoiceType = VOICE_TYPE_NAME[mstVoice.svtVoiceType]

    return voice_line


def get_nice_voice_group(
    region: Region,
    voice: MstSvtVoice,
    costume_ids: dict[int, int],
    subtitle_ids: dict[str, str],
    play_conds: list[MstVoicePlayCond],
    mstVoices: dict[str, MstVoice],
    mstSvtGroups: list[MstSvtGroup],
) -> NiceVoiceGroup:
    return NiceVoiceGroup(
        svtId=voice.id,
        voicePrefix=voice.voicePrefix,
        type=VOICE_TYPE_NAME[voice.type],
        voiceLines=(
            get_nice_voice_line(
                region,
                script,
                voice.id,
                voice.voicePrefix,
                voice.type,
                costume_ids,
                subtitle_ids,
                play_conds,
                mstVoices,
                mstSvtGroups,
            )
            for script in voice.scriptJson
        ),
    )


def get_nice_voice(
    region: Region, raw_svt: ServantEntity, costume_ids: dict[int, int]
) -> list[NiceVoiceGroup]:
    subtitle_ids = {subtitle.id: subtitle.serif for subtitle in raw_svt.mstSubtitle}
    mstVoices = {voice.id: voice for voice in raw_svt.mstVoice}

    return [
        get_nice_voice_group(
            region,
            voice,
            costume_ids,
            subtitle_ids,
            raw_svt.mstVoicePlayCond,
            mstVoices,
            raw_svt.mstSvtGroup,
        )
        for voice in raw_svt.mstSvtVoice
    ]
