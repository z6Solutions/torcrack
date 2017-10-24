# torcrack

[A simple Tor enabled, multi-process SSH dictionary attack in Python3.]

# requirements

-argparse

-PySocks

-Paramiko

-tor

# installation

git clone https://github.com/norksec/torcrack.git

pip3 install argparse pysocks paramiko

apt-get install -y tor

# usage

Make sure the tor service is running:

service tor restart

python3 torcrack.py -h for commands

# to do:

-try to reduce SSH Banner errors with a higher number of parallel processes
