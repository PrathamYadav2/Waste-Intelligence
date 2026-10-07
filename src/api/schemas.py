from datetime import datetime
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field

class ErrorBody(BaseModel):
    code: str; message: str; details: Optional[Any] = None
    request_id: Optional[str] = None
class ErrorResponse(BaseModel):
    error: ErrorBody

class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]; version: str; time: datetime
    components: dict[str, str] = Field(default_factory=dict)   # e.g. {"model": "NOT_LOADED"}

class ClassScore(BaseModel):
    label: str; confidence: float = Field(ge=0, le=1)
class ClassifyResponse(BaseModel):
    request_id: str; model_version: str
    prediction: ClassScore; top_k: list[ClassScore]
    material: Optional[str] = None

class AnalyzeRequestMeta(BaseModel):
    region: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    condition: Optional[str] = None            # manual input only
class RecoveryRequest(BaseModel):
    waste_class: str; material: Optional[str] = None
    condition: Optional[str] = None; region: Optional[str] = None
class RecoveryResponse(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=100)
    score_version: str; route: str
    factor_breakdown: dict[str, Any]; explanation: str
class RecommendationItem(BaseModel):
    recommendation_id: int; action: str; route: Optional[str]; priority: Literal["low","medium","high"]
    explanation: str; community_action: Optional[str]; component_trace: list[dict[str, str]]
class Page(BaseModel):
    page: int = 1; page_size: int = 20; total: int = 0
