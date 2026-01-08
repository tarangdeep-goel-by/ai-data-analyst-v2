"""
AI Query API Router
Handles AI-powered data analysis queries
"""

import os
from fastapi import APIRouter, HTTPException
from typing import Dict

from api.schemas import AIQueryRequest, AIQueryResponse
from src.ai_agent import AIAgent
from src.project_manager import ProjectManager
from src.chat_manager import ChatManager
from src.version_manager import VersionManager
from src.eda_utils import generate_eda_context

router = APIRouter()

# Initialize managers
BASE_DIR = os.getenv("DATA_DIR", "data")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

pm = ProjectManager(BASE_DIR)
cm = ChatManager(BASE_DIR)
vm = VersionManager(BASE_DIR)

# Global dict to store AI agents per chat
# Key: f"{project_id}_{chat_id}", Value: AIAgent instance
active_agents: Dict[str, AIAgent] = {}


def get_or_create_agent(project_id: str, chat_id: str) -> AIAgent:
    """
    Get existing AI agent for a chat or create new one

    Args:
        project_id: Project UUID
        chat_id: Chat UUID

    Returns:
        AIAgent instance
    """
    agent_key = f"{project_id}_{chat_id}"

    # Check if agent already exists
    if agent_key in active_agents:
        agent = active_agents[agent_key]
        # Verify it's still configured for the same project/chat
        if agent.current_project_id == project_id and agent.current_chat_id == chat_id:
            return agent

    # Create new agent
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")

    agent = AIAgent(api_key=GEMINI_API_KEY, base_dir=BASE_DIR)

    # Load dataframe
    df = vm.load_current_dataframe(project_id)
    if df is None:
        raise HTTPException(status_code=500, detail="Failed to load project dataframe")

    # Get project
    project = pm.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Generate EDA context
    dataset_context = generate_eda_context(df, project.name)

    # Start chat session
    success = agent.start_chat_session(
        project_id=project_id,
        chat_id=chat_id,
        dataframe=df,
        dataset_context=dataset_context
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to start AI chat session")

    # Store agent
    active_agents[agent_key] = agent

    return agent


@router.post("/{project_id}/{chat_id}/query", response_model=AIQueryResponse)
async def query_ai(project_id: str, chat_id: str, request: AIQueryRequest):
    """
    Send a query to the AI agent and get response with code execution

    Args:
        project_id: Project UUID
        chat_id: Chat UUID
        request: Query request with user's question

    Returns:
        AI response with code, explanation, and results
    """
    try:
        # Verify project exists
        project = pm.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Verify chat exists
        if not cm.chat_exists(project_id, chat_id):
            raise HTTPException(status_code=404, detail="Chat not found")

        # Get or create AI agent
        agent = get_or_create_agent(project_id, chat_id)

        # Process query
        result = agent.process_query(request.query)

        # Check if successful
        if not result.get("success", False):
            return AIQueryResponse(
                success=False,
                output_type="exploratory",
                code="",
                explanation="",
                error=result.get("error", "Unknown error occurred")
            )

        # Build response with URLs for static files
        response = AIQueryResponse(
            success=True,
            output_type=result.get("output_type", "exploratory"),
            code=result.get("code", ""),
            explanation=result.get("explanation", ""),
            output=result.get("output"),
            result=result.get("result")
        )

        # Add plot URL if plot was generated
        if result.get("plot_path"):
            plot_filename = os.path.basename(result["plot_path"])
            response.plot_path = result["plot_path"]
            response.plot_url = f"/static/plots/{plot_filename}"

        # Add download URL if dataframe was modified
        if result.get("modified_dataframe_path"):
            csv_filename = os.path.basename(result["modified_dataframe_path"])
            response.modified_dataframe_path = result["modified_dataframe_path"]
            response.download_url = f"/static/downloads/{csv_filename}"
            response.modification_summary = result.get("modification_summary")

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}/{chat_id}/session")
async def clear_ai_session(project_id: str, chat_id: str):
    """
    Clear AI agent session for a chat (forces re-initialization on next query)

    Args:
        project_id: Project UUID
        chat_id: Chat UUID

    Returns:
        Success message
    """
    try:
        agent_key = f"{project_id}_{chat_id}"

        if agent_key in active_agents:
            del active_agents[agent_key]
            return {"success": True, "message": "AI session cleared"}

        return {"success": True, "message": "No active session found"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def ai_health_check():
    """
    Health check for AI service

    Returns:
        Service status and active agent count
    """
    return {
        "status": "healthy",
        "gemini_configured": bool(GEMINI_API_KEY),
        "active_agents": len(active_agents)
    }
