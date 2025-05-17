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
            json.dump({'servers': {}, 'aliases': {}}, f)

    try:
        with open(config_path) as f:
            config = json.load(f)
    except json.decoder.JSONDecodeError:
        print('Invalid JSON in config-file.')
        sys.exit(0)
    return config

def run_command(cmd, indent = False):
    result = subprocess.run(
        cmd, 
        shell=True, 
        check=False,
        capture_output=True, 
        text=True
    )

    if result.stdout:
        for line in result.stdout.splitlines():
            if indent:
                print(f"    {line}")
            else:
                print(line)

    if result.stderr:
        for line in result.stderr.splitlines():
            if indent:
                print(f"    {line}")
            else:
                print(line)

def print_styled(text, style=None, newline=True):
    """
    Prints text with specified styles (bold, italic, colors) using ANSI escape codes.

    Args:
        text (str): The text to print
        style (str or list): Style(s) to apply. Can be:
            - "bold", "italic", "underline"
            - "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"
            - "light_black", "light_red", etc. for lighter colors
        newline (bool): If True (default), adds a newline at the end
    """
    # ANSI escape codes for styles
    styles = {
        # Text styles
        'bold': '\033[1m',
        'italic': '\033[3m',
        'underline': '\033[4m',
        # Colors
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        # Light colors
        'light_black': '\033[90m',
        'light_red': '\033[91m',
        'light_green': '\033[92m',
        'light_yellow': '\033[93m',
        'light_blue': '\033[94m',
        'light_magenta': '\033[95m',
        'light_cyan': '\033[96m',
        'light_white': '\033[97m',
    }

    # Reset code
    reset = '\033[0m'

    # Process styles
    style_codes = []
    if style:
        if isinstance(style, str):
            style = [style]
        for s in style:
            if s in styles:
                style_codes.append(styles[s])

    # Apply styles
    styled_text = ''.join(style_codes) + text + reset

    # Print with or without newline
    end = '\n' if newline else ''
    print(styled_text, end=end)

