from importlib import import_module
import os

class SeaModes:
  def __init__(self, modes_path, mode, seagle):
    self.modes_path = modes_path
    self._seagle = seagle
    self._modes = {}
    self._load_modes()
    self.set_mode(mode)

  def _load_modes(self):
    for name in os.listdir(self.modes_path):
      module = import_module(f"{self.modes_path}.{name}.main")
      obj = getattr(module, f"{name.upper()}Mode", None)
      # self._seagle.config.modes[name] = module.CONFIG
      if obj is None:
        raise Exception(f"mode '{name}' not found")
      self._modes[name] = obj(name, self._seagle)

  @property
  def list(self):
    return list(self._modes.keys())

  def set_mode(self, name):
    mode = self._modes.get(name)
    if mode is None:
      raise Exception(f"mode '{name}' not found")
    
    self.mode = mode
  
  def is_mode(self, name):
    return name == self.mode.name
