from urllib.parse import urlparse

from core.page import Page


class Site:
  def __init__(self, url, storage):
    parsed_url = urlparse(url)
    # http://localhsot:8000
    self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    self.url = urlparse(self.base_url)

    self.storage = storage.open_folder(f"{self.url.scheme}_{self.url.hostname}_{self.url.port if self.url.port else '80'}")

    self.pages = {}

    if len(parsed_url.path.strip()) >= 0:
      query = f"?{parsed_url.query}" if parsed_url.query else ""
      self.set_page(f"{parsed_url.path}{query}")
    else:
      self.set_page("/")

  @property
  def page(self):
    return self.current_page
  
  def add_page(self, path):
    return self.pages.setdefault(path, self.get_page(path))
  
  def get_page(self, path):
    path = path if path.startswith("/") else f"/{path}"
    return Page(f"{self.base_url}{path}", self.storage)

  # set page  
  def set_page(self, path):
    page = self.pages.get(path)
    if page is None:
      page = self.get_page(path)
      self.pages[page.url.path] = page

    self.current_page = page
  
