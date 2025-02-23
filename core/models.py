from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class DataType(str, Enum):
    EXPERIMENTAL = "experimental"
    OBSERVATIONAL = "observational"
    COMPUTATIONAL = "computational"
    SURVEY = "survey"

class DatasetMetadata(BaseModel):
    title: str
    description: str
    data_type: DataType
    keywords: List[str]
    authors: List[str]
    creation_date: datetime
    license: str
    file_hash: str
    size_bytes: int
    price_tokens: float

class Transaction(BaseModel):
    transaction_id: str
    seller_address: str
    buyer_address: str
    dataset_id: str
    amount: float
    timestamp: datetime
    status: str

class ResearchAgent(BaseModel):
    agent_id: str
    name: str
    description: str
    capabilities: List[str]
    active_tasks: int
    reputation_score: float
    total_tasks_completed: int
