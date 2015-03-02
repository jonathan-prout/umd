#!/usr/bin/env python
## TODO load at run type
sql = None
def load():
	pass
snmp_refresh_types = {
	'asi output mode'									:'full',
	'asi service remux'									:'locked',
	'aspect ratio'										:'locked',
	'Biss Status'										:'locked',
	'CASID'												:'locked',
	'castatus'											:'full',
	'DeviceType'										:'full',
	'director_encrypted'								:'full',
	'dr5000ChannelConfigurationInputSatInterface'		:'sat',
	'dr5000StatusDecodeCurrentProgramScrambled'			:'sat',
	'dr5000StatusInputSatModulation'					:'sat',
	'dr5000StatusInputSatRollOff'						:'sat',
	'dr5000StatusInputType'								:'sat',
	'Eb / No'											:'sat',
	'encoder temperature centrigrade'					:'full',
	'frame rate den'									:'full',
	'frame rate num'									:'full',
	'input_selection '									:'all',
	'inputtsbitrate'									:'all',
	'inputtsbitrate '									:'all',
	'inSatModType'										:'sat',
	'inSatSetupFecRate'									:'sat',
	'inSatSetupInputSelect '							:'sat',
	'inSatSetupRollOff'									:'sat',
	'inSatSetupRollOff '								:'sat',
	'inSatSetupSatelliteFreq'							:'sat',
	'inSatSetupSymbolRate'								:'ip',
	'ip input has vlan'									:'ip',
	'ip input multicast address'						:'ip',
	'ip input udp port'									:'ip',
	'ip input vlan ID'									:'ip',
	'ip output remux'									:'full',
	'ip output scramble'								:'full',
	'LockState'											:'all',
	'mux biss encrypted session word'					:'locked',
	'mux biss session word'								:'locked',
	'mux bitrate'										:'all',
	'mux scrambling'									:'locked',
	'mux status'										:'all',
	'numServices'										:'full',
	'pilotSymbolStatus'									:'sat',
	'polarisation'										:'sat',
	'SatLockState'										:'sat',
	'SatStatusFEC'										:'sat',
	'service name'										:'locked',
	'ServiceID'											:'full',
	'Table_Service_ID'									:'full',
	'Table_Service_Name'								:'full',
	'tableEncryptionType'								:'full',
	'video aspect ratio'								:'locked',
	'video bandwidth'									:'full',
	'video bitrate'										:'full',
	'video delay'										:'full',
	'video frame rate'									:'full',
	'video GOP length'									:'full',
	'video GOP structure'								:'full',
	'Video Horizontal Resolution'						:'full',
	'video max bitrate'									:'full',
	'video pid'											:'full',
	'video profile level'								:'full',
	'video state'										:'full',
	'video vertical resolution'							:'full'
}