from __future__ import absolute_import
from __future__ import division
from past.builtins import basestring
from builtins import bytes
from builtins import chr
from builtins import hex
from builtins import str, getattr
from builtins import range


from builtins import object
from past.utils import old_div

import numbers
import datetime
import json
import re 
from base64 import b64encode, b64decode 
import unicodedata
import typing

class processingError(Exception):
	"""Specific error on processing so we can handle data we no to be wrong"""
	pass

def hexdecode(s:str)->bytes:
	""" Decodes hex str to bytes 
	"""
	
	l = []
	for i in range(0, len(s), 2):
		if s[i:i+2] != "0x":
			l.append(int(s[i]+s[i+1], 16))
	return bytes(l)



def b64encode_jpeg(data):
	return b64encode(data)

	
def toNumber(val):
	if isinstance(val, numbers.Number):
		return val  #it's already a number
	elif isinstance(val, basestring): # it's a string
		val = val.replace(" ", "")
		try:
			return ord(val)
		except (SyntaxError, TypeError, ValueError):
			pass 
		if val.replace('.','',1).isdigit(): #it's a string with 0 or 1 decimal points in it
			if "." in val:
				return float(val) #it's a float
			else:
				
				return int(val) #it's an int
		else:
			if "0x" in val:
					return ord(hexdecode(val))
			else:
				n = 0
				for b in range(len(val)):
					n += ord(val[b]) << (8 * (len(val) -1 -b))
				return n 
					
				
	return float(val) # Just try to make it a float anyway. 
def lessthan(val1, val2):
	try:
		return val1 < val2
	except TypeError:
		return toNumber(val1) < toNumber(val2)

def greaterthan(val1, val2):
	
	try:
		return val1 > val2
	except TypeError:
		return toNumber(val1) > toNumber(val2)

def _not(val1, val2): 
	
	return val1 != val2

def equals(val1, val2): 
	
	return val1 == val2


def contains(s, match):
	return match in s
def inrange(num, data):
	try:
		low, high = data
	except Exception as e: #Don't catch BaseException
		return True
	low = int(low)
	high = int(high)
	try:
		return  all([
			float(num) >= low, float(num) <= high
			])
				
	except (TypeError, ValueError):
		return False

def notinrange(num, data):
	return not inrange(num, data)


def dict_replace(data, replacements):
	""" simillar to dict.get(data, "") but casts data as either string or int"""
	if any((isinstance(data, list), isinstance(data, tuple))):
			for i in range(len(data)):
				data[i] = dict_replace(data[i], replacements)
			return data
	for func in (str, int):
		try:
			
			return replacements[func(data)]
		except KeyError:
			continue
		except ValueError:
			continue
	return data

def floatReplace(numerator, data = {"replacements":{}, "default":None}):
	""" trim text and make a float. supply a dict like {"replacements"[replacement 1, replacement2], "default"-1}"""
	for r in data["replacements"]:
		numerator = numerator.replace(r, "")
	numerator = numerator.strip()
	try:
		return float(numerator)
	except Exception as e: #Don't catch BaseException
		return data["default"]
def floatDivision(numerator, denominator):
	return float(numerator)/ denominator



def findbrackets(s):
	""" returns a list of text in brackets 
		eg s = "(spam),(eggs)"
		returns ["spam", "eggs"]
	"""
	l = []
	while ")" in s:
		res = s[s.find("(")+1:s.find(")")]
		if res == "":
			break
		l.append(res)
		s = s[s.find(")")+1:]
	return l

def appendToText(data, text_):
	return "%s%s" % (text_, data)

def getEnumFromMib(d):
	""" dict from enum in compiled mib """
	res = {}
	for k, v in list(d.items()):
		try:
			if v.get("nodetype") == "namednumber":
				res[v.get("number")] = k 
		except (AttributeError, TypeError):
			continue
	return res

def noop(*args, **kwargs):
	""" Does nothing
	"""
	pass

def makeDictKeysStrings(d):
	for k, v in list(d.items()):
		if isinstance(k, (int, float)):
			d[str(k)] = v
			del d[k]
		if isinstance(v, dict):
			makeDictKeysStrings(v)
			

