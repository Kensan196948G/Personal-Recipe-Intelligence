#!/usr/bin/env python3
"""プロジェクトファイルを読み取って表示"""
import os

base = "/mnt/Linux-ExHDD/Personal-Recipe-Intelligence"

# backend ディレクトリを確認
backend_services = os.path.join(base, "backend", "services")

print("=" * 100)
print("PROJECT SCAN RESULTS")
print("=" * 100)

# ディレクトリ存在確認
print(f"\n1. Directory Check:")
print(f"   backend/services exists: {os.path.exists(backend_services)}")

if os.path.exists(backend_services):
    print(f"\n2. Files in backend/services:")
    try:
        files = os.listdir(backend_services)
        for f in sorted(files):
            fpath = os.path.join(backend_services, f)
            if os.path.isfile(fpath):
                size = os.path.getsize(fpath)
                print(f"   - {f} ({size:,} bytes)")
    except Exception as e:
        print(f"   Error: {e}")

# recipe_service.py を読み取り
print(f"\n3. Content of recipe_service.py:")
print("=" * 100)
recipe_service_path = os.path.join(backend_services, "recipe_service.py")
if os.path.exists(recipe_service_path):
    try:
        with open(recipe_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content[:2000])  # 最初の2000文字
            if len(content) > 2000:
                print(f"\n... (total {len(content)} characters)")
    except Exception as e:
        print(f"Error reading: {e}")
else:
    print("FILE NOT FOUND")

# recipe_service_new.py を読み取り
print(f"\n4. Content of recipe_service_new.py:")
print("=" * 100)
recipe_service_new_path = os.path.join(backend_services, "recipe_service_new.py")
if os.path.exists(recipe_service_new_path):
    try:
        with open(recipe_service_new_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content[:2000])  # 最初の2000文字
            if len(content) > 2000:
                print(f"\n... (total {len(content)} characters)")
    except Exception as e:
        print(f"Error reading: {e}")
else:
    print("FILE NOT FOUND")

# backend全体の構造
print(f"\n5. Backend Structure:")
print("=" * 100)
backend_path = os.path.join(base, "backend")
if os.path.exists(backend_path):
    for root, dirs, files in os.walk(backend_path):
        level = root.replace(backend_path, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 2 * (level + 1)
        for file in files:
            if not file.startswith('.'):
                print(f"{sub_indent}{file}")
