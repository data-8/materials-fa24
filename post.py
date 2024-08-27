import os
import subprocess
import re
from edapi import EdAPI
from datetime import datetime, timedelta

# Assuming your classes Homework, Lab, and Project are defined in a file named `release_script.py`
from ed_posts import Homework, Lab, Project

def get_latest_commit_message():
    result = subprocess.run(['git', 'log', 'main', '-1', "--pretty=format:'%H %B'"], stdout=subprocess.PIPE)
    commit_hash, commit_message = result.stdout.decode('utf-8').strip().split(' ', 1)
    return commit_hash, commit_message

def main():
    commit_hash, commit_message = get_latest_commit_message()
    print(f"Latest commit hash: {commit_hash}")
    print(f"Latest commit message: {commit_message}")

    match = re.match(r"Release assignment\(s\) (.+)", commit_message)
    if match:
        assignment = match.group(1)
        if re.match(r"hw\d{2}", assignment):
            hw_num = re.search(r"\d{2}", assignment).group(0)
            Homework.make_post(hw_num)
        elif re.match(r"lab\d{2}", assignment):
            lab_num = re.search(r"\d{2}", assignment).group(0)
            Lab.make_post(lab_num)
        elif re.match(r"project\d", assignment):
            project_num = re.search(r"\d", assignment).group(0)
            Project.make_post(project_num)
        else:
            print("No matching assignment type found.")
    else:
        print("No valid release assignment commit message found.")

if __name__ == "__main__":
    main()
