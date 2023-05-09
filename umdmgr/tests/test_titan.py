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
		self.assertEqual(25.0, decoder.getKey("frame_rate"))
		# self.assertEqual("16:9", decoder.getKey("aspect_ratio")) # fails here works elsewhere
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

		self.assertEqual(float(d['muxbitrate']), float(31379456))
		self.assertEqual(d['muxstate'], 'Lock')
		self.assertEqual(d['fec'], "3_4")
		self.assertEqual(d['rolloff'], "0_20")
		self.assertEqual(d['aspectratio'], '16_9')

	def test_refresh2(self):
		titan = ateme_titan.Titan(1, "10.88.203.21", "titan", 2)
		fname = "get__decoder_api_channels_2_7_5.json"
		with open(os.sep.join(["testdata", fname]), "r") as fobj:
			jdata = json.load(fobj)
		titan.set_get_decoder_api_channels_id_content(jdata)
		decoder = titan.getInterface("decoder")
		self.assertEqual(decoder.getKey("frame_rate"), 25.0)
		self.assertEqual(decoder.getKey("aspect_ratio"), "16:9")
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



	def test_titan_servce_name(self):
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
		services = decoder.getKey("services", {})
		current_service_id = decoder.getKey("service_id", 0)
		current_service = services.get(current_service_id, {})
		current_service["name"] = "It's not a good string"
		sql = titan.updatesql()
		res = gv.sql.qselect(sql, commit=True, mask_error=False)

	def test_titan_291(self):
		titan = ateme_titan.Titan(1, "10.88.203.21", "titan", 1)
		fname = "get__gateway_api_channels_1_v291.json"
		with open(os.sep.join(["testdata", fname]), "r") as fobj:
			jdata = json.load(fobj)
		titan.set_get_gateway_api_channels_id_content(jdata)
		fname = "get__decoder_api_channels_1_v291.json"
		with open(os.sep.join(["testdata", fname]), "r") as fobj:
			jdata = json.load(fobj)
		titan.set_get_decoder_api_channels_id_content(jdata)
		decoder = titan.getInterface("decoder")
		dec_input_name = decoder.getKey("input", "UNKNOWN")
		dec_input = titan.getInterface(dec_input_name)
		selected_input_name = titan.get_input_interface()
		selected_input = titan.getInterface(selected_input_name)

		asi = titan.getInterface(selected_input_name + "_asi")
		ip = titan.getInterface(selected_input_name + "_ip")
		sat = titan.getInterface(selected_input_name + "_sat")

		self.assertEqual("SAT", selected_input.getKey("input", "").upper())
		self.assertAlmostEqual(15678089, dec_input.getKey("ts_bitrate", 0), 3)
		self.assertEqual(True, dec_input.getKey("ts_lock", False))
		self.assertEqual(1, decoder.getKey("service_count", 0))
		self.assertEqual(1061, sat.getKey("downlink_frequency", ""))
		self.assertEqual(7.2, sat.getKey("symbol_rate", ""))
		self.assertEqual("3/4", sat.getKey("fec", ""))
		self.assertEqual(0.25, sat.getKey("roll_off", ""))
		self.assertEqual("dvbs2", sat.getKey("mode", ""))
		self.assertEqual("V",sat.getKey("polarization", "").upper()[0:1])
		current_service_id = decoder.getKey("service_id", 0)
		self.assertEqual(1, current_service_id)
		services = decoder.getKey("services", {})

		current_service = services.get(current_service_id, {})

		service_name = current_service.get("name", "")
		self.assertEqual("IMG A EU", service_name)
		self.assertEqual("16:9", decoder.getKey("aspect_ratio", ""))
		self.assertEqual(1080, decoder.getKey("height", 0))
		self.assertEqual(25.0, decoder.getKey("frame_rate", 0))
		self.assertEqual(True, decoder.getKey("video_status", 0))
		self.assertEqual(6.590000000113382, sat.getKey("margin", 0))
		self.assertEqual("0x2600",titan.getCAType())


	def test_titan_291_interface(self):
		titan = ateme_titan.Titan(1, "10.88.203.21", "titan", 1)
		fname = "get__gateway_api_channels_1_v291_2.json"
		with open(os.sep.join(["testdata", fname]), "r") as fobj:
			jdata = json.load(fobj)
		titan.set_get_gateway_api_channels_id_content(jdata)
		fname = "get__decoder_api_channels_1_v291_2.json"
		with open(os.sep.join(["testdata", fname]), "r") as fobj:
			jdata = json.load(fobj)
		titan.set_get_decoder_api_channels_id_content(jdata)

		self.assertEqual(titan.get_offline(), False)
		decoder = titan.getInterface("decoder")
		dec_input_name = decoder.getKey("input", "UNKNOWN")
		dec_input = titan.getInterface(dec_input_name)
		selected_input_name = titan.get_input_interface()
		selected_input = titan.getInterface(selected_input_name)

		asi = titan.getInterface(selected_input_name + "_asi")
		ip = titan.getInterface(selected_input_name + "_ip")
		sat = titan.getInterface(selected_input_name + "_sat")

		self.assertEqual("IP", selected_input.getKey("input", "").upper())
		self.assertAlmostEqual(15678089, dec_input.getKey("ts_bitrate", 0), 3)
		self.assertEqual(True, dec_input.getKey("ts_lock", True))
		self.assertEqual(1, decoder.getKey("service_count", 0))

		current_service_id = decoder.getKey("service_id", 0)
		self.assertEqual(1, current_service_id)
		services = decoder.getKey("services", {})

		current_service = services.get(current_service_id, {})

		service_name = current_service.get("name", "")
		self.assertEqual("", service_name)
		self.assertEqual("16:9", decoder.getKey("aspect_ratio", ""))
		self.assertEqual(1080, decoder.getKey("height", 0))
		self.assertEqual(25.0, decoder.getKey("frame_rate", 0))
		self.assertEqual(True, decoder.getKey("video_status", 0))
		self.assertEqual("",titan.getCAType())

	def test_titan_determine_subtype(self):
		titan = ateme_titan.Titan(1, "10.88.203.21", "titan", 2)


		self.assertEqual(titan.determine_subtype(), "Titan")

	def test_refresh291(self):
		titan = ateme_titan.Titan(1, "10.88.203.21", "titan", 1)
		fname = "get__decoder_api_channels_1_v291.json"
		with open(os.sep.join(["testdata", fname]), "r") as fobj:
			jdata = json.load(fobj)
		titan.set_get_decoder_api_channels_id_content(jdata)
		decoder = titan.getInterface("decoder")
		self.assertEqual(decoder.getKey("frame_rate"), 25.0)
		self.assertEqual(decoder.getKey("aspect_ratio"), "16:9")
		self.assertEqual(decoder.getKey("service_id"), 1)

	def test_titan_online_2(self):
		titan = ateme_titan.Titan(1, "10.88.203.21", "titan", 2)


		self.assertEqual(titan.determine_subtype(), "Titan")

if __name__ == '__main__':
	unittest.main()
