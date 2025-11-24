#!/usr/bin/env python3
import os
import sys
import argparse
import re
import shutil

def modify_config_rs(server_url, server_key):
    file_path = 'libs/hbb_common/src/config.rs'
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace RENDEZVOUS_SERVERS
    # Pattern: pub const RENDEZVOUS_SERVERS: &[&str] = &["..."];
    if server_url:
        print(f"Updating RENDEZVOUS_SERVERS to {server_url}")
        pattern_servers = r'pub const RENDEZVOUS_SERVERS: &\[&str\] = &\[".*?"\];'
        replacement_servers = f'pub const RENDEZVOUS_SERVERS: &[&str] = &["{server_url}"];'
        content = re.sub(pattern_servers, replacement_servers, content)

    # Replace RS_PUB_KEY
    # Pattern: pub const RS_PUB_KEY: &str = "...";
    if server_key:
        print(f"Updating RS_PUB_KEY")
        pattern_key = r'pub const RS_PUB_KEY: &str = ".*?";'
        replacement_key = f'pub const RS_PUB_KEY: &str = "{server_key}";'
        content = re.sub(pattern_key, replacement_key, content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def modify_runner_rc(app_name):
    file_path = 'flutter/windows/runner/Runner.rc'
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if app_name:
        print(f"Updating Runner.rc with App Name: {app_name}")
        # Update ProductName
        content = re.sub(r'VALUE "ProductName", ".*?"', f'VALUE "ProductName", "{app_name}"', content)
        # Update FileDescription
        content = re.sub(r'VALUE "FileDescription", ".*?"', f'VALUE "FileDescription", "{app_name}"', content)
        # Update LegalCopyright (Generic)
        content = re.sub(r'VALUE "LegalCopyright", ".*?"', f'VALUE "LegalCopyright", "Copyright © {app_name}"', content)
        # Update CompanyName (Generic)
        content = re.sub(r'VALUE "CompanyName", ".*?"', f'VALUE "CompanyName", "{app_name}"', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def modify_pubspec_yaml(app_name):
    file_path = 'flutter/pubspec.yaml'
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if app_name:
        print(f"Updating pubspec.yaml description")
        # Update description
        content = re.sub(r'description: .*', f'description: {app_name} Remote Desktop', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def copy_resources():
    custom_res_dir = 'custom_resources'
    if not os.path.exists(custom_res_dir):
        print(f"No {custom_res_dir} directory found. Skipping resource copy.")
        return

    # Map source in custom_resources to destination
    resource_map = {
        'icon.ico': ['res/icon.ico', 'flutter/windows/runner/resources/app_icon.ico'],
        'logo.svg': ['res/logo.svg'],
        'tray-icon.ico': ['res/tray-icon.ico'],
        'icon.png': ['res/icon.png'] # Used for flutter icons generation
    }

    for src_name, dest_list in resource_map.items():
        src_path = os.path.join(custom_res_dir, src_name)
        if os.path.exists(src_path):
            for dest in dest_list:
                dest_dir = os.path.dirname(dest)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                print(f"Copying {src_name} to {dest}")
                shutil.copy2(src_path, dest)
        else:
            print(f"Warning: {src_name} not found in {custom_res_dir}")

def main():
    parser = argparse.ArgumentParser(description='Customize RustDesk Build')
    parser.add_argument('--app-name', type=str, help='Application Name')
    parser.add_argument('--server-url', type=str, help='Rendezvous Server URL')
    parser.add_argument('--server-key', type=str, help='Rendezvous Server Public Key')
    
    args = parser.parse_args()

    print("Starting Customization...")
    
    modify_config_rs(args.server_url, args.server_key)
    modify_runner_rc(args.app_name)
    modify_pubspec_yaml(args.app_name)
    copy_resources()
    
    print("Customization Complete.")

if __name__ == '__main__':
    main()
