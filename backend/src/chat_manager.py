"""
Chat Manager for AI Data Analyst v2.0
Handles chat CRUD operations and message management
"""

from typing import Optional, List
from datetime import datetime

from .models import Chat, Message
from .state_manager import StateManager


class ChatManager:
    """
    Manages chats and messages for projects
    Handles chat creation, switching, and message history
    """

    def __init__(self, base_dir: str = "data"):
        """
        Initialize chat manager

        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir
        self.state_manager = StateManager(base_dir)

    # ===== Chat Creation =====

    def create_chat(
        self,
        project_id: str,
        chat_name: Optional[str] = None
    ) -> Optional[Chat]:
        """
        Create a new chat for a project

        Args:
            project_id: Project UUID
            chat_name: Custom chat name (auto-generated if None)

        Returns:
            Chat object or None if failed
        """
        try:
            # Auto-generate name if not provided
            if chat_name is None:
                existing_chats = self.list_chats(project_id)
                chat_name = f"Chat {len(existing_chats) + 1}"

            # Create chat object
            chat = Chat.create_new(
                project_id=project_id,
                name=chat_name
            )

            # Save chat with empty message list
            success = self.state_manager.save_chat(chat, messages=[])

            if not success:
                print("Failed to save chat")
                return None

            return chat

        except Exception as e:
            print(f"Error creating chat: {e}")
            return None

    # ===== Chat Retrieval =====

    def get_chat(
        self,
        project_id: str,
        chat_id: str
    ) -> Optional[tuple[Chat, List[Message]]]:
        """
        Get chat and its messages

        Args:
            project_id: Project UUID
            chat_id: Chat UUID

        Returns:
            Tuple of (Chat, List[Message]) or None if not found
        """
        return self.state_manager.load_chat(project_id, chat_id)

    def get_chat_metadata(
        self,
        project_id: str,
        chat_id: str
    ) -> Optional[Chat]:
        """
        Get only chat metadata (without messages)

        Args:
            project_id: Project UUID
            chat_id: Chat UUID

        Returns:
            Chat object or None if not found
        """
        result = self.state_manager.load_chat(project_id, chat_id)
        if result is None:
            return None
        return result[0]  # Return only chat, not messages

    def list_chats(self, project_id: str) -> List[Chat]:
        """
        List all chats for a project (metadata only)

        Args:
            project_id: Project UUID

        Returns:
            List of Chat objects (sorted by updated_at, most recent first)
        """
        chat_ids = self.state_manager.list_chat_ids(project_id)
        chats = []

        for chat_id in chat_ids:
            chat = self.get_chat_metadata(project_id, chat_id)
            if chat is not None:
                chats.append(chat)

        # Sort by updated_at (most recent first)
        chats.sort(key=lambda c: c.updated_at, reverse=True)

        return chats

    def chat_exists(self, project_id: str, chat_id: str) -> bool:
        """Check if chat exists"""
        return self.state_manager.chat_exists(project_id, chat_id)

    # ===== Chat Updates =====

    def update_chat_metadata(
        self,
        project_id: str,
        chat_id: str,
        name: Optional[str] = None
    ) -> Optional[Chat]:
        """
        Update chat metadata

        Args:
            project_id: Project UUID
            chat_id: Chat UUID
            name: New chat name (optional)

        Returns:
            Updated Chat object or None if failed
        """
        try:
            result = self.get_chat(project_id, chat_id)
            if result is None:
                print(f"Chat {chat_id} not found")
                return None

            chat, messages = result

            # Update fields
            if name is not None:
                chat.name = name

            chat.updated_at = datetime.utcnow()

            # Save updated chat
            success = self.state_manager.save_chat(chat, messages)

            if not success:
                print("Failed to save updated chat")
                return None

            return chat

        except Exception as e:
            print(f"Error updating chat: {e}")
            return None

    def rename_chat(
        self,
        project_id: str,
        chat_id: str,
        new_name: str
    ) -> Optional[Chat]:
        """
        Rename a chat

        Args:
            project_id: Project UUID
            chat_id: Chat UUID
            new_name: New chat name

        Returns:
            Updated Chat object or None if failed
        """
        return self.update_chat_metadata(project_id, chat_id, name=new_name)

    # ===== Message Operations =====

    def add_message(
        self,
        project_id: str,
        chat_id: str,
        message: Message
    ) -> bool:
        """
        Add a message to a chat

        Args:
            project_id: Project UUID
            chat_id: Chat UUID
            message: Message object to add

        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.get_chat(project_id, chat_id)
            if result is None:
                print(f"Chat {chat_id} not found")
                return False

            chat, messages = result

            # Add message
            messages.append(message)

            # Update chat metadata
            chat.message_count = len(messages)
            chat.updated_at = datetime.utcnow()

            # Save updated chat
            return self.state_manager.save_chat(chat, messages)

        except Exception as e:
            print(f"Error adding message: {e}")
            return False

    def add_user_message(
        self,
        project_id: str,
        chat_id: str,
        content: str
    ) -> Optional[Message]:
        """
        Add a user message to a chat

        Args:
            project_id: Project UUID
            chat_id: Chat UUID
            content: Message content

        Returns:
            Message object if successful, None otherwise
        """
        try:
            message = Message.create_user_message(chat_id=chat_id, content=content)
            success = self.add_message(project_id, chat_id, message)

            if success:
                return message
            return None

        except Exception as e:
            print(f"Error adding user message: {e}")
            return None

    def add_assistant_message(
        self,
        project_id: str,
        chat_id: str,
        content: str,
        code: Optional[str] = None,
        output_type: Optional[str] = None,
        output: Optional[str] = None,
        result: any = None,
        plot_path: Optional[str] = None,
        modified_dataframe_path: Optional[str] = None,
        modification_summary: Optional[dict] = None,
        explanation: Optional[str] = None,
        thinking: Optional[str] = None
    ) -> Optional[Message]:
        """
        Add an assistant message to a chat

        Args:
            project_id: Project UUID
            chat_id: Chat UUID
            content: Message content
            code: Generated code (optional)
            output_type: Type of output (optional)
            output: Output text (optional)
            result: Result data (optional)
            plot_path: Path to plot image (optional)
            explanation: Explanation text (optional)
            thinking: AI thinking/reasoning (optional)

        Returns:
            Message object if successful, None otherwise
        """
        try:
            message = Message.create_assistant_message(
                chat_id=chat_id,
                content=content,
                code=code,
                output_type=output_type,
                output=output,
                result=result,
                plot_path=plot_path,
                modified_dataframe_path=modified_dataframe_path,
                modification_summary=modification_summary,
                explanation=explanation,
                thinking=thinking
            )

            success = self.add_message(project_id, chat_id, message)

            if success:
                return message
            return None

        except Exception as e:
            print(f"Error adding assistant message: {e}")
            return None

    def get_messages(
        self,
        project_id: str,
        chat_id: str
    ) -> List[Message]:
        """
        Get all messages for a chat

        Args:
            project_id: Project UUID
            chat_id: Chat UUID

        Returns:
            List of Message objects (chronological order)
        """
        result = self.get_chat(project_id, chat_id)
        if result is None:
            return []

        chat, messages = result
        return messages

    def get_last_n_messages(
        self,
        project_id: str,
        chat_id: str,
        n: int = 10
    ) -> List[Message]:
        """
        Get the last N messages from a chat

        Args:
            project_id: Project UUID
            chat_id: Chat UUID
            n: Number of messages to retrieve

        Returns:
            List of last N messages
        """
        messages = self.get_messages(project_id, chat_id)
        return messages[-n:] if len(messages) > n else messages

    # ===== Gemini Chat History =====

    def update_gemini_history(
        self,
        project_id: str,
        chat_id: str,
        gemini_history: list
    ) -> bool:
        """
        Update Gemini chat history for a chat
        This is used to maintain Gemini's conversation context

        Args:
            project_id: Project UUID
            chat_id: Chat UUID
            gemini_history: Serializable Gemini history (list of dicts)

        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.get_chat(project_id, chat_id)
            if result is None:
                print(f"Chat {chat_id} not found")
                return False

            chat, messages = result

            # Update Gemini history
            chat.gemini_chat_history = gemini_history
            chat.updated_at = datetime.utcnow()

            # Save updated chat
            return self.state_manager.save_chat(chat, messages)

        except Exception as e:
            print(f"Error updating Gemini history: {e}")
            return False

    def get_gemini_history(
        self,
        project_id: str,
        chat_id: str
    ) -> list:
        """
        Get Gemini chat history for a chat

        Args:
            project_id: Project UUID
            chat_id: Chat UUID

        Returns:
            Gemini chat history list (empty if not found)
        """
        chat = self.get_chat_metadata(project_id, chat_id)
        if chat is None:
            return []
        return chat.gemini_chat_history

    # ===== Chat Deletion =====

    def delete_chat(self, project_id: str, chat_id: str) -> bool:
        """
        Delete a chat and all its messages

        Args:
            project_id: Project UUID
            chat_id: Chat UUID

        Returns:
            True if successful, False otherwise
        """
        return self.state_manager.delete_chat(project_id, chat_id)

    def clear_chat_messages(self, project_id: str, chat_id: str) -> bool:
        """
        Clear all messages from a chat (keep chat metadata)

        Args:
            project_id: Project UUID
            chat_id: Chat UUID

        Returns:
            True if successful, False otherwise
        """
        try:
            chat = self.get_chat_metadata(project_id, chat_id)
            if chat is None:
                return False

            # Reset chat metadata
            chat.message_count = 0
            chat.gemini_chat_history = []
            chat.updated_at = datetime.utcnow()

            # Save with empty messages
            return self.state_manager.save_chat(chat, messages=[])

        except Exception as e:
            print(f"Error clearing chat messages: {e}")
            return False

    # ===== Chat Statistics =====

    def get_chat_stats(self, project_id: str, chat_id: str) -> dict:
        """
        Get statistics for a chat

        Returns:
            Dict with message count, timestamps, etc.
        """
        try:
            result = self.get_chat(project_id, chat_id)
            if result is None:
                return {}

            chat, messages = result

            user_message_count = sum(1 for m in messages if m.role == "user")
            assistant_message_count = sum(1 for m in messages if m.role == "assistant")

            return {
                "chat_id": chat.id,
                "chat_name": chat.name,
                "created_at": chat.created_at.isoformat(),
                "updated_at": chat.updated_at.isoformat(),
                "total_messages": len(messages),
                "user_messages": user_message_count,
                "assistant_messages": assistant_message_count
            }

        except Exception as e:
            print(f"Error getting chat stats: {e}")
            return {}

    # ===== Search Operations =====

    def search_messages(
        self,
        project_id: str,
        chat_id: str,
        query: str
    ) -> List[Message]:
        """
        Search messages in a chat by content

        Args:
            project_id: Project UUID
            chat_id: Chat UUID
            query: Search query (case-insensitive)

        Returns:
            List of matching messages
        """
        messages = self.get_messages(project_id, chat_id)
        query_lower = query.lower()

        return [
            m for m in messages
            if query_lower in m.content.lower()
        ]

    def search_all_chats(
        self,
        project_id: str,
        query: str
    ) -> dict:
        """
        Search all chats in a project

        Args:
            project_id: Project UUID
            query: Search query

        Returns:
            Dict mapping chat_id to list of matching messages
        """
        chats = self.list_chats(project_id)
        results = {}

        for chat in chats:
            matching_messages = self.search_messages(project_id, chat.id, query)
            if matching_messages:
                results[chat.id] = {
                    "chat_name": chat.name,
                    "messages": matching_messages
                }

        return results

    # ===== Utility Methods =====

    def get_chat_count(self, project_id: str) -> int:
        """Get total number of chats for a project"""
        return len(self.state_manager.list_chat_ids(project_id))

    def get_total_message_count(self, project_id: str) -> int:
        """Get total number of messages across all chats"""
        chats = self.list_chats(project_id)
        return sum(chat.message_count for chat in chats)

    def export_chat_history(
        self,
        project_id: str,
        chat_id: str
    ) -> dict:
        """
        Export complete chat history as dict

        Returns:
            Dict with chat metadata and all messages
        """
        try:
            result = self.get_chat(project_id, chat_id)
            if result is None:
                return {}

            chat, messages = result

            return {
                "chat": chat.to_dict(),
                "messages": [m.to_dict() for m in messages]
            }

        except Exception as e:
            print(f"Error exporting chat history: {e}")
            return {}
