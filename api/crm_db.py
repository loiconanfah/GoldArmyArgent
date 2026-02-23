import json
import os
from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db")
CRM_FILE = os.path.join(DB_DIR, "crm_data.json")

class CRMItem(BaseModel):
    id: str
    company: str
    role: str
    status: str  # 'todo', 'applied', 'followup', 'interview'
    date_added: str
    notes: str = ""
    contact_email: str = ""
    match_score: int = 0

def _get_crm_file(user_id: str):
    return os.path.join(DB_DIR, f"crm_data_{user_id}.json")

def _ensure_db(user_id: str):
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    file_path = _get_crm_file(user_id)
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f)

def get_crm_data(user_id: str) -> List[Dict[Any, Any]]:
    _ensure_db(user_id)
    with open(_get_crm_file(user_id), "r", encoding="utf-8") as f:
        return json.load(f)

def save_crm_data(user_id: str, data: List[Dict[Any, Any]]):
    _ensure_db(user_id)
    with open(_get_crm_file(user_id), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def add_crm_item(user_id: str, item: CRMItem) -> CRMItem:
    data = get_crm_data(user_id)
    item_dict = item.model_dump()
    data.append(item_dict)
    save_crm_data(user_id, data)
    return item

def update_crm_item(user_id: str, item_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    data = get_crm_data(user_id)
    for item in data:
        if item["id"] == item_id:
            item.update(updates)
            save_crm_data(user_id, data)
            return item
    return None

def delete_crm_item(user_id: str, item_id: str):
    data = get_crm_data(user_id)
    data = [item for item in data if item["id"] != item_id]
    save_crm_data(user_id, data)
