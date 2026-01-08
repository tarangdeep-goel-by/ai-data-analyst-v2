"""
Pydantic schemas for API request/response models
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# PROJECT SCHEMAS
# ============================================================================

class ProjectBase(BaseModel):
    name: str
    original_filename: str
    total_rows: int
    total_columns: int


class ProjectCreate(BaseModel):
    name: str


class ProjectResponse(ProjectBase):
    id: str
    created_at: datetime
    updated_at: datetime
    current_version: int

    class Config:
        from_attributes = True


# ============================================================================
# CHAT SCHEMAS
# ============================================================================

class ChatBase(BaseModel):
    name: str


class ChatCreate(ChatBase):
    pass


class ChatResponse(ChatBase):
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    class Config:
        from_attributes = True


# ============================================================================
# MESSAGE SCHEMAS
# ============================================================================

class MessageBase(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: str
    chat_id: str
    timestamp: datetime
    output_type: Optional[str] = None  # "exploratory", "visualization", "modification"
    code: Optional[str] = None
    output: Optional[str] = None
    result: Optional[str] = None
    plot_path: Optional[str] = None
    modified_dataframe_path: Optional[str] = None
    modification_summary: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# AI QUERY SCHEMAS
# ============================================================================

class AIQueryRequest(BaseModel):
    query: str


class AIQueryResponse(BaseModel):
    success: bool
    output_type: str
    code: str
    explanation: str
    output: Optional[str] = None
    result: Optional[str] = None
    plot_path: Optional[str] = None
    plot_url: Optional[str] = None  # URL for frontend to fetch
    modified_dataframe_path: Optional[str] = None
    download_url: Optional[str] = None  # URL for CSV download
    modification_summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ============================================================================
# EDA CONTEXT SCHEMAS
# ============================================================================

class EDAContextResponse(BaseModel):
    dataset_name: str
    total_rows: int
    total_columns: int
    columns: List[Dict[str, Any]]  # Column info with types, nulls, unique, ranges
    sample_data: List[Dict[str, Any]]  # First few rows
    distributions: Optional[Dict[str, List[Dict[str, Any]]]] = None  # Value distributions


# ============================================================================
# FILE UPLOAD SCHEMAS
# ============================================================================

class FileUploadResponse(BaseModel):
    success: bool
    message: str
    project_id: Optional[str] = None
    error: Optional[str] = None


# ============================================================================
# ERROR SCHEMAS
# ============================================================================

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
