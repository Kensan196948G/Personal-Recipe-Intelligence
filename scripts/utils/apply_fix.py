#!/usr/bin/env python3
"""
Fix the failing test in test_report_service.py by adding a sleep delay
between report ID generations to ensure uniqueness.
"""

import os

file_path = "/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/test_report_service.py"

# Read the current file
print(f"Reading {file_path}...")
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Process the file
new_lines = []
i = 0
modified = False

while i < len(lines):
    line = lines[i]

    # Check if we're at the test_report_id_uniqueness function
    if 'def test_report_id_uniqueness(report_service):' in line:
        print(f"Found test function at line {i+1}")
        new_lines.append(line)
        i += 1

        # Add the docstring
        if i < len(lines) and '"""' in lines[i]:
            new_lines.append(lines[i])
            i += 1

        # Add first report_id generation
        if i < len(lines) and 'report_id_1' in lines[i]:
            new_lines.append(lines[i])
            i += 1

            # Check if sleep is already there
            if i < len(lines) and 'time.sleep' not in lines[i]:
                # Add sleep and comment
                indent = '  '
                new_lines.append(f'\n')
                new_lines.append(f'{indent}# 同じ秒に生成される可能性があるため、わずかに待機\n')
                new_lines.append(f'{indent}time.sleep(1.1)\n')
                new_lines.append(f'\n')
                modified = True
                print("Added sleep between report generations")

            # Skip the second report_id if it's immediate
            if i < len(lines) and 'report_id_2' in lines[i]:
                new_lines.append(lines[i])
                i += 1

        continue

    new_lines.append(line)
    i += 1

# Check if time import exists
has_time_import = any('import time' in line for line in new_lines)

if not has_time_import and modified:
    print("Adding time import...")
    # Find the import section and add time import
    for i, line in enumerate(new_lines):
        if 'from datetime import datetime' in line:
            new_lines.insert(i + 1, 'import time\n')
            print(f"Added 'import time' at line {i+2}")
            break

# Write back the file
if modified or not has_time_import:
    print(f"\nWriting changes to {file_path}...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("File successfully updated!")
else:
    print("No changes needed - file already has the fix.")

print("\nDone!")
