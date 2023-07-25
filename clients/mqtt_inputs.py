#!/usr/bin/env python3
# coding=utf-8
# -*- coding: utf-8 -*-

from gi.repository import GLib, Gio, GObject
from dbus_client import DBusGPIO_Client
import itertools
import logging
logging.basicConfig(level = logging.INFO)

import json

import paho.mqtt.client as MQTT
import yaml
import time
import atexit

from mqtt_hassio import MQTT_config, HA_device, HA_config
from mqtt_config import SH_Config


class MQTT_Sensors(DBusGPIO_Client):
	""" Revers output, controlled via MQTT"""
	def init(self, mqtt, common, inputs):
		self.name = common['name']
		self.inputs = [ i for i in inputs ]
		super().init( self.inputs, [] )

		self.get_inputs_state = lambda : { i:self.inputs_state[i] for i in self.inputs }
		logging.info("Started...")

		self.mqtt_cfg = MQTT_config(mqtt['topic'])
		self.ha_dev = HA_device(self.mqtt_cfg, common['manufacturer'], common['model'], common['model_name'], common['sw_version'])

		self.ha_cfg = []
		for inp in inputs:
			self.ha_cfg.append( [inp, HA_config(self.mqtt_cfg, self.ha_dev, inputs[inp], inp, icon='mdi:gesture-double-tap', dev_type='sensor')] )


		self.mqtt_client = MQTT.Client(str(self.trigger_name))	#create new instance
		self.mqtt_client.on_connect = self.mqtt_on_connect
		self.mqtt_client.on_message = self.mqtt_message		#attach function to callback
		self.mqtt_client.connect(mqtt['brocker'])		#connect to broker
		self.mqtt_client.loop_start()				#start the loop

		self.HA_status = self.mqtt_cfg.get_tha()+'/status'
		self.mqtt_client.subscribe([(self.ha_cfg[0][1].get_listen_topic(), 0), (self.ha_cfg[0][1].get_listen_topic()+'/#', 0), (self.HA_status, 0)])
		atexit.register(self.discovery_unreg)


	def dev_online(self):
		for out, dev in self.ha_cfg:
			self.mqtt_client.publish(dev.get_availability_topic(), 'online', retain=True)
	def dev_offline(self):
		for out,dev in self.ha_cfg:
			self.mqtt_client.publish(dev.get_availability_topic(), 'offline', retain=True)


	def mqtt_send_current_switch_state(self, out, dev, state):
		self.mqtt_client.publish(dev.get_state_topic(), '{"state":"%s"}'%('ON' if (state) else 'OFF'), retain=True )

	def mqtt_on_connect(self, client, userdata, flags, rc):
		print("Connected with result code "+str(rc))
		self.discovery_send()

	def discovery_unreg(self):
		self.dev_offline()
		self.mqtt_client.loop_stop()

	def discovery_send(self):
		for out, dev in self.ha_cfg:
			#if out == 42:
			#	print(dev.cfg_topic)
			self.mqtt_client.publish(dev.cfg_topic, json.dumps(dev.get_cfg()), retain=True)
			time.sleep(0.2)
		#self.dev_offline()
		time.sleep(2)
		self.dev_online()
		for inp, dev in self.ha_cfg:
			self.mqtt_send_current_switch_state(inp, dev, self._GetInputState(inp))

	def mqtt_message(self, client, userdata, message):
		msg = str(message.payload.decode("utf-8"))
		print( message.topic, msg )
		if ((message.topic == self.HA_status) and (msg == 'online')):
			print('Update status on HA...')
			time.sleep(5)
			self.discovery_send()
		else:
			print("Received message: ", msg)
#		elif msg in ('ON', 'OFF'):
#			for out, dev in self.ha_cfg:
#				if (message.topic == dev.get_cmd_topic()):
#					self.On(out, 'mqtt') if (msg == 'ON') else self.Off(out, 'mqtt')
#					break

	def _InputChanged(self, num, state):
		print("Public event on MQTT...")
#	def _OutputChanged(self, num, state, comments):
		for inp, dev in self.ha_cfg:
			if (num == inp):
				self.mqtt_send_current_switch_state(inp, dev, state)
				break

if __name__ == "__main__":
	cfg = SH_Config.from_config("/etc/SmartHouse/mqtt_gpios_inputs.yaml")
	mq = MQTT_Sensors(cfg['mqtt'], cfg['common'], cfg['sensors'])
	del cfg

	try:
		loop = GLib.MainLoop()
		loop.run()
	except KeyboardInterrupt:
		print("Interrupted")
