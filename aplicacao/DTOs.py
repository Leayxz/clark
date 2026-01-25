from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class AuthServiceResponse:
      msg: Optional[str]
      code: Optional[int]
      data: Optional[Any]
