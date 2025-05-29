from lib.plugin import create_plugin

plugin = create_plugin()

@plugin.on("load")
def on_load():
  pass

@plugin.cmd("eho")
def on_echo(*args):
  print(args)
