"""
Project Manager for AI Data Analyst v2.0
Handles project CRUD operations and orchestrates state/version management
"""

import os
from typing import Optional, List
from datetime import datetime
import pandas as pd

from .models import Project, Chat
from .state_manager import StateManager
from .version_manager import VersionManager
from .utils import (
    get_current_csv_path,
    get_file_size_mb,
    sanitize_filename
)


class ProjectManager:
    """
    Manages projects (CSV files with metadata)
    Orchestrates StateManager and VersionManager
    """

    def __init__(self, base_dir: str = "data"):
        """
        Initialize project manager

        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir
        self.state_manager = StateManager(base_dir)
        self.version_manager = VersionManager(base_dir)

    # ===== Project Creation =====

    def create_project(
        self,
        csv_dataframe: pd.DataFrame,
        original_filename: str,
        project_name: Optional[str] = None
    ) -> Optional[Project]:
        """
        Create a new project from CSV DataFrame

        Args:
            csv_dataframe: DataFrame to create project from
            original_filename: Original CSV filename
            project_name: Custom project name (defaults to filename without extension)

        Returns:
            Project object or None if failed
        """
        try:
            # Sanitize and set project name
            if project_name is None:
                # Use filename without extension
                project_name = os.path.splitext(original_filename)[0]

            project_name = sanitize_filename(project_name)

            # Create project object
            project = Project.create_new(
                name=project_name,
                filename=original_filename,
                rows=len(csv_dataframe),
                cols=len(csv_dataframe.columns),
                size_mb=0.0  # Will update after saving
            )

            # Create initial version (v1)
            version = self.version_manager.create_initial_version(
                project_id=project.id,
                csv_dataframe=csv_dataframe,
                original_filename=original_filename
            )

            if version is None:
                print("Failed to create initial version")
                return None

            # Update project file size
            current_path = get_current_csv_path(self.base_dir, project.id)
            project.file_size_mb = get_file_size_mb(current_path)

            # Create default chat
            default_chat = Chat.create_new(
                project_id=project.id,
                name="Chat 1"
            )

            # Save chat
            self.state_manager.save_chat(default_chat, messages=[])

            # Update project with chat info
            project.active_chat_id = default_chat.id
            project.chat_ids = [default_chat.id]

            # Save project metadata
            success = self.state_manager.save_project_metadata(project)

            if not success:
                print("Failed to save project metadata")
                return None

            return project

        except Exception as e:
            print(f"Error creating project: {e}")
            return None

    # ===== Project Retrieval =====

    def get_project(self, project_id: str) -> Optional[Project]:
        """
        Get project by ID
        Returns Project object or None if not found
        """
        return self.state_manager.load_project_metadata(project_id)

    def list_all_projects(self) -> List[Project]:
        """
        Get all projects
        Returns list sorted by updated_at (most recent first)
        """
        return self.state_manager.load_all_projects()

    def get_project_with_dataframe(
        self,
        project_id: str
    ) -> Optional[tuple[Project, pd.DataFrame]]:
        """
        Get project and its current DataFrame

        Returns:
            Tuple of (Project, DataFrame) or None if not found
        """
        project = self.get_project(project_id)
        if project is None:
            return None

        df = self.version_manager.load_current_dataframe(project_id)
        if df is None:
            return None

        return project, df

    def project_exists(self, project_id: str) -> bool:
        """Check if project exists"""
        return self.state_manager.project_exists(project_id)

    # ===== Project Updates =====

    def update_project_metadata(
        self,
        project_id: str,
        name: Optional[str] = None,
        active_chat_id: Optional[str] = None
    ) -> Optional[Project]:
        """
        Update project metadata

        Args:
            project_id: Project UUID
            name: New project name (optional)
            active_chat_id: Set active chat (optional)

        Returns:
            Updated Project object or None if failed
        """
        try:
            project = self.get_project(project_id)
            if project is None:
                print(f"Project {project_id} not found")
                return None

            # Update fields
            if name is not None:
                project.name = sanitize_filename(name)

            if active_chat_id is not None:
                project.active_chat_id = active_chat_id

            # Update timestamp
            project.updated_at = datetime.utcnow()

            # Save updated metadata
            success = self.state_manager.save_project_metadata(project)

            if not success:
                print("Failed to save updated metadata")
                return None

            return project

        except Exception as e:
            print(f"Error updating project: {e}")
            return None

    def refresh_project_stats(self, project_id: str) -> Optional[Project]:
        """
        Refresh project statistics (rows, columns, size, version)
        Useful after DataFrame modifications

        Returns:
            Updated Project object or None if failed
        """
        try:
            project = self.get_project(project_id)
            if project is None:
                return None

            # Load current DataFrame
            df = self.version_manager.load_current_dataframe(project_id)
            if df is None:
                return None

            # Update stats
            project.total_rows = len(df)
            project.total_columns = len(df.columns)

            current_path = get_current_csv_path(self.base_dir, project_id)
            project.file_size_mb = get_file_size_mb(current_path)

            # Get latest version number
            latest_version = self.version_manager.get_latest_version(project_id)
            if latest_version:
                project.current_version = latest_version.version_number

            project.updated_at = datetime.utcnow()

            # Save updated metadata
            self.state_manager.save_project_metadata(project)

            return project

        except Exception as e:
            print(f"Error refreshing project stats: {e}")
            return None

    def add_chat_to_project(self, project_id: str, chat_id: str) -> bool:
        """
        Add chat ID to project's chat list

        Args:
            project_id: Project UUID
            chat_id: Chat UUID to add

        Returns:
            True if successful, False otherwise
        """
        try:
            project = self.get_project(project_id)
            if project is None:
                return False

            # Add chat ID if not already present
            if chat_id not in project.chat_ids:
                project.chat_ids.append(chat_id)
                project.updated_at = datetime.utcnow()

                # Save updated metadata
                return self.state_manager.save_project_metadata(project)

            return True

        except Exception as e:
            print(f"Error adding chat to project: {e}")
            return False

    def remove_chat_from_project(self, project_id: str, chat_id: str) -> bool:
        """
        Remove chat ID from project's chat list

        Args:
            project_id: Project UUID
            chat_id: Chat UUID to remove

        Returns:
            True if successful, False otherwise
        """
        try:
            project = self.get_project(project_id)
            if project is None:
                return False

            # Remove chat ID if present
            if chat_id in project.chat_ids:
                project.chat_ids.remove(chat_id)

                # If this was the active chat, clear it
                if project.active_chat_id == chat_id:
                    # Set to first remaining chat, or None
                    project.active_chat_id = project.chat_ids[0] if project.chat_ids else None

                project.updated_at = datetime.utcnow()

                # Save updated metadata
                return self.state_manager.save_project_metadata(project)

            return True

        except Exception as e:
            print(f"Error removing chat from project: {e}")
            return False

    # ===== Project Deletion =====

    def delete_project(self, project_id: str) -> bool:
        """
        Delete project and all associated data
        Removes project directory, all chats, versions, etc.

        Args:
            project_id: Project UUID

        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete entire project directory
            success = self.state_manager.delete_project(project_id)

            if success:
                print(f"Project {project_id} deleted successfully")

            return success

        except Exception as e:
            print(f"Error deleting project: {e}")
            return False

    # ===== Project Search =====

    def search_projects(self, query: str) -> List[Project]:
        """
        Search projects by name
        Case-insensitive substring match

        Args:
            query: Search query

        Returns:
            List of matching projects
        """
        all_projects = self.list_all_projects()
        query_lower = query.lower()

        return [
            p for p in all_projects
            if query_lower in p.name.lower() or query_lower in p.original_filename.lower()
        ]

    # ===== Project Statistics =====

    def get_project_stats(self, project_id: str) -> dict:
        """
        Get comprehensive statistics for a project

        Returns:
            Dict with project info, version stats, chat count, etc.
        """
        try:
            project = self.get_project(project_id)
            if project is None:
                return {}

            version_stats = self.version_manager.get_version_stats(project_id)
            chat_count = len(self.state_manager.list_chat_ids(project_id))

            return {
                "project_id": project.id,
                "project_name": project.name,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
                "rows": project.total_rows,
                "columns": project.total_columns,
                "file_size_mb": project.file_size_mb,
                "current_version": project.current_version,
                "chat_count": chat_count,
                "version_stats": version_stats
            }

        except Exception as e:
            print(f"Error getting project stats: {e}")
            return {}

    def get_all_stats(self) -> dict:
        """
        Get statistics for all projects

        Returns:
            Dict with total counts, storage size, etc.
        """
        try:
            projects = self.list_all_projects()

            total_rows = sum(p.total_rows for p in projects)
            total_size_mb = sum(p.file_size_mb for p in projects)
            total_chats = sum(len(self.state_manager.list_chat_ids(p.id)) for p in projects)

            return {
                "total_projects": len(projects),
                "total_rows": total_rows,
                "total_size_mb": round(total_size_mb, 2),
                "total_chats": total_chats,
                "storage_size_mb": self.state_manager.get_storage_size(),
                "projects": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "rows": p.total_rows,
                        "size_mb": p.file_size_mb
                    }
                    for p in projects
                ]
            }

        except Exception as e:
            print(f"Error getting all stats: {e}")
            return {}

    # ===== Utility Methods =====

    def rename_project(self, project_id: str, new_name: str) -> Optional[Project]:
        """
        Rename a project

        Args:
            project_id: Project UUID
            new_name: New project name

        Returns:
            Updated Project object or None if failed
        """
        return self.update_project_metadata(project_id, name=new_name)

    def set_active_chat(self, project_id: str, chat_id: str) -> Optional[Project]:
        """
        Set the active chat for a project

        Args:
            project_id: Project UUID
            chat_id: Chat UUID to set as active

        Returns:
            Updated Project object or None if failed
        """
        return self.update_project_metadata(project_id, active_chat_id=chat_id)

    def get_active_chat_id(self, project_id: str) -> Optional[str]:
        """
        Get the active chat ID for a project

        Returns:
            Chat UUID or None if no active chat
        """
        project = self.get_project(project_id)
        return project.active_chat_id if project else None
