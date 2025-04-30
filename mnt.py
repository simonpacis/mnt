#!/usr/bin/env python3
# mnt.py

import os
import json
import sys
import time


config_folder = os.path.expanduser('~/.config/mnt')
config_path = os.path.join(config_folder, 'config.json')

def setup_config():
    if not os.path.exists(config_folder):
        os.makedirs(config_folder)


    if not os.path.exists(config_path):
        with open(config_path, 'w') as f:
            json.dump({'servers': {}}, f)

    try:
        with open(config_path) as f:
            config = json.load(f)
    except json.decoder.JSONDecodeError:
        print('Invalid JSON in config-file.')
        sys.exit(0)
    return config

def save_config():
    with open(config_path, 'w') as f:
        json.dump(config, f)
    return True

def add_server():
    try:
        server = sys.argv[2]
        server_command = sys.argv[3]  # Joins with spaces, no extra quotes
        unmount_command = sys.argv[4]  # Joins with spaces, no extra quotes
    except IndexError:
        print('No server given. Usage: mnt add <server_name> <mount_command> <unmount_command> [mount_path]. E.g. \"mnt add sshfs user@example.com:/remote/path /local/mount\"')
        sys.exit(0)

    try:
        mount_path = sys.argv[5]
    except IndexError:
        mount_path = None

    if server in config['servers']:
        print(f"Server \"{server}\" already exists. Use command \"mnt update <server_name> <command>\" to change it.")
        sys.exit(0)

    config['servers'][server] = {
            'name': server,
            'command': server_command,
            'unmount_command': unmount_command,
            'mounted_time': None,
            'mount_path': mount_path
            }

    print(f"Added server \"{server}\" with command \"{server_command}\"")

    save_config()
    sys.exit(0)

def unmount_server():
    try:
        server_name = sys.argv[2]
    except IndexError:
        print('No server given. Usage: mnt unmount <server_name>')

    if server_name not in config['servers']:
        print(f"Server \"{server}\" does not exist. Use command \"mnt add\" to add it.")
        sys.exit(0)

    server = config['servers'][server_name]

    os.system(server['unmount_command'])
    sys.exit(0)

def update_server():
    try:
        server = sys.argv[2]
        prop = sys.argv[3]
        if(prop != 'mount' and prop != 'unmount'):
            print('Invalid property. Must be "mount" or "unmount"')
            sys.exit(0)
        server_command = " ".join(sys.argv[4:])  # Joins with spaces, no extra quotes
    except IndexError:
        print('No server given. Usage: mnt update <server_name> <mount|unmount> <command>. E.g. \"mnt update sshfs user@example.com:/remote/path /local/mount\"')
        sys.exit(0)

    if server not in config['servers']:
        print(f"Server \"{server}\" does not exist. Use command \"mnt add <server_name> <command>\" to add it.")
        sys.exit(0)

    if prop == 'mount':
        config['servers'][server]['command'] = server_command
    elif prop == 'unmount':
        config['servers'][server]['unmount_command'] = server_command

    print(f"Updated server \"{server}\" with command \"{server_command}\"")

    save_config()
    sys.exit(0)

def delete_server():
    try:
        server = sys.argv[2]
    except IndexError:
        print('No server given. Usage: mnt delete <server_name>. E.g. \"mnt delete sshfs\"')
        sys.exit(0)

    if server not in config['servers']:
        print(f"Server \"{server}\" does not exist. Use command \"mnt add <server_name> <command>\" to add it.")
        sys.exit(0)

    del config['servers'][server]

    save_config()

    print(f"Deleted server \"{server}\"")

    sys.exit(0)

def list_servers():
    print('Servers:')
    for server in config['servers']:
        server = config['servers'][server]
        print(f"Name: {server['name']}")
        print(f"Command: {server['command']}")
        print(f"Mounted: {server['mounted_time'] is not None}")
        print('')
    sys.exit(0)

def mount(server):
    config_server = config['servers'][server['name']]
    config_server['mounted_time'] = int(time.time())
    save_config()

    os.system(server['command'])
    sys.exit(0)

def help():
    print("""mnt - Mount and remote command management tool

Usage:
    mnt <command> [arguments]
    mnt <server_name>          # Shortcut for 'mnt mount <server_name>'

Core Commands:
    mount <server>             Mount a configured server
    unmount <server>           Unmount a configured server
    cd <server>               Change to server's mount directory (requires shell integration)
    ssh-exec [server] <cmd>    Execute remote command (uses last mounted server if omitted)

Server Management:
    add <name> <mount_cmd> <unmount_cmd> [mount_path]   Add new server configuration
    update <name> <mount|unmount> <command>             Update server commands
    delete <name>                                       Delete server configuration
    list                                                List all configured servers
    enable-ssh-exec <args>                              Configure server for SSH commands
    enable-cd                                          Show instructions for cd integration

SSH Configuration:
    enable-ssh-exec <server> <host> <user> [key_path] [remote_dir]
        Configure SSH access for a server
        Example: mnt enable-ssh-exec myserver example.com user ~/.ssh/id_rsa /projects
        * Only host and user are required

Examples:
    mnt add web sshfs "user@host:/path ~/mnt/web" "umount ~/mnt/web"
    mnt web                      # Mounts 'web' server
    mnt cd web                   # Changes to web's mount directory
    mnt ssh-exec web ls -la      # Run command on 'web'
    mnt ssh-exec make            # Run on last mounted server
    mnt enable-cd               # Show cd integration instructions
""")
    sys.exit(0)

