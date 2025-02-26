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
    #data = {
    #    "slot_index": reader.i32(),
    #    "count": reader.i32(),
    #    "item": {
    #        "static_id": reader.fstring(),
    #        "dynamic_id": {
    #            "created_world_id": reader.guid(),
    #            "local_id_in_created_world": reader.guid(),
    #        },
    #    },
    #    "trailing_bytes_length": len(reader.read_to_end()),
    #}
    # 初始化一个空字典，用于存储解码后的数据
    data: Dict[str, Any] = {}
    
    # 从字节序列中读取并解析槽位索引（slot_index），并将其存储在data字典中
    data["slot_index"] = reader.i32()
    
    # 从字节序列中读取并解析数量（count），并将其存储在data字典中
    data["count"] = reader.i32()
    
    # 初始化一个字典，用于存储物品（item）的相关信息
    item: Dict[str, Any] = {}
    
    # 从字节序列中读取并解析物品的静态ID（static_id），并将其存储在item字典中
    item["static_id"] = reader.fstring()
    
    # 初始化一个字典，用于存储动态ID（dynamic_id）的相关信息
    dynamic_id: Dict[str, Any] = {}
    
    # 从字节序列中读取并解析创建世界的ID（created_world_id），并将其存储在dynamic_id字典中
    dynamic_id["created_world_id"] = reader.guid()
    
    # 从字节序列中读取并解析在创建世界中的本地ID（local_id_in_created_world），并将其存储在dynamic_id字典中
    dynamic_id["local_id_in_created_world"] = reader.guid()
    
    # 将包含动态ID信息的字典存储在item字典中
    item["dynamic_id"] = dynamic_id
    
    # 将包含物品信息的字典存储在data字典中
    data["item"] = item
    
    # 读取并解析剩余的字节序列的长度，并将其存储在data字典中
    # 注意：这里假设剩余的字节序列可能包含一些未解析的数据或填充字节
    data["trailing_bytes_length"] = len(reader.read_to_end())
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
    # 从输入字典中读取槽位索引（slot_index），并使用writer对象的i32方法将其编码为字节序列
    writer.i32(p["slot_index"])
    
    # 从输入字典中读取数量（count），并使用writer对象的i32方法将其编码为字节序列
    writer.i32(p["count"])
    
    # 从输入字典中读取物品的静态ID（static_id），并使用writer对象的fstring方法将其编码为字节序列
    writer.fstring(p["item"]["static_id"])
    
    # 从输入字典中读取创建世界的ID（created_world_id），并使用writer对象的guid方法将其编码为字节序列
    writer.guid(p["item"]["dynamic_id"]["created_world_id"])
    
    # 从输入字典中读取在创建世界中的本地ID（local_id_in_created_world），并使用writer对象的guid方法将其编码为字节序列
    writer.guid(p["item"]["dynamic_id"]["local_id_in_created_world"])
    
    # 根据输入字典中的trailing_bytes_length字段，写入指定数量的空字节（\x00）作为填充字节
    writer.write(b"\x00" * p["trailing_bytes_length"])
    encoded_bytes = writer.bytes()
    return encoded_bytes
