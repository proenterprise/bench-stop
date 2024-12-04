#!/usr/bin/env python

"""
Port Management Utility for Bench

This script manages bench service ports by gracefully shutting them down or forcefully
closing them if necessary. It handles ports for different services (1100x, 1200x, etc.)
where 'x' is determined by the redis_cache.conf configuration.

Usage:
    cd ~/bench-directory
    python3 stop.py

The script will attempt a graceful port shutdown first, followed by a forceful
closure if needed. Supports both Linux and other Unix-based systems.
"""

import os, socket, errno, time, platform

def get_port_suffix():
    """
    Reads the port suffix from redis_cache.conf file.
    
    Returns:
        str: Last digit of the port number from config, or '0' if not found
    
    Exits:
        If redis_cache.conf file is not found in config directory
    """
    try:
        with open("./config/redis_cache.conf") as f:
            for line in f:
                if line.startswith('port'):
                    return line.split()[1][-1]
    except IOError:
        print('Error: Ensure this is running from your bench directory, ./config/redis_cache.conf not found.')
        exit(1)
    return '0'

def stop_port(port, is_linux):
    """
    Attempts to stop services running on a specific port.
    
    First tries to bind to the port to check if it's in use.
    If port is in use:
    1. Attempts graceful port shutdown
    2. If still in use, forces port closure using OS-specific commands
    
    Args:
        port (int): Port number to stop
        is_linux (bool): True if running on Linux, False otherwise
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", port))
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            # Try graceful Redis shutdown first, redirect stderr to /dev/null
            os.system(f"echo 'shutdown' | redis-cli -h 127.0.0.1 -p {port} 2>/dev/null")
            time.sleep(1)
            
            # Force kill if still in use
            if is_linux:
                os.system(f"fuser {port}/tcp -k")
            else:
                os.system(f"lsof -i tcp:{port} | grep -v PID | awk '{{print $2}}' | xargs kill")
    finally:
        sock.close()
        print(f'Closed Port {port}')

def main():
    """
    Main execution function.
    
    Determines port suffix and OS type, then attempts to stop services
    on all required ports (1100x, 1200x, 1300x, 900x, 800x).
    """
    port_suffix = get_port_suffix()
    is_linux = 'Linux' in platform.platform()
    
    for base_port in [1100, 1200, 1300, 900, 800]:
        port = int(f"{base_port}{port_suffix}")
        stop_port(port, is_linux)
    
    print('bench stopped')

if __name__ == '__main__':
    main()