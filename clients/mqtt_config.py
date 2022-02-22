#!/usr/bin/env python3
#coding=utf-8
#-*- coding: utf-8 -*-

import yaml


class SH_Config(dict):
	def __init__(self, **cfg):
		super().__init__()
		self.__dict__ = self
		for key in cfg: self.__setitem__(key, cfg[key])

	@staticmethod
	def from_config(config_yaml_path):
		with open(config_yaml_path) as file:
			device_config = yaml.safe_load(file)
			device = SH_Config(**device_config)
			return device


if __name__ == "__main__":
	cfg = SH_Config.from_config("/etc/SmartHouse/mqtt_gpios.yaml")

	for key in cfg:
		print(key, ' === ', cfg[key], '\n')
