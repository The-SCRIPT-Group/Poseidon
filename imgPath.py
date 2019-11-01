from systemName import systemName
from pathlib import Path
import os

def imgPath():
	#returns path to store captcha accordig to OS
	if systemName()=="windows":
		return "C:/captcha.jpeg"
	else:
		return str(Path.home())+"/captcha.jpeg"
