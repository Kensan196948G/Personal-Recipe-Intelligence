#!/bin/bash

# Read the original file
echo "Reading original file..."
cat /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/test_report_service.py

# Replace with fixed version
echo -e "\n\nReplacing with fixed version..."
cp /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/test_report_service_fixed.py \
   /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/test_report_service.py

echo "File replaced successfully!"

# Cleanup
rm /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/test_report_service_fixed.py
rm /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/fix_test.py

echo "Done!"
