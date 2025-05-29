from core.core import Seagle

from core.config import ConfigSingleton
from lib.parser import parse_config

from core.models import ConfigModel
from sys import argv

ConfigSingleton()._set_config(parse_config("config.json", ConfigModel))

SITE = input("Enter url : ")
#
seagle = Seagle(SITE)
seagle.cmdloop()

