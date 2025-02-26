from typing import Any, Sequence

from palworld_save_tools.archive import *


def decode(
    reader: FArchiveReader, type_name: str, size: int, path: str
) -> dict[str, Any]:
    if type_name != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {type_name}")
    value = reader.property(type_name, size, path, nested_caller_path=path)
    data_bytes = value["value"]["values"]
    value["value"] = decode_bytes(reader, data_bytes)
    return value


def decode_bytes(
    parent_reader: FArchiveReader, c_bytes: Sequence[int]
) -> Optional[dict[str, Any]]:
    if len(c_bytes) == 0:
        return None
    reader = parent_reader.internal_copy(bytes(c_bytes), debug=False)
    data = {
        "player_uid": reader.guid(),
        "instance_id": reader.guid(),
        "permission_tribe_id": reader.byte(),
    }
    # 检查是否已到达reader的末尾（即是否还有未读取的数据）
    # 如果没有到达末尾，则读取剩余的所有数据作为未知数据
    # 并将这些数据以整数列表的形式存储在data字典中
    if not reader.eof():
        data["unknown_data"] = [int(b) for b in reader.read_to_end()]
        #可能存在未知数据或未完全读取的情况，因此这里选择不抛出异常
        # raise Exception("Warning: EOF not reached")
    return data


def encode(
    writer: FArchiveWriter, property_type: str, properties: dict[str, Any]
) -> int:
    if property_type != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {property_type}")
    del properties["custom_type"]
    encoded_bytes = encode_bytes(properties["value"])
    properties["value"] = {"values": [b for b in encoded_bytes]}
    return writer.property_inner(property_type, properties)


def encode_bytes(p: dict[str, Any]) -> bytes:
    if p is None:
        return bytes()
    writer = FArchiveWriter()
    writer.guid(p["player_uid"])
    writer.guid(p["instance_id"])
    writer.byte(p["permission_tribe_id"])
    # 检查字典p中是否包含"unknown_data"字段，如果包含，则执行以下操作：
    # 从字典p中读取"unknown_data"字段的值（一个字节列表），并将其转换为字节序列
    # 然后使用writer对象的write方法将这些字节写入到writer对象中
    if "unknown_data" in p:
        writer.write(bytes(p["unknown_data"]))
    encoded_bytes = writer.bytes()
    return encoded_bytes
