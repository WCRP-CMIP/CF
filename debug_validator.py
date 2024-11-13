#!/usr/bin/env python3
"""Debug script to understand why validator isn't detecting wrong order"""

import json
from collections import OrderedDict
from pathlib import Path

# Test with a sample file
test_file = "/Users/daniel.ellis/WIPwork/CF/src-data/area-type-table/ice-free-land.json"

# Read the file
with open(test_file, 'r', encoding='utf-8') as f:
    content = f.read().strip()

# Load JSON preserving order
data = json.loads(content, object_pairs_hook=OrderedDict)

print("Original data keys:", list(data.keys()))

# Sort according to validator rules
sorted_data = OrderedDict()

# Priority keys in order
priority_keys = ['id', 'validation-key', 'ui-label', 'description']
for key in priority_keys:
    if key in data:
        sorted_data[key] = data[key]

# Other keys alphabetically
remaining_keys = sorted([
    k for k in data.keys() 
    if k not in priority_keys and k not in ['@context', 'type']
])
for key in remaining_keys:
    sorted_data[key] = data[key]

# @context and type at the end
if '@context' in data:
    sorted_data['@context'] = data['@context']
if 'type' in data:
    sorted_data['type'] = data['type']

print("Sorted data keys:", list(sorted_data.keys()))

# Compare
print("\nComparison:")
print("data.keys() == sorted_data.keys():", list(data.keys()) == list(sorted_data.keys()))
print("Are they the same?", data.keys() == sorted_data.keys())

# Let's check each key
for i, (k1, k2) in enumerate(zip(data.keys(), sorted_data.keys())):
    print(f"  Position {i}: '{k1}' vs '{k2}' - {'✓' if k1 == k2 else '✗'}")
