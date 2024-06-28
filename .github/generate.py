import urllib.request
import json,os,sys

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

# Example usage
owner = 'octocat'  # Replace with the repository owner
repo = 'Hello-World'  # Replace with the repository name
path = ''  # Replace with the path to the directory you want to inspect, or leave empty for the root

directories = get_github_directories('cf-convention', 'cf-convention.github.io', 'Data/cf-standard-names/')
print("Directories:", directories)
latest = max([int(el) for el in directories if el.isdigit()])

current = int(os.popen("git ls-remote --tags origin | awk '{print $2}' | grep -v '{}' | sort -V | tail -n1").strip().split('/v')[-1])

print(current, latest)

if current >= latest:
    sys.exit("No new version available")





# https://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml
# https://raw.githubusercontent.com/cf-convention/cf-convention.github.io/main/Data/cf-standard-names/85/src/cf-standard-name-table.xml