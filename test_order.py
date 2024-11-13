#!/usr/bin/env python3
"""Test why JSON validator isn't detecting order issues"""

import json
from collections import OrderedDict

# Sample JSON content from the file
content = '''{
  "@context": "_context_",
  "id": "area-type-table/ice-free-land",
  "type": [
    "area-type-table",
    "cf"
  ],
  "validation-key": "ice-free-land",
  "ui-label": "Ice Free Land",
  "cf-name": "ice_free_land",
  "description": null
}'''

# Load as OrderedDict
data = json.loads(content, object_pairs_hook=OrderedDict)
print("Original order:", list(data.keys()))

# Create sorted version
sorted_data = OrderedDict()

# Priority keys
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

# @context and type at end
if '@context' in data:
    sorted_data['@context'] = data['@context']
if 'type' in data:
    sorted_data['type'] = data['type']

print("Expected order:", list(sorted_data.keys()))

# Test comparisons
print("\nComparisons:")
print(f"list(data.keys()): {list(data.keys())}")
print(f"list(sorted_data.keys()): {list(sorted_data.keys())}")
print(f"Are lists equal? {list(data.keys()) == list(sorted_data.keys())}")

# The issue: let's see what happens with the actual comparison
original_keys = list(data.keys())
sorted_keys = list(sorted_data.keys())

print(f"\nDirect comparison: {original_keys} != {sorted_keys}")
print(f"Result: {original_keys != sorted_keys}")
