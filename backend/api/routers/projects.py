"""
Projects API Router
Handles project creation, retrieval, and management
"""

import os
import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List

from api.schemas import (
    ProjectResponse,
    FileUploadResponse,
    EDAContextResponse,
    ErrorResponse
)
from src.project_manager import ProjectManager
from src.version_manager import VersionManager
from src.eda_utils import generate_eda_context

router = APIRouter()

# Initialize managers
BASE_DIR = os.getenv("DATA_DIR", "data")
pm = ProjectManager(BASE_DIR)
vm = VersionManager(BASE_DIR)


@router.get("/", response_model=List[ProjectResponse])
async def list_projects():
    """Get all projects"""
    try:
        projects = pm.list_all_projects()
        return [
            ProjectResponse(
                id=p.id,
                name=p.name,
                original_filename=p.original_filename,
                total_rows=p.total_rows,
                total_columns=p.total_columns,
                created_at=p.created_at,
                updated_at=p.updated_at,
                current_version=p.current_version
            )
            for p in projects
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Get project by ID"""
    try:
        project = pm.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        return ProjectResponse(
            id=project.id,
            name=project.name,
            original_filename=project.original_filename,
            total_rows=project.total_rows,
            total_columns=project.total_columns,
            created_at=project.created_at,
            updated_at=project.updated_at,
            current_version=project.current_version
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=FileUploadResponse)
async def upload_project(
    file: UploadFile = File(...),
    project_name: str = Form(...)
):
    """Upload CSV and create new project"""
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.CSV')):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")

        # Read CSV
        contents = await file.read()

        # Try to parse CSV
        try:
            df = pd.read_csv(pd.io.common.BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

        # Create project
        project = pm.create_project(
            csv_dataframe=df,
            original_filename=file.filename,
            project_name=project_name
        )

        return FileUploadResponse(
            success=True,
            message="Project created successfully",
            project_id=project.id
        )

    except HTTPException:
        raise
    except Exception as e:
        return FileUploadResponse(
            success=False,
            message="Failed to create project",
            error=str(e)
        )


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """Delete project"""
    try:
        success = pm.delete_project(project_id)
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"success": True, "message": "Project deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/context", response_model=EDAContextResponse)
async def get_project_context(project_id: str):
    """Get EDA context for project"""
    try:
        project = pm.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Load current dataframe
        df = vm.load_current_dataframe(project_id)

        # Generate EDA context
        context_str = generate_eda_context(df, project.name)

        # Parse context for structured response
        columns_info = []
        for col in df.columns:
            col_info = {
                "name": col,
                "dtype": str(df[col].dtype),
                "non_null": int(df[col].notna().sum()),
                "unique": int(df[col].nunique())
            }

            # Add range for numeric columns
            if pd.api.types.is_numeric_dtype(df[col]) and df[col].notna().any():
                col_info["min"] = float(df[col].min())
                col_info["max"] = float(df[col].max())

            # Add top values for low-cardinality columns
            if df[col].nunique() <= 20 and df[col].nunique() > 0:
                value_counts = df[col].value_counts()
                col_info["values"] = [
                    {"value": str(k), "count": int(v)}
                    for k, v in value_counts.items()
                ]

            columns_info.append(col_info)

        # Get distributions for low-cardinality columns
        distributions = {}
        low_card_cols = [col for col in df.columns if df[col].nunique() <= 20 and df[col].nunique() > 1]
        for col in low_card_cols[:10]:  # Limit to 10
            value_counts = df[col].value_counts()
            distributions[col] = [
                {
                    "value": str(k),
                    "count": int(v),
                    "percentage": round(v / len(df) * 100, 2)
                }
                for k, v in value_counts.items()
            ]

        return EDAContextResponse(
            dataset_name=project.name,
            total_rows=len(df),
            total_columns=len(df.columns),
            columns=columns_info,
            sample_data=df.head(10).to_dict(orient='records'),
            distributions=distributions if distributions else None
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
