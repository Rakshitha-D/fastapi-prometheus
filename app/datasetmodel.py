import json
from pydantic import BaseModel,Field
from typing_extensions import Any, Dict, List, Optional, TypedDict, Union
from datetime import datetime


class Dataset(BaseModel):
    id: str
    dataset_id: str
    type: str
    name: str | None = None
    validation_config: object | None = None
    extraction_config: object | None = None
    dedup_config : object | None = None
    data_schema: object | None = None
    denorm_config: object | None = None
    router_config: object | None = None
    dataset_config: object | None = None
    status: str | None = None
    tags: List[str] | None = None
    data_version: int | None = None
    created_by: str | None = None
    updated_by: str | None = None

class UpdateDataset(BaseModel):
    #id: Optional[str]= None
    #dataset_id: str | None = None
    type: str | None = None
    name: str | None = None
    validation_config: dict | None = None
    extraction_config: dict | None = None
    dedup_config: dict | None = None
    data_schema: dict | None = None
    denorm_config: dict | None = None
    router_config: dict | None = None
    dataset_config: dict | None = None
    status: str | None = None
    tags: List[str] | None = None
    data_version: int | None = None
    created_by: str | None = None
    updated_by: str | None = None

"""
class ValidationConfig(BaseModel):
    validate: bool
    mode: str
    validation_mode: str

class DedupConfig(BaseModel):
    drop_duplicates: bool
    dedup_key: str
    dedup_period: int

class ExtractionConfig(BaseModel):
    is_batch_event: bool
    extraction_key: str
    dedup_config: DedupConfig
    batch_id: str
"""