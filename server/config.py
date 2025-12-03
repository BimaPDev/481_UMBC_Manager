import json
import os

CONFIG_FILE = "settings.json"

DEFAULT_CONFIG = {
    "FORM_ID": "17aGxa61B0h_YjCJQAGLu4e0Q9kzLzt4eLzSevoi7M9Q",
    "REF_SHEET_ID": "1QU-OSGOIW1yhGnI6KNyNwJPIj6EAL_AIZDHefVM0I0s",
    "REF_SHEET_TAB": "Form Responses",
    "TEMPLATE_DOC_ID": "1jqfnp7MuszXsgbosCCWWCs8AaZNyDKHa4n1zWthFRCg",
    "OUTPUT_TITLE_PREFIX": "Computer Science 4 Year Plan: ",
    "FOLDER_NAME": "CMSC-447-CS-Preadvising"
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception as e:
            print(f"Error loading config: {e}")
    return DEFAULT_CONFIG

def save_config(new_config):
    try:
        # Merge with existing to ensure we don't lose keys if partial update
        current = load_config()
        updated = {**current, **new_config}
        with open(CONFIG_FILE, "w") as f:
            json.dump(updated, f, indent=2)
        return updated
    except Exception as e:
        print(f"Error saving config: {e}")
        return None
