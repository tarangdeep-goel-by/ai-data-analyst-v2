"""
Utility functions for AI Data Analyst v2.0
Handles file operations, JSON I/O, and helper functions
"""

import os
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Optional
from datetime import datetime
import pandas as pd


def ensure_directory(path: str) -> None:
    """
    Create directory if it doesn't exist
    Creates parent directories as needed
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def safe_read_json(file_path: str, default: Any = None) -> Any:
    """
    Safely read JSON file with error handling
    Returns default value if file doesn't exist or is corrupted
    """
    try:
        if not os.path.exists(file_path):
            return default

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Failed to read {file_path}: {e}")
        return default


def safe_write_json(file_path: str, data: Any, indent: int = 2) -> bool:
    """
    Safely write JSON file with atomic operation
    Writes to temp file first, then renames to prevent corruption
    """
    try:
        # Ensure directory exists
        ensure_directory(os.path.dirname(file_path))

        # Write to temporary file first
        temp_fd, temp_path = tempfile.mkstemp(
            dir=os.path.dirname(file_path),
            suffix='.json.tmp'
        )

        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)

            # Atomic rename
            shutil.move(temp_path, file_path)
            return True

        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e

    except Exception as e:
        print(f"Error: Failed to write {file_path}: {e}")
        return False


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes
    Returns 0.0 if file doesn't exist
    """
    try:
        if not os.path.exists(file_path):
            return 0.0
        size_bytes = os.path.getsize(file_path)
        return round(size_bytes / (1024 * 1024), 2)
    except Exception:
        return 0.0


def get_csv_info(file_path: str) -> dict:
    """
    Get CSV file information (rows, columns, size)
    Returns dict with row_count, column_count, file_size_mb
    """
    try:
        df = pd.read_csv(file_path)
        return {
            "row_count": len(df),
            "column_count": len(df.columns),
            "file_size_mb": get_file_size_mb(file_path)
        }
    except Exception as e:
        print(f"Error reading CSV info from {file_path}: {e}")
        return {
            "row_count": 0,
            "column_count": 0,
            "file_size_mb": 0.0
        }


def format_timestamp(dt: datetime, format_str: str = "%Y%m%d_%H%M%S") -> str:
    """
    Format datetime as string for filenames
    Default: YYYYMMDD_HHMMSS
    """
    return dt.strftime(format_str)


def format_display_timestamp(dt: datetime) -> str:
    """
    Format datetime for display in UI
    Example: "Jan 6, 2026 3:00 PM"
    """
    return dt.strftime("%b %d, %Y %I:%M %p")


def generate_version_filename(version_number: int, timestamp: Optional[datetime] = None) -> str:
    """
    Generate version filename
    Format: v{N}_{timestamp}.csv
    Example: v1_20260106_120000.csv
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    ts_str = format_timestamp(timestamp)
    return f"v{version_number}_{ts_str}.csv"


def delete_directory(path: str) -> bool:
    """
    Safely delete directory and all contents
    Returns True if successful, False otherwise
    """
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
        return True
    except Exception as e:
        print(f"Error deleting directory {path}: {e}")
        return False


def copy_file(src: str, dst: str) -> bool:
    """
    Copy file from source to destination
    Creates destination directory if needed
    """
    try:
        ensure_directory(os.path.dirname(dst))
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        print(f"Error copying file from {src} to {dst}: {e}")
        return False


def validate_csv_file(file_path: str) -> tuple[bool, Optional[str]]:
    """
    Validate that file is a valid CSV
    Returns (is_valid, error_message)
    """
    try:
        if not os.path.exists(file_path):
            return False, "File does not exist"

        # Try to read the CSV
        df = pd.read_csv(file_path)

        # Check for empty DataFrame
        if df.empty:
            return False, "CSV file is empty"

        # Check for at least one column
        if len(df.columns) == 0:
            return False, "CSV has no columns"

        return True, None

    except pd.errors.EmptyDataError:
        return False, "CSV file is empty"
    except pd.errors.ParserError as e:
        return False, f"Invalid CSV format: {str(e)}"
    except Exception as e:
        return False, f"Error reading CSV: {str(e)}"


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate string to max length with suffix
    Example: "Very long text here" -> "Very long text he..."
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters
    Keeps alphanumeric, spaces, hyphens, underscores, and dots
    """
    import re
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace multiple spaces with single space
    sanitized = re.sub(r'\s+', ' ', sanitized)
    # Trim whitespace
    sanitized = sanitized.strip()
    # Ensure not empty
    if not sanitized:
        sanitized = "unnamed"
    return sanitized


