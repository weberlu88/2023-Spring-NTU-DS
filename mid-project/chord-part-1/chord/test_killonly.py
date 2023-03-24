#!/usr/bin/python3

import msgpackrpc
import time
import subprocess

def killall_running_nodes():
	# Get list of all processes with name starting with "chord"
	try:
		processes = subprocess.check_output(["pgrep", "chord"], universal_newlines=True).split()
		# Kill each process in the list
		for pid in processes:
			subprocess.run(["kill", pid])
			
		print(f"info: Killed {len(processes)} chord processes.")
	except:
		print("info: no runnung chord processes.")

killall_running_nodes()
