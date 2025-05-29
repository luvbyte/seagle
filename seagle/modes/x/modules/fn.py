

class Fn:
  def __init__(self):
    self.about = "This is 'fn' module"

  def info(self, obj, key=None):
    if key:
      return f"[red]+------[/] {key}\n{obj.__dict__.get(key, '[red]Key not found!!![/]')}"
    return "\n".join([f"[red]+------>[/] {k}\n{v}\n" for k, v in obj.__dict__.items() if not k.startswith("_")])
  
  def __str__(self):
    return self.about
