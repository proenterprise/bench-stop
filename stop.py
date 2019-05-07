""" stop.py is an attempt at creating an easy 'bench stop' command

    Expected improvements:
    - import port suffix from config/redis_cache.conf - done
    - check for exceptions - done
    - use SIGTERM - done
    - Refactor code and merge with bench 
            - check for production where stop command will use supervisor
            - check for non-ubuntu platforms
"""


import os, socket, errno

# Declaring part of ports.
# Getting port suffix from current  redis config.
ports = [1100, 1200, 1300, 900, 800]
lines = {}
port_suffix = 0;
sockets = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

with open("./config/redis_cache.conf") as config_file:
    for line in config_file:
        key, value = line.partition(" ")[::2]
        lines[key.strip()] = value.strip()
    port_suffix =  lines["port"][-1:]
config_file.close()

# Closing open ports after combining each port prefix and suffix
for port in ports:
  port = int("".join([str(port), str(port_suffix)]))
  try:
    sockets.bind(("127.0.0.1", port))
  except socket.error as e:
    if e.errno == errno.EADDRINUSE:
      os.system("echo 'shutdown' | redis-cli -h 127.0.0.1 -p %d" % port)
      if e.errno == errno.EADDRINUSE:
        os.system("sudo kill `sudo lsof -t -i: %d`" % port)
      else:
        print 'Port %d' % port, 'was closed'
  else:
    print 'Port %d' % port, 'already closed'
sockets.close()
print 'bench stopped'
