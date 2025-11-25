#!/usr/bin/env python3
import os
import sys
import argparse
import re
import shutil
import urllib.request

def modify_config_rs(project_root, server_url, server_key):
    file_path = os.path.join(project_root, 'libs/hbb_common/src/config.rs')
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

def modify_default_settings(project_root, api_server):
    if not api_server:
        return

    file_path = os.path.join(project_root, 'libs/hbb_common/src/config.rs')
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

def modify_hard_settings(password):
    if not password:
        return

    file_path = 'libs/hbb_common/src/config.rs'
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"Updating HARD_SETTINGS with permanent password")
    # Replace HARD_SETTINGS
    # Pattern: pub static ref HARD_SETTINGS: RwLock<HashMap<String, String>> = Default::default();
    pattern_settings = r'pub\s+static\s+ref\s+HARD_SETTINGS\s*:\s*RwLock<HashMap<String,\s*String>>\s*=\s*Default::default\(\);'
    
    # We use RwLock::new(HashMap::from([...])) to initialize with password
    replacement_settings = (
        'pub static ref HARD_SETTINGS: RwLock<HashMap<String, String>> = RwLock::new(HashMap::from([\n'
        f'        ("password".to_owned(), "{password}".to_owned())\n'
        '    ]));'
    )
    
    content, count = re.subn(pattern_settings, replacement_settings, content)
    if count == 0:
        print("Warning: HARD_SETTINGS not found or not replaced.")
    else:
        print("HARD_SETTINGS replaced.")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def verify_changes(args):
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

        hard_settings = re.search(r'pub static ref HARD_SETTINGS: RwLock<HashMap<String, String>> = RwLock::new\(HashMap::from\(\[\s*\("password"\.to_owned\(\), ".*?"\.to_owned\(\)\)\s*\]\)\);', content, re.DOTALL)
        if hard_settings:
            print("  HARD_SETTINGS updated with permanent password.")
            print(f"  {hard_settings.group(0)}")

    else:
        print(f"  Error: {file_path} not found.")

    if args.extra_args:
        main_dart_path = "flutter/lib/main.dart"
        with open(main_dart_path, "r", encoding="utf-8") as f:
            if "args = List.from(args)..addAll([" in f.read():
                print(f"Verified: Extra args injected into {main_dart_path}")
            else:
                print(f"WARNING: Extra args injection not found in {main_dart_path}")

    print("-" * 30)

def inject_extra_args(extra_args_str):
    print(f"Injecting extra args: {extra_args_str}")
    import shlex
    
    try:
        # Split args respecting quotes
        extra_args_list = shlex.split(extra_args_str)
        # Format as Dart list items: "'arg1', 'arg2'"
        dart_args = ", ".join([f"'{arg}'" for arg in extra_args_list])
        
        main_dart_path = "flutter/lib/main.dart"
        with open(main_dart_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Find main function
        target = "Future<void> main(List<String> args) async {"
        if target in content:
            # Inject code to append args
            injection = f"\n  args = List.from(args)..addAll([{dart_args}]);"
            new_content = content.replace(target, target + injection)
            
            with open(main_dart_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Successfully injected extra args into {main_dart_path}")
        else:
            print(f"Error: Could not find main function in {main_dart_path}")
            
    except Exception as e:
        print(f"Error injecting extra args: {e}")

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
        'icon.png': ['res/icon.png'], # Used for flutter icons generation
        'logo.png': ['flutter/assets/logo.png'] # Used for app logo in UI
    }

    for src_name, dest_list in resource_map.items():
        src_path = os.path.join(custom_res_dir, src_name)
        if os.path.exists(src_path):
            for dest in dest_list:
                dest_dir = os.path.dirname(dest)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)

    
    content, count = re.subn(pattern_settings, replacement_settings, content)
    if count == 0:
        print("Warning: DEFAULT_SETTINGS not found or not replaced.")
    else:
        print("DEFAULT_SETTINGS replaced.")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def modify_runner_rc(project_root, app_name):
    file_path = os.path.join(project_root, 'flutter/windows/runner/Runner.rc')
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

def modify_pubspec_yaml(project_root, app_name):
    file_path = os.path.join(project_root, 'flutter/pubspec.yaml')
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

