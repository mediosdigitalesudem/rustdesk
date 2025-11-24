#!/usr/bin/env python3
import os
import sys
import argparse
import re
import shutil
import urllib.request

def modify_config_rs(server_url, server_key):
    file_path = 'libs/hbb_common/src/config.rs'
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if server_url:
        print(f"Updating RENDEZVOUS_SERVERS to {server_url}")
        # Replace RENDEZVOUS_SERVERS
        pattern_servers = r'pub\s+const\s+RENDEZVOUS_SERVERS\s*:\s*&\[&str\]\s*=\s*&\[".*?"\];'
        replacement_servers = f'pub const RENDEZVOUS_SERVERS: &[&str] = &["{server_url}"];'
        content, count = re.subn(pattern_servers, replacement_servers, content)
        if count == 0:
            print("Warning: RENDEZVOUS_SERVERS not found or not replaced.")
        else:
            print("RENDEZVOUS_SERVERS replaced.")

        # Replace PROD_RENDEZVOUS_SERVER
        print(f"Updating PROD_RENDEZVOUS_SERVER to {server_url}")
        pattern_prod = r'pub\s+static\s+ref\s+PROD_RENDEZVOUS_SERVER\s*:\s*RwLock<String>\s*=\s*RwLock::new\(".*?"\.to_owned\(\)\);'
        replacement_prod = f'pub static ref PROD_RENDEZVOUS_SERVER: RwLock<String> = RwLock::new("{server_url}".to_owned());'
        content, count = re.subn(pattern_prod, replacement_prod, content)
        if count == 0:
            print("Warning: PROD_RENDEZVOUS_SERVER not found or not replaced.")
        else:
            print("PROD_RENDEZVOUS_SERVER replaced.")

    if server_key:
        print(f"Updating RS_PUB_KEY")
        # Replace RS_PUB_KEY
        pattern_key = r'pub\s+const\s+RS_PUB_KEY\s*:\s*&str\s*=\s*".*?";'
        replacement_key = f'pub const RS_PUB_KEY: &str = "{server_key}";'
        content, count = re.subn(pattern_key, replacement_key, content)
        if count == 0:
            print("Warning: RS_PUB_KEY not found or not replaced.")
        else:
            print("RS_PUB_KEY replaced.")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def modify_default_settings(api_server):
    if not api_server:
        return

    file_path = 'libs/hbb_common/src/config.rs'
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"Updating DEFAULT_SETTINGS with api-server: {api_server}")
    # Replace DEFAULT_SETTINGS
    # Pattern: pub static ref DEFAULT_SETTINGS: RwLock<HashMap<String, String>> = Default::default();
    pattern_settings = r'pub\s+static\s+ref\s+DEFAULT_SETTINGS\s*:\s*RwLock<HashMap<String,\s*String>>\s*=\s*Default::default\(\);'
    
    # We use RwLock::new(HashMap::from([...])) to initialize with api-server
    replacement_settings = (
        'pub static ref DEFAULT_SETTINGS: RwLock<HashMap<String, String>> = RwLock::new(HashMap::from([\n'
        f'        ("api-server".to_owned(), "{api_server}".to_owned())\n'
        '    ]));'
    )
    
    content, count = re.subn(pattern_settings, replacement_settings, content)
    if count == 0:
        print("Warning: DEFAULT_SETTINGS not found or not replaced.")
    else:
        print("DEFAULT_SETTINGS replaced.")

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

def download_resource(url, filename):
    if not url:
        return
    
    custom_res_dir = 'custom_resources'
    if not os.path.exists(custom_res_dir):
        os.makedirs(custom_res_dir)
        
    dest_path = os.path.join(custom_res_dir, filename)
    print(f"Downloading {filename} from {url}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"Downloaded {filename}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

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
    parser.add_argument('--api-server', type=str, help='API Server URL')
    parser.add_argument('--icon-url', type=str, help='URL for icon.ico')
    parser.add_argument('--logo-url', type=str, help='URL for logo.svg')
    parser.add_argument('--tray-icon-url', type=str, help='URL for tray-icon.ico')
    parser.add_argument('--icon-png-url', type=str, help='URL for icon.png')
    
    args = parser.parse_args()

    print("Starting Customization...")
    
    # Download resources if URLs are provided
    download_resource(args.icon_url, 'icon.ico')
    download_resource(args.logo_url, 'logo.svg')
    download_resource(args.tray_icon_url, 'tray-icon.ico')
    download_resource(args.icon_png_url, 'icon.png')

    modify_config_rs(args.server_url, args.server_key)
    modify_default_settings(args.api_server)
    modify_runner_rc(args.app_name)
    modify_pubspec_yaml(args.app_name)
    copy_resources()
    
    verify_changes()
    
    print("Customization Complete.")

def verify_changes():
    print("-" * 30)
    print("Verifying Changes in config.rs:")
    file_path = 'libs/hbb_common/src/config.rs'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract and print relevant lines
        rendezvous = re.search(r'pub const RENDEZVOUS_SERVERS: &\[&str\] = &\[".*?"\];', content)
        if rendezvous:
            print(f"  {rendezvous.group(0)}")
            
        prod_server = re.search(r'pub static ref PROD_RENDEZVOUS_SERVER: RwLock<String> = RwLock::new\(".*?"\.to_owned\(\)\);', content)
        if prod_server:
            print(f"  {prod_server.group(0)}")

        rs_pub_key = re.search(r'pub const RS_PUB_KEY: &str = ".*?";', content)
        if rs_pub_key:
            print(f"  {rs_pub_key.group(0)}")

        default_settings = re.search(r'pub static ref DEFAULT_SETTINGS: RwLock<HashMap<String, String>> = RwLock::new\(HashMap::from\(\[\s*\("api-server"\.to_owned\(\), ".*?"\.to_owned\(\)\)\s*\]\)\);', content, re.DOTALL)
        if default_settings:
            print("  DEFAULT_SETTINGS updated with api-server.")
            print(f"  {default_settings.group(0)}")
    else:
        print(f"  Error: {file_path} not found.")
    print("-" * 30)

if __name__ == '__main__':
    main()
