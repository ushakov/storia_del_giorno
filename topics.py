from typing import List
from langchain_core.pydantic_v1 import BaseModel, Field

class Theme(BaseModel):
  theme: str = Field(description="The suggested theme")
  topics: List[str] = Field(description="The suggested topics for the theme")


class ThemeList(BaseModel):
  themes: List[Theme] = Field(description="The suggested themes and topics")