def download_resource(url, dest_path):
    if not url:
        return
    
    print(f"Downloading {os.path.basename(dest_path)} from {url}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"Downloaded {os.path.basename(dest_path)}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def modify_hard_settings(project_root, password):
    if not password:
        return

    file_path = os.path.join(project_root, 'libs/hbb_common/src/config.rs')
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"Updating HARD_SETTINGS with permanent password")
    # Replace HARD_SETTINGS
    # Pattern: pub static ref HARD_SETTINGS: RwLock<HashMap<String, String>> = Default::default();
    pattern_settings = r'pub\s+static\s+ref\s+HARD_SETTINGS\s*:\s*RwLock<HashMap<String,\s*String>>\s*=\s*Default::default\(\);'
    
    # We use RwLock::new(HashMap::from([...])) to initialize with password
    replacement_settings = (
        'pub static ref HARD_SETTINGS: RwLock<HashMap<String, String>> = RwLock::new(HashMap::from([\n'
        f'        ("password".to_owned(), "{password}".to_owned())\n'
        '    ]));'
    )
    
    content, count = re.subn(pattern_settings, replacement_settings, content)
    if count == 0:
        print("Warning: HARD_SETTINGS not found or not replaced.")
    else:
        print("HARD_SETTINGS replaced.")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def verify_changes(project_root, app_name, server_url):
    print("-" * 30)
    print("Verifying Changes in config.rs:")
    file_path = os.path.join(project_root, 'libs/hbb_common/src/config.rs')
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

        hard_settings = re.search(r'pub static ref HARD_SETTINGS: RwLock<HashMap<String, String>> = RwLock::new\(HashMap::from\(\[\s*\("password"\.to_owned\(\), ".*?"\.to_owned\(\)\)\s*\]\)\);', content, re.DOTALL)
        if hard_settings:
            print("  HARD_SETTINGS updated with permanent password.")
            print(f"  {hard_settings.group(0)}")

    else:
        print(f"  Error: {file_path} not found.")

    main_dart_path = os.path.join(project_root, "flutter/lib/main.dart")
    if os.path.exists(main_dart_path):
        with open(main_dart_path, "r", encoding="utf-8") as f:
            content = f.read()
            if f'"{app_name}"' in content:
                print(f"  Verified: App name '{app_name}' injected into {main_dart_path}")
            else:
                print(f"  WARNING: App name injection not found in {main_dart_path}")
    else:
        print(f"  Error: {main_dart_path} not found.")

    print("-" * 30)

