import urllib.request
import json,os,sys
import xml.etree.ElementTree as ET


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


current = os.popen("git ls-remote --tags origin | awk '{print $2}' | grep -v '{}' | sort -V | tail -n1").read().strip().split('/v')[-1] or '-1.-1'
current = current.split('.') 


# 'cf-standard-names'


directories = get_github_directories('cf-convention', 'cf-convention.github.io', f'Data/cf-standard-names/')

# print("Directories:", directories)
latest = max([int(el) for el in directories if el.isdigit()])


if int(current[0] or -1) < latest:
    # sys.exit('No new version available')

    # URL of the XML file
    xml_url = f'https://raw.githubusercontent.com/cf-convention/cf-convention.github.io/main/Data/cf-standard-names/{latest}/src/cf-standard-name-table.xml'

    # Convert XML to JSON
    json_data = json.loads(xml_to_json(xml_url))

    for i in json_data:
        
        out = {
            "@id":f'cf:standard_name/{i["id"]}',
            "@type": "standard-name",
            "name": i["id"],
            "description": i["description"],
            "canonical_units": i.get("canonical_units", None),
            "amip": i.get("amip", None),
            "grib": i.get("grib", None),            
        }
        
        json.dump(out,open(f'standard-name/{i["id"]}.json', 'w'), indent=2)
        
directories2 = get_github_directories('cf-convention', 'cf-convention.github.io', f'Data/area-type-table/')

# print("Directories:", directories)
latest2 = max([int(el) for el in directories2 if el.isdigit()])    

if int(current[1] or -1) < latest2:
    # sys.exit('No new version available')

    # URL of the XML file
    xml_url2 = f'https://raw.githubusercontent.com/cf-convention/cf-convention.github.io/main/Data/area-type-table/{latest2}/src/area-type-table.xml'

    # Convert XML to JSON
    json_data2 = json.loads(xml_to_json(xml_url2))

    for i in json_data2:
        
        out = {
            "@id":f'cf:area-type-table/{i["id"]}',
            "@type": "area-type-table",
            "name": i["id"],
            "description": i["description"],   
        }
        
        json.dump(out,open(f'area-type-table/{i["id"]}.json', 'w'), indent=2)
        

tag = f'{latest}.{latest2}'
if tag != current:
    
    
    print(os.popen("mkdir -p compiled; updateld --exclude-dirs='compiled' --override --base-dir='./' --type-prefix='cf'").read())

    print(os.popen('combine-graphs compiled/graph_data . graph ./scripts').read())
    
    
    
    # push to git 
    add = os.popen('git add .').read()
    commit =os.popen(f'git commit -m "Update to standard-names v{latest} and area-type-table v{latest2}"').read()
    tag = os.popen(f'git tag -a "v{tag}" -m "Version v{tag}"').read()
    push = os.popen(f'git push origin "v{tag}"').read()
    
    print(add, commit, tag, push)
    
    release = f'gh release create "v{tag}" -n "Automated update on new release" -t "standard-names {latest}, area-type-table {latest2}"'
    print(os.popen(release).read())
    
    os.popen('git push origin main').read()

# https://github.com/cf-convention/cf-convention.github.io/blob/main/Data/area-type-table/2/src/area-type-table.xml

# https://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml
# https://raw.githubusercontent.com/cf-convention/cf-convention.github.io/main/Data/cf-standard-names/85/src/cf-standard-name-table.xml