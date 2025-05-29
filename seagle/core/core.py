from core.plugins import PluginsManager
from core.config import get_config
from core.apps import AppsManager
from core.console import console
from core.modes import SeaModes
from core.store import Store
from core.site import Site

from core import __version__

from lib.storage import ensure_dirs, Storage
from lib.cmd import BaseCmd

from os import getcwd
from pathlib import Path

from templates import banners

import shlex


class Core:
  def __init__(self, url):
    self.config = get_config()
    self.console = console
    self.store = Store()
    self.storage = Storage("sg_storage")

    self.sites = {}
    self.change_site(url)
  
  @property
  def namespaces(self):
    return {
      "site": self.site,
      "page": self.site.page,
      "core": self,
      "store": self.store,
      "config": self.config,
      "console": self.console
    }

  def resolve_path(self, path):
    try:
        protocol, full_path = path.split("://", 1)
    except ValueError:
        return Path(path)
    base_paths = {
        "seagle": Path(__file__).resolve().parent.parent,
        "cwd": Path(getcwd())
    }
    return base_paths.get(protocol, Path()) / full_path

  def get_site(self, url):
    return Site(url, self.storage.cache)

  def add_site(self, url):
    site = self.sites.get(url)
    if site is None:
      site = self.get_site(url)
      self.sites[site.base_url] = site
    return site

  def change_site(self, url):
    if len(url.strip()) <= 0:
      return f"Current site : [blue]{self.site.url_string}[/]"

    self.site = self.add_site(url)
    return f"Current site : [blue]{url}[/]"
  
  def info(self):
    return "\n".join([f"[red]+------>[/] {k}\n{v}\n" for k, v in self.__dict__.items() if not k.startswith("_")])

class Seagle(BaseCmd):
  def __init__(self, url):
    self.core = Core(url)
    super().__init__(self.core.console)
    # 
    self.apps = AppsManager(Path("apps"), self.core)
    self.plugins = PluginsManager(self.core)

    console.clear()
    self.do_banner(...)
    console.print_center(f"created by [blue]luvbyte[/] 💖 v{__version__}\n")
    console.print_center(f"Target : [blue]{self.core.site.base_url}[/]\n")

    self.modes = SeaModes(Path("modes"), self.config.mode, self)

  @property
  def prompt(self):
    return self.mode.prompt

  @property
  def mode(self):
    return self.modes.mode

  @property
  def config(self):
    return self.core.config

  def do_banner(self, _):
    """
    Prints banner

    usage: banner
    """
    console.print_center(banners.random())
  def do_plugin(self, line):
    """
    Run plugin command

    usage: plugin <name> <command> <args>
    """
    self._exec_command(lambda: self.plugins.run_command(shlex.split(line.args)), True, True)
  
  def do_open(self, line):
    return self.apps.open_app(line.arg_list)
  def complete_open(self, text, *_):
    return [name for name in self.apps.installed if name.startswith(text)]

  def do_luvbyte(self, line):
    """
    Greetings ... :)

    usage: luvbyte <color>
    COLORS : blue, purple, orange...try yourself
    """
    hearts = {
      "blue": "💙", "purple": "💜",
      "orange": "🧡"
    }
    heart = hearts.get(line.args, '🤍')
    text = f" /)/)  {heart} is for you\n( •.•)ノ\n/   /\nし-Ｊ"
    
    console.print(f"{text}\n", markup=False, highlight=False)
  def complete_luvbyte(self, text, *_):
    return [i for i in ("blue", "purple", "orange") if i.startswith(text)]

  def default(self, line):
    self.mode.__run_command__(line)
