from lib.modes import SimpleMode
import shlex


class EVMode(SimpleMode):
  def init(self):
    self._prompt = self.get_config("prompt", " /)/) < - > [{RED}{page.url.path}{RESET}] {GREEN}{page.url.query}{RESET}\n(๑'ᴗ') ")
    self.registers = {}

  @property
  def namespaces(self):
    return {
      **self.registers,
      **self.core.namespaces
    }

  def _eval_line(self, line):
    globs = self.namespaces
    locs = {}
    try:
      # Try to compile as an expression
      code = compile(line, "<input>", "eval")
      result = eval(code, globs, locs)
      return result
    except SyntaxError:
      # If it's not an expression, execute as a statement
      exec(line, globs, locs)

  def _complete(self, text, namespace, sp_word=":", func_suffix=""):
    #namespace = self.namespaces # dict
    #func_suffix = "" # add suffix if function
    #sp_word = ":" # split word
  
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

  def complete(self, text, *args):
    return self._complete(text, self.namespaces, sp_word=".", func_suffix="()")

  def default(self, line):
    return self._eval_line(line.raw)
  
  def cmd(self, line):
    return self._eval_line(line.args)