class Server:

    prop_list = ["name", "command","unmount_command","mounted_time","mount_path","append_mount_path","host","key_path","remote_dir","pre_command","shell","port","tunnel_port","tunnel_host","tunnel_username","tunnel_key_path","remote_tunnel_port","tunnel_forwarded_host"]

    def __init__(self, name, parent_name, command, unmount_command, append_mount_path, mounted_time, mount_path, is_alias = False, aliased_properties = [], host=None, key_path=None, remote_dir=None, pre_command=None, shell=None, port="22", tunnel_port=None, tunnel_host=None, tunnel_key_path=None, remote_tunnel_port=None, tunnel_username=None, tunnel_forwarded_host=None):
        self.is_alias = is_alias
        self.name = name
        self.parent_name = parent_name 
        self.command = command
        self.unmount_command = unmount_command
        self.append_mount_path = append_mount_path
        self.mounted_time = mounted_time
        self.mount_path = mount_path
        self.host = host
        self.key_path = key_path
        self.remote_dir = remote_dir
        self.pre_command = pre_command
        self.shell = shell
        self.port = port
        self.tunnel_port = tunnel_port 
        self.tunnel_host = tunnel_host
        self.tunnel_key_path = tunnel_key_path
        self.remote_tunnel_port = remote_tunnel_port
        self.tunnel_username = tunnel_username
        self.tunnel_forwarded_host = tunnel_forwarded_host
        self.aliased_properties = aliased_properties

    def store_if_not_aliased(self, prop):
        if prop not in self.aliased_properties and self.is_alias is False:
            config['servers'][self.name][prop] = getattr(self, prop, None) 

    def get(self, prop):
        return getattr(self, prop, None)

    def set(self, prop, value, save = True):
        setattr(self, prop, value)
        if save:
            if self.is_alias:
                self.set_aliased(prop, value, False)
            self.save_server()

    def set_aliased(self, prop, value, save = True):
        self.is_alias = True
        if prop not in self.aliased_properties:
            self.aliased_properties.append(prop)
        setattr(self, prop, value)
        if save:
            self.save_server()
    
    def save_server(self):
        if self.is_alias:
            if self.name not in config['aliases']:
                config['aliases'][self.name] = {}
        else:
            if self.name not in config['servers']:
                config['servers'][self.name] = {}

        if self.is_alias:
            for prop in self.aliased_properties:
                config['aliases'][self.name][prop] = getattr(self, prop, None)

        for prop in self.prop_list:
            self.store_if_not_aliased(prop)

        save_config()

    def assemble_mount_command(self):
        if self.get('command') == "sshfs":
            if self.get('port') is not None:
                command = f"{self.get('command')} -p {self.get('port')} {self.get('host')}"
            else:
                command = f"{self.get('command')} {self.get('host')}"
            if self.remote_dir:
                command = command + f":{self.get('remote_dir')}"
            if self.key_path:
                key_path = os.path.expanduser(self.get('key_path'))
                command = command + f" -o IdentityFile={key_path}"
            if self.append_mount_path:
                command = command + f" {self.get('mount_path')}"
                if not os.path.exists(self.get('mount_path')):
                    os.makedirs(self.get('mount_path'), exist_ok=True)
            return command
        else:
            command = f"{self.get('command')}"
            if self.append_mount_path:
                command = command + f" {self.get('mount_path')}"
                if not os.path.exists(self.get('mount_path')):
                    os.makedirs(self.get('mount_path'), exist_ok=True)
            return command

    def assemble_unmount_command(self):
        command = f"{self.get('unmount_command')}"
        if self.append_mount_path:
            command = command + f" {self.get('mount_path')}"
        return command

    def setup_tunnel(self):
        cmd = f"ssh -f -N -L {self.get('tunnel_port')}:{self.get('tunnel_forwarded_host')}:{self.get('remote_tunnel_port')} {self.get('tunnel_username')}@{self.get('tunnel_host')}"
        if self.get('tunnel_key_path') is not None:
            cmd += f" -i {os.path.expanduser(self.get('tunnel_key_path'))}"
        print_styled(cmd, "italic")
        run_command(cmd, indent = False)

    def destroy_tunnel(self):
        cmd = f"kill $(lsof -ti :{self.tunnel_port})"
        print_styled(cmd, "italic")
        run_command(cmd, indent = False)

    def mount(self, exit = True, indent = False):
        self.set("mounted_time", int(time.time()))
        if self.get("tunnel_port") is not None:
            self.setup_tunnel()
        cmd = self.assemble_mount_command()
        print_styled(cmd, "italic")
        run_command(cmd, indent)
        if exit:
            sys.exit(0)

    def unmount(self, exit = True, indent = False):
        cmd = self.assemble_unmount_command()
        if self.get("tunnel_port") is not None:
            self.destroy_tunnel()
        print_styled(cmd, "italic")
        run_command(cmd, indent)
        if exit:
            sys.exit(0)

    def is_latest(self):
        if self.name == last_mounted_server():
            return True
        else:
            return False

    def list(self):
        if not self.is_alias:
            print_styled(f"--- {self.name} {'(latest)' if self.is_latest() else ''}  ---", "bold")
            print(f"Mount command: \"{self.get('command')}\"")
            print(f"Host: \"{self.get('host')}\"")
            print(f"Unmount command: \"{self.get('unmount_command')}\"")
            print(f"Mounted at: {self.get('mounted_time')} {'(latest)' if self.is_latest() else ''}")
            print(f"Mount path: {self.get('mount_path')}")
            print(f"Remote directory: {self.get('remote_dir')}")
            if self.get('port') is not None:
                print(f"Port: {self.get('port')}")
            if self.get('shell') is not None:
                print('- SSH Exec')
                print(f"  Shell: {self.get('shell')}")
            if self.get('pre_command') is not None:
                print(f"  Pre command: {self.get('pre_command')}")
            if self.get('key_path') is not None:
                print(f"  Key path: {self.get('key_path')}")
            if self.get('tunnel_port') is not None:
                print('- SSH Tunnel')
                print(f"  Local tunnel port: {self.get('tunnel_port')}")
                print(f"  Remote tunnel port: {self.get('remote_tunnel_port')}")
                print(f"  Tunnel host: {self.get('tunnel_host')}")
                print(f"  Tunnel username: {self.get('tunnel_username')}")
                print(f"  Tunnel destination: {self.get('tunnel_forwarded_host')}")
                if self.get('tunnel_key_path') is not None:
                    print(f"  Tunnel key path: {self.get('tunnel_key_path')}")
            print_alias = False
            for alias in config['aliases']:
                alias = config['aliases'][alias]
                if alias['server_name'] == self.name:
                    if not print_alias:
                        print('- Aliases')
                        print_alias = True
                    print(f"--- {alias['name']} --- {'(latest)' if alias['name'] == last_mounted_server() else ''}")
                    for prop in alias:
                        if prop != 'server_name' and prop != 'name':
                            if prop == 'mounted_time':
                                print(f"  {prop}: {alias[prop]} {'(latest)' if alias['name'] == last_mounted_server() else ''}")
                            else:
                                print(f"  {prop}: {alias[prop]}")

            print('')


