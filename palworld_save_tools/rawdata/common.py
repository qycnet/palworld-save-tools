from typing import Any

from palworld_save_tools.archive import Any, FArchiveReader, FArchiveWriter


def pal_item_and_num_read(reader: FArchiveReader) -> dict[str, Any]:
    return {
        "item_id": {
            "static_id": reader.fstring(),
            "dynamic_id": {
                "created_world_id": reader.guid(),
                "local_id_in_created_world": reader.guid(),
            },
        },
        "num": reader.u32(),
    }


def pal_item_and_slot_writer(writer: FArchiveWriter, p: dict[str, Any]) -> None:
    writer.fstring(p["item_id"]["static_id"])
    writer.guid(p["item_id"]["dynamic_id"]["created_world_id"])
    writer.guid(p["item_id"]["dynamic_id"]["local_id_in_created_world"])
    writer.u32(p["num"])


# pal_item_booth_trade_info_read函数用于从FArchiveReader对象中读取交易摊位的信息
# 它返回一个包含产品详情、成本详情以及卖家玩家UID的字典
def pal_item_booth_trade_info_read(reader: FArchiveReader) -> dict[str, Any]:
    return {
        # 产品详情字典
        "product": {
            # 产品的静态ID，使用fstring方法从reader中读取
            "static_id": reader.fstring(),
            # 产品的动态ID字典，包含创建世界的ID和在该世界中的本地ID
            "dynamic_id": {
                "created_world_id": reader.guid(),  # 创建世界的GUID
                "local_id_in_created_world": reader.guid(),  # 在创建世界中的本地ID
            },
            # 产品的数量，使用u32方法从reader中读取
            "num": reader.u32(),
        },
        # 成本详情字典
        "cost": {
            # 成本的静态ID，使用fstring方法从reader中读取
            "static_id": reader.fstring(),
            # 成本的动态ID字典，包含创建世界的ID和在该世界中的本地ID
            "dynamic_id": {
                "created_world_id": reader.guid(),  # 创建世界的GUID
                "local_id_in_created_world": reader.guid(),  # 在创建世界中的本地ID
            },
            # 成本的数量，使用u32方法从reader中读取
            "num": reader.u32(),
        },
        # 卖家玩家的UID，使用guid方法从reader中读取
        "seller_player_uid": reader.guid(),
    }

# pal_item_booth_trade_info_writer函数用于将交易摊位的信息写入FArchiveWriter对象
# 它接受一个包含产品详情、成本详情以及卖家玩家UID的字典作为参数，不返回任何值
def pal_item_booth_trade_info_writer(writer: FArchiveWriter, p: dict[str, Any]) -> None:
    # 写入产品的静态ID
    writer.fstring(p["product"]["static_id"])
    # 写入产品的动态ID，包括创建世界的ID和在该世界中的本地ID
    writer.guid(p["product"]["dynamic_id"]["created_world_id"])
    writer.guid(p["product"]["dynamic_id"]["local_id_in_created_world"])
    # 写入产品的数量
    writer.u32(p["product"]["num"])
    # 写入成本的静态ID
    writer.fstring(p["cost"]["static_id"])
    # 写入成本的动态ID，包括创建世界的ID和在该世界中的本地ID
    writer.guid(p["cost"]["dynamic_id"]["created_world_id"])
    writer.guid(p["cost"]["dynamic_id"]["local_id_in_created_world"])
    # 写入成本的数量
    writer.u32(p["cost"]["num"])
    # 写入卖家玩家的UID
    writer.guid(p["seller_player_uid"])

# pal_pal_booth_trade_info_read函数用于从FArchiveReader对象中读取PAL交易摊位的信息
# 它返回一个包含PAL ID、成本详情以及卖家玩家UID的字典
def pal_pal_booth_trade_info_read(reader: FArchiveReader) -> dict[str, Any]:
    return {
        # PAL ID字典
        "pal_id": {
            # 玩家UID，使用guid方法从reader中读取
            "player_uid": reader.guid(),
            # 实例ID，使用guid方法从reader中读取
            "instance_id": reader.guid(),
            # 调试名称，使用fstring方法从reader中读取
            "debug_name": reader.fstring(),
        },
        # 成本详情字典
        "cost": {
            # 成本的静态ID，使用fstring方法从reader中读取
            "static_id": reader.fstring(),
            # 成本的动态ID字典，包含创建世界的ID和在该世界中的本地ID
            "dynamic_id": {
                "created_world_id": reader.guid(),  # 创建世界的GUID
                "local_id_in_created_world": reader.guid(),  # 在创建世界中的本地ID
            },
            # 成本的数量，使用u32方法从reader中读取
            "num": reader.u32(),
        },
        # 卖家玩家的UID，使用guid方法从reader中读取
        "seller_player_uid": reader.guid(),
    }

# pal_pal_booth_trade_info_writer函数用于将PAL交易摊位的信息写入FArchiveWriter对象
# 它接受一个包含PAL ID、成本详情以及卖家玩家UID的字典作为参数，不返回任何值
def pal_pal_booth_trade_info_writer(writer: FArchiveWriter, p: dict[str, Any]) -> None:
    # 写入PAL ID的玩家UID
    writer.guid(p["pal_id"]["player_uid"])
    # 写入PAL ID的实例ID
    writer.guid(p["pal_id"]["instance_id"])
    # 写入PAL ID的调试名称
    writer.fstring(p["pal_id"]["debug_name"])
    # 写入成本的静态ID
    writer.fstring(p["cost"]["static_id"])
    # 写入成本的动态ID，包括创建世界的ID和在该世界中的本地ID
    writer.guid(p["cost"]["dynamic_id"]["created_world_id"])
    writer.guid(p["cost"]["dynamic_id"]["local_id_in_created_world"])
    # 写入成本的数量
    writer.u32(p["cost"]["num"])
    # 写入卖家玩家的UID
    writer.guid(p["seller_player_uid"])

# lab_research_rep_info_read函数用于从FArchiveReader对象中读取实验室研究报告的信息
# 它返回一个包含研究ID和工作量的字典
def lab_research_rep_info_read(reader: FArchiveReader) -> dict[str, Any]:
    return {
        # 研究ID，使用fstring方法从reader中读取
        "research_id": reader.fstring(),
        # 工作量，使用float方法从reader中读取
        "work_amount": reader.float(),
    }

# lab_research_rep_info_writer函数用于将实验室研究报告的信息写入FArchiveWriter对象
# 它接受一个包含研究ID和工作量的字典作为参数，不返回任何值
def lab_research_rep_info_writer(writer: FArchiveWriter, p: dict[str, Any]) -> None:
    # 写入研究ID
    writer.fstring(p["research_id"])
    # 写入工作量
    writer.float(p["work_amount"])
