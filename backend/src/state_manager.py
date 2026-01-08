"""
State Manager for AI Data Analyst v2.0
Handles persistence and disk I/O for all data
"""

import os
from typing import Optional, List
from pathlib import Path

from .models import Project, Chat, Message, AppConfig
from .utils import (
    ensure_directory,
    safe_read_json,
    safe_write_json,
    get_metadata_path,
    get_chat_file_path,
    get_project_directory,
    get_eda_context_path,
    delete_directory
)


class StateManager:
    """
    Manages persistence of all application state to disk
    Handles projects, chats, messages, and app configuration
    """

    def __init__(self, base_dir: str = "data"):
        """
        Initialize state manager

        Args:
            base_dir: Base directory for all data storage (default: "data")
        """
        self.base_dir = base_dir
        self.config_path = os.path.join(base_dir, "config.json")
        self._initialize_directories()

    def _initialize_directories(self) -> None:
        """Create necessary directory structure if it doesn't exist"""
        ensure_directory(self.base_dir)
        ensure_directory(os.path.join(self.base_dir, "projects"))
        ensure_directory(os.path.join(self.base_dir, "plots"))

    # ===== App Config =====

    def load_config(self) -> AppConfig:
        """
        Load application configuration
        Creates default config if not found
        """
        data = safe_read_json(self.config_path)

        if data is None:
            # Create default config
            config = AppConfig.create_default()
            self.save_config(config)
            return config

        return AppConfig.from_dict(data)

    def save_config(self, config: AppConfig) -> bool:
        """Save application configuration to disk"""
        return safe_write_json(self.config_path, config.to_dict())

    # ===== Project Operations =====

    def save_project_metadata(self, project: Project) -> bool:
        """
        Save project metadata to disk
        Creates project directory if needed
        """
        project_dir = get_project_directory(self.base_dir, project.id)

        # Ensure project directories exist
        ensure_directory(project_dir)
        ensure_directory(os.path.join(project_dir, "chats"))
        ensure_directory(os.path.join(project_dir, "versions"))

        # Save metadata
        metadata_path = get_metadata_path(self.base_dir, project.id)
        return safe_write_json(metadata_path, project.to_dict())

    def load_project_metadata(self, project_id: str) -> Optional[Project]:
        """
        Load project metadata from disk
        Returns None if project not found
        """
        metadata_path = get_metadata_path(self.base_dir, project_id)
        data = safe_read_json(metadata_path)

        if data is None:
            return None

        return Project.from_dict(data)

    def list_project_ids(self) -> List[str]:
        """
        List all project IDs
        Returns list of project directory names
        """
        projects_dir = os.path.join(self.base_dir, "projects")

        if not os.path.exists(projects_dir):
            return []

        # Get all subdirectories in projects/
        project_ids = []
        for item in os.listdir(projects_dir):
            item_path = os.path.join(projects_dir, item)
            if os.path.isdir(item_path):
                project_ids.append(item)

        return project_ids

    def load_all_projects(self) -> List[Project]:
        """
        Load all projects from disk
        Returns list of Project objects
        """
        project_ids = self.list_project_ids()
        projects = []

        for project_id in project_ids:
            project = self.load_project_metadata(project_id)
            if project is not None:
                projects.append(project)

        # Sort by updated_at (most recent first)
        projects.sort(key=lambda p: p.updated_at, reverse=True)

        return projects

    def delete_project(self, project_id: str) -> bool:
        """
        Delete project and all associated data
        Removes entire project directory
        """
        project_dir = get_project_directory(self.base_dir, project_id)
        return delete_directory(project_dir)

    def project_exists(self, project_id: str) -> bool:
        """Check if project exists on disk"""
        project_dir = get_project_directory(self.base_dir, project_id)
        return os.path.exists(project_dir)

    # ===== Chat Operations =====

    def save_chat(self, chat: Chat, messages: List[Message]) -> bool:
        """
        Save chat and its messages to disk
        Overwrites existing chat file
        """
        chat_path = get_chat_file_path(self.base_dir, chat.project_id, chat.id)

        # Ensure chats directory exists
        ensure_directory(os.path.dirname(chat_path))

        # Prepare chat data with messages
        chat_data = chat.to_dict()
        chat_data["messages"] = [msg.to_dict() for msg in messages]

        return safe_write_json(chat_path, chat_data)

    def load_chat(self, project_id: str, chat_id: str) -> Optional[tuple[Chat, List[Message]]]:
        """
        Load chat and its messages from disk
        Returns tuple of (Chat, List[Message]) or None if not found
        """
        chat_path = get_chat_file_path(self.base_dir, project_id, chat_id)
        data = safe_read_json(chat_path)

        if data is None:
            return None

        # Deserialize chat
        chat = Chat.from_dict(data)

        # Deserialize messages
        messages = []
        for msg_data in data.get("messages", []):
            messages.append(Message.from_dict(msg_data))

        return chat, messages

    def list_chat_ids(self, project_id: str) -> List[str]:
        """
        List all chat IDs for a project
        Returns list of chat IDs
        """
        chats_dir = os.path.join(
            get_project_directory(self.base_dir, project_id),
            "chats"
        )

        if not os.path.exists(chats_dir):
            return []

        # Get all .json files in chats/ directory
        chat_ids = []
        for filename in os.listdir(chats_dir):
            if filename.endswith('.json'):
                # Remove .json extension to get chat ID
                chat_id = filename[:-5]
                chat_ids.append(chat_id)

        return chat_ids

    def load_all_chats(self, project_id: str) -> List[tuple[Chat, List[Message]]]:
        """
        Load all chats for a project
        Returns list of (Chat, List[Message]) tuples
        """
        chat_ids = self.list_chat_ids(project_id)
        chats = []

        for chat_id in chat_ids:
            result = self.load_chat(project_id, chat_id)
            if result is not None:
                chats.append(result)

        # Sort by updated_at (most recent first)
        chats.sort(key=lambda c: c[0].updated_at, reverse=True)

        return chats

    def delete_chat(self, project_id: str, chat_id: str) -> bool:
        """
        Delete chat file
        Returns True if successful
        """
        chat_path = get_chat_file_path(self.base_dir, project_id, chat_id)

        try:
            if os.path.exists(chat_path):
                os.remove(chat_path)
            return True
        except Exception as e:
            print(f"Error deleting chat {chat_id}: {e}")
            return False

    def chat_exists(self, project_id: str, chat_id: str) -> bool:
        """Check if chat exists on disk"""
        chat_path = get_chat_file_path(self.base_dir, project_id, chat_id)
        return os.path.exists(chat_path)

    # ===== EDA Context Operations =====

    def save_eda_context(self, project_id: str, eda_context: dict) -> bool:
        """
        Save EDA context for a project
        Used to cache EDA analysis results
        """
        eda_path = get_eda_context_path(self.base_dir, project_id)
        return safe_write_json(eda_path, eda_context)

    def load_eda_context(self, project_id: str) -> Optional[dict]:
        """
        Load cached EDA context for a project
        Returns None if not found
        """
        eda_path = get_eda_context_path(self.base_dir, project_id)
        return safe_read_json(eda_path)

    def delete_eda_context(self, project_id: str) -> bool:
        """
        Delete EDA context (used when CSV changes)
        Returns True if successful
        """
        eda_path = get_eda_context_path(self.base_dir, project_id)

        try:
            if os.path.exists(eda_path):
                os.remove(eda_path)
            return True
        except Exception as e:
            print(f"Error deleting EDA context: {e}")
            return False

    # ===== Utility Methods =====

    def get_storage_size(self) -> float:
        """
        Calculate total storage size in MB
        Returns total size of data directory
        """
        total_size = 0

        try:
            for dirpath, dirnames, filenames in os.walk(self.base_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)

            return round(total_size / (1024 * 1024), 2)

        except Exception as e:
            print(f"Error calculating storage size: {e}")
            return 0.0

    def cleanup_orphaned_plots(self, active_plot_paths: List[str]) -> int:
        """
        Remove plot files not referenced by any message
        Returns number of files deleted
        """
        plots_dir = os.path.join(self.base_dir, "plots")

        if not os.path.exists(plots_dir):
            return 0

        deleted_count = 0

        try:
            for filename in os.listdir(plots_dir):
                filepath = os.path.join(plots_dir, filename)

                # Check if this plot is referenced
                if filepath not in active_plot_paths:
                    os.remove(filepath)
                    deleted_count += 1

        except Exception as e:
            print(f"Error cleaning up plots: {e}")

        return deleted_count

    def export_project_info(self) -> dict:
        """
        Export summary information about all projects
        Useful for debugging and statistics
        """
        projects = self.load_all_projects()

        return {
            "total_projects": len(projects),
            "total_storage_mb": self.get_storage_size(),
            "projects": [
                {
                    "id": p.id,
                    "name": p.name,
                    "created_at": p.created_at.isoformat(),
                    "file_size_mb": p.file_size_mb,
                    "chat_count": len(self.list_chat_ids(p.id))
                }
                for p in projects
            ]
        }
