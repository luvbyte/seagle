from lib.modes import Mode
import shlex



class SGMode(Mode):
  def init(self):
    self.add_cmd(self.cmd, markup=True, highlight=True, plain=False)
    self.add_complete(self.complete)

  def _auto_complete_word(self, options, text, line):
    """Auto completes word and stops"""
    args = line.strip().split()
    return [c for c in options if c.startswith(text)] if len(args) <= 1 or args[1] not in options else []
  def _auto_complete_word_leg(self, options, text, line):
    if not line:
      return options
    return [c for c in options if c.startswith(text)]
  
  def do_mode(self, mode):
    if len(mode) <= 0:
      return f"Current mode: [green]{self._seagle.modes.mode}[/]"
    return self._seagle.modes.set_mode(mode)
  def complete_mode(self, *args):
    return self._auto_complete_word(self._seagle.modes.list, *args)

  def do_goto(self, url):
    return self.core.site.set_page(url)
  def complete_goto(self, *args):
    return self._auto_complete_word_leg(self.core.site.pages.keys(), *args)

  def do_change(self, url):
    return self.core.change_site(url)
  def complete_change(self, *args):
    return self._auto_complete_word(self.core.sites.keys(), *args)
  
  def _code(self, _):
    code = []
    try:
      while True:
        line = input()
        if line.strip() == ":qr":
          break
        else:
          code.append(line)
    except KeyboardInterrupt:
      return ""
    return "\n".join(code)

  def do_code(self, args):
    return exec(self._code(args), self.core.namespaces)

  def cmd(self, line):
    args = line.arg_list
    if len(args) < 1:
      raise Exception("Subcommand required!!")

    return getattr(self, f"do_{args[0]}", lambda *_: f"command [red]'{args[0]}'[/] not found")(" ".join(args[1:]))
  
  def complete(self, text, line, begidx, endidx):
    completes_func = [name[3:] for name in dir(self) if name.startswith("do_")]
    args = line.split(" ") # [sg, mo]
    if len(args) > 1 and args[1] in completes_func:
      return getattr(self, "complete_" + args[1])(text, " ".join(args[1:]))

    return [name for name in completes_func if name.startswith(text)]
