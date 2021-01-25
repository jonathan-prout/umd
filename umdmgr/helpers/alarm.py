"""
Created on 1 avr. 2016

@author: prout


============
bagels.alarm
============


The BAGELS alarm module maps RFC 3164 alarm levels onto an Enum. 
RFC 3164 maps the alarm severity on a neumerical scale so alarms can be ranked due to severity. 

The RFC 3164 looks like this:
 
RFC 3164::

        *   0       Emergency: system is unusable
        *   1       Alert: action must be taken immediately
        *   2       Critical: critical conditions
        *   3       Error: error conditions
        *   4       Warning: warning conditions
        *   5       Notice: normal but significant condition
        *   6       Informational: informational messages
        *   7       Debug: debug-level messages
           
           
The Bagels alarm levels are as following:

	*	0	"Emergency",
	*	1	"Critical" ,
	*	2	"Error",
	*	3	"Major",
	*	4	"Minor",
	*	5	"Warning",
	*	6	"Indeterminate",
	*	7	"Notice",
	*	8	"Info",
	*	9	"Cleared",
	*	10	"Debug",
	*	11	"Redundant",
	*	12	"OK"    
	
.. graphviz::

	digraph alarm {
	  
	    subgraph cluster_0{
	        style=filled;
	        color=lightgrey;
	        
	        "Most Severe" [shape=diamond]
	        "Least Severe" [shape=diamond]
	        "Most Severe" -> "Least Severe" [color="black:invis:black"]
	        
	        "Emergency" [shape=rectangle, style=filled, color = "#AA5555"] ;
	        "Critical" [shape=rectangle, style=filled, color = "#BB7777"] ;
	        "Error" [shape=rectangle, style=filled, color = "Red"] ;
	        "Major" [shape=rectangle, style=filled, color = "#f89406"]; 
	        "Minor" [shape=rectangle, style=filled, color = "Orange"] ;
	        "Warning" [shape=rectangle, style=filled, color = "Yellow"] ;
	        "Indeterminate" [shape=rectangle, style=filled, color = "Grey"]; 
	        "Notice" [shape=rectangle, style=filled, color = "#aaaaff"]; 
	        "Info" [shape=rectangle, style=filled, color = "#aaaaff"];
	        "Cleared" [shape=rectangle, style=filled, color = "GreenYellow"];
	        "Debug" [shape=rectangle, style=filled, color = "Green"];
	        "Redundant"[shape=rectangle, style=filled, color = "#42c4A8"];
	        "OK"[shape=rectangle, style=filled, color = "Green"];
	        
	        
	        "Emergency" ->
	        "Critical" ->
	        "Error" ->
	        "Major"->
	        "Minor" ->
	        "Warning" ->
	        "Indeterminate" ->
	        "Notice" ->
	        "Info" ->
	        "Cleared"->
	        "Debug"->
	        "Redundant"->
	        "OK"
	    }
	    { rank=same "Least Severe" "OK"} 
	    { rank=same "Most Severe" "Emergency"} 
	
	}      
"""
from __future__ import absolute_import

from helpers.processing import case_insensitive_enum as enum

_levels = [	
			"Emergency",
			"Critical" ,
			"Error",
			"Major",
			"Minor",
			"Warning",
			"Indeterminate",
			"Notice",
			"Info",
			"Cleared",
			"Debug",
			"Redundant",
			"OK"
		]

level = enum(_levels)

default_level = level.Warning
def level_name_to_int(s):
    i = 0
    s = s.strip().upper()
    for i in range( len(_levels)):
        if _levels[i].upper() == s:
            return i
        
    if bagels.settings.strict:
        raise ValueError("{} is not a known alarm level".format(s))
    else:
        return level.Indeterminate
    
def level_int_to_string(i):
    try:
        return _levels[i]
    except IndexError as e:
        if bagels.settings.strict:
            raise e
        else:
            return "Indeterminate"
def to_string(x):
    """ 1 (int) returns "Critical"
        "1" (str) returns "Critical"
        "Critical" returns "Critical"
    
    """
    try:
        return level_int_to_string(int(x))
    except TypeError:
        return x
    
