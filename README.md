# mnt - Mount Manager & Remote Command Tool

A simple, dependency free Python tool to store and execute the commands you use to mount and unmount filesystems. Intended for use with e.g. sshfs. Allows you to execute commands on the server as well, see section SSH Exec.

Note: There is *no* security built into this tool. Use only in completely trusted environments.

## Installation
```bash
git clone https://github.com/simonpacis/mnt.git && cd mnt && mv mnt.py /usr/local/bin/mnt && sudo chmod +x /usr/local/bin/mnt
```

## Help 
```bash
mnt - Mount manager and remote execution tool

Usage:
    mnt <command> [args]
    mnt <server_name>                Shortcut for: mnt mount <server_name>

Commands:
  General:
    help                            Show this help message
    list                            List all configured servers
    <server_name>                   Mount server

  Mounting:
    mount <server_name>            Mount the specified server
    unmount <server_name>          Unmount the specified server
    cd <server_name>               Change to server's mount path (requires shell integration)

  Server Management:
    add <name> <mount_cmd> <unmount_cmd> [mount_path]
                                    Add a server config. mount_path is optional.
    update <name> <property> <value>
                                    Update a server property. Run: mnt update <name> help
    delete <name>                   Delete a server

  SSH Execution:
    ssh-exec [<server>] <command>  Run command on remote server
    enable-ssh-exec <server> <host> <user> [key_path] [remote_dir] [shell] [pre_command]
                                    Enable SSH execution support

  Misc:
    refresh <server_name>          Refresh 'mounted_time' for a server
    enable-cd                      Show instructions for shell cd integration

Examples:
    mnt add web "sshfs user@host:/path" "umount ~/mnt/web" ~/mnt/web
    mnt web                        Mounts 'web'
    mnt ssh-exec web ls -l         Executes remote command
    mnt enable-ssh-exec web host.com user ~/.ssh/id_rsa /remote/path
```

## SSH Exec
I typically use Vim, and in vim you can type ```!command``` to execute a shell command. Lacking this functionality when I use sshfs, I decided to implement what I call "SSH Exec" into mnt. Using it and a simple Vim-function, I am able to type ```!! command```, and execute the command on the remote server. This is not enabled by default for an added server, but must be manually enabled through the command enable-ssh-exec. [See this Gist for my Vim-implementation](https://gist.github.com/simonpacis/ac0bf1aa8587a152fa0de27dbdaa4b93).
