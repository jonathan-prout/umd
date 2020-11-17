octShift = [24,16,8,0]
def ipRange(net, mask):
	
	binNet = 0
	On = 0
	for oct in net.split("."):
		binNet += int(oct) << octShift[On]
		On += 1
		
	On = 0
	binMask = 0
	for oct in mask.split("."):
		binMask += int(oct) << octShift[On]
		On += 1
		
	subnet = binNet & binMask
	myIP = subnet
	iprange = []
	while myIP & binMask == subnet:
		iprange.append(printIP(myIP))
		myIP += 1
	return iprange
		

def printIP(l):
     octs = []
     for o in octShift:
             octs.append(((255 << o) & l) >> o)
     return "%d.%d.%d.%d"%(octs[0],octs[1],octs[2],octs[3])

def printIP(l):
     octs = []
     octShift = [24,16,8,0]    
     for o in octShift:
             octs.append(((255 << o) & l) >> o)
     return "%d.%d.%d.%d"%(octs[0],octs[1],octs[2],octs[3])

def ipv4toint(net):

    binNet = 0
    On = 0
    for _oct in net.split("."):
        binNet += int(_oct) << octShift[On]
        On += 1
    return binNet

def ismulticast(ipv4addrss):
    return ipv4toint(ipv4addrss) & (0b11110000<<24)  == ipv4toint("224.0.0.0")

