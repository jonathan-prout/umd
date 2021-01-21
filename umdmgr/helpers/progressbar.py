from __future__ import print_function
from __future__ import division
from builtins import range
from past.utils import old_div
def clearscreen():
	import os
	# works on Windows or Linux, also Vista
	os.system(['clear','cls'][os.name == 'nt'])
	

def progressbarhelper(top, bottom):
	if bottom == 0:
		percentage = 0 #Don't try to divide by zero
	else:
		percentage = (old_div(top, bottom)) * 50
	line ="*                                                     *"
	progressbar = ""
	for i in range (1, 50):
			if percentage >= i:
					progressbar += "="
			else:
					progressbar += " "
	print("* [" + progressbar + "] *")
	samples = "%d"%top  + " / " + "%d"%bottom + ", " + "%d"%(percentage * 2) + "%"
	printline = line[0:2] + samples + line[len(samples)+2:]
	print(printline)

def progressbar(top, bottom, headding="Progress", cls="True"):
		top = float(top)
		bottom = float(bottom)
		if cls == "True":
			clearscreen()
		print("*******************************************************")
		line ="*                                                     *"
		printline = line[0:2] + headding + line[len(headding)+2:]
		print(printline)
		progressbarhelper(top, bottom)
		print("*******************************************************")
		
def progressbar2line(top1, bottom1, top2, bottom2, headding="Progress"):

	clearscreen()
	print("*******************************************************")

	line ="*                                                     *"
	printline = line[0:2] + headding + line[len(headding)+2:]
	print(printline)

	top = float(top1)
	bottom = float(bottom1)
	progressbarhelper(top, bottom)
	top = float(top2)
	bottom = float(bottom2)
	bottom = float(bottom2)
	progressbarhelper(top, bottom)
	print("*******************************************************")
