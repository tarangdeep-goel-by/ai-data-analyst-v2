"""
Version Manager for AI Data Analyst v2.0
Handles CSV version control and history tracking
"""

import os
import shutil
from typing import Optional, List
from datetime import datetime
import pandas as pd

from .models import Version
from .utils import (
    ensure_directory,
    safe_read_json,
    safe_write_json,
    get_version_log_path,
    get_version_csv_path,
    get_current_csv_path,
    get_file_size_mb,
    generate_version_filename,
    detect_dataframe_changes,
    copy_file
)


class VersionManager:
    """
    Manages CSV file versions for a project
    Tracks all modifications with full history
    """

    def __init__(self, base_dir: str = "data"):
        """
        Initialize version manager

        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir

    # ===== Version Log Operations =====

    def _load_version_log(self, project_id: str) -> dict:
        """
        Load version log for a project
        Returns dict with version history
        """
        log_path = get_version_log_path(self.base_dir, project_id)
        data = safe_read_json(log_path)

        if data is None:
            # Initialize empty log
            return {
                "project_id": project_id,
                "versions": []
            }

        return data

    def _save_version_log(self, project_id: str, log_data: dict) -> bool:
        """Save version log to disk"""
        log_path = get_version_log_path(self.base_dir, project_id)
        return safe_write_json(log_path, log_data)

    # ===== Version Creation =====

    def create_initial_version(
        self,
        project_id: str,
        csv_dataframe: pd.DataFrame,
        original_filename: str
    ) -> Optional[Version]:
        """
        Create initial version (v1) for a new project

        Args:
            project_id: Project UUID
            csv_dataframe: DataFrame to save
            original_filename: Original CSV filename

        Returns:
            Version object or None if failed
        """
        try:
            # Generate version filename
            version_filename = generate_version_filename(1)
            version_path = get_version_csv_path(self.base_dir, project_id, version_filename)

            # Ensure versions directory exists
            ensure_directory(os.path.dirname(version_path))

            # Save CSV
            csv_dataframe.to_csv(version_path, index=False)

            # Also save as current.csv
            current_path = get_current_csv_path(self.base_dir, project_id)
            csv_dataframe.to_csv(current_path, index=False)

            # Create version object
            version = Version.create_new(
                version_number=1,
                project_id=project_id,
                file_path=f"versions/{version_filename}",
                file_size_mb=get_file_size_mb(version_path),
                change_description="Initial upload",
                row_count=len(csv_dataframe),
                column_count=len(csv_dataframe.columns)
            )

            # Save to version log
            log_data = self._load_version_log(project_id)
            log_data["versions"].append(version.to_dict())
            self._save_version_log(project_id, log_data)

            return version

        except Exception as e:
            print(f"Error creating initial version: {e}")
            return None

    def create_new_version(
        self,
        project_id: str,
        csv_dataframe: pd.DataFrame,
        change_description: Optional[str] = None,
        chat_id: Optional[str] = None,
        message_id: Optional[str] = None
    ) -> Optional[Version]:
        """
        Create new version after modification

        Args:
            project_id: Project UUID
            csv_dataframe: Modified DataFrame
            change_description: Description of changes (auto-detected if None)
            chat_id: Chat that created this version
            message_id: Message that created this version

        Returns:
            Version object or None if failed
        """
        try:
            # Load version history
            log_data = self._load_version_log(project_id)
            current_version_number = len(log_data["versions"])
            new_version_number = current_version_number + 1

            # Auto-detect changes if not provided
            if change_description is None:
                current_path = get_current_csv_path(self.base_dir, project_id)
                if os.path.exists(current_path):
                    old_df = pd.read_csv(current_path)
                    change_description = detect_dataframe_changes(old_df, csv_dataframe)
                    if change_description is None:
                        change_description = "No changes detected"
                else:
                    change_description = "Modified dataset"

            # Generate version filename
            version_filename = generate_version_filename(new_version_number)
            version_path = get_version_csv_path(self.base_dir, project_id, version_filename)

            # Save new version
            csv_dataframe.to_csv(version_path, index=False)

            # Update current.csv
            current_path = get_current_csv_path(self.base_dir, project_id)
            csv_dataframe.to_csv(current_path, index=False)

            # Create version object
            version = Version.create_new(
                version_number=new_version_number,
                project_id=project_id,
                file_path=f"versions/{version_filename}",
                file_size_mb=get_file_size_mb(version_path),
                change_description=change_description,
                row_count=len(csv_dataframe),
                column_count=len(csv_dataframe.columns),
                chat_id=chat_id,
                message_id=message_id
            )

            # Add to version log
            log_data["versions"].append(version.to_dict())
            self._save_version_log(project_id, log_data)

            return version

        except Exception as e:
            print(f"Error creating new version: {e}")
            return None

    # ===== Version Retrieval =====

    def get_version_history(self, project_id: str) -> List[Version]:
        """
        Get all versions for a project
        Returns list of Version objects, sorted by version number
        """
        log_data = self._load_version_log(project_id)
        versions = []

        for version_data in log_data.get("versions", []):
            versions.append(Version.from_dict(version_data))

        # Sort by version number (ascending)
        versions.sort(key=lambda v: v.version_number)

        return versions

    def get_version(self, project_id: str, version_number: int) -> Optional[Version]:
        """
        Get specific version by number
        Returns Version object or None if not found
        """
        versions = self.get_version_history(project_id)

        for version in versions:
            if version.version_number == version_number:
                return version

        return None

    def get_latest_version(self, project_id: str) -> Optional[Version]:
        """Get the most recent version"""
        versions = self.get_version_history(project_id)

        if not versions:
            return None

        return versions[-1]  # Last item (highest version number)

    def get_current_version_number(self, project_id: str) -> int:
        """Get the current version number"""
        latest = self.get_latest_version(project_id)
        return latest.version_number if latest else 0

    # ===== Version Loading =====

    def load_version_dataframe(
        self,
        project_id: str,
        version_number: int
    ) -> Optional[pd.DataFrame]:
        """
        Load DataFrame from a specific version

        Args:
            project_id: Project UUID
            version_number: Version number to load

        Returns:
            DataFrame or None if not found
        """
        try:
            version = self.get_version(project_id, version_number)
            if version is None:
                print(f"Version {version_number} not found")
                return None

            # Extract filename from version.file_path (e.g., "versions/v1_20260106.csv")
            version_filename = os.path.basename(version.file_path)
            version_path = get_version_csv_path(self.base_dir, project_id, version_filename)

            if not os.path.exists(version_path):
                print(f"Version file not found: {version_path}")
                return None

            return pd.read_csv(version_path)

        except Exception as e:
            print(f"Error loading version {version_number}: {e}")
            return None

    def load_current_dataframe(self, project_id: str) -> Optional[pd.DataFrame]:
        """
        Load current.csv for a project
        This is the active version being worked on
        """
        try:
            current_path = get_current_csv_path(self.base_dir, project_id)

            if not os.path.exists(current_path):
                print(f"Current CSV not found: {current_path}")
                return None

            return pd.read_csv(current_path)

        except Exception as e:
            print(f"Error loading current CSV: {e}")
            return None

    # ===== Version Reversion =====

    def revert_to_version(
        self,
        project_id: str,
        target_version_number: int,
        chat_id: Optional[str] = None,
        message_id: Optional[str] = None
    ) -> Optional[Version]:
        """
        Revert to a previous version
        Creates new version (copy of old one) rather than deleting history

        Args:
            project_id: Project UUID
            target_version_number: Version to revert to
            chat_id: Chat requesting revert
            message_id: Message requesting revert

        Returns:
            New Version object (copy of old version) or None if failed
        """
        try:
            # Load target version
            old_df = self.load_version_dataframe(project_id, target_version_number)
            if old_df is None:
                print(f"Cannot load version {target_version_number}")
                return None

            # Create new version with old data
            description = f"Reverted to v{target_version_number}"
            new_version = self.create_new_version(
                project_id=project_id,
                csv_dataframe=old_df,
                change_description=description,
                chat_id=chat_id,
                message_id=message_id
            )

            return new_version

        except Exception as e:
            print(f"Error reverting to version {target_version_number}: {e}")
            return None

    # ===== Version Download =====

    def get_version_download_path(
        self,
        project_id: str,
        version_number: int
    ) -> Optional[str]:
        """
        Get file path for downloading a version
        Returns absolute path to version CSV file
        """
        version = self.get_version(project_id, version_number)
        if version is None:
            return None

        version_filename = os.path.basename(version.file_path)
        return get_version_csv_path(self.base_dir, project_id, version_filename)

    def get_current_download_path(self, project_id: str) -> str:
        """Get file path for downloading current version"""
        return get_current_csv_path(self.base_dir, project_id)

    # ===== Version Statistics =====

    def get_version_stats(self, project_id: str) -> dict:
        """
        Get statistics about version history

        Returns:
            Dict with version count, total size, etc.
        """
        versions = self.get_version_history(project_id)

        if not versions:
            return {
                "version_count": 0,
                "total_size_mb": 0.0,
                "earliest_version": None,
                "latest_version": None
            }

        total_size = sum(v.file_size_mb for v in versions)

        return {
            "version_count": len(versions),
            "total_size_mb": round(total_size, 2),
            "earliest_version": versions[0].version_number,
            "latest_version": versions[-1].version_number,
            "earliest_created": versions[0].created_at.isoformat(),
            "latest_created": versions[-1].created_at.isoformat()
        }

    # ===== Utility Methods =====

    def detect_modification(self, project_id: str, new_dataframe: pd.DataFrame) -> bool:
        """
        Check if DataFrame differs from current version
        Returns True if modification detected
        """
        try:
            current_df = self.load_current_dataframe(project_id)
            if current_df is None:
                return True

            # Compare shapes
            if current_df.shape != new_dataframe.shape:
                return True

            # Compare columns
            if not current_df.columns.equals(new_dataframe.columns):
                return True

            # Compare values
            return not current_df.equals(new_dataframe)

        except Exception as e:
            print(f"Error detecting modification: {e}")
            return True  # Assume modified on error

    def cleanup_old_versions(
        self,
        project_id: str,
        keep_count: int = 10
    ) -> int:
        """
        Delete old versions, keeping only the most recent N versions
        Returns number of versions deleted
        """
        try:
            versions = self.get_version_history(project_id)

            if len(versions) <= keep_count:
                return 0  # Nothing to delete

            # Keep last N versions, delete the rest
            versions_to_delete = versions[:-keep_count]
            deleted_count = 0

            for version in versions_to_delete:
                version_filename = os.path.basename(version.file_path)
                version_path = get_version_csv_path(self.base_dir, project_id, version_filename)

                if os.path.exists(version_path):
                    os.remove(version_path)
                    deleted_count += 1

            # Update version log
            log_data = self._load_version_log(project_id)
            log_data["versions"] = [v.to_dict() for v in versions[-keep_count:]]
            self._save_version_log(project_id, log_data)

            return deleted_count

        except Exception as e:
            print(f"Error cleaning up versions: {e}")
            return 0
