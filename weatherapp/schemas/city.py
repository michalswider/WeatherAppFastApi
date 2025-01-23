from pydantic import BaseModel, Field


class AddCityRequest(BaseModel):
    city: str = Field(min_length=3, max_length=50)
