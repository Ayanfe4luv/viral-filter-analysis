import ast
import json
import os

def extract_translations():
    with open("fasta_analysis_app_final.py", "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if getattr(target, 'id', None) == 'TRANSLATIONS':
                    val = ast.literal_eval(node.value)
                    
                    en_path = "assets/translations/en.json"
                    ru_path = "assets/translations/ru.json"
                    
                    # Merge with existing v2.1 keys if they exist
                    existing_en = {}
                    if os.path.exists(en_path):
                        with open(en_path, "r", encoding="utf-8") as f:
                            existing_en = json.load(f)
                            
                    existing_ru = {}
                    if os.path.exists(ru_path):
                        with open(ru_path, "r", encoding="utf-8") as f:
                            existing_ru = json.load(f)
                    
                    # Legacy keys take a backseat to our new V2.1 keys if overlapping
                    merged_en = {**val["en"], **existing_en}
                    merged_ru = {**val["ru"], **existing_ru}
                    
                    os.makedirs("assets/translations", exist_ok=True)
                    
                    with open(en_path, "w", encoding="utf-8") as out:
                        json.dump(merged_en, out, indent=2, ensure_ascii=False)
                    with open(ru_path, "w", encoding="utf-8") as out:
                        json.dump(merged_ru, out, indent=2, ensure_ascii=False)
                        
                    print("Translations successfully merged and saved to JSON files.")
                    return

if __name__ == "__main__":
    extract_translations()
