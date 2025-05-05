# mnt - Mount Manager & Remote Command Tool

A simple, dependency free Python tool to store and execute the commands you use to mount and unmount filesystems. Intended for use with e.g. sshfs. Allows you to execute commands on the server as well, see section SSH Exec.

Note: There is *no* security built into this tool. Use only in completely trusted environments.

## Installation
```bash
git clone https://github.com/simonpacis/mnt.git && cd mnt && mv mnt.py /usr/local/bin/mnt && sudo chmod +x /usr/local/bin/mnt
```

## Help 
```bash
mnt - Mount and remote command management tool

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
```

## SSH Exec
I typically use Vim, and in vim you can type "!command" to execute a shell command. Lacking this functionality when I use sshfs, I decided to implement what I call "SSH Exec" into mnt. Using it and a simple Vim-function, I am able to type "!! command", and execute the command on the remote server. This is not enabled by default for an added server, but must be manually enabled through the command enable-ssh-exec. [See this Gist for my Vim-implementation]()
