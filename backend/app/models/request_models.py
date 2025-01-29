from pydantic import BaseModel

class AnalyzeRequest(BaseModel):
    repository_url: str