def get_server_or_alias_prop(prop, server, alias, aliased_properties = []):
    if alias:
        if prop in alias:
            if prop not in aliased_properties:
                aliased_properties.append(prop)
            return alias[prop]
        elif prop in server:
            return server[prop]
        else:
            return None
    else:
        if prop in server:
            return server[prop]
        else:
            return None

def get_server(index = 2, server_name = None):
    if index is not None and server_name is None:
        try:
            server_name = sys.argv[index]
        except IndexError:
            print_styled("No server given.", "red")
            sys.exit(0)

    if server_name not in config['servers'] and server_name not in config['aliases']:
        print_styled( f"Server \"{server_name}\" does not exist.", "red")
        sys.exit(0)

    alias = None
    if server_name in config['aliases']:
        is_alias = True
        alias = config['aliases'][server_name]

    if server_name in config['servers']:
        is_alias = False
        server = config['servers'][server_name]

    if is_alias:
        server = config['servers'][alias['server_name']]

    aliased_properties = []
    name = server_name
    if is_alias:
        parent_name = alias['server_name']
    else:
        parent_name = None
    command = get_server_or_alias_prop('command', server, alias, aliased_properties)
    unmount_command = get_server_or_alias_prop('unmount_command', server, alias, aliased_properties)
    append_mount_path = get_server_or_alias_prop('append_mount_path', server, alias, aliased_properties)
    mounted_time = get_server_or_alias_prop('mounted_time', server, alias, aliased_properties)
    mount_path = get_server_or_alias_prop('mount_path', server, alias, aliased_properties)
    host = get_server_or_alias_prop('host', server, alias, aliased_properties)
    key_path = get_server_or_alias_prop('key_path', server, alias, aliased_properties)
    remote_dir = get_server_or_alias_prop('remote_dir', server, alias, aliased_properties)
    pre_command = get_server_or_alias_prop('pre_command', server, alias, aliased_properties)
    shell = get_server_or_alias_prop('shell', server, alias, aliased_properties)
    port = get_server_or_alias_prop('port', server, alias, aliased_properties)
    tunnel_port = get_server_or_alias_prop('tunnel_port', server, alias, aliased_properties)
    tunnel_host = get_server_or_alias_prop('tunnel_host', server, alias, aliased_properties)
    tunnel_key_path = get_server_or_alias_prop('tunnel_key_path', server, alias, aliased_properties)
    remote_tunnel_port = get_server_or_alias_prop('remote_tunnel_port', server, alias, aliased_properties)
    tunnel_username = get_server_or_alias_prop('tunnel_username', server, alias, aliased_properties)
    tunnel_forwarded_host = get_server_or_alias_prop('tunnel_forwarded_host', server, alias, aliased_properties)

    return Server(
            name,
            parent_name,
            command,
            unmount_command,
            append_mount_path,
            mounted_time,
            mount_path,
            is_alias,
            aliased_properties,
            host,
            key_path,
            remote_dir,
            pre_command,
            shell,
            port,
            tunnel_port,
            tunnel_host,
            tunnel_key_path,
            remote_tunnel_port,
            tunnel_username,
            tunnel_forwarded_host
            )


def save_config():
    with open(config_path, 'w') as f:
        json.dump(config, f)
    return True

