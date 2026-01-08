"""
Data models for AI Data Analyst v2.0
Defines core entities: Project, Chat, Message, Version
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Optional
import uuid
import json


def generate_uuid() -> str:
    """Generate a unique identifier"""
    return str(uuid.uuid4())


def current_timestamp() -> datetime:
    """Get current UTC timestamp"""
    return datetime.utcnow()


@dataclass
class Project:
    """
    Represents a CSV project with metadata
    Each project can have multiple chats and versions
    """
    id: str
    name: str
    original_filename: str
    created_at: datetime
    updated_at: datetime
    current_version: int
    total_rows: int
    total_columns: int
    file_size_mb: float
    active_chat_id: Optional[str] = None
    chat_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON storage"""
        return {
            "id": self.id,
            "name": self.name,
            "original_filename": self.original_filename,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "current_version": self.current_version,
            "total_rows": self.total_rows,
            "total_columns": self.total_columns,
            "file_size_mb": self.file_size_mb,
            "active_chat_id": self.active_chat_id,
            "chat_ids": self.chat_ids
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Project':
        """Deserialize from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            original_filename=data["original_filename"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            current_version=data["current_version"],
            total_rows=data["total_rows"],
            total_columns=data["total_columns"],
            file_size_mb=data["file_size_mb"],
            active_chat_id=data.get("active_chat_id"),
            chat_ids=data.get("chat_ids", [])
        )

    @classmethod
    def create_new(cls, name: str, filename: str, rows: int, cols: int, size_mb: float) -> 'Project':
        """Factory method to create a new project"""
        now = current_timestamp()
        return cls(
            id=generate_uuid(),
            name=name,
            original_filename=filename,
            created_at=now,
            updated_at=now,
            current_version=1,
            total_rows=rows,
            total_columns=cols,
            file_size_mb=size_mb,
            active_chat_id=None,
            chat_ids=[]
        )


@dataclass
class Chat:
    """
    Represents a chat session within a project
    Each chat has its own message history and Gemini session
    """
    id: str
    project_id: str
    name: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    gemini_chat_history: list = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON storage"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "message_count": self.message_count,
            "gemini_chat_history": self.gemini_chat_history
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Chat':
        """Deserialize from dictionary"""
        return cls(
            id=data["id"],
            project_id=data["project_id"],
            name=data["name"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            message_count=data["message_count"],
            gemini_chat_history=data.get("gemini_chat_history", [])
        )

    @classmethod
    def create_new(cls, project_id: str, name: str) -> 'Chat':
        """Factory method to create a new chat"""
        now = current_timestamp()
        return cls(
            id=generate_uuid(),
            project_id=project_id,
            name=name,
            created_at=now,
            updated_at=now,
            message_count=0,
            gemini_chat_history=[]
        )


@dataclass
class Message:
    """
    Represents a single message in a chat
    Can be user message or assistant response with code/output
    """
    id: str
    chat_id: str
    role: str  # "user" | "assistant"
    content: str
    timestamp: datetime

    # Assistant-specific fields
    code: Optional[str] = None
    output_type: Optional[str] = None  # "exploratory" | "visualization" | "modification"
    output: Optional[str] = None
    result: Any = None
    plot_path: Optional[str] = None
    explanation: Optional[str] = None
    thinking: Optional[str] = None

    # DataFrame modification fields
    modified_dataframe_path: Optional[str] = None
    modification_summary: Optional[dict] = None

    # Judge validation (Phase 5)
    judge_score: Optional[float] = None
    judge_feedback: Optional[str] = None

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON storage"""
        return {
            "id": self.id,
            "chat_id": self.chat_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "code": self.code,
            "output_type": self.output_type,
            "output": self.output,
            "result": self._serialize_result(self.result),
            "plot_path": self.plot_path,
            "explanation": self.explanation,
            "thinking": self.thinking,
            "modified_dataframe_path": self.modified_dataframe_path,
            "modification_summary": self.modification_summary,
            "judge_score": self.judge_score,
            "judge_feedback": self.judge_feedback
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """Deserialize from dictionary"""
        return cls(
            id=data["id"],
            chat_id=data["chat_id"],
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            code=data.get("code"),
            output_type=data.get("output_type"),
            output=data.get("output"),
            result=data.get("result"),
            plot_path=data.get("plot_path"),
            explanation=data.get("explanation"),
            thinking=data.get("thinking"),
            modified_dataframe_path=data.get("modified_dataframe_path"),
            modification_summary=data.get("modification_summary"),
            judge_score=data.get("judge_score"),
            judge_feedback=data.get("judge_feedback")
        )

    @classmethod
    def create_user_message(cls, chat_id: str, content: str) -> 'Message':
        """Factory method to create a user message"""
        return cls(
            id=generate_uuid(),
            chat_id=chat_id,
            role="user",
            content=content,
            timestamp=current_timestamp()
        )

    @classmethod
    def create_assistant_message(
        cls,
        chat_id: str,
        content: str,
        code: Optional[str] = None,
        output_type: Optional[str] = None,
        output: Optional[str] = None,
        result: Any = None,
        plot_path: Optional[str] = None,
        explanation: Optional[str] = None,
        thinking: Optional[str] = None,
        modified_dataframe_path: Optional[str] = None,
        modification_summary: Optional[dict] = None
    ) -> 'Message':
        """Factory method to create an assistant message"""
        return cls(
            id=generate_uuid(),
            chat_id=chat_id,
            role="assistant",
            content=content,
            timestamp=current_timestamp(),
            code=code,
            output_type=output_type,
            output=output,
            result=result,
            plot_path=plot_path,
            explanation=explanation,
            thinking=thinking,
            modified_dataframe_path=modified_dataframe_path,
            modification_summary=modification_summary
        )

    @staticmethod
    def _serialize_result(result: Any) -> Any:
        """
        Serialize result field for JSON storage
        Handles pandas DataFrames and other complex types
        """
        if result is None:
            return None

        # Handle pandas DataFrame
        try:
            import pandas as pd
            if isinstance(result, pd.DataFrame):
                return {
                    "_type": "dataframe",
                    "data": result.to_dict(orient="records"),
                    "columns": list(result.columns)
                }
        except ImportError:
            pass

        # Handle lists and dicts
        if isinstance(result, (list, dict, str, int, float, bool)):
            return result

        # Fallback: convert to string
        return str(result)


@dataclass
class Version:
    """
    Represents a version of the CSV file
    Tracks all modifications with full history
    """
    version_number: int
    project_id: str
    created_at: datetime
    created_by_chat_id: Optional[str]
    created_by_message_id: Optional[str]
    file_path: str
    file_size_mb: float
    change_description: str
    row_count: int
    column_count: int

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON storage"""
        return {
            "version_number": self.version_number,
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat(),
            "created_by_chat_id": self.created_by_chat_id,
            "created_by_message_id": self.created_by_message_id,
            "file_path": self.file_path,
            "file_size_mb": self.file_size_mb,
            "change_description": self.change_description,
            "row_count": self.row_count,
            "column_count": self.column_count
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Version':
        """Deserialize from dictionary"""
        return cls(
            version_number=data["version_number"],
            project_id=data["project_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            created_by_chat_id=data.get("created_by_chat_id"),
            created_by_message_id=data.get("created_by_message_id"),
            file_path=data["file_path"],
            file_size_mb=data["file_size_mb"],
            change_description=data["change_description"],
            row_count=data["row_count"],
            column_count=data["column_count"]
        )

    @classmethod
    def create_new(
        cls,
        version_number: int,
        project_id: str,
        file_path: str,
        file_size_mb: float,
        change_description: str,
        row_count: int,
        column_count: int,
        chat_id: Optional[str] = None,
        message_id: Optional[str] = None
    ) -> 'Version':
        """Factory method to create a new version"""
        return cls(
            version_number=version_number,
            project_id=project_id,
            created_at=current_timestamp(),
            created_by_chat_id=chat_id,
            created_by_message_id=message_id,
            file_path=file_path,
            file_size_mb=file_size_mb,
            change_description=change_description,
            row_count=row_count,
            column_count=column_count
        )


@dataclass
class AppConfig:
    """
    Global application configuration
    Stored in data/config.json
    """
    version: str
    last_active_project_id: Optional[str] = None
    judge_enabled: bool = True
    judge_threshold_trigger: str = "user_request"  # "user_request" | "always" | "never"
    judge_quality_threshold: int = 70

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON storage"""
        return {
            "version": self.version,
            "last_active_project_id": self.last_active_project_id,
            "judge_settings": {
                "enabled": self.judge_enabled,
                "threshold_trigger": self.judge_threshold_trigger,
                "quality_threshold": self.judge_quality_threshold
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AppConfig':
        """Deserialize from dictionary"""
        judge_settings = data.get("judge_settings", {})
        return cls(
            version=data.get("version", "2.0.0"),
            last_active_project_id=data.get("last_active_project_id"),
            judge_enabled=judge_settings.get("enabled", True),
            judge_threshold_trigger=judge_settings.get("threshold_trigger", "user_request"),
            judge_quality_threshold=judge_settings.get("quality_threshold", 70)
        )

    @classmethod
    def create_default(cls) -> 'AppConfig':
        """Create default configuration"""
        return cls(
            version="2.0.0",
            last_active_project_id=None,
            judge_enabled=True,
            judge_threshold_trigger="user_request",
            judge_quality_threshold=70
        )
