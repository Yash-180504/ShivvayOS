from datetime import datetime

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error_code: str
    error_message: str
    failed_at: datetime
