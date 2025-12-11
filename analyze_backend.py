#!/usr/bin/env python3
"""Backend ディレクトリの構造を分析"""

import os
import sys

def analyze_directory(path, prefix="", max_depth=3, current_depth=0):
    """ディレクトリ構造を再帰的に表示"""
    if current_depth >= max_depth:
        return

    try:
        items = sorted(os.listdir(path))
        for item in items:
            if item.startswith('.'):
                continue

            item_path = os.path.join(path, item)

            if os.path.isdir(item_path):
                print(f"{prefix}📁 {item}/")
                analyze_directory(item_path, prefix + "  ", max_depth, current_depth + 1)
            else:
                size = os.path.getsize(item_path)
                print(f"{prefix}📄 {item} ({size} bytes)")
    except PermissionError:
        print(f"{prefix}[Permission Denied]")

# Main
backend_path = "/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend"

if os.path.exists(backend_path):
    print("Backend Directory Structure:")
    print("="*80)
    analyze_directory(backend_path)
else:
    print(f"Backend directory not found: {backend_path}")

# Check specific files
print("\n" + "="*80)
print("Checking recipe_service files:")
print("="*80)

services_path = os.path.join(backend_path, "services")
if os.path.exists(services_path):
    for filename in ["recipe_service.py", "recipe_service_new.py"]:
        filepath = os.path.join(services_path, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"\n{filename}: {len(lines)} lines")
                print("-"*80)
                # 最初の50行を表示
                for i, line in enumerate(lines[:50], 1):
                    print(f"{i:4d} | {line.rstrip()}")
                if len(lines) > 50:
                    print(f"... ({len(lines) - 50} more lines)")
        else:
            print(f"\n{filename}: NOT FOUND")
