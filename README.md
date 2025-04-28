# mnt - Mount Manager & Remote Command Tool

A simple tool to store and execute the commands you use to mount and unmount filesystems. Intended for use with e.g. sshfs.

Note: There is *no* security built into this tool. Use only in completely trusted environments.

## Installation
```bash
git clone https://github.com/simonpacis/mnt.git
cd mnt
sudo ln -s $(pwd)/mnt.py /usr/local/bin/mnt
```

## Basic Usage
```bash
# Add a server
mnt add myserver "sshfs user@host:/path /local/mount" "fusermount -u /local/mount"

# Mount/unmount
mnt myserver          # Mounts 'myserver'
mnt unmount myserver  # Unmounts

# SSH command execution
mnt enable-ssh-exec myserver example.com user
mnt ssh-exec myserver ls -la

# Shell integration
mnt cd myserver       # Changes to mount directory (requires setup)
mnt enable-cd        # Shows setup instructions
```

## Full Documentation
Run `mnt help` for complete command reference.
