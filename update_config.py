import os
import subprocess
from github import Github

# Get the GitHub token from the environment
token = os.getenv('GH_TOKEN')

# Initialize the GitHub client
g = Github(token)

# The repository where the config.yml needs to be updated
repo = g.get_repo("data-8/fa24")

# Fetch the latest changes with a depth of 2 to ensure we have the previous commit
try:
    subprocess.run(["git", "fetch", "--depth", "2"], check=True)
    # Get the hash of the second last commit
    previous_commit = subprocess.check_output(["git", "log", "--format=%H", "-n", "2"]).decode('utf-8').split()[1]
    print(f"Previous commit hash: {previous_commit}")
except subprocess.CalledProcessError as e:
    print(f"Error fetching the full history or getting the previous commit: {e.output.decode('utf-8')}")
    exit(1)

# Get the changed files compared to the previous commit
try:
    output = subprocess.check_output(["git", "diff", "--name-only", previous_commit, "HEAD"])
    changed_files = output.decode("utf-8").splitlines()
    print(f"Changed files: {changed_files}")
except subprocess.CalledProcessError as e:
    print(f"Error getting changed files: {e.output.decode('utf-8')}")
    exit(1)

# Define the base URL
base_url = "https://data8.datahub.berkeley.edu/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Fdata-8%2Fmaterials-fa24&branch=main&urlpath=tree%2Fmaterials-fa24%2F{parent_directory}%2F{sub_directory}%2F{sub_directory}.ipynb&branch=main"

# Find new directories
new_dirs = set()
for file in changed_files:
    parts = file.split('/')
    print(f"Checking file: {file}, parts: {parts}")
    if parts[0] in ["hw", "lab", "proj"] and len(parts) > 1:
        new_dirs.add((parts[0], parts[1]))

if not new_dirs:
    print("No new directories found.")
    exit(0)

print(f"New directories detected: {new_dirs}")

# Clone the fa24 repository
try:
    subprocess.run(["git", "clone", f"https://{token}@github.com/data-8/fa24.git"], check=True)
    os.chdir("fa24")
except subprocess.CalledProcessError as e:
    print(f"Error cloning repository: {e.output.decode('utf-8')}")
    exit(1)

# Read the current config.yml file
try:
    with open("_config.yml", "r") as f:
        lines = f.readlines()
    print(f"Read _config.yml")
except FileNotFoundError:
    print("_config.yml file not found.")
    exit(1)

# Update the config.yml file
for parent_directory, sub_directory in new_dirs:
    new_link = base_url.format(parent_directory=parent_directory, sub_directory=sub_directory)
    for i, line in enumerate(lines):
        if f"{sub_directory}:" in line:
            name = line.split(":", 1)[1].strip().strip('"').strip("'")  # Remove any surrounding quotes
            lines[i] = f"    {sub_directory}: \"[{name}]({new_link})\"\n"
            print(f"Updated line {i}: {lines[i]}")

# Write the changes to the config.yml file
try:
    with open("_config.yml", "w") as f:
        f.writelines(lines)
    print(f"Updated _config.yml")
except IOError as e:
    print(f"Error writing to _config.yml: {e}")
    exit(1)

try:
    subprocess.run(["git", "config", "user.name", "jedwin3210"], check=True)
    subprocess.run(["git", "config", "user.email", "jedwin321@berkeley.edu"], check=True)
    subprocess.run(["git", "add", "_config.yml"], check=True)
    subprocess.run(["git", "commit", "-m", "Update _config.yml with new directories"], check=True)
    push_url = f"https://{token}@github.com/data-8/fa24.git"
    subprocess.run(["git", "push", push_url], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error during git operations: {str(e)}")
    exit(1)