def add_server():

    print_styled('Adding new server. You will be guided through it.', "bold")

    server_name = "" 
    while server_name in config['servers'] or server_name in config['aliases'] or server_name == "":
        server_name = input("Enter server name: ")

        if server_name in config['servers'] or server_name in config['aliases']:
            print_styled(f"Server \"{server_name}\" already exists. Try another.", "red")


    command = ""
    while command == "":
        command = input("Enter mount command: (e.g. sshfs) ")

    do_port = ""
    while do_port == "":
        do_port = input("Use a port different than 22? (y/n) ")
        if do_port == "y" or do_port == "Y":
            port = ""
            while port == "":
                port = input("Enter port: (e.g. 9000) ")
        else:
            do_port = None
            port = None


    unmount_command = ""
    while unmount_command == "":
        unmount_command = input("Enter unmount command: (e.g. fusermount -u) ")

    mount_path = ""
    while mount_path == "":
        mount_path = input("Enter mount path: (e.g. /mnt) ")

    append_mount_path = True

    host = ""
    while host == "":
        host = input("Enter host: (e.g. user@example.com) ")

    remote_dir = ""
    while remote_dir == "":
        remote_dir = input("Enter remote directory: (e.g. /var/www/public_html) ")

    do_key_path = ""
    while do_key_path == "":
        do_key_path = input("Use key path? (y/n) ")
        if do_key_path == "y" or do_key_path == "Y":
            key_path = ""
            while key_path == "":
                key_path = input("Enter key path: (e.g. ~/.ssh/my_key) ")
        else:
            do_key_path = None
            key_path = None


    ssh_exec = ""
    shell = None
    pre_command = None
    while ssh_exec == "":
        ssh_exec = input("Use SSH exec? (y/n) ")
        if ssh_exec == "y" or ssh_exec == "Y":
            ssh_exec = True

            shell = ""
            while shell == "":
                shell = input("Which shell is being used on the server? (e.g. bash) ")

            do_pre_command = ""
            while do_pre_command == "":
                do_pre_command = input("Execute pre command (any ssh exec commands will be ran like so: {pre_command} && {command})? (y/n)")
                if do_pre_command == "y" or do_pre_command == "Y":
                    pre_command = ""
                    while pre_command == "":
                        pre_command = input("Enter pre command: (e.g. ls -la)")
                else:
                    pre_command = None


    server = Server(
            server_name,
            None,
            command,
            unmount_command,
            append_mount_path,
            None,
            mount_path,
            False,
            [],
            host,
            key_path,
            remote_dir,
            pre_command,
            shell,
            port
            )

    server.save_server()

    do_tunnel = ""
    while do_tunnel == "":
        do_tunnel = input("Does this server require an SSH tunnel to be opened before mounting? (y/n) ")
        if do_tunnel == "y" or do_tunnel == "Y":
            add_tunnel(server_name, False)

    print_styled(f"Added server \"{server_name}\"", "green")

    sys.exit(0)

def add_alias():
    print_styled('Servers: ', "bold")
    try:
        servers = []
        for i, server_name in enumerate(config['servers']):
            servers.append(server_name)
            print(f"{i+1}) {server_name}")
        server_name = input("Choose which server you want to create alias for: ")
        server_name = servers[int(server_name) - 1]
    except IndexError:
        print_styled('Index does not exist.', "red")
        sys.exit(0)
    server = get_server(None, server_name)
    
    alias = ""
    while alias == "":
        alias = input("Enter alias name: ")

        if alias in config['aliases']:
            print_styled(f"Alias \"{alias}\" already exists. Try another.", "red")
            alias = ""



    config['aliases'][alias] = {
            'name': alias,
            'server_name': server_name
            }

    print('Alias setup only includes changing the remote directory and mount path. However, using mnt update you can change any other property.')

    remote_dir = ""
    while remote_dir == "":
        remote_dir = input("Enter remote directory: (e.g. /var/www/public_html) ")
        config['aliases'][alias]['remote_dir'] = remote_dir

    mount_path = ""
    while mount_path == "":
        mount_path = input("Enter mount path: (e.g. /mnt) ")
        config['aliases'][alias]['mount_path'] = mount_path

    print_styled(f"Added alias \"{alias}\" for server \"{server_name}\"", "green")
    save_config()
    sys.exit(0)

