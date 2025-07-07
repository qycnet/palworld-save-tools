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


def connect_info_item_reader(reader: FArchiveReader) -> dict[str, Any]:
    return {
        "connect_to_model_instance_id": reader.guid(),
        "index": reader.byte(),
    }


def connect_info_item_writer(writer: FArchiveWriter, properties: dict[str, Any]):
    writer.guid(properties["connect_to_model_instance_id"])
    writer.byte(properties["index"])


def decode_bytes(
    parent_reader: FArchiveReader, c_bytes: Sequence[int]
) -> Optional[dict[str, Any]]:
    if len(c_bytes) == 0:
        return {"values": []}
    reader = parent_reader.internal_copy(bytes(c_bytes), debug=False)
    data: dict[str, Any] = {
        "supported_level": reader.i32(),
        "connect": {
            "index": reader.byte(),
            "any_place": reader.tarray(connect_info_item_reader),
        },
    }
    # We are guessing here, we don't have information about the type without mapping object names -> types
    # Stairs have 2 connectors (up and down),
    # Roofs have 4 connectors (front, back, right, left)
    # 检查reader对象是否已到达文件末尾，如果没有，则执行以下操作：
    # 从reader对象中读取剩余的所有字节，并将它们转换为一个整数列表
    # 然后将这个整数列表存储在data字典的"unknown_data"键下
    # 这些未知数据可能包含额外的信息或填充数据

    if not reader.eof():
        data["unknown_data"] = [int(b) for b in reader.read_to_end()]
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
    writer.i32(p["supported_level"])
    writer.byte(p["connect"]["index"])
    writer.tarray(connect_info_item_writer, p["connect"]["any_place"])
    if "unknown_data" in p:
        writer.write(bytes(p["unknown_data"]))
    encoded_bytes = writer.bytes()
    return encoded_bytes
