#!/usr/bin/env python3
"""Fix JSON file ordering in CF data"""

import json
import os
from collections import OrderedDict
from pathlib import Path

def fix_json_order(file_path):
    """Fix the key order in a JSON file to match validator expectations"""
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Build ordered dictionary with correct key order
    ordered = OrderedDict()
    
    # Priority keys in order
    priority_keys = ['id', 'validation-key', 'ui-label', 'description']
    for key in priority_keys:
        if key in data:
            ordered[key] = data[key]
    
    # Other keys alphabetically (excluding @context and type)
    other_keys = sorted([k for k in data.keys() 
                        if k not in priority_keys and k not in ['@context', 'type']])
    for key in other_keys:
        ordered[key] = data[key]
    
    # @context and type at the end
    if '@context' in data:
        ordered['@context'] = data['@context']
    if 'type' in data:
        ordered['type'] = data['type']
    
    # Write back with correct formatting
    with open(file_path, 'w') as f:
        json.dump(ordered, f, indent=4, ensure_ascii=False, sort_keys=False)
        f.write('\n')

def main():
    """Fix all JSON files in src-data"""
    base_dir = 'src-data'
    
    # Find all JSON files
    json_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    
    print(f"Found {len(json_files)} JSON files to fix")
    
    # Fix each file
    fixed_count = 0
    for file_path in json_files:
        try:
            fix_json_order(file_path)
            fixed_count += 1
            if fixed_count % 100 == 0:
                print(f"Fixed {fixed_count} files...")
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
    
    print(f"\n✅ Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
