#!/usr/bin/env python3

import os
import sys
import pwd
import grp
import shutil
import subprocess

def backup_file(path):
    backup_path = path + ".bak"
    shutil.copy2(path, backup_path)
    print(f"Backed up {path} to {backup_path}")

def replace_in_file(file_path, old_str, new_str):
    with open(file_path, 'r') as f:
        content = f.read()
    content = content.replace(old_str, new_str)
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"Replaced '{old_str}' with '{new_str}' in {file_path}")

def main():
    if os.geteuid() != 0:
        print("Error: This script must be run as root.")
        sys.exit(1)

    if len(sys.argv) != 3:
        print(f"Usage: sudo python3 -m emNaviBase.init.rename_username old_username new_username")
        sys.exit(1)

    old_username = sys.argv[1]
    new_username = sys.argv[2]

    # Check if old user exists
    try:
        pwd.getpwnam(old_username)
    except KeyError:
        print(f"Error: User '{old_username}' does not exist.")
        sys.exit(1)

    old_home = f"/home/{old_username}"
    new_home = f"/home/{new_username}"

    if not os.path.isdir(old_home):
        print(f"Error: Home directory for user '{old_username}' does not exist.")
        sys.exit(1)

    if os.path.exists(new_home):
        print(f"Error: Home directory for new username '{new_username}' already exists.")
        sys.exit(1)

    # Backup critical files
    print("Backing up system files...")
    for path in ["/etc/passwd", "/etc/shadow", "/etc/group"]:
        backup_file(path)

    # Replace username in system files
    print(f"Replacing '{old_username}' with '{new_username}' in system files...")
    for path in ["/etc/passwd", "/etc/shadow", "/etc/group"]:
        replace_in_file(path, old_username, new_username)

    # Rename home directory
    print(f"Renaming home directory from {old_home} to {new_home}...")
    shutil.move(old_home, new_home)

    # Update ownership
    try:
        subprocess.run(
            ["chown", "-R", f"{new_username}:{new_username}", new_home],
            check=True
        )
        print(f"Ownership of {new_home} updated to {new_username}:{new_username}")
    except subprocess.CalledProcessError:
        print("Failed to change ownership.")
        sys.exit(1)

    print("Username and home directory replacement completed.")
    print("Please reboot the system to apply the changes: sudo reboot")

if __name__ == "__main__":
    main()
