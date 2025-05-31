import shlex
from lib.utils import dynamic_import
from lib.parser import parse_config
from pydantic import BaseModel, Field


class ScriptConfigModel(BaseModel):
  description: str = Field("", description="Description")
  require: str = Field("page, console", description="require")
  lang: str = Field("py", description="Language to parse")
  code: str = Field("", description="Description")


# Script handlers
class ScriptBase:
  def __init__(self, script_path, get_script):
    self.script_path = script_path
    self.get_script = get_script
  
    self.config = None
    
    self.init()

  @property
  def filename(self):
    return self.script_path.stem
  
  def init(self):
    pass

  def __depricated_parse_custom_format(self, text: str, match_prefix: str) -> dict:
    lines = text.strip().splitlines()
    result = {}
    current_key = None
    current_value = []
  
    for line in lines:
      if line.startswith(match_prefix):
        # Save previous section
        if current_key is not None:
          result[current_key] = '\n'.join(current_value).strip()
  
        # Split the line into key and optional value
        parts = line[1:].split(' ', 1)
        current_key = parts[0].strip()
        current_value = [parts[1].strip()] if len(parts) > 1 else []
      else:
        current_value.append(line)

    # Save last section
    if current_key is not None:
      result[current_key] = '\n'.join(current_value).strip()

    return result

  def _parse_custom_format(self, text: str, match_prefix: str, stop_key: str) -> dict:
    lines = text.strip().splitlines()
    result = {}
    current_key = None
    current_value = []
  
    i = 0
    while i < len(lines):
      line = lines[i]
      if line.startswith(match_prefix):
        if current_key is not None:
          result[current_key] = '\n'.join(current_value).strip()
  
        line_content = line[len(match_prefix):].lstrip()
        if ' ' in line_content:
          key, value = line_content.split(' ', 1)
          key = key.strip()
          value = value.strip()
        else:
          key = line_content.strip()
          value = ''
  
        if key == stop_key:
          code_lines = [value] if value else []
          code_lines.extend(lines[i + 1:])
          result['code'] = '\n'.join(code_lines).strip()
          return result
  
        current_key = key
        current_value = [value] if value else []
      else:
        current_value.append(line)
      i += 1
  
    if current_key is not None:
      result[current_key] = '\n'.join(current_value).strip()
  
    return result

  def parse_file(self, filename, match_prefix, stop_key):
    with open(filename, "r") as f:
      return ScriptConfigModel(**self._parse_custom_format(f.read(), match_prefix, stop_key))

  def run(self, core, args):
    return None

class SGScriptHandler(ScriptBase):
  def init(self):
    self.config = self.parse_file(self.script_path, ":", "code")

  def lang_py(self, sg):
    exec(self.config.code, { "sg": sg })
    return sg.retvalue

  def lang_lua(self, sg):
    from lupa import LuaRuntime
    runtime = LuaRuntime(unpack_returned_tuples=True)
    runtime.globals().sg = sg
    runtime.execute(self.config.code)
    return sg.retvalue

  def run(self, core, args):
    sg = self.get_script({ name: core.namespaces.get(name) for name in self.config.require.split(",") if name in core.namespaces }, args)
    func = {k: getattr(self, k) for k in dir(self) if k.startswith("lang_")}.get(f"lang_{self.config.lang}")
    if not callable(func):
      raise Exception(f"lang '{self.config.lang}' not support")
    return func(sg)

class TextHandler(ScriptBase):
  def run(self, core, args):
    with open(self.script_path, "r") as file:
      return file.read()

# handlers for extensions
HANDLERS = {
  "": SGScriptHandler,
  ".txt": TextHandler
}

def create_handler(script_path, get_script):
  ext = script_path.suffix
  handler = HANDLERS.get(ext)
  if handler is None:
    raise Exception(f"Handler not found for '[red]{ext}[/]' extension")

  return handler(script_path, get_script)

def run_script(script_path, get_script, core):
  return create_handler(script_path, get_script).run(core)
