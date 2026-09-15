from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SolveCreate(BaseModel):
    raw_time_ms: int = Field(..., gt=0, description="Time in milliseconds")
    scramble: str = Field(..., min_length=5, description="Applied WCA scramble sequence")
    penalty: Literal["none", "+2", "dnf"] = "none"


class SolveUpdate(BaseModel):
    penalty: Literal["none", "+2", "dnf"]


class SolveResponse(BaseModel):
    id: int
    user_id: int
    raw_time_ms: int
    final_time_ms: int | None
    formatted_time: str
    penalty: Literal["none", "+2", "dnf"]
    scramble: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StatsResponse(BaseModel):
    total_solves: int
    pb: str | None = None  # Personal Best Single formatted
    pb_raw_ms: int | None = None
    ao5: str | None = None  # Current Average of 5
    ao12: str | None = None  # Current Average of 12
    ao100: str | None = None  # Current Average of 100
    best_ao5: str | None = None
    best_ao12: str | None = None
