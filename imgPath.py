from systemName import systemName
from pathlib import Path
import os

def imgPath():
	if systemName()=="windows":
		return "C:/captcha.jpeg"
	else:
		return str(Path.home())+"/captcha.jpeg"
