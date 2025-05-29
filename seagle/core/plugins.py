import importlib
import os

from pathlib import Path


class PluginsManager:
  def __init__(self, core):
    self._plugins = {}
    self.plugins_path = Path("plugins")
    self.load_plugins(core)
  
  def load_plugins(self, core):
    for plugin_name in os.listdir(self.plugins_path):
      module_file = importlib.import_module(f"{self.plugins_path}.{plugin_name}.main")
      self._plugins[plugin_name] = module_file
      # load event
      module_file.plugin._sg = core
      module_file.plugin._emit("load")

  def run_command(self, args):
    if len(args) <= 0:
      raise Exception("Missing plugin name!!!")
    plugin_name = args[0]
    plugin_module = self._plugins.get(plugin_name)
    if plugin_module is None:
      raise Exception(f"plugin [red]'{plugin_name}'[/] not found")

    return plugin_module.plugin if len(args) <= 1 else plugin_module.plugin._run_command(args[1], *args[2:])

