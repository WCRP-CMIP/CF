#!/usr/bin/env python3
"""Direct test of the validator logic on a single file"""

import json
from collections import OrderedDict
from pathlib import Path

# Read an actual file
file_path = Path("/Users/daniel.ellis/WIPwork/CF/src-data/area-type-table/ice-free-land.json")

# Read the JSON file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read().strip()

print("Original content:")
print(content)
print("\n" + "="*60 + "\n")

# Load JSON as OrderedDict to preserve order
data = json.loads(content, object_pairs_hook=OrderedDict)

# Sort keys according to specification
sorted_data = OrderedDict()

# Standard key order for all files
priority_keys = ['id', 'validation-key', 'ui-label', 'description']
for key in priority_keys:
    if key in data:
        sorted_data[key] = data[key]

# Then add remaining keys alphabetically (excluding @context and type)
remaining_keys = sorted([
    k for k in data.keys() 
    if k not in priority_keys and k not in ['@context', 'type']
])
for key in remaining_keys:
    sorted_data[key] = data[key]

# Finally add @context and type at the end
if '@context' in data:
    sorted_data['@context'] = data['@context']
if 'type' in data:
    sorted_data['type'] = data['type']

# Generate expected content
expected_content = json.dumps(sorted_data, indent=4, ensure_ascii=False, sort_keys=False) + '\n'

print("Expected content:")
print(expected_content)
print("\n" + "="*60 + "\n")

# Compare
print("Content comparison:")
print(f"Original length: {len(content)}")
print(f"Expected length: {len(expected_content)}")
print(f"Are they equal? {content == expected_content}")

# Character by character comparison
if content != expected_content:
    print("\nFinding differences:")
    for i, (c1, c2) in enumerate(zip(content, expected_content)):
        if c1 != c2:
            print(f"First difference at position {i}: '{c1}' vs '{c2}'")
            print(f"Context: ...{content[max(0,i-20):i+20]}...")
            break

# Check the key order
print("\nKey order:")
print(f"Original: {list(data.keys())}")
print(f"Expected: {list(sorted_data.keys())}")
