"""
Chats API Router
Handles chat creation, retrieval, and message management
"""

import os
from fastapi import APIRouter, HTTPException
from typing import List

from api.schemas import (
    ChatCreate,
    ChatResponse,
    MessageResponse,
    ErrorResponse
)
from src.chat_manager import ChatManager
from src.project_manager import ProjectManager

router = APIRouter()

# Initialize managers
BASE_DIR = os.getenv("DATA_DIR", "data")
cm = ChatManager(BASE_DIR)
pm = ProjectManager(BASE_DIR)


@router.get("/{project_id}", response_model=List[ChatResponse])
async def list_chats(project_id: str):
    """List all chats for a project"""
    try:
        # Verify project exists
        project = pm.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get chats
        chats = cm.list_chats(project_id)

        return [
            ChatResponse(
                id=chat.id,
                project_id=chat.project_id,
                name=chat.name,
                created_at=chat.created_at,
                updated_at=chat.updated_at,
                message_count=chat.message_count
            )
            for chat in chats
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}", response_model=ChatResponse)
async def create_chat(project_id: str, chat_data: ChatCreate):
    """Create a new chat for a project"""
    try:
        # Verify project exists
        project = pm.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Create chat
        chat = cm.create_chat(
            project_id=project_id,
            chat_name=chat_data.name
        )

        if not chat:
            raise HTTPException(status_code=500, detail="Failed to create chat")

        return ChatResponse(
            id=chat.id,
            project_id=chat.project_id,
            name=chat.name,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            message_count=chat.message_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/{chat_id}", response_model=ChatResponse)
async def get_chat(project_id: str, chat_id: str):
    """Get chat by ID"""
    try:
        # Verify project exists
        project = pm.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get chat
        chat = cm.get_chat_metadata(project_id, chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        return ChatResponse(
            id=chat.id,
            project_id=chat.project_id,
            name=chat.name,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            message_count=chat.message_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{project_id}/{chat_id}", response_model=ChatResponse)
async def update_chat(project_id: str, chat_id: str, chat_data: ChatCreate):
    """Update/rename a chat"""
    try:
        # Verify project exists
        project = pm.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Update chat
        chat = cm.rename_chat(project_id, chat_id, chat_data.name)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found or failed to update")

        return ChatResponse(
            id=chat.id,
            project_id=chat.project_id,
            name=chat.name,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            message_count=chat.message_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}/{chat_id}")
async def delete_chat(project_id: str, chat_id: str):
    """Delete a chat"""
    try:
        # Verify project exists
        project = pm.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Delete chat
        success = cm.delete_chat(project_id, chat_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found or failed to delete")

        return {"success": True, "message": "Chat deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(project_id: str, chat_id: str):
    """Get all messages for a chat"""
    try:
        # Verify project exists
        project = pm.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get messages
        messages = cm.get_messages(project_id, chat_id)

        return [
            MessageResponse(
                id=msg.id,
                chat_id=msg.chat_id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp,
                output_type=msg.output_type,
                code=msg.code,
                output=msg.output,
                result=msg.result,
                plot_path=msg.plot_path,
                modified_dataframe_path=msg.modified_dataframe_path,
                modification_summary=msg.modification_summary,
                explanation=msg.explanation
            )
            for msg in messages
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}/{chat_id}/messages")
async def clear_chat_messages(project_id: str, chat_id: str):
    """Clear all messages from a chat (keep chat metadata)"""
    try:
        # Verify project exists
        project = pm.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Clear messages
        success = cm.clear_chat_messages(project_id, chat_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found or failed to clear messages")

        return {"success": True, "message": "Chat messages cleared"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
