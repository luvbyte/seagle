import requests
from bs4 import BeautifulSoup

from core.models import PageConfig
from urllib.parse import urlparse
from lib.utils import hash_text

from core.data import Data

class Response:
  def __init__(self, res, ctype):
    self._raw = res # restricted
    self.url = self._raw.url
    self.content_type = ctype
    
    self.status_code = self.raw.status_code
    self.headers = self.raw.headers

    self._content = self.raw.text

    self.init()
  
  def init(self):
    pass

  @property
  def content(self):
    return self._content

  @property
  def raw(self):
    return self._raw

  def info(self):
    return "\n".join([f"[red]+------>[/] {k}\n{v}\n" for k, v in self.__dict__.items() if not k.startswith("_")])

class HTMLResponse(Response):
  def init(self):
    self._content = BeautifulSoup(self.raw.content, "html.parser")

class JSONResponse(Response):
  def init(self):
    self._content = self.raw.json()

def get_response(res) -> Response:
  ctype = res.headers.get("Content-Type")
  if "text/html" in ctype:
    return HTMLResponse(res, ctype)
  elif "application/json" in ctype:
    return JSONResponse(res, ctype)
  else:
    return Response(res, ctype)

class Page:
  def __init__(self, url, storage):
    # raw url
    self.url = urlparse(url)
    self.base_url = f"{self.url.scheme}://{self.url.netloc}"
    # update redability
    self.storage = storage.open_folder(f'paths/{hash_text(self.url.path)}')
    self.config = PageConfig(**{
      "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
      }
    })
    # page data to store
    self.data = Data(self.storage.open_folder(".data"))

  @property
  def url_string(self):
    query = f"?{self.url.query}" if self.url.query else ""
    return f"{self.base_url}{self.url.path}{query}"

  def fetch(self, url=None, method="GET", body=None, headers=None, cookies={}, cache=False):
    """
    Send request using requests
    """
    url = f"{self.base_url}{url}" if url else self.url_string
    headers = self.config.headers.update(headers) if headers else self.config.headers
    if cache:
      return self.data.sg_data(hash_text(url), lambda: requests.request(url=url, method=method, headers=headers, data=body, cookies=cookies))
    return requests.request(url=url, method=method, headers=headers, data=body, cookies=cookies)

  def response(self, *args, **kwargs) -> Response:
    """
    Default response with cached using query and params
    """
    return get_response(self.fetch(*args, **kwargs))
  
  @property
  def res(self) -> Response:
    return self.response(cache=True)

  def parse_html(self, response):
    if isinstance(response, HTMLResponse):
      return response.content
    else:
      return BeautifulSoup(response.content, "html.parser")

  @property
  def html(self):
    # return self.data.sg_data("parsed-get-html", lambda: self.parse_html(), "df")
    # return self.data.sg_data("parsed-get-html", lambda: self.parse_html())
    return self.parse_html(self.res)

  @property
  def code(self):
    return self.res.status_code
  
  @property
  def info(self):
    return self.res.info()