def gettypename(t):
	""" typename from compiled mib"""
	for key in ["name", "basetype"]: 
		name = t.get(key)
		if name: 
			return name
	return ""
def processStr(data, ignored=None):
		""" process string for database insertion """
		if not isinstance(data, (str, bytes)):
			""" If I have a list of strings, then do as for each list """
			if hasattr(data, "__iter__"):
				for i in range(len(data)):
					data[i] = processStr(data[i])
				return data 
			else:
				data = str(data)  # SHould raise ValueError?
		if ignored is None: 
			ignored = r'[^\w]'
		data = decodeUTF8(data)
		data = data.strip()
		data = unicodedata.normalize('NFKD', data).encode('ascii', 'ignore')
		data = data.decode("ascii") #required py3
		"""
		data = data.replace(';', ' ')
		data = data.replace('%', ' ')
		data = data.replace('&', ' ')
		data = data.replace('*', ' ')
		data = data.replace(',', ' ')
		data = data.replace('?', ' ')
		data = data.replace('{', ' ')
		data = data.replace('}', ' ')
		data = data.replace('(', ' ')
		data = data.replace(')', ' ')
		data = data.replace('[', ' ')
		data = data.replace(']', ' ')
		data = data.replace('^', ' ')
		data = data.replace('+', ' ')
		data = data.replace('|', ' ')
		data = data.replace('-', ' ')
		data = data.replace('_', ' ')
		data = data.replace('"', ' ')
		data = data.replace('\'', ' ')
		data = data.replace('#', ' ')
		data = data.replace(':', ' ')
		data = data.replace('!', ' ')
		data = data.replace('`', ' ')
		data = data.replace('.', ' ')
		data = data.replace('\n', '')
		"""
		data = data.strip()
		data = re.sub(ignored, '', data)
		return data

_compiledRegexes = {}
def regexMatchGroup(s, regex):
	s = decodeUTF8(s)
	if regex not in _compiledRegexes:
		_compiledRegexes[regex] = re.compile(regex)
	return _compiledRegexes[regex].match(s).group()
	
	
def decodeUTF8(data):
	""" bytes or str to str """
	try:
		return data.decode("UTF-8")
	except AttributeError: # Python 3 hackery
		return data 
	except UnicodeDecodeError as e:
		raise processingError(str(e) )


def macstr(data, ignored= None):
	def h(b): #byte to 2 digit hex zero padded
		return "{:>02}".format(hex(b)[2:].upper())
	bs = data.encode("ISO-8859-1") #Decode to bytes
	return ":".join([h(b) for b in bs]) #Format as string
def encodeUTF8(data):
	""" str or bytes to bytes """
	try:
		return data.encode("UTF-8")
	except AttributeError: # Python 3 hackery
		return data 
	except UnicodeDecodeError as e:
		raise processingError(str(e) )
	

	
class enum(object):
	""" supply an iterable constructor. The instance now gets these as attributes starting from zero.
	"""

	
	__locked = False
	def __init__(self, l):
		i = 0
		self._attriblist = l
		for x in l:
			setattr(self, x, i)
			i += 1
		self.__locked = False
	def __getitem__(self, item):
		return self._attriblist[item]
	def __contains__(self, item):
		return item in range(len(self._attriblist))
	
	
	
	def __setattr__(self, name, value):
		if self.__locked:
			print(f"Prevented assignment to {name}")
		else:
			object.__setattr__(self, name, value)
class case_insensitive_enum(enum):
	""" This enum has a getattr that checks for a lower case version of the enum values 
	"""
	def __getattr__(self, a):
		for i in range(len(self._attriblist)):
			if a.lower() == self._attriblist[i].lower():
				return 	self.__dict__[self._attriblist[i]]
		raise AttributeError 


class bitopt(object):
	def __init__(self, value):
		
		self.value = int(value) 
	def __repr__(self, *args, **kwargs):
		return "bvaluetopt ({})".format(self.value)
	def __eq__(self, other):
		return self.value == other 
	def __contains__(self, other)->bool:
		return self.value & int(other) == self.value 
	def __or__(self, other):
		return  bitopt(other.__or__(self.value))
	def __and__(self, other):
		return int(other).__and__(self.value)
	def __int__(self):
		return self.value 
	def __str__(self):
		return str(self.value)
