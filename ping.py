import subprocess
from systemName import systemName

def ping(host):
	#Returns True if destination is recheble
	if systemName()=="windows":
		param = "-n"
	else:
		param = "-c"
	return subprocess.call(["ping", param, "1", host])==0
