# app/services/export.py
import json
from io import StringIO
from datetime import datetime, date

class ExportService:
    DEFAULT_FIELDS = {
        "trends": ["id", "industry_id", "name"],
        "posts": [
            "id", "group_id", "industry_id", "message_id", "text", 
            "posted_at", "cleaned_text", "normalized_text", "embedding" # Добавили сюда
        ],
        "industries": ["id", "name"],
        "groups": ["id", "vk_id", "title"]
    }

    @staticmethod
    def prepare_row(item, fields):
        row = {}
        for field in fields:
            val = getattr(item, field, None)
            
            if isinstance(val, (datetime, date)):
                val = val.isoformat()
            elif hasattr(val, "to_list"): 
                val = val.to_list()
            
            row[field] = val
        return row

    @staticmethod
    def to_sql(data, table_name):
        if not data: return "-- No data"
        
        columns = list(data[0].keys())
        lines = [f"-- Export {table_name}"]
        
        for row in data:
            values = []
            for col in columns:
                v = row[col]
                if v is None: values.append("NULL")
                elif isinstance(v, str): 
                    values.append("'" + v.replace("'", "''") + "'")
                else: values.append(str(v))
            
            lines.append(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});")
        return "\n".join(lines)

