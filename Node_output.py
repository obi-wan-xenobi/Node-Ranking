import subprocess
import json
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import re
import os

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
    filename = "nodes_data.json"
    
    with open(filename, "r") as file:
        current_content = json.load(file)

    current_content.extend(data)
    
    timestamp = datetime.now().isoformat()
    current_content.append({"Last Updated": timestamp})
    
    with open(filename, "w") as file:
        json.dump(current_content, file, indent=4)

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
        owner = "obi-wan-xenobi"
        repo = "Node-Ranking"
        branch = "main"
        filename = "nodes_data.json"
        token = os.environ.get("GITHUB_PAT")  # Access the PAT stored as environment variable
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filename}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        with open(filename, "r") as file:
            content = file.read()
        response = requests.get(url, headers=headers)
        response_json = response.json()
        if "content" not in response_json:
            print("Error: No content found in the API response.")
        else:
            sha = response_json["sha"]
            payload = {
                "message": "Update JSON file",
                "content": content,
                "branch": branch,
                "sha": sha
            }
            response = requests.put(url, headers=headers, json=payload)
            if response.status_code == 200:
                print("JSON file updated successfully.")
            else:
                print(f"Failed to update JSON file. Status code: {response.status_code}")
    else:
        print("No changes to commit.")
