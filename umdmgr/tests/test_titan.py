import json
import os
import unittest

from server.equipment import ateme_titan
from server import umdserver
from server import gv
from helpers import mysql
import multiprocessing

def startdb():
	gv.sql = mysql.mysql()
	gv.sql.gv = gv
	gv.sql.autocommit = True
	gv.sql.mutex = multiprocessing.RLock()

class TestTitan(unittest.TestCase):
	def setUp(self) -> None:
		startdb()

	def test_refresh(self):
		titan = ateme_titan.Titan(1, "10.88.203.21", "titan", 2)
		fname = "get__decoder_api_channels_2.json"
		with open(os.sep.join(["testdata", fname]), "r") as fobj:
			jdata = json.load(fobj)
		titan.set_get_decoder_api_channels_id_content(jdata)
		decoder = titan.getInterface("decoder")
		self.assertEqual(decoder.getKey("frame_rate"), 25.0)
		self.assertEqual(decoder.getKey("aspect_ratio"), "16_9")
		self.assertEqual(decoder.getKey("service_id"), 1)

	def test_sql1_sql_generation_noerror(self):
		titan = ateme_titan.Titan(1, "10.0.0.1", "titan", 1)
		fname = "get__decoder_api_channels_1.json"
		with open(os.sep.join(["testdata", fname]), "r") as fobj:
			jdata = json.load(fobj)
		titan.set_get_decoder_api_channels_id_content(jdata)
		sql = titan.updatesql()

	def test_sql2_sql_generation_noerror(self):
		titan = ateme_titan.Titan(1, "10.0.0.1", "titan", 2)
		fname = "get__decoder_api_channels_2.json"
		with open(os.sep.join(["testdata", fname]), "r") as fobj:
			jdata = json.load(fobj)
		titan.set_get_decoder_api_channels_id_content(jdata)
		sql = titan.updatesql()

	def test_sql4_muxstate(self):
		titan = ateme_titan.Titan(1, "10.0.0.1", "titan", 2)
		fname = "titandata2.json"
		with open(os.sep.join(["testdata", fname]), "r") as fobj:
			titan.data = json.load(fobj)

		sql = titan.updatesql().split(",")
		d = {}
		for line in sql:
			try:
				k, v = line.split("=")
				d[k.strip()] = v.strip().replace("'", "")
			except ValueError:
				continue

		self.assertEqual(d['muxbitrate'], '31379456')
		self.assertEqual(d['muxstate'], 'Lock')
		self.assertEqual(d['fec'], '3_4')
		self.assertEqual(d['rolloff'], '0_20')
		self.assertEqual(d['aspectratio'], '16_9')

	def test_refresh2(self):
		titan = ateme_titan.Titan(1, "10.88.203.21", "titan", 2)
		fname = "get__decoder_api_channels_2_7_5.json"
		with open(os.sep.join(["testdata", fname]), "r") as fobj:
			jdata = json.load(fobj)
		titan.set_get_decoder_api_channels_id_content(jdata)
		decoder = titan.getInterface("decoder")
		self.assertEqual(decoder.getKey("frame_rate"), 25.0)
		self.assertEqual(decoder.getKey("aspect_ratio"), "16_9")
		self.assertEqual(decoder.getKey("service_id"), 2910)

	def test_titan_catype_1(self):
		titan = ateme_titan.Titan(1, "10.88.203.21", "titan", 2)
		fname = "get__gateway_api_channels_1_2.json"
		with open(os.sep.join(["testdata", fname]), "r") as fobj:
			jdata = json.load(fobj)
		titan.set_get_gateway_api_channels_id_content(jdata)
		fname = "get__decoder_api_channels_1_2.json"
		with open(os.sep.join(["testdata", fname]), "r") as fobj:
			jdata = json.load(fobj)
		titan.set_get_decoder_api_channels_id_content(jdata)
		decoder = titan.getInterface("decoder")

		self.assertEqual(titan.getCAType(), "0x2610")


	def test_titan_catype_2(self):
		titan = ateme_titan.Titan(1, "10.88.203.21", "titan", 2)
		fname = "get__gateway_api_channels_3_v286.json"
		with open(os.sep.join(["testdata", fname]), "r") as fobj:
			jdata = json.load(fobj)
		titan.set_get_gateway_api_channels_id_content(jdata)
		fname = "get__decoder_api_channels_3_v286.json"
		with open(os.sep.join(["testdata", fname]), "r") as fobj:
			jdata = json.load(fobj)
		titan.set_get_decoder_api_channels_id_content(jdata)
		decoder = titan.getInterface("decoder")

		self.assertEqual(titan.getCAType(), "0x2610")

	def test_titan_online_2(self):
		titan = ateme_titan.Titan(1, "10.88.203.21", "titan", 2)


		self.assertEqual(titan.determine_subtype(), "Titan")

if __name__ == '__main__':
	unittest.main()
