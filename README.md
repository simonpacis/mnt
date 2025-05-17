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
```

## SSH Exec
I typically use Vim, and in vim you can type ```!command``` to execute a shell command. Lacking this functionality when I use sshfs, I decided to implement what I call "SSH Exec" into mnt. Using it and a simple Vim-function, I am able to type ```!! command```, and execute the command on the remote server. This is not enabled by default for an added server, but must be manually enabled through the command enable-ssh-exec. [See this Gist for my Vim-implementation](https://gist.github.com/simonpacis/ac0bf1aa8587a152fa0de27dbdaa4b93).
