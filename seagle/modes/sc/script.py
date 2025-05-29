import os
from pathlib import Path
from lib.script import Script
from .handlers import create_handler

def check_script_path(path: Path):
  if not path.exists() or path.is_dir():
    return None
  return path

class ScriptsManager:
  def __init__(self, scripts_path, core):
    self.scripts_path = scripts_path

  # resolve url, rel, abs paths for script
  def resolve_path(self, script_name):
    # paths too look for file
    if script_name.startswith("./"):
      return Path(os.getcwd(), script_name)
    elif script_name.startswith("/"):
      return Path(script_name)
    else:
      return self.scripts_path / script_name

  def run_script(self, args, core):
    return self.load_script(args).run()

  def load_script(self, args):
    if len(args) <= 0:
      raise Exception("Require script name!!!")
    
    script_name = args[0]
    # check and fetch protocols here
    script_path = check_script_path(self.resolve_path(script_name))
    if script_path is None:
      raise Exception(f"Script [red]'{script_name}'[/] not found")
    
    return create_handler(script_path, lambda apis: Script(script_path, args[1:], apis))