def inject_extra_args(project_root, extra_args_str):
    print(f"Injecting extra args: {extra_args_str}")
    import shlex
    
    try:
        # Split args respecting quotes
        extra_args_list = shlex.split(extra_args_str)
        # Format as Dart list items: "'arg1', 'arg2'"
        dart_args = ", ".join([f"'{arg}'" for arg in extra_args_list])
        
        main_dart_path = os.path.join(project_root, "flutter/lib/main.dart")
        with open(main_dart_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Find main function
        target = "Future<void> main(List<String> args) async {"
        if target in content:
            # Inject code to append args
            injection = f"\n  args = List.from(args)..addAll([{dart_args}]);"
            new_content = content.replace(target, target + injection)
            
            with open(main_dart_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Successfully injected extra args into {main_dart_path}")
        else:
            print(f"Error: Could not find main function in {main_dart_path}")
            
    except Exception as e:
        print(f"Error injecting extra args: {e}")

def copy_resources(project_root, custom_res_dir):
    if not os.path.exists(custom_res_dir):
        print(f"No {custom_res_dir} directory found. Skipping resource copy.")
        return

    # Map source in custom_resources to destination
    resource_map = {
        'icon.ico': [os.path.join(project_root, 'res/icon.ico'), os.path.join(project_root, 'flutter/windows/runner/resources/app_icon.ico')],
        'logo.svg': [os.path.join(project_root, 'res/logo.svg')],
        'tray-icon.ico': [os.path.join(project_root, 'res/tray-icon.ico')],
        'icon.png': [os.path.join(project_root, 'res/icon.png')], # Used for flutter icons generation
        'logo.png': [os.path.join(project_root, 'flutter/assets/logo.png')] # Used for app logo in UI
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

def modify_build_py(project_root, args):
    print("Modifying build.py...")
    build_py_path = os.path.join(project_root, 'build.py')
    with open(build_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace rustdesk.exe with {app_name}.exe (careful with case and context)
    # For flutter build, it expects the exe name to match the pubspec name (usually)
    # But build.py has hardcoded 'rustdesk.exe' in several places.
    
    # We need to be careful. If we changed pubspec name, flutter produces {pubspec_name}.exe
    # Let's assume pubspec name is sanitized app_name.
    sanitized_name = args.app_name.lower().replace(" ", "_").replace("-", "_")
    
    # In build_flutter_windows:
    # python3 ./generate.py -f ... -e .../rustdesk.exe
    # We DO NOT want to change the input file name here, because flutter still builds rustdesk.exe
    # content = content.replace(f'/rustdesk.exe', f'/{sanitized_name}.exe')
    
    # In main (cargo build section):
    # mv target/release/rustdesk.exe target/release/RustDesk.exe
    # We want: mv target/release/rustdesk.exe target/release/{app_name}.exe
    # But cargo still produces rustdesk.exe unless we change Cargo.toml bin name.
    # So we only change the destination.
    content = content.replace('target/release/RustDesk.exe', f'target/release/{args.app_name}.exe')
    
    # cp -rf target/release/RustDesk.exe {res_dir}
    # Already handled by above replacement if consistent.
    
    with open(build_py_path, 'w', encoding='utf-8') as f:
        f.write(content)

def modify_portable_generate(project_root, app_name):
    print("Modifying libs/portable/generate.py...")
    gen_path = os.path.join(project_root, 'libs', 'portable', 'generate.py')
    with open(gen_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The magic string "rustdesk" might be used for installation folder name
    # f.write("rustdesk".encode(encoding=encoding))
    # We replace it with app_name
    content = content.replace('"rustdesk".encode', f'"{app_name}".encode')
    
    # Default executable name
    # options.executable = 'rustdesk.exe'
    sanitized_name = app_name.lower().replace(" ", "_").replace("-", "_")
    content = content.replace("'rustdesk.exe'", f"'{sanitized_name}.exe'")
    
    with open(gen_path, 'w', encoding='utf-8') as f:
        f.write(content)

def modify_main_cpp(project_root, app_name):
    print("Modifying flutter/windows/runner/main.cpp...")
    cpp_path = os.path.join(project_root, 'flutter', 'windows', 'runner', 'main.cpp')
    with open(cpp_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace default app name
    content = content.replace('std::wstring app_name = L"RustDesk";', f'std::wstring app_name = L"{app_name}";')
    
    # Disable Rust override to ensure our name sticks
    # We use app_name.empty() which is false (since we set it above) but not a compile-time constant,
    # avoiding error C4127 (conditional expression is constant).
    content = content.replace('if (get_rustdesk_app_name(app_name_buffer, 512) == 0)', 'if (app_name.empty() && get_rustdesk_app_name(app_name_buffer, 512) == 0)')
    
    with open(cpp_path, 'w', encoding='utf-8') as f:
        f.write(content)

def modify_main_dart(project_root, app_name):
    print("Modifying flutter/lib/main.dart...")
    dart_path = os.path.join(project_root, 'flutter', 'lib', 'main.dart')
    with open(dart_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace bind.mainGetAppNameSync() with our string
    # We need to be careful about the context.
    # title: isWeb ? '${bind.mainGetAppNameSync()} ...' : bind.mainGetAppNameSync(),
    
    # Regex replacement might be safer or just string replace if unique enough.
    content = content.replace('bind.mainGetAppNameSync()', f'"{app_name}"')
    
    with open(dart_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    parser = argparse.ArgumentParser(description='Customize RustDesk build')
    parser.add_argument('--app-name', required=True, help='Application Name')
    parser.add_argument('--server-url', required=True, help='Rendezvous Server URL')
    parser.add_argument('--server-key', required=True, help='Rendezvous Server Public Key')
    parser.add_argument('--api-server', help='API Server URL')
    parser.add_argument('--permanent-password', help='Permanent Password')
    parser.add_argument('--icon-url', help='URL for icon.ico')
    parser.add_argument('--logo-url', help='URL for logo.svg')
    parser.add_argument('--tray-icon-url', help='URL for tray-icon.ico')
    parser.add_argument('--icon-png-url', help='URL for icon.png')
    parser.add_argument('--logo-png-url', help='URL for logo.png')
    parser.add_argument('--extra-args', help='Extra arguments to inject into main.dart (e.g. --view-style=adaptive)')

    args = parser.parse_args()

    project_root = os.getcwd()

    print(f"Customizing RustDesk: {args.app_name}")

    modify_config_rs(project_root, args.server_url, args.server_key)
    if args.api_server:
        modify_default_settings(project_root, args.api_server)
    if args.permanent_password:
        modify_hard_settings(project_root, args.permanent_password)
    
    modify_runner_rc(project_root, args.app_name)
    modify_pubspec_yaml(project_root, args.app_name)
    
    # New deep customization functions
    modify_build_py(project_root, args)
    modify_portable_generate(project_root, args.app_name)
    modify_main_cpp(project_root, args.app_name)
    modify_main_dart(project_root, args.app_name)

    # Download and copy resources
    
    custom_res_dir = os.path.join(project_root, 'custom_resources')
    os.makedirs(custom_res_dir, exist_ok=True)

    if args.icon_url:
        download_resource(args.icon_url, os.path.join(custom_res_dir, 'icon.ico'))
    if args.logo_url:
        download_resource(args.logo_url, os.path.join(custom_res_dir, 'logo.svg'))
    if args.logo_png_url:
        download_resource(args.logo_png_url, os.path.join(custom_res_dir, 'logo.png'))
    if args.tray_icon_url:
        download_resource(args.tray_icon_url, os.path.join(custom_res_dir, 'tray-icon.ico'))
    if args.icon_png_url:
        download_resource(args.icon_png_url, os.path.join(custom_res_dir, 'icon.png'))

    copy_resources(project_root, custom_res_dir)

    if args.extra_args:
        inject_extra_args(project_root, args.extra_args)

    verify_changes(project_root, args.app_name, args.server_url)
    print("Customization complete.")

if __name__ == '__main__':
    main()