def add_tunnel(server_name = None, exit = True):
    if server_name is None:
        try:
            servers = []
            for i, server_name in enumerate(config['servers']):
                servers.append(server_name)
                print(f"{i+1}) {server_name}")
            server_name = input("Choose which server you want to add tunnel to: ")
            server_name = servers[int(server_name) - 1]
        except IndexError:
            print_styled('Index does not exist.', "red")
            sys.exit(0)
    server = get_server(None, server_name)

    tunnel_port = ""
    while tunnel_port == "":
        tunnel_port = input("Enter local tunnel port (the port you want to access from locally): ")
    tunnel_username = ""
    while tunnel_username == "":
        tunnel_username = input("Enter username for tunnel server (e.g. root): ")
    tunnel_host = ""
    while tunnel_host == "":
        tunnel_host = input("Enter tunnel server host (e.g. example.com): ")

    tunnel_forwarded_host = ""
    while tunnel_forwarded_host == "":
        tunnel_forwarded_host = input("Enter destination server host (the end server you want to log in to through the tunnel) (e.g. example-2.com): ")
    remote_tunnel_port = ""
    while remote_tunnel_port == "":
        remote_tunnel_port = input("Enter remote tunnel port (the port you use to log in to the server with, typically 22): ")

    tunnel_key_path = input("Enter tunnel key path (blank for no key): ")
    if tunnel_key_path == "":
        tunnel_key_path = None

    server.set('tunnel_port', tunnel_port)
    server.set('tunnel_host', tunnel_host)
    server.set('tunnel_key_path', tunnel_key_path)
    server.set('remote_tunnel_port', remote_tunnel_port)
    server.set('tunnel_username', tunnel_username)
    server.set('tunnel_forwarded_host', tunnel_forwarded_host)

    print_styled(f"Added tunnel for server \"{server.name}\"", "green")

    if exit:
        sys.exit(0)

def unmount_server():
    if sys.argv[2] == "all":
        print_styled('Unmounting all servers', 'bold')
        for server_name in config['servers']:
            print_styled(f"Unmounting server \"{server_name}\"", "cyan")
            server = get_server(None, server_name)
            try:
                server.unmount(False, True)
            except Exception:
                continue
        for alias in config['aliases']:
            server = get_server(None, alias)
            print_styled(f"Unmounting server \"{alias}\"", "cyan")
            try:
                server.unmount(False, True)
            except Exception:
                continue
        sys.exit(0)
    server = get_server(2)
    server.unmount()

def update_server():
    prop_list = ["mount","unmount","mount_path","append_mount_path","host","key_path","remote_dir","pre_command","shell","port","tunnel_port","tunnel_host","tunnel_key_path","remote_tunnel_port","tunnel_username","tunnel_forwarded_host"]
    try:
        server = sys.argv[2]
        prop = sys.argv[3]
        if prop not in prop_list:
            print_styled(f"Invalid property. Must be one of: {', '.join(prop_list)}", "red")
            sys.exit(0)
        server_command = " ".join(sys.argv[4:])  # Joins with spaces, no extra quotes
    except IndexError:
        print_styled('No server given. Usage: mnt update <server_name> <mount|unmount> <command>.', "red")
        sys.exit(0)

    if server not in config['servers']:
        print_styled(f"Server \"{server}\" does not exist. Use command \"mnt add <server_name> <command>\" to add it.", "red")
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
    elif prop == "pre_command":
        config['servers'][server]['pre_command'] = server_command
    elif prop == "shell":
        config['servers'][server]['shell'] = server_command
    elif prop == "port":
        config['servers'][server]['port'] = server_command
    elif prop == "tunnel_port":
        config['servers'][server]['tunnel_port'] = server_command
    elif prop == "tunnel_host":
        config['servers'][server]['tunnel_host'] = server_command
    elif prop == "tunnel_key_path":
        config['servers'][server]['tunnel_key_path'] = server_command
    elif prop == "remote_tunnel_port":
        config['servers'][server]['remote_tunnel_port'] = server_command
    elif prop == "tunnel_username":
        config['servers'][server]['tunnel_username'] = server_command
    elif prop == "tunnel_forwarded_host":
        config['servers'][server]['tunnel_forwarded_host'] = server_command


    print_styled(f"Updated server \"{server}\" prop \"{prop}\" to \"{server_command}\"", "green")

    save_config()
    sys.exit(0)

