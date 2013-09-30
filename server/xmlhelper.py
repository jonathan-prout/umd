#################################
#
# xmlhelper, library of routines for
# ipgp player to handle xml files
#
#################################

# 11/03/11 - JP  Cleaned up comments.
from xml.dom import minidom



def stringtoxml(string):
	# stringtoxml takes a string and returns an xml
	# object using minidom.parse.
	# This is useful since other xmlhelper scripts require 
	# xml objects as their input.
	#from taskscript import debug
	#debug("String To XML has been called with a " + str(type(string)) + " object.")
	from xml.dom import minidom
	import StringIO
	# Python's minidom parse module breaks with the & symbol in strings. 
	# Omneon will reply with a & in the file URI for username & password on exporters
	# since this part of the file is not needed we can simply string-replace it
	string = string.replace("&","_")
	filelikeobject = StringIO.StringIO(string)
	xml = minidom.parse(filelikeobject)
	return xml

def getAttributesFromTags(tag, attribute, document):
	# takes tag and attribute as string and document as file like object
	# returns list of the attributes' values
	"""
	try:
		xmldoc = minidom.parse(document)
		taglist = xmldoc.getElementsByTagName(tag)
	except (IOError, OSError):  
		taglist = document.getElementsByTagName(tag)
	"""
	taglist = document.getElementsByTagName(tag)
	returnlist = []
	i = 0
	while i < len(taglist):
		tag = taglist[i]
		try:
			tagattr = tag.attributes[attribute]
			returnlist.append(tagattr.value)
		except:
			pass
				
	 
		i = i + 1
	return returnlist

def getAttributesFromTagsConditional(tag, attribute, document, condition, value):
	# takes tag and attribute as string and document as file like object
	# returns list of the attributes' values as before, but only where condition = value
	#print attribute
	taglist = document.getElementsByTagName(tag)
	returnlist = []
	i = 0
	while i < len(taglist):
		tag = taglist[i]
		try:
			tagattr = tag.attributes[attribute]
			tagcondition = tag.attributes[condition]
			if tagcondition.value == value: 
				returnlist.append(tagattr.value)
		except:
			pass        
		i = i + 1
	return returnlist

def getTextFromTag(tag, document):
	# Tag as string. Document as file like object
	# returns a list. each item in the list is a string. Each item corresponds to  an occurance of the tag. 
	taglist = document.getElementsByTagName(tag)
	returnlist = []
	i = 0
	while i < len(taglist):
		tagiterator = taglist[i]
		try:
			returnlist.append(tagiterator.firstChild.data)
		except:
			pass
		i += 1
	return returnlist
				
def getTextFromTagWithin(tagtoget, containedwithintag, document):
	# Tag as string. containedwithintag as string, Document as file like object
	# returns a list. each item in the list is a string. Each item corresponds to  an occurance of the tag. 
	#<containedwithintag>
	#	<tagtoget>This text will be returned</tagtoget>
	#</containedwithintag>
	#<othertag>
	#	<tagtoget>This text will not</tagtoget>
	#</othertag>
	
	taglist = document.getElementsByTagName(containedwithintag)
	returnlist = []
	i = 0
	while i < len(taglist):
		tagiterator = taglist[i]
		returnlist.append(getTextFromTag(tagtoget, tagiterator))
		i += 1
	return returnlist