def enable_ssh_exec():
    try:
        server_name = sys.argv[2]
        host = sys.argv[3]
        username = sys.argv[4]
        key_path = os.path.expanduser(sys.argv[5]) if len(sys.argv) > 5 else None
        remote_dir = sys.argv[6] if len(sys.argv) > 6 else None
    except IndexError:
        print('Usage: mnt enable-ssh-exec <server_name> <host> <username> [<key_path>] [<remote_dir>]')
        print('Example (minimal): mnt enable-ssh-exec my_server example.com user')
        print('Example (full): mnt enable-ssh-exec my_server example.com user ~/.ssh/id_rsa /projects')
        sys.exit(1)

    if server_name not in config['servers']:
        print(f'Error: Server "{server_name}" does not exist. Create it first with "mnt add"')
        sys.exit(1)

    # Update existing server configuration
    server = config['servers'][server_name]
    server['host'] = f"{username}@{host}"
    if key_path:
        server['key_path'] = key_path
    if remote_dir:
        server['remote_dir'] = remote_dir
    save_config()

    print(f"Configured SSH execution for server '{server_name}':")
    print(f"- Host: {username}@{host}")
    if key_path:
        print(f"- SSH Key: {key_path}")
    if remote_dir:
        print(f"-  Remote directory: {remote_dir}")
    print("\nNote: Only host is required. Other fields are optional.")

    sys.exit(0)

def last_mounted_server():
    """Returns name of most recently mounted server or None"""
    last_server = None
    last_time = None

    for server_name in config['servers']:
        server = config['servers'][server_name]
        if server['mounted_time'] is not None:
            if last_time is None or server['mounted_time'] > last_time:
                last_server = server_name
                last_time = server['mounted_time']

    return last_server

def ssh_exec():
    try:
        # Try to get server name from args
        server_name = sys.argv[2]
        server = config['servers'][server_name]
        command = " ".join(sys.argv[3:])  # If server found, command starts from argv[3]
    except (KeyError, IndexError):
        # No valid server specified - use last mounted with full command
        server_name = last_mounted_server()
        command = " ".join(sys.argv[2:])  # If no server, command starts from argv[2]
        
        if server_name is None:
            print('Error: No server specified and no last-mounted server available')
            print('Usage: mnt ssh-exec [<server_name>] <command>')
            sys.exit(1)

    try:
        server = config['servers'][server_name]
    except KeyError:
        print(f'Error: Server "{server_name}" not found in config')
        sys.exit(1)

    # Build SSH command components
    ssh_parts = ['ssh']

    # Add identity file if specified
    if 'key_path' in server:
        ssh_parts.extend(['-i', os.path.expanduser(server['key_path'])])

    # Check for required host
    if 'host' not in server:
        print(f'Error: Server "{server_name}" missing host configuration')
        print('Run: mnt enable-ssh-exec to configure')
        sys.exit(1)

    # Add host
    ssh_parts.append(server['host'])

    # Add remote directory if specified
    remote_cmd = command
    if 'remote_dir' in server:
        # Escape single quotes in path
        escaped_dir = server['remote_dir'].replace("'", "'\\''")
        # Wrap in login shell to load aliases/functions
        remote_cmd = f"bash -lic 'cd '\''{escaped_dir}'\'' && {command}'"
    else:
        # Still use login shell even without cd
        remote_cmd = f"bash -lic '{command}'"

# Final command assembly
    full_cmd = ' '.join(ssh_parts) + f' "{remote_cmd}"'

    # Execute
    print(f"Executing: {full_cmd}")
    os.system(full_cmd)
    sys.exit(0)

def cd_mount_path():
    try:
        # Try to get server name from args
        server_name = sys.argv[1]
        server = config['servers'][server_name]
    except KeyError:
        # No server specified - use last mounted
        server_name = last_mounted_server()
        if server_name is None:
            print('Error: No server specified and no last-mounted server available')
            print('Usage: mnt cd [<server_name>]')
            sys.exit(1)

    if server_name not in config['servers']:
        print(f"Server \"{server_name}\" does not exist. Use command \"mnt add <server_name> <command>\" to add it.")
        sys.exit(0)

    server = config['servers'][server_name]

    if 'mount_path' not in server:
        print(f"Server \"{server_name}\" does not have a mount path.")

    print(server['mount_path'])
    sys.exit(0)

def enable_cd():
    print("""If the cd-command just outputs the mount path, you must install the cd-help script. To do so, add this to your .bashrc/.zshrc:
mnt() {
  if [[ "$1" == "cd" ]]; then
    cd "$(command mnt "$@")"
  else
    command mnt "$@"
  fi
}""")

if __name__ == '__main__':
    config = setup_config()

    try:
        command = sys.argv[1]
    except IndexError:
        print('No command given.')
        sys.exit(0)

    if command in config['servers']:
        mount(config['servers'][command])
    else:
        if command == 'mount':
            try:
                server = sys.argv[2]
            except IndexError:
                print('No server given. Usage: mnt mount <server_name>. E.g. \"mnt mount sshfs\"')
                sys.exit(0)
            mount(config['servers'][sys.argv[2]])
        elif command == 'add':
            add_server()
        elif command == 'unmount':
            unmount_server()
        elif command == 'update':
            update_server()
        elif command == 'delete':
            delete_server()
        elif command == 'list':
            list_servers()
        elif command == 'cd':
            cd_mount_path()
        elif command == 'enable-cd':
            enable_cd()
        elif command == 'ssh-exec':
            ssh_exec()
        elif command == 'enable-ssh-exec':
            enable_ssh_exec()
        elif command == 'help' or command == '-h':
            help()
        else:
            print('Unknown command: ' + command)
            sys.exit(0)