def delete_server():
    try:
        server = sys.argv[2]
    except IndexError:
        print_styled('No server given. Usage: mnt delete <server_name>. E.g. \"mnt delete sshfs\"', "red")
        sys.exit(0)

    if server not in config['servers'] and server not in config['aliases']:
        print_styled(f"Server \"{server}\" does not exist. Use command \"mnt add <server_name> <command>\" to add it.", "red")
        sys.exit(0)

    sure = ""
    while sure != "y" and sure != "Y" and sure != "n" and sure != "N":
        sure = input(f"Are you sure you want to delete server \"{server}\"? (y/n) ")
        if sure == "n" or sure == "N":
            sys.exit(0)

    if server in config['aliases']:
        del config['aliases'][server]
    elif server in config['servers']:
        del config['servers'][server]

    save_config()

    print_styled(f"Deleted server \"{server}\"", "green")

    sys.exit(0)

def list_servers():
    print_styled('\nmnt servers:\n', "bold")
    for server in config['servers']:
        server = get_server(None, server)
        server.list()

    sys.exit(0)

def mount(config_server):
    server = get_server(None, config_server['name'])
    server.mount()

def help():
    print_styled('mnt.py', ["bold","italic"])
    print("""
mnt - Mount manager and remote execution tool

Usage:
    mnt <command> [args]
    mnt <server_name>                Mount specified server (shortcut for 'mnt mount')

Commands:
  General:
    help                            Show this help message
    list                            List all configured servers and aliases

  Server Management:
    add                             Interactive server setup wizard
    tunnel                          Interactive SSH tunnel setup wizard
    alias                           Create a new server alias
    delete <name>                   Delete a server or alias
    update <name> <property> <value> Update server properties:
        Properties: command, unmount_command, mount_path, append_mount_path,
                   host, key_path, remote_dir, pre_command, shell

  Mount Operations:
    mount <name>                    Mount a server/alias
    unmount <name|all>              Unmount a server/alias, or all of them
    refresh <name>                  Update mounted timestamp

  Remote Execution:
    ssh-exec [<name>] <command>     Execute command on remote server
                                    - Auto-detects from cwd or last mounted
    ssh <name>                      Logs into an SSH shell

  Navigation:
    cd <name>                       Output mount path for shell integration
    enable-cd                       Show shell integration instructions

Examples:
    mnt add                         # Interactive server setup
    mnt alias                       # Create alias for existing server
    mnt web                         # Mount server 'web'
    mnt ssh-exec web ls -l          # Execute command on 'web'
    mnt update web host user@newhost.com  # Update host property

Server Properties:
    command:        Mount command (e.g. sshfs)
    unmount_command: Unmount command (e.g. fusermount -u)
    mount_path:     Local mount path
    append_mount_path: Whether to append mount path to command (bool)
    host:           Remote host (user@host)
    key_path:       SSH key path
    remote_dir:     Remote directory path
    pre_command:    Command to run before main command
    shell:          Remote shell (e.g. bash)
""")
    sys.exit(0)


def last_mounted_server():
    """Returns name of most recently mounted server or alias, or None"""
    last_name = None
    last_time = None

    for server_name, server in config['servers'].items():
        if server['mounted_time'] is not None:
            if last_time is None or server['mounted_time'] > last_time:
                last_name = server_name
                last_time = server['mounted_time']

    for alias in config['aliases'].values():
        try: 
            if alias['mounted_time'] is not None:
                if last_time is None or alias['mounted_time'] > last_time:
                    last_name = alias['name']
                    last_time = alias['mounted_time']
        except KeyError:
            pass

    return last_name

def get_server_from_mount_path(cwd):
    for group in ('servers', 'aliases'):
        for name, entry in config[group].items():
            if entry['mount_path'] == cwd:
                return name
    return None

def ssh_shell():
    server = get_server(2)

    if server.get('shell') is None:
        print_styled('Error: No shell specified for server', "red")
        sys.exit(1)

    if server.get('port') is not None:
        cmd = f"ssh -p {server.get('port')} -t {server.get('host')}"
    else:
        cmd = f"ssh -t {server.get('host')}"
    if server.get('key_path') is not None:
        cmd += f" -i {os.path.expanduser(server.get('key_path'))}"

    # Properly structure the remote command to first cd then start shell
    remote_cmd = f"'cd {server.get('remote_dir')} && {server.get('shell')} --login'"
    cmd += f" {remote_cmd}"

    print_styled(cmd, "italic")
    os.system(cmd)
    sys.exit(0)


