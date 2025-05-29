from lib.modes import SimpleMode
from lib import colors

from .modules.fn import Fn
import shlex



class XMode(SimpleMode):
  def init(self):
    self._prompt = self.get_config("prompt", " /)/) < _ > [{BLUE}{page.url.path}{RESET}] {GREEN}{page.url.query}{RESET}\n(๑'ᴗ') ")
    # expose objects
    self.registers = {
      "fn": Fn()
    }

  @property
  def namespaces(self):
    return {
      **self.registers,
      **self.core.namespaces
    }

  def _complete(self, text, namespace, sp_word=":", func_suffix=""):
    if not text:
      return list(namespace)
  
    parts = text.split(sp_word)
    obj = namespace
    completions = []
    prefix = sp_word.join(parts[:-1])
  
    def check_property(obj, name):
      try:
        attr = type(obj).__dict__.get(name)
        if isinstance(attr, property):
          return None
        return getattr(obj, name)
      except Exception:
        return None
  
    for i, part in enumerate(parts):
      is_last = (i == len(parts) - 1)
  
      if isinstance(obj, dict):
        # For dict, only allow completion on first part
        if i > 0:
          return []
        matches = [k for k in obj if k.startswith(part)]
        if is_last:
          completions = [f"{prefix}:{m}" if prefix else m for m in matches]
        obj = obj.get(part)
  
      else:
        try:
          attrs = dir(obj)
          matches = [
            attr for attr in attrs
            if attr.startswith(part) and (not attr.startswith('_') or part.startswith('_'))
          ]
  
          if is_last:
            if text.endswith(sp_word):
              # Text ends with colon -> suggest callable methods with "()"
              completions = [
                f"{m}()" if callable(check_property(obj, m)) else m
                for m in matches
              ]
            else:
              completions = [
                f"{prefix}{sp_word}{m}()" if callable(check_property(obj, m)) else f"{prefix}{sp_word}{m}"
                for m in matches
              ]
  
          obj = getattr(obj, part, None)
        except Exception:
          return []
  
      # If obj is dict and not the last part, abort early
      if isinstance(obj, dict) and not is_last:
        return []
  
    if len(completions) == 1:
      value = completions[0]
      if value.endswith("()"):
        return [value[:-2] + func_suffix]
      return completions + [value + sp_word]
  
    return completions

  def complete(self, text, *_):
    return self._complete(text, self.namespaces)

  def _exec_line(self, line):
    args = []
    kwargs = {}
  
    obj = self.namespaces  # assuming you're starting from this dict
  
    arg_split = shlex.split(line)
    command_chain = arg_split[0].split(":")
  
    # Resolve the method/attribute/key chain
    for cmd in command_chain:
      if isinstance(obj, dict):
        obj = obj.get(cmd)
      else:
        obj = getattr(obj, cmd, None)
  
      if obj is None:
        raise Exception(f"Method or key '{cmd}' not found")
  
    def resolve(value):
      if value.startswith("$"):
        return eval(value[1:], self.namespaces, {})
      return value
  
    # Parse arguments
    for arg in arg_split[1:]:
      if "=" in arg:
        k, v = arg.split("=", 1)
        kwargs[k] = resolve(v)
      else:
        args.append(resolve(arg))
    return obj(*args, **kwargs) if callable(obj) else obj

  def default(self, line):
    return self._exec_line(line.raw)

  def cmd(self, line):
    return self._exec_line(line.args)
