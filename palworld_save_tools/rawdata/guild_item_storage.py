from typing import Any, Optional, Sequence
from palworld_save_tools.archive import FArchiveReader, FArchiveWriter

# decode函数用于解码一个ArrayProperty类型的属性
# 它接受一个FArchiveReader对象、属性类型名称、属性大小以及属性路径作为参数
# 并返回一个包含解码后数据的字典
def decode(
    reader: FArchiveReader, type_name: str, size: int, path: str
) -> dict[str, Any]:
    # 检查属性类型是否为ArrayProperty，如果不是，则抛出异常
    if type_name != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {type_name}")
    # 使用reader对象的property方法读取属性数据
    # 该方法返回一个字典，其中包含属性的值和其他相关信息
    value = reader.property(type_name, size, path, nested_caller_path=path)
    
    # 从返回的字典中提取字节序列数据
    data_bytes = value["value"]["values"]
    
    # 使用decode_bytes函数解码字节序列数据，并将解码后的数据存回value字典中
    value["value"] = decode_bytes(reader, data_bytes)
    
    # 返回包含解码后数据的字典
    return value

# decode_bytes函数用于解码一个字节序列，并返回一个包含解码后数据的字典
def decode_bytes(
    parent_reader: FArchiveReader, m_bytes: Sequence[int]
) -> dict[str, Any]:
    # 创建一个FArchiveReader对象的内部副本，用于读取字节序列数据
    # 注意：这里假设parent_reader具有internal_copy方法，该方法在原始代码中未定义，可能是自定义的或来自某个库
    reader = parent_reader.internal_copy(bytes(m_bytes), debug=False)
    
    # 读取并返回包含容器ID的字典
    # 假设容器ID是一个GUID，用于唯一标识存储数据的容器
    data = {"container_id": reader.guid()}
    if not reader.eof():
        data["trailing_bytes"] = [int(b) for b in reader.read_to_end()]
    return data

# encode函数用于编码一个ArrayProperty类型的属性
# 它接受一个FArchiveWriter对象、属性类型名称以及包含属性数据的字典作为参数
# 并返回编码后的属性大小（字节数）
def encode(
    writer: FArchiveWriter, property_type: str, properties: dict[str, Any]
) -> int:
    # 检查属性类型是否为ArrayProperty，如果不是，则抛出异常
    if property_type != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {property_type}")
    
    # 从属性字典中删除自定义类型字段（如果存在）
    # 假设自定义类型字段不是编码过程所需的
    del properties["custom_type"]
    
    # 使用encode_bytes函数编码属性数据中的值部分
    # 并将编码后的字节序列转换为列表形式存回属性字典中
    encoded_bytes = encode_bytes(properties["value"])
    properties["value"] = {"values": [b for b in encoded_bytes]}
    
    # 使用writer对象的property_inner方法编码属性，并返回编码后的大小（字节数）
    return writer.property_inner(property_type, properties)

# encode_bytes函数用于编码一个包含容器ID的字典，并返回编码后的字节序列
def encode_bytes(p: Optional[dict[str, Any]]) -> bytes:
    # 如果输入字典为空，则返回一个空字节序列
    if p is None:
        return b""
    
    # 创建一个FArchiveWriter对象，用于将数据编码为字节序列

    writer = FArchiveWriter()
    # 写入容器ID（假设它是一个GUID）
    writer.guid(p["container_id"])
    # 获取编码后的字节序列
    if "trailing_bytes" in p:
        writer.write(bytes(p["trailing_bytes"]))
    encoded_bytes = writer.bytes()
    # 返回编码后的字节序列
    return encoded_bytes
