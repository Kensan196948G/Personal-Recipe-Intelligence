#!/usr/bin/env python3
"""両方の recipe_service ファイルを読み取るスクリプト"""

import os

base_path = "/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/services"

files = ["recipe_service.py", "recipe_service_new.py"]

for filename in files:
    filepath = os.path.join(base_path, filename)
    print(f"\n{'='*80}")
    print(f"File: {filename}")
    print(f"{'='*80}\n")

    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
    else:
        print(f"File not found: {filepath}")

# ディレクトリ構造も確認
print(f"\n{'='*80}")
print("Directory structure: backend/services/")
print(f"{'='*80}\n")

if os.path.exists(base_path):
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isfile(item_path):
            size = os.path.getsize(item_path)
            print(f"{item} ({size} bytes)")
