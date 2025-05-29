import os
import pickle

class DataFile:
  def __init__(self, file_path, data):
    self.file_path = file_path
    self.set(data)

  def exists(self):
    return os.path.exists(self.file_path)

  def get(self):
    with open(f"{self.file_path}.pkl", "rb") as file:
      return pickle.load(file)
    
  def set(self, data):
    with open(f"{self.file_path}.pkl", "wb") as file:
      return pickle.dump(data, file)

  @property
  def data(self):
    return self.get()

class DataObj:
  def __init__(self, data):
    self._data = data
  
  def set(self, data):
    self._data = data
  
  def get(self):
    return self._data

class Data:
  def __init__(self, storage):
    self.storage = storage
    self._data = {}
  
  @property
  def items(self):
    return self._data

  # saves data to file
  def sg_data(self, key, func, dtype=None):
    db_data = self._data.get(key)
    if db_data is not None:
      return db_data.get()

    data = func()

    if dtype == "df":
      db_data = DataFile(self.storage.path / key, data)
    else:
      db_data = DataObj(data)

    self._data[key] = db_data
    return data
