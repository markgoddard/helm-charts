#!/usr/bin/env python3

from ruamel.yaml import YAML
from pathlib import Path
import sys

# Initialize YAML processor with better formatting
yaml = YAML()
yaml.preserve_quotes = True  # Match double quotes used by cr/helm
yaml.width = 80  # Match line wrapping of cr/helm
yaml.default_flow_style = False

# Start with current index or empty structure
try:
    with open('index.yaml', 'r') as f:
        merged = yaml.load(f) or {}
except FileNotFoundError:
    merged = {'apiVersion': 'v1', 'entries': {}}

# Ensure entries dict exists
if 'entries' not in merged:
    merged['entries'] = {}

# Merge each remote index
for index_file in Path('temp-indexes').glob('*-index.yaml'):
    try:
        with open(index_file, 'r') as f:
            remote_index = yaml.load(f)

        if remote_index and 'entries' in remote_index:
            for chart_name, versions in remote_index['entries'].items():
                if chart_name not in merged['entries']:
                    merged['entries'][chart_name] = []

                # Add versions, avoiding duplicates
                existing_versions = {v.get('version'): v for v in merged['entries'][chart_name]}

                for version in versions:
                    version_num = version.get('version')
                    if version_num not in existing_versions:
                        merged['entries'][chart_name].append(version)
    except Exception as e:
        print(f"Error processing {index_file}: {e}")

# Sort versions for each chart (newest first)
for chart_name in merged['entries']:
    merged['entries'][chart_name].sort(
        key=lambda x: x.get('created', ''),
        reverse=True
    )

# Write merged index preserving original formatting
with open('index.yaml', 'w') as f:
    yaml.dump(merged, f)
