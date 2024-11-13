#!/usr/bin/env python3
"""
CF Data Generation Script

This script fetches CF standard names, area type tables, and standardized region lists
from the cf-convention GitHub repository and generates JSON-LD files for each entry.

The script:
1. Checks for new versions of CF data
2. Downloads and parses XML files
3. Generates JSON-LD files with proper metadata
4. Validates all generated JSON files
5. Commits changes and creates releases using git utilities
"""

import urllib.request
import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import OrderedDict

# Import CMIP-LD utilities
sys.path.append('/Users/daniel.ellis/WIPwork/CMIP-LD')
from cmipld.utils.git.git_commit_management import addall, commit, push
from cmipld.utils.git.release import newrelease
from cmipld.generate.validate_json import JSONValidator

# Configuration
base = 'src-data/'
GITHUB_OWNER = 'cf-convention'
GITHUB_REPO = 'cf-convention.github.io'


def get_github_directories(owner, repo, path=''):
    """
    Get a list of directories in a specific directory of a GitHub repository using only standard Python libraries.

    Parameters:
    owner (str): Owner of the GitHub repository.
    repo (str): Name of the GitHub repository.
    path (str): Path to the directory in the repository. Default is the root directory.

    Returns:
    list: List of directories in the specified GitHub repository directory.
    """
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
    try:
        with urllib.request.urlopen(url) as response:
            contents = json.loads(response.read().decode())
            directories = [item['name'] for item in contents if item['type'] == 'dir']
            return directories
    except urllib.error.HTTPError as e:
        print(f"HTTP error: {e.code}")
    except urllib.error.URLError as e:
        print(f"URL error: {e.reason}")
    except json.JSONDecodeError as e:
        print("Failed to decode JSON response")
    return []


def xml_to_json(xml_url):
    """
    Fetches an XML file from a URL, parses it, and converts it to JSON.

    Parameters:
    xml_url (str): URL of the XML file.

    Returns:
    str: JSON string representation of the parsed XML data.
    """
    try:
        # Fetch XML content from URL
        with urllib.request.urlopen(xml_url) as response:
            xml_data = response.read()

        # Parse XML content
        root = ET.fromstring(xml_data)

        # Initialize an empty list to store dictionaries (each representing an entry)
        entries = []

        # Iterate through each <entry> element in the XML
        for entry_elem in root.findall('.//entry'):
            entry = {}

            # Extract attributes
            entry['id'] = entry_elem.attrib.get('id', '')

            # Extract child elements
            for child_elem in entry_elem:
                entry[child_elem.tag] = child_elem.text

            # Append entry dictionary to the list
            entries.append(entry)

        # Convert list of dictionaries to JSON string
        json_data = json.dumps(entries, indent=2)
        
        return json_data
    
    except Exception as e:
        print(f"Error: {e}")
        return None


def parse_region_list_xml(xml_url):
    """
    Parse the standardized region list XML which has a different structure.
    
    Parameters:
    xml_url (str): URL of the XML file.
    
    Returns:
    list: List of dictionaries representing the parsed region entries.
    """
    try:
        # Fetch XML content from URL
        with urllib.request.urlopen(xml_url) as response:
            xml_data = response.read()
        
        # Parse XML content
        root = ET.fromstring(xml_data)
        
        # Initialize an empty list to store dictionaries
        entries = []
        
        # Try multiple possible structures based on CF conventions
        
        # Method 1: Look for <region> elements directly
        regions = root.findall('.//region')
        if regions:
            for region_elem in regions:
                entry = {}
                # Get ID from attribute
                if 'id' in region_elem.attrib:
                    entry['id'] = region_elem.attrib['id']
                elif 'name' in region_elem.attrib:
                    entry['id'] = region_elem.attrib['name']
                    entry['name'] = region_elem.attrib['name']
                else:
                    # Use text content as ID if no attributes
                    if region_elem.text and region_elem.text.strip():
                        entry['id'] = region_elem.text.strip().lower().replace(' ', '_')
                        entry['description'] = region_elem.text.strip()
                    else:
                        continue
                
                # Get description from text or child elements
                if region_elem.text and region_elem.text.strip() and 'description' not in entry:
                    entry['description'] = region_elem.text.strip()
                
                # Get any other attributes
                for attr_name, attr_value in region_elem.attrib.items():
                    if attr_name not in entry:
                        entry[attr_name] = attr_value
                
                entries.append(entry)
        
        # Method 2: Look for <standard_region> elements (alternative naming)
        if not entries:
            regions = root.findall('.//standard_region') + root.findall('.//standardized_region')
            for region_elem in regions:
                entry = {'id': region_elem.attrib.get('id', '')}
                if not entry['id'] and region_elem.text:
                    entry['id'] = region_elem.text.strip().lower().replace(' ', '_')
                if entry['id']:
                    entry['description'] = region_elem.text.strip() if region_elem.text else ''
                    entries.append(entry)
        
        # Method 3: Generic approach - find any element with region-related content
        if not entries:
            # Look through all elements for region-like content
            for elem in root.iter():
                if elem.tag in ['region', 'standard_region', 'standardized_region', 'entry']:
                    entry = {}
                    
                    # Try to extract ID
                    if 'id' in elem.attrib:
                        entry['id'] = elem.attrib['id']
                    elif 'name' in elem.attrib:
                        entry['id'] = elem.attrib['name'].lower().replace(' ', '_')
                        entry['name'] = elem.attrib['name']
                    elif elem.text and elem.text.strip():
                        # Use first line of text as ID
                        text = elem.text.strip()
                        entry['id'] = text.split('\n')[0].lower().replace(' ', '_').replace(',', '')
                        entry['description'] = text
                    else:
                        continue
                    
                    # Add all attributes
                    for k, v in elem.attrib.items():
                        if k not in entry:
                            entry[k] = v
                    
                    if entry.get('id'):
                        entries.append(entry)
        
        # Deduplicate by ID
        seen_ids = set()
        unique_entries = []
        for entry in entries:
            if entry['id'] not in seen_ids:
                seen_ids.add(entry['id'])
                unique_entries.append(entry)
        
        return unique_entries
    
    except Exception as e:
        print(f"Error parsing region list XML from {xml_url}: {e}")
        return []