class bitmask(object):
	""" supply an iterable constructor. The instance now gets these as attributes as bits starting from 1.
	"""
	__locked = False
	def __init__(self, l):
		i = 1
		self._attriblist = l
		for x in l:
			setattr(self, x, bitopt(i))
			i = i << 1
		self.__locked = False
	def __getitem__(self, item)->int:
		return getattr(self, item)
	def __contains__(self, other)->bool:
		return hasattr(self, other)
	
	def compStrList(self, strList: typing.List[str])->int:
		""" Supply a string list, and get an int of the compared strings """
		value = 0
		for item in strList: 
			value +=  int(self[item]) 
		return value 
	
	def compare(self, other)->typing.Generator[int, None, None]:
		if isinstance(other, (bitopt,int)):
			for attr in self._attriblist:
				a = getattr(self, attr)
				if other & a == a:
					yield a 
		elif isinstance(other,(list, tuple)):
			for i in other:
				for attr in self._attriblist:
					a = getattr(self, attr)
					if i & a == a:
						yield a 
		else:
			raise TypeError("Call this with int or list, tuple of ints")
	
			
	
	
	
	def __setattr__(self, name, value):
		if self.__locked:
			print(f"Prevented assignment to {name}")
		else:
			object.__setattr__(self, name, value)
def uniqueAdd(l, items):
	for item in items:
		if item not in l:
			l.append(item)
	return l


def uniqueKey(key, items, target):
	l = target.getKey(key)
	l2 = uniqueAdd(l, items)
	if l2 != l:
		target.setKey(key, l2)
	
def hasAttrOrKey(obj, key):
	if hasattr(obj, "get_key"):
		return obj.get_key(key)
	else:
		return hasattr(obj, key)   
	
	
def floatSimilar(num1, num2, marginPercent):
	""" returns true if num1 and num2 are numeric and  within margin percent of each other """
	try:
		num1 = float(num1)
	except (TypeError, ValueError):
		return False
	try:
		num2 = float(num2)
	except (TypeError, ValueError):
		return False	
	marginPercent = float(marginPercent)/ 100
	
	if num1 + (num1 * marginPercent) > num2:
		if num1 - (num1 * marginPercent) < num2:
			return True
	return False

def ipv4equal(ip1, ip2):
	""" list of int for octets or string for ipv4 address
	'192.168.0.1' or [192,168,0,1]"""
	if not ip1:
		return False
	if not ip2:
		return False
	if isinstance(ip1, basestring):
		ip1 = [int(octet) for octet in ip1.split(".")]
	if isinstance(ip2, basestring):
		ip2 = [int(octet) for octet in ip2.split(".")] 
	for i in range(4):
		if ip1[i] != ip2[i]:
			return False
	return True

def boolean(val, *args, **kwargs):
	try:  # BOOL, INT, 
		return int(val) > 0
	except Exception as e: #Don't catch BaseException
		pass
	if val.lower() in ["true", "yes"]:
		return True
	elif val.lower() in ["false", "no"]:
		return False
	
	return False







def model_key_format(model):
	d = {}
	for k in list(model.keys()):
		d[k] = {"nodetype":"virtual", "type":model.conf["properties"].get(k, {}).get("type", "")}
	return d


def ipv4str(data, null = None):
	return ".".join(([str(ord(x)) for x in data]))

def findSpaces(s):
	spaces = []
	i = 0
	while s:
		space = s.find(" ")
		if not space: break
		i += space
		spaces.append(i)
		s = s[space+1:]
		i += 1
	return spaces


def decodeHexString(s:str)->str:
	"""Decodes a string of hex to an ascii string
	
	:example: "656E6700" returns "eng\0"
	"""
	r = ""
	for h in range(0,len(s), 2):
		i = int(s[h:h+2], 16)
		o = chr(i)
		r += o 
	return r

def encodeHexString(s:str)->str:
	"""Encodes a string of hex to an ascii string
	 
	:example
	:  "eng\0"  returns  "656E6700"
	"""
	r = ""
	for h in range(0,len(s)):
		i = ord(s[h])
		o = "{:>02s}".format(hex(i)[2:]).upper()
		r += o 
	return r