def ssh_exec():
    try:
        # Try to get server name from args
        server_name = sys.argv[2]
        if server_name in config['servers'] or server_name in config['aliases']:
            server = get_server(None, server_name)
        else:
            raise IndexError('Server not found')
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
            print_styled('Error: No server specified, no mount path at provided cwd, and no last-mounted server available', "red")
            print_styled('Usage: mnt ssh-exec [<server_name>] [<mount_path>] <command>')
            sys.exit(1)

        server = get_server(None, server_name)

    # Build SSH command components
    ssh_parts = ['ssh', '-tt']  # Force pseudo-terminal allocation
    if server.get('port') is not None:
        ssh_parts.extend(['-p', str(server.get('port'))])

    # Add identity file if specified
    if server.get('key_path') is not None:
        ssh_parts.extend(['-i', os.path.expanduser(server.get('key_path'))])

    # Check for required host
    if server.get('host') is None:
        print_styled(f'Error: Server "{server_name}" missing host configuration', "red")
        print('Run: mnt enable-ssh-exec to configure')
        sys.exit(1)

    # Add host
    ssh_parts.append(server.get('host'))

    # Handle remote command construction
    remote_cmd = ""
    if server.get('shell') is not None:
        remote_cmd = server.get('shell') + ' -ic "'
    if server.get('remote_dir') is not None:
        # Use sh -c for better quoting behavior
        remote_cmd = remote_cmd + f"cd {shlex.quote(server.get('remote_dir'))} && "
    if server.get('pre_command') is not None:
        remote_cmd = remote_cmd + server.get('pre_command') + " && "

    remote_cmd = remote_cmd + command

    if server.get('shell') is not None:
        remote_cmd = remote_cmd + '" '


    # Execute with proper shell handling
    full_cmd = ssh_parts + [remote_cmd]
    
    if server.get('pre_command') is not None:
        print_styled(f"[{server_name}:{server.get('remote_dir')}] {server.get('pre_command')} && {command}", "italic")
    else:
        print_styled(f"[{server_name}:{server.get('remote_dir')}] {command}", "italic")
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
            print_styled('Error: No server specified and no last-mounted server available', "red")
            print('Usage: mnt cd [<server_name>]')
            sys.exit(1)

    server = get_server(None, server_name)

    if server.get('mount_path') is None:
        print_styled(f"Server \"{server_name}\" does not have a mount path.", "red")
        sys.exit(1)

    print(server.get('mount_path'))
    sys.exit(0)

def refresh_server():
    server = get_server(2)
    server.set("mounted_time", int(time.time()))
    print_styled(f"Refreshed mount time of \"{server_name}\".", "green")

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
        print_styled('mnt.py', ["bold","italic"])
        print_styled('No command given.', "red")
        sys.exit(0)

    if command == 'mount':
        try:
            server = sys.argv[2]
        except IndexError:
            print_styled('No server given. Usage: mnt mount <server_name>. E.g. \"mnt mount sshfs\"', "red")
            sys.exit(0)
        if server in config['servers']:
            mount(config['servers'][sys.argv[2]])
        elif server in config['aliases']:
            mount(config['aliases'][sys.argv[2]])
        else:
            print_styled(f"Server \"{server}\" does not exist. Use command \"mnt add <server_name> <command>\" to add it.", "red")
            sys.exit(0)
    elif command == 'add':
        add_server()
    elif command == 'alias':
        add_alias()
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
    elif command == 'ssh':
        ssh_shell()
    elif command == 'refresh':
        refresh_server()
    elif command == 'tunnel':
        add_tunnel()
    elif command == 'help' or command == '-h':
        help()
    else:
        if command in config['servers']:
            mount(config['servers'][command])
            sys.exit(0)
        elif command in config['aliases']:
            mount(config['aliases'][command])
            sys.exit(0)
        print_styled('Unknown command: ' + command, "red")
        sys.exit(0)

