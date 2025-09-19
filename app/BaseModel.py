from sqlalchemy.orm import validates, declarative_mixin
from sqlalchemy.inspection import inspect
from datetime import datetime, date

@declarative_mixin
class BaseModel:
    """提供共用驗證邏輯，其他 Model 繼承即可"""

    @validates("*")  # ✅ "*" 表示驗證所有欄位
    def _normalize(self, key, value):
        # 通用處理：空字串 → None
        
        if value == "":
            return None

        # 找到該欄位的型別
        column = inspect(self.__class__).columns.get(key)
        if column is None:
            return value  # 找不到就跳過

        column_type = column.type.__class__.__name__

        # 日期欄位
        if column_type == "Date":
            if isinstance(value, str):
                return datetime.strptime(value, "%Y-%m-%d").date()
            if isinstance(value, date) or value is None:
                return value
            raise ValueError(f"{key} 必須是 date 或 YYYY-MM-DD 字串")

        # 日期時間欄位
        if column_type == "DateTime":
            if isinstance(value, str):
                return datetime.fromisoformat(value)
            if isinstance(value, datetime) or value is None:
                return value
            raise ValueError(f"{key} 必須是 datetime 或 ISO 格式字串")

        return value
