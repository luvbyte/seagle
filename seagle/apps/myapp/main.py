from lib.app import App

class SGApp(App):
  @property
  def prompt(self):
    return "App > "


