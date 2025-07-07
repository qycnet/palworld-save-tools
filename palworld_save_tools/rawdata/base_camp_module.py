from typing import Any, Sequence

from palworld_save_tools.archive import *
from palworld_save_tools.rawdata.common import (
    pal_item_and_num_read,
    pal_item_and_slot_writer,
)

NO_OP_TYPES = [
    "EPalBaseCampModuleType::Energy",
    "EPalBaseCampModuleType::Medical",
    "EPalBaseCampModuleType::ResourceCollector",
    "EPalBaseCampModuleType::ItemStorages",
    "EPalBaseCampModuleType::FacilityReservation",
    "EPalBaseCampModuleType::ObjectMaintenance",
    "EPalBaseCampModuleType::ItemStackInfo",  # 物品堆叠信息模块，可能用于提供关于物品堆叠的详细信息或管理堆叠物品
]


def decode(
    reader: FArchiveReader, type_name: str, size: int, path: str
) -> dict[str, Any]:
    if type_name != "MapProperty":
        raise Exception(f"Expected MapProperty, got {type_name}")
    value = reader.property(type_name, size, path, nested_caller_path=path)
    # module map
    module_map = value["value"]
    for module in module_map:
        module_type = module["key"]
        module_bytes = module["value"]["RawData"]["value"]["values"]
        module["value"]["RawData"]["value"] = decode_bytes(
            reader, module_bytes, module_type
        )
    return value


def transport_item_character_info_reader(reader: FArchiveReader) -> dict[str, Any]:
    return {
        "item_infos": reader.tarray(pal_item_and_num_read),
        "character_location": reader.vector_dict(),
    }


PASSIVE_EFFECT_ENUM = {
    0: "EPalBaseCampPassiveEffectType::None",
    1: "EPalBaseCampPassiveEffectType::WorkSuitability",
    2: "EPalBaseCampPassiveEffectType::WorkHard",
    3: "EPalBaseCampPassiveEffectType::AllWorkSpeed",  # 所有工作速度被动效果，可能提高所有工作的执行速度
    4: "EPalBaseCampPassiveEffectType::SanityDecreaseSuppressor",  # 理智下降抑制被动效果，可能减少由于长时间工作或压力导致的理智下降
    5: "EPalBaseCampPassiveEffectType::EPalBaseCampPassiveEffectType_MAX",  # 枚举类型的最大值，通常用作边界值或检查枚举值是否有效的标志
}


def module_passive_effect_reader(reader: FArchiveReader) -> dict[str, Any]:
    data: dict[str, Any] = {}
    data["type"] = reader.byte()
    if data["type"] not in PASSIVE_EFFECT_ENUM:
        raise Exception(f"Unknown passive effect type {data['type']}")
    elif data["type"] == 2:
        data["work_hard_type"] = reader.byte()
        # 从reader中读取接下来的12个字节作为未知数据（可能是保留字段或未来使用的字段）
        # 并将这些数据以字节列表的形式存储在data字典中
        data["unknown_trailer"] = [b for b in reader.read(12)]
    return data


def decode_bytes(
    parent_reader: FArchiveReader, b_bytes: Sequence[int], module_type: str
) -> dict[str, Any]:
    reader = parent_reader.internal_copy(bytes(b_bytes), debug=False)
    data: dict[str, Any] = {}
    if module_type in NO_OP_TYPES:
        pass
    elif module_type == "EPalBaseCampModuleType::TransportItemDirector":
        try:
            data["transport_item_character_infos"] = reader.tarray(
                transport_item_character_info_reader
            )
            data["trailing_bytes"] = reader.byte_list(4)
        except Exception as e:
            print(
                f"Warning: Failed to decode transport item director, please report this: {e} ({bytes(b_bytes)!r})"
            )
            return {"values": b_bytes}
    elif module_type == "EPalBaseCampModuleType::PassiveEffect":
        try:
            data["passive_effects"] = reader.tarray(module_passive_effect_reader)
        except Exception as e:
            reader.data.seek(0)
            print(
                f"Warning: Failed to decode passive effect, please report this: {e} ({bytes(b_bytes)!r})"
            )
            return {"values": b_bytes}
    else:
        print(
            f"Warning: Unknown base camp module type {module_type}, falling back to raw bytes"
        )
        return {"values": b_bytes}

    if not reader.eof():
        print(f"Warning: EOF not reached for {module_type}, falling back to raw bytes")
        return {"values": b_bytes}

    return data


def encode(
    writer: FArchiveWriter, property_type: str, properties: dict[str, Any]
) -> int:
    if property_type != "MapProperty":
        raise Exception(f"Expected MapProperty, got {property_type}")
    del properties["custom_type"]

    module_map = properties["value"]
    for module in module_map:
        module_type = module["key"]
        if "values" not in module["value"]["RawData"]["value"]:
            module["value"]["RawData"]["value"]["values"] = encode_bytes(
                module["value"]["RawData"]["value"], module_type
            )

    return writer.property_inner(property_type, properties)


def transport_item_character_info_writer(
    writer: FArchiveWriter, p: dict[str, Any]
) -> None:
    writer.tarray(pal_item_and_slot_writer, p["item_infos"])
    writer.vector_dict(p["character_location"])


def module_passive_effect_writer(writer: FArchiveWriter, p: dict[str, Any]) -> None:
    writer.byte(p["type"])
    if p["type"] == 2:
        writer.byte(p["work_hard_type"])
        writer.write(bytes(p["unknown_trailer"]))


def encode_bytes(p: dict[str, Any], module_type: str) -> bytes:
    writer = FArchiveWriter()

    if "values" in p:
        writer.write(bytes(p["values"]))
        return writer.bytes()

    if module_type in NO_OP_TYPES:
        pass
    elif module_type == "EPalBaseCampModuleType::TransportItemDirector":
        writer.tarray(
            transport_item_character_info_writer, p["transport_item_character_infos"]
        )
        writer.write(bytes(p["trailing_bytes"]))
    elif module_type == "EPalBaseCampModuleType::PassiveEffect":
        writer.tarray(module_passive_effect_writer, p["passive_effects"])

    encoded_bytes = writer.bytes()
    return encoded_bytes