def get_project_directory(base_dir: str, project_id: str) -> str:
    """Get full path to project directory"""
    return os.path.join(base_dir, "projects", project_id)


def get_chat_file_path(base_dir: str, project_id: str, chat_id: str) -> str:
    """Get full path to chat JSON file"""
    return os.path.join(base_dir, "projects", project_id, "chats", f"{chat_id}.json")


def get_current_csv_path(base_dir: str, project_id: str) -> str:
    """Get path to current CSV file"""
    return os.path.join(base_dir, "projects", project_id, "current.csv")


def get_eda_context_path(base_dir: str, project_id: str) -> str:
    """Get path to EDA context JSON file"""
    return os.path.join(base_dir, "projects", project_id, "eda_context.json")


def get_metadata_path(base_dir: str, project_id: str) -> str:
    """Get path to project metadata JSON file"""
    return os.path.join(base_dir, "projects", project_id, "metadata.json")


def get_version_log_path(base_dir: str, project_id: str) -> str:
    """Get path to version log JSON file"""
    return os.path.join(base_dir, "projects", project_id, "versions", "version_log.json")


def get_version_csv_path(base_dir: str, project_id: str, version_filename: str) -> str:
    """Get path to version CSV file"""
    return os.path.join(base_dir, "projects", project_id, "versions", version_filename)


def get_plot_path(base_dir: str, plot_id: str) -> str:
    """Get path to plot image file"""
    return os.path.join(base_dir, "plots", f"{plot_id}.png")


def format_file_size(size_mb: float) -> str:
    """
    Format file size for display
    Example: 1.23 MB, 456.78 KB
    """
    if size_mb < 1.0:
        return f"{size_mb * 1024:.2f} KB"
    elif size_mb < 1024:
        return f"{size_mb:.2f} MB"
    else:
        return f"{size_mb / 1024:.2f} GB"


def dataframe_equals(df1: pd.DataFrame, df2: pd.DataFrame) -> bool:
    """
    Check if two DataFrames are equal
    Compares shape, columns, and values
    """
    try:
        # Check shape
        if df1.shape != df2.shape:
            return False

        # Check columns
        if not df1.columns.equals(df2.columns):
            return False

        # Check values
        return df1.equals(df2)

    except Exception:
        return False


def detect_dataframe_changes(df_old: pd.DataFrame, df_new: pd.DataFrame) -> Optional[str]:
    """
    Detect changes between two DataFrames
    Returns description of changes or None if identical
    """
    try:
        if dataframe_equals(df_old, df_new):
            return None

        changes = []

        # Check row count
        if len(df_old) != len(df_new):
            row_diff = len(df_new) - len(df_old)
            if row_diff > 0:
                changes.append(f"Added {row_diff} rows")
            else:
                changes.append(f"Removed {abs(row_diff)} rows")

        # Check column count
        old_cols = set(df_old.columns)
        new_cols = set(df_new.columns)

        added_cols = new_cols - old_cols
        removed_cols = old_cols - new_cols

        if added_cols:
            changes.append(f"Added columns: {', '.join(added_cols)}")
        if removed_cols:
            changes.append(f"Removed columns: {', '.join(removed_cols)}")

        # If no structural changes detected but DataFrames differ
        if not changes:
            changes.append("Modified data values")

        return "; ".join(changes)

    except Exception as e:
        return f"Unknown changes (error: {str(e)})"