def ensure_directory(path):
    """Ensure a directory exists, create if it doesn't."""
    Path(path).mkdir(parents=True, exist_ok=True)


def validate_generated_files():
    """Validate all generated JSON files."""
    print(f"\n🔍 Validating generated JSON files...")
    
    validator = JSONValidator(base, max_workers=8, dry_run=False)
    success = validator.run()
    
    if success:
        print("✅ All JSON files validated successfully")
    else:
        print("❌ Some JSON files had validation errors")
    
    return success


# Get current version from git tags
current = os.popen("git ls-remote --tags origin | awk '{print $2}' | grep -v '{}' | sort -V | tail -n1").read().strip().split('/v')[-1] or '-1.-1.-1'
current = current.split('.') 

# Process CF Standard Names
directories = get_github_directories(GITHUB_OWNER, GITHUB_REPO, f'Data/cf-standard-names/')
latest = max([int(el) for el in directories if el.isdigit()])

if int(current[0] or -1) < latest:
    print(f"📊 Processing CF Standard Names (version {latest})")
    
    # URL of the XML file
    xml_url = f'https://raw.githubusercontent.com/cf-convention/cf-convention.github.io/main/Data/cf-standard-names/{latest}/src/cf-standard-name-table.xml'

    # Convert XML to JSON
    json_data = json.loads(xml_to_json(xml_url))
    
    ensure_directory(f'{base}standard-name')

    for i in json_data:
        # Store original CF ID
        cf_id = i['id']
        
        # Transform ID: replace _ with -
        transformed_id = cf_id.replace('_', '-')
        
        # Create UI label: replace _ with space and capitalize words
        ui_label = ' '.join(word.capitalize() for word in cf_id.split('_'))
        
        # Build ordered dictionary with correct key order
        out = OrderedDict([
            ("id", f'{transformed_id}'),
            ("validation-key", transformed_id.lower()),
            ("ui-label", ui_label),
            ("description", i["description"]),
        ])
        
        # Add optional fields in alphabetical order
        if i.get("amip"):
            out["amip"] = i["amip"]
        if i.get("canonical_units"):
            out["canonical_units"] = i["canonical_units"]
        out["cf-name"] = cf_id
        if i.get("grib"):
            out["grib"] = i["grib"]
        
        # Add @context and type at the end
        out["@context"] = '_context_'
        out["type"] = ["wcrp:standard-name", 'cf']
        
        with open(f'{base}standard-name/{transformed_id}.json', 'w') as f:
            json.dump(out, f, indent=4, ensure_ascii=False, sort_keys=False)
            f.write('\n')  # Add trailing newline
        
# Process Area Type Tables
directories2 = get_github_directories(GITHUB_OWNER, GITHUB_REPO, f'Data/area-type-table/')
latest2 = max([int(el) for el in directories2 if el.isdigit()])    

