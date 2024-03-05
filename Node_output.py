import csv
import requests
from bs4 import BeautifulSoup

# Send a GET request to the website
url = "http://186.233.186.56:5002/nodes"
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find the table containing the nodes information
    table = soup.find("table")
    
    # Initialize a list to store nodes data
    nodes_data = []
    
    # Iterate over each row in the table
    for row in table.find_all("tr")[1:]:
        # Extract data from each cell in the row
        cells = row.find_all("td")
        node_ip = cells[0].text
        block_id = int(cells[1].text)
        tx_hash = cells[2].text
        time_diff_str = cells[3].text
        time_diff = float(time_diff_str.replace("ms", "").replace("s", "").replace("µ", ""))  # Convert µs to ms directly
        timestamp = cells[4].text
        
        nodes_data.append((node_ip, block_id, time_diff))
    
    # Sort the nodes based on their block ID and time differences
    sorted_nodes = sorted(nodes_data, key=lambda x: (-x[1], x[2]))
    
    # Get the top 50 nodes with the highest block ID and lowest time differences
    top_50_nodes = sorted_nodes[:50]
    
    # Calculate the Xenobi ranking
    xenobi_ranking = None
    for i, (node_ip, _, _) in enumerate(top_50_nodes, start=1):
        if node_ip.startswith("74.50.77"):
            xenobi_ranking = i
            break
    
    # Write data to CSV file
    with open("nodes_data.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Rank", "Node IP", "Block ID", "Time Diff for Last Block (ms)"])
        for i, (node_ip, block_id, time_diff) in enumerate(top_50_nodes, start=1):
            writer.writerow([i, node_ip, block_id, time_diff])
        
        # Write Xenobi ranking
        if xenobi_ranking is not None:
            writer.writerow(["Xenobi Ranking", xenobi_ranking])
    
    print("Data has been written to nodes_data.csv file.")
else:
    print("Failed to retrieve data from the website.")
