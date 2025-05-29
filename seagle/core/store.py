
class Store:
  def __init__(self):
    pass

  @property
  def items(self):
    return self.__dict__

  def clear(self):
    self.__dict__.clear()

