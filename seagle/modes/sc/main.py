from .script import ScriptsManager
from lib.modes import SimpleMode
from pathlib import Path
import os
import shlex

class SCMode(SimpleMode):
  def init(self):
    self.scripts = ScriptsManager(Path(self.get_config("scripts_path", self.mode_path / "scripts")), self.core)
    self._prompt = self.get_config("prompt", "< 💌 > ")
  
  @property
  def prompt(self):
    return self._prompt
  
  def complete(self, text, line, begidx, endidx):
    if text.startswith(("./", "/")):
      return self._seagle.path_complete(text, line, begidx, endidx)

    base_dir = self.scripts.scripts_path
    completions = self._seagle.path_complete(os.path.join(base_dir, text), line, begidx, endidx)

    return [
      os.path.relpath(path, base_dir) + "/" if os.path.isdir(path) else os.path.relpath(path, base_dir)
      for path in completions
    ]
  
  def _run_script(self, line):
    runner = self.scripts.load_script(shlex.split(line))
    if not runner.config:
      return runner.run(self.core)
      
    wait_timer = 5 if "site" in runner.config.require else 0
    show_info = False if wait_timer == 0 else True
  
    if show_info:
      self.core.console.print_panel(
        "NAME    {name}\nREQUIRE [ [red]{config.require}[/] ]".format_map({"name": runner.filename, "config": runner.config}), 
        title="Script"
      )

    if wait_timer > 0 and not self.core.console.wait(wait_timer, "Running script in"):
      raise Exception("Script canceled to run")
  
    return runner.run(self.core)
  
  def default(self, line):
    return self._run_script(line.raw)
  
  # main func
  def cmd(self, line):
    return self._run_script(line.args)

