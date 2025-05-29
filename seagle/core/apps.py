from lib.utils import dynamic_import
import os

# basic module
class AppBase:
  def __init__(self, app_name, apps_path, core):
    self.app_name = app_name
    self.apps_path = apps_path
    self.app_path = apps_path / app_name
    self.module_file = dynamic_import(f"{self.app_path / 'main.py'}", f"app_{self.app_name}")

    self._module = self.module_file.SGApp(self.app_name, self.app_path, core) # sea module class instance
  
  def run(self):
    return self._module._run_module()

class AppsManager:
  def __init__(self, apps_path, core):
    self.sea_core = core
    self.apps_path = apps_path
  
  @property
  def installed(self):
    return os.listdir(self.apps_path)
  
  def load_module(self, module_name, *args):
    # module file
    if not (self.apps_path / module_name).exists():
      raise Exception(f"App : [red]{module_name}[/] not found")
    return AppBase(module_name, self.apps_path, self.sea_core, *args)

  def open_app(self, arg_list):
    if len(arg_list) <= 0:
      raise Exception("Enter app name to use!!")

    return self.load_module(arg_list[0]).run()
