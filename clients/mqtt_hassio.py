#!/usr/bin/env python3
# coding=utf-8
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(level = logging.INFO)

import json
import re

class MQTT_config():
	def __init__(self, topic_base, topic_hassio='homeassistant'):
		self.tb = topic_base
		self.tha = topic_hassio

	def get_tb(self): return self.tb
	def get_tha(self): return self.tha


class HA_device():
	def __init__(self, mqtt_cfg, manufacturer, model, model_name, sw_version):
		self.mqtt_cfg = mqtt_cfg
		self.model = model
		self.device = {
			'identifiers': ["%s_%s"%(self.mqtt_cfg.get_tb(), model_name.replace(' ', '_'))],
			'manufacturer': manufacturer,
			'model': model,
			'name': model_name,
			'sw_version': sw_version,
		}

	def get_device(self): return self.device
	def get_model(self): return self.model


class HA_config():
	def __init__(self, mqtt_cfg, ha_dev, name, uid, icon = None, dev_type=None):
		self.mqtt_cfg = mqtt_cfg
		self.ha_dev = ha_dev
		self.name = name
		self.name_topics = self.name.replace(' ', '_').replace(',', '_')
		self.uid = str(uid)
		self.icon = icon
		self.cfg = self.generate_config()
		if (self.icon != None): self.append('icon', self.icon)
		if (dev_type): eval('self.set_cfg_'+dev_type+'()')

	def get_availability_topic(self): return self.mqtt_cfg.get_tb()+'/'+self.name_topics+'/availability'
	def get_state_topic(self): return self.state_topic
	def get_listen_topic(self): return self.listen_topic
	def get_cmd_topic(self): return self.cmd_topic
	def get_cfg(self): return self.cfg
	def get_uid(self): return self.uid

	def generate_config(self):
		self.state_topic = self.mqtt_cfg.get_tb()+'/'+self.ha_dev.get_model()+'/'+self.name_topics
		self.listen_topic = self.mqtt_cfg.get_tb()+'/'+self.ha_dev.get_model()
		return {
			"device": self.ha_dev.get_device(),
			"availability": [
				{"topic": self.get_availability_topic()}
			],
			'availability_mode': 'all',
			'name': self.name,
			'state_topic': self.get_state_topic(),
			"unique_id": str(self.uid)+'_'+self.name.replace(' ', '_'),
			"value_template": '{{ value_json.state }}',
			"platform": "mqtt",
		}

	def append(self, key, value): self.cfg[key] = value
	def set_cfg_switch(self):
		self.cfg_topic = '%s/switch/%s/%s/config'%(self.mqtt_cfg.get_tha(), self.ha_dev.get_model().replace(' ', '_'), 'switch_'+self.uid)
		self.cmd_topic = self.mqtt_cfg.get_tb()+'/'+self.ha_dev.get_model()+'/'+self.name_topics+'/set'
		self.json_attr_topic = self.mqtt_cfg.get_tb()+'/'+self.ha_dev.get_model()+'/'+self.name_topics+'/set'
		self.append('command_topic', self.get_cmd_topic())
#		self.append('json_attributes_topic', self.json_attr_topic)
		self.append('payload_off', 'OFF')
		self.append('payload_on', 'ON')

if __name__ == "__main__":
	mqtt_cfg = MQTT_config('smarthouse')
	ha_dev = HA_device(mqtt_cfg, 'Weekend', 'DBus Relays', 'DBus Relay', '0.0.2')

	ha_cfg_sw1 = HA_config(mqtt_cfg, ha_dev, 'Lamp: кабинет Гриши.', '001', icon='mdi:lightbulb', dev_type='switch')
	ha_cfg_sw2 = HA_config(mqtt_cfg, ha_dev, 'Lamp: коридор',        '002', icon='mdi:lightbulb', dev_type='switch')
#	ha_cfg.set_cfg_switch()

	print(ha_cfg_sw1.cfg_topic, json.dumps(ha_cfg_sw1.get_cfg()), '\n')
	print(ha_cfg_sw2.cfg_topic, json.dumps(ha_cfg_sw2.get_cfg()))
