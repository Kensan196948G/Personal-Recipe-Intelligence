#!/bin/bash
# Explore project structure

echo "=== Root Directory ==="
ls -la /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/

echo -e "\n=== Backend Structure ==="
find /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend -type f -name "*.py" 2>/dev/null | head -50

echo -e "\n=== Frontend Structure ==="
find /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/frontend -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" \) 2>/dev/null | head -50

echo -e "\n=== Test Files ==="
find /mnt/Linux-ExHDD/Personal-Recipe-Intelligence -type f -name "*test*.py" -o -name "*test*.js" 2>/dev/null

echo -e "\n=== Config Files ==="
ls -la /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/*.json 2>/dev/null
ls -la /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/*.toml 2>/dev/null
ls -la /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/pytest.ini 2>/dev/null
