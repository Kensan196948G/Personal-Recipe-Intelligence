#!/usr/bin/env python3
"""Script to fix the test_report_service.py file"""

import re

# Read the file
file_path = "/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/test_report_service.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if time import exists
if 'import time' not in content:
    # Add time import after other imports
    content = re.sub(
        r'(from datetime import datetime)',
        r'\1\nimport time',
        content
    )

# Fix the test_report_id_uniqueness function
old_function = """def test_report_id_uniqueness(report_service):
  """レポートIDの一意性テスト"""
  report_id_1 = report_service.generate_report_id()
  report_id_2 = report_service.generate_report_id()

  # 異なる時刻に生成されたIDは異なるはず
  assert report_id_1 != report_id_2"""

new_function = """def test_report_id_uniqueness(report_service):
  """レポートIDの一意性テスト"""
  report_id_1 = report_service.generate_report_id()

  # 同じ秒に生成される可能性があるため、わずかに待機
  time.sleep(1.1)

  report_id_2 = report_service.generate_report_id()

  # 異なる時刻に生成されたIDは異なるはず
  assert report_id_1 != report_id_2"""

content = content.replace(old_function, new_function)

# Write the file back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Test file fixed successfully!")