if int(current[1] or -1) < latest2:
    print(f"📊 Processing Area Type Tables (version {latest2})")
    
    # URL of the XML file
    xml_url2 = f'https://raw.githubusercontent.com/cf-convention/cf-convention.github.io/main/Data/area-type-table/{latest2}/src/area-type-table.xml'

    # Convert XML to JSON
    json_data2 = json.loads(xml_to_json(xml_url2))
    
    ensure_directory(f'{base}area-type-table')

    for i in json_data2:
        # Store original CF ID
        cf_id = i['id']
        
        # Transform ID: replace _ with -
        transformed_id = cf_id.replace('_', '-')
        
        # Create UI label: replace _ with space and capitalize words
        ui_label = ' '.join(word.capitalize() for word in cf_id.split('_'))
        
        # Build ordered dictionary with correct key order
        out = OrderedDict([
            ("id", f'{transformed_id}'),
            ("validation-key", transformed_id.lower()),
            ("ui-label", ui_label),
            ("description", i["description"]),
            ("cf-name", cf_id),
            ("@context", '_context_'),
            ("type",["wcrp:area-type-table", 'cf']),
        ])
        
        with open(f'{base}area-type-table/{transformed_id}.json', 'w') as f:
            json.dump(out, f, indent=4, ensure_ascii=False, sort_keys=False)
            f.write('\n')  # Add trailing newline

# Process Standardized Region List
# Region list version tracking - use 1 if not tracked before
# latest3 = 1 if len(current) < 3 or int(current[2] or -1) < 0 else int(current[2])
latest3=0
region_dir = f'{base}standardized-region'

# Only process if directory doesn't exist or is empty
if not os.path.exists(region_dir) or len(os.listdir(region_dir)) == 0:
    print(f"📊 Processing Standardized Region List")
    
    # URL of the XML file
    region_url = 'https://raw.githubusercontent.com/cf-convention/cf-convention.github.io/main/Data/standardized-region-list/standardized-region-list.current.xml'
    
    # Parse region list XML
    region_entries = parse_region_list_xml(region_url)
    
    if region_entries:
        ensure_directory(region_dir)
        
        for entry in region_entries:
            # Ensure we have an ID
            cf_id = entry.get('id', '')
            if not cf_id:
                continue
            
            # Transform ID: replace _ with -
            transformed_id = cf_id.replace('_', '-')
            
            # Create UI label: replace _ with space and capitalize words
            ui_label = ' '.join(word.capitalize() for word in cf_id.split('_'))
            
            # Build ordered dictionary with correct key order
            out = OrderedDict([
                ("id", f'{transformed_id}'),
                ("validation-key", transformed_id.lower()),
                ("ui-label", ui_label),
                ("description", entry.get('description', entry.get('name', ''))),
            ])
            
            # Add any additional fields from the XML (in alphabetical order)
            extra_fields = []
            for key, value in entry.items():
                if key not in ['id', 'description', 'name'] and value:
                    extra_fields.append((key, value))
            
            # Sort extra fields and add them
            for key, value in sorted(extra_fields):
                out[key] = value
            
            # Add cf-name
            out["cf-name"] = cf_id
            
            # Add @context and type at the end
            out["@context"] = '_context_'
            out["type"] = ["wcrp:standardized-region", 'cf']
            
            with open(f'{region_dir}/{transformed_id}.json', 'w') as f:
                json.dump(out, f, indent=4, ensure_ascii=False, sort_keys=False)
                f.write('\n')  # Add trailing newline
        
        latest3 += 1  # Increment region version

# Create new tag with all three versions
tag = f'{latest}.{latest2}.{latest3}'
current_tag = '.'.join(current)

if tag != current_tag:
    # Validate all generated files before committing
    if not validate_generated_files():
        print("\n❌ Validation failed, aborting commit")
        sys.exit(1)
    
    
    print('FUNCTION LIKE UPDATEALL HERE')
    # print(os.popen('update_all').read())
    
    # Push to git using CMIP-LD utilities
    addall()
    commit(f'Update to standard-names v{latest}, area-type-table v{latest2}, and regions v{latest3}')
    
    # Create and push tag
    os.popen(f'git tag -a "v{tag}" -m "Version v{tag}"').read()
    os.popen(f'git push origin "v{tag}"').read()
    
    # Create GitHub release
    release_title = f"standard-names {latest}, area-type-table {latest2}, regions {latest3}"
    release_notes = f"Automated update on new release"
    
    # Get repository info
    try:
        import subprocess
        remote_url = subprocess.check_output(['git', 'remote', 'get-url', 'origin']).decode().strip()
        if 'github.com' in remote_url:
            if remote_url.startswith('https://'):
                parts = remote_url.replace('https://github.com/', '').replace('.git', '').split('/')
            else:
                parts = remote_url.replace('git@github.com:', '').replace('.git', '').split('/')
            
            if len(parts) >= 2:
                repo_owner, repo_name = parts[0], parts[1]
            else:
                repo_owner, repo_name = 'WCRP-CMIP', 'CF'
        else:
            repo_owner, repo_name = 'WCRP-CMIP', 'CF'
    except:
        repo_owner, repo_name = 'WCRP-CMIP', 'CF'
    
    newrelease(repo_owner, repo_name, f"v{tag}", release_notes, release_title)
    
    # Push to main
    push('main')
    
    print(f"✅ Successfully created release v{tag}")
else:
    print(f"✅ Everything is up to date (version {current_tag})")