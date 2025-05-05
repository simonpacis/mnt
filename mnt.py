#!/usr/bin/env python3
# mnt.py

import os
import json
import sys
import time
import shlex
import subprocess


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
        append_mount_path = True

    except IndexError:
        append_mount_path = False
        mount_path = None

    if server in config['servers']:
        print(f"Server \"{server}\" already exists. Use command \"mnt update <server_name> <command>\" to change it.")
        sys.exit(0)

    config['servers'][server] = {
            'name': server,
            'command': server_command,
            'unmount_command': unmount_command,
            'append_mount_path': append_mount_path,
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
    server['mounted_time'] = None
    save_config()

    append_mount_path = False
    try:
        append_mount_path = server['append_mount_path']
    except KeyError:
        pass
    if(append_mount_path and server['mount_path']):
        cmd = server['unmount_command'] + " " + server['mount_path']
    else:
        cmd = server['unmount_command']
    print(cmd)
    os.system(cmd)
    sys.exit(0)

def update_server():
    prop_list = ["mount","unmount","mount_path","append_mount_path","host","key_path","remote_dir"]
    try:
        server = sys.argv[2]
        prop = sys.argv[3]
        if prop not in prop_list:
            print(f"Invalid property. Must be one of: {', '.join(prop_list)}")
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
    elif prop == "mount_path":
        config['servers'][server]['mount_path'] = server_command
    elif prop == "append_mount_path":
        if server_command == "true" or server_command == "True":
            config['servers'][server]['append_mount_path'] = True
        else:
            config['servers'][server]['append_mount_path'] = False
    elif prop == "host":
        config['servers'][server]['host'] = server_command
    elif prop == "key_path":
        config['servers'][server]['key_path'] = server_command
    elif prop == "remote_dir":
        config['servers'][server]['remote_dir'] = server_command

    print(f"Updated server \"{server}\" prop \"{prop}\" to \"{server_command}\"")

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
    print('\nmnt servers:\n')
    last_mounted = last_mounted_server()
    for server in config['servers']:
        server = config['servers'][server]
        if server['name'] == last_mounted:
            print(f"--- {server['name']} (latest) ---")
        else:
            print(f"--- {server['name']} ---")
        print(f"Mount command: \"{server['command']}\"")
        print(f"Unmount command: \"{server['unmount_command']}\"")
        if server['name'] == last_mounted:
            print(f"Mounted at: {server['mounted_time']} (latest)")
        else:
            print(f"Mounted at: {server['mounted_time']}")
        if server['mount_path'] is not None:
            print(f"Mount path: {server['mount_path']}")
            print(f"Append mount path? {server['append_mount_path']}")
        try:
            if server['host'] is not None:
                print('- SSH Exec') 
                print(f"  Host: {server['host']}")
                if server['key_path'] is not None:
                    print(f"  Key path: {server['key_path']}")
                if server['remote_dir'] is not None:
                    print(f"  Remote directory: {server['remote_dir']}")
        except KeyError:
            pass
        print('')
    sys.exit(0)

def mount(server):
    config_server = config['servers'][server['name']]
    config_server['mounted_time'] = int(time.time())
    save_config()

    append_mount_path = False
    try:
        append_mount_path = server['append_mount_path']
    except KeyError:
        pass
    if(append_mount_path and server['mount_path']):
        if not os.path.exists(server['mount_path']):
            os.makedirs(server['mount_path'], exist_ok=True)
        cmd = server['command'] + " " + server['mount_path']
    else:
        cmd = server['command']
    print(cmd)
    os.system(cmd)
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
    add <name> <mount_cmd> <unmount_cmd> [mount_path]   Add new server configuration.
                                                            Note: If mount_path is specified, it will be appended
                                                            to the end of your mount and unmount commands. Can be disabled using "update".
    update <name> <prop> <command>                      Update a property on a given server.
                                                        Type "mnt update <name> help" to see all properties you can update.
    delete <name>                                       Delete server configuration
    refresh <name>                                      Updates the mounted at time for the server
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

def get_server_from_mount_path(cwd):
    for server in config['servers']:
        server = config['servers'][server]
        if server['mount_path'] == cwd:
            return server['name']
    return None

def ssh_exec():
    try:
        # Try to get server name from args
        server_name = sys.argv[2]
        server = config['servers'][server_name]
        command = " ".join(sys.argv[3:])  # If server found, command starts from argv[3]
    except (KeyError, IndexError):
        cwd = sys.argv[2]
        if not os.path.exists(cwd): # CWD does not exist, use last mounted
            server_name = last_mounted_server()
            command = " ".join(sys.argv[2:])
        else:
            server_name = get_server_from_mount_path(cwd)
            command = " ".join(sys.argv[3:])

        if server_name is None:
            print('Error: No server specified, no mount path at provided cwd, and no last-mounted server available')
            print('Usage: mnt ssh-exec [<server_name>] [<mount_path>] <command>')
            sys.exit(1)

    try:
        server = config['servers'][server_name]
    except KeyError:
        print(f'Error: Server "{server_name}" not found in config')
        sys.exit(1)

    # Build SSH command components
    ssh_parts = ['ssh', '-tt']  # Force pseudo-terminal allocation

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

    # Handle remote command construction
    if 'remote_dir' in server:
        # Use sh -c for better quoting behavior
        remote_cmd = f"cd {shlex.quote(server['remote_dir'])} && {command}"
    else:
        remote_cmd = command

    # Execute with proper shell handling
    full_cmd = ssh_parts + [remote_cmd]

    print(command)
    p = subprocess.Popen(full_cmd, stderr=subprocess.PIPE)
    _, stderr = p.communicate()

    # Filter out any line that starts with "Connection to" and ends with "closed."
    filtered_stderr = b'\n'.join(
        line for line in stderr.splitlines()
        if not (
            line.startswith(b'Connection to ')
            and line.endswith(b' closed.')
        )
    )

    if filtered_stderr:
        sys.stderr.buffer.write(filtered_stderr)
        sys.stderr.buffer.write(b'\n')
    sys.exit(p.returncode)

def cd_mount_path():
    try:
        # Try to get server name from args
        server_name = sys.argv[2]
    except (KeyError, IndexError):
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

def refresh_server():
    try:
        server_name = sys.argv[2]
    except IndexError:
        print('No server given. Usage: mnt refresh <server_name>. E.g. \"mnt refresh sshfs\"')
        sys.exit(0)

    if server_name not in config['servers']:
        print(f"Server \"{server}\" does not exist. Use command \"mnt add\" to add it.")
        sys.exit(0)


    config_server = config['servers'][server_name]
    config_server['mounted_time'] = int(time.time())

    save_config()

    print(f"Refreshed mount time of \"{server_name}\".")

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
    elif command == 'refresh':
        refresh_server()
    elif command == 'help' or command == '-h':
        help()
    else:
        if command in config['servers']:
            mount(config['servers'][command])
            sys.exit(0)
        print('Unknown command: ' + command)
        sys.exit(0)

