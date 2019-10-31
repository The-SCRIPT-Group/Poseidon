import platform
def systemName():
	#returns System Name i.e. "windows" or "linux" in lower case
	return platform.system().lower()
