from typing import Any, Optional, Sequence
from palworld_save_tools.archive import FArchiveReader, FArchiveWriter
from palworld_save_tools.rawdata.common import (
    lab_research_rep_info_read,  # 用于读取实验室研究报告信息的函数
    lab_research_rep_info_writer,  # 用于写入实验室研究报告信息的函数
)

# decode函数用于解码一个ArrayProperty类型的属性，该属性包含实验室研究报告的相关信息
# 它接受一个FArchiveReader对象、属性类型名称、属性大小以及属性路径作为参数
# 并返回一个包含解码后实验室研究报告信息的字典
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
    
    # 使用decode_bytes函数解码字节序列数据，得到实验室研究报告信息
    # 并将解码后的信息存回value字典中
    value["value"] = decode_bytes(reader, data_bytes)
    
    # 返回包含解码后实验室研究报告信息的字典
    return value

# decode_bytes函数用于解码一个字节序列，该字节序列包含实验室研究报告的信息
# 它接受一个FArchiveReader对象和一个字节序列作为参数
# 并返回一个包含解码后实验室研究报告信息的字典
def decode_bytes(
    parent_reader: FArchiveReader, m_bytes: Sequence[int]
) -> dict[str, Any]:
    # 创建一个FArchiveReader对象的内部副本，用于读取字节序列数据
    reader = parent_reader.internal_copy(bytes(m_bytes), debug=False)
    
    # 初始化一个空字典，用于存储解码后的实验室研究报告信息
    data: dict[str, Any] = {}
    
    # 使用reader对象的tarray方法和lab_research_rep_info_read函数
    # 读取并解码实验室研究报告的信息列表
    data["research_info"] = reader.tarray(lab_research_rep_info_read)
    
    # 使用reader对象的fstring方法读取当前研究的ID
    data["current_research_id"] = reader.fstring()
    
    # 返回包含解码后实验室研究报告信息的字典
    return data

# encode函数用于编码一个ArrayProperty类型的属性，该属性包含实验室研究报告的相关信息
# 它接受一个FArchiveWriter对象、属性类型名称以及包含属性数据的字典作为参数
# 并返回编码后的属性大小（字节数）
def encode(
    writer: FArchiveWriter, property_type: str, properties: dict[str, Any]
) -> int:
    # 检查属性类型是否为ArrayProperty，如果不是，则抛出异常
    if property_type != "ArrayProperty":
        raise Exception(f"Expected ArrayProperty, got {property_type}")
    
    # 从属性字典中删除自定义类型字段（如果存在）
    del properties["custom_type"]
    
    # 使用encode_bytes函数编码属性数据中的值部分
    # 得到编码后的字节序列
    encoded_bytes = encode_bytes(properties["value"])
    
    # 将编码后的字节序列转换为列表形式存回属性字典中
    properties["value"] = {"values": [b for b in encoded_bytes]}
    
    # 使用writer对象的property_inner方法编码属性，并返回编码后的大小（字节数）
    return writer.property_inner(property_type, properties)

# encode_bytes函数用于编码一个包含实验室研究报告信息的字典
# 它接受一个可选的字典作为参数（如果为None，则返回一个空字节序列）
# 并返回编码后的字节序列
def encode_bytes(p: Optional[dict[str, Any]]) -> bytes:
    # 如果输入字典为空，则返回一个空字节序列
    if p is None:
        return b""
    
    # 创建一个FArchiveWriter对象，用于将数据编码为字节序列
    writer = FArchiveWriter()
    
    # 使用writer对象的tarray方法和lab_research_rep_info_writer函数
    # 编码实验室研究报告的信息列表
    writer.tarray(lab_research_rep_info_writer, p["research_info"])
    
    # 使用writer对象的fstring方法编码当前研究的ID
    writer.fstring(p["current_research_id"])
    
    # 获取编码后的字节序列
    encoded_bytes = writer.bytes()
    
    # 返回编码后的字节序列
    return encoded_bytes
