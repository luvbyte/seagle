#from sys import exit
#from os import getcwd
#from pathlib import Path

class ConfigSingleton:
  _instance = None
  _config = None

  def __new__(cls):
    if cls._instance is None:
      cls._instance = super(ConfigSingleton, cls).__new__(cls)
    return cls._instance

  def _set_config(self, config):
    self._config = config

  def get_config(self):
    if self._config is None:
      raise Exception("Config not intialised")
      exit()
    return self._config

def get_config():
  return ConfigSingleton().get_config()
