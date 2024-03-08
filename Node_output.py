import subprocess
import requests
from bs4 import BeautifulSoup
import json
import base64  # Add this import statement for base64
from datetime import datetime
import os
import re

def parse_time_diff(time_diff_str):
    time_pattern = re.compile(r'(\d+(\.\d+)?)([mµ]s|s)?')
    match = time_pattern.match(time_diff_str)
    if match:
        value = float(match.group(1))
        unit = match.group(3)
        if unit == 's':
            value *= 1000
        return value
    else:
        return None

def update_json_file(data):
    # GitHub repository information
    owner = "obi-wan-xenobi"
    repo = "Node-Ranking"
    branch = "main"
    filename = "nodes_data.json"
    
    # Personal Access Token (PAT)
    token = os.environ.get("GITHUB_PAT")  # Access the PAT stored as environment variable
    
    # GitHub API URL for updating file content
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filename}"
    
    # Compose the request headers
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Fetch the current content of the JSON file
    response = requests.get(url, headers=headers)
    response_json = response.json()

    print("Response JSON:", response_json)  # Debug print statement
    
    if "content" not in response_json:
        print("Error: No content found in the API response.")
        return
    
    content = response_json["content"]
    
    if not content:
        print("Error: Empty content received from the API response.")
        return
    
    try:
        import base64
        current_content = json.loads(base64.b64decode(content).decode("utf-8"))
    except json.decoder.JSONDecodeError as e:
        print(f"Error decoding JSON content: {e}")
        return

    # Merge the new data with the existing content
    current_content.extend(data)
    
    # Add timestamp to the data
    timestamp = datetime.now().isoformat()
    current_content.append({"Last Updated": timestamp})  # Add timestamp field
    
    # Encode the updated content to JSON
    updated_content = json.dumps(current_content, indent=4)
    
    # Compose the request payload
    payload = {
        "message": "Update JSON file",
        "content": updated_content,
        "branch": branch,
        "sha": response_json["sha"]
    }
    
    # Make a PUT request to update the file
    response = requests.put(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("JSON file updated successfully.")
    else:
        print(f"Failed to update JSON file. Status code: {response.status_code}")


def main():
    url = "http://186.233.186.56:5002/nodes"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table")
        nodes_data = []
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            node_ip = cells[0].text
            block_id = int(cells[1].text)
            tx_hash = cells[2].text
            time_diff_str = cells[3].text
            time_diff = parse_time_diff(time_diff_str)
            if time_diff is not None:
                nodes_data.append({"Node IP": node_ip, "Block ID": block_id, "Time Diff": time_diff})
        sorted_nodes = sorted(nodes_data, key=lambda x: (-x["Block ID"], x["Time Diff"]))
        top_50_nodes = sorted_nodes[:50]
        xenobi_ranking = None
        for i, node in enumerate(top_50_nodes, start=1):
            if node["Node IP"].startswith("74.50.77"):
                xenobi_ranking = i
                break
        if xenobi_ranking is not None:
            top_50_nodes.append({"Xenobi Ranking": xenobi_ranking})
        update_json_file(top_50_nodes)
    except requests.RequestException as e:
        print(f"Error retrieving data from website: {e}")

def has_changes_to_commit():
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    return bool(result.stdout.strip())

if __name__ == "__main__":
    main()
    if has_changes_to_commit():
        subprocess.run(["git", "config", "user.name", "obi-wan-xenobi"])
        subprocess.run(["git", "config", "user.email", "obiwanxenobi@gmail.com"])
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "Update data"])
        subprocess.run(["git", "push"])
        print("Changes committed successfully.")
    else:
        print("No changes to commit.")
