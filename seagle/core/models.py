from pydantic import BaseModel, Field, ConfigDict, root_validator
from typing import Any, Dict, List, Optional, Literal


class BaseModelStrict(BaseModel):
  model_config = ConfigDict(validate_assignment=True)

class PageConfig(BaseModelStrict):
  headers: Dict[str, str] = Field(..., description="Headers")

class DebugModel(BaseModelStrict):
  error_trace: bool = Field(False, description="Error trace")

class ConfigModel(BaseModelStrict):
  modes: Dict[str, Dict[str, Any]] = Field({}, description="Modes config")
  mode: str = Field("x", description="Mode to use at start")

  debug: DebugModel = Field(default_factory=DebugModel, description="Debug config")


