#!/usr/bin/env python3
"""
Backend Demo - Test AI Agent without UI
Run queries directly against the AI agent to verify Phase 1 & 2
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.project_manager import ProjectManager
from src.chat_manager import ChatManager
from src.version_manager import VersionManager
from src.ai_agent import AIAgent
from src.eda_utils import generate_eda_context


def print_banner(text):
    """Print a nice banner"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_result(result):
    """Print query result nicely"""
    if not result["success"]:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        return

    print(f"\n✅ Success!")
    print(f"Output Type: {result['output_type']}")

    if result.get('explanation'):
        print(f"\n📝 Explanation:")
        print(f"   {result['explanation']}")

    if result.get('code'):
        print(f"\n💻 Code Generated:")
        print("   " + "\n   ".join(result['code'].split('\n')))

    if result.get('output'):
        print(f"\n📊 Output:")
        print("   " + "\n   ".join(result['output'].split('\n')))

    if result.get('plot_path'):
        print(f"\n🎨 Plot saved to: {result['plot_path']}")

    if result.get('modified_dataframe_path'):
        print(f"\n💾 Modified data saved to: {result['modified_dataframe_path']}")
        if result.get('modification_summary'):
            s = result['modification_summary']
            print(f"   Rows: {s['rows_before']} → {s['rows_after']}")
            print(f"   Columns: {s['cols_before']} → {s['cols_after']}")


def load_user_data():
    """Load user journey data from CSV"""
    csv_path = './sample_data.csv'

    if not os.path.exists(csv_path):
        print(f"\n❌ Error: CSV file not found at {csv_path}")
        sys.exit(1)

    try:
        df = pd.read_csv(csv_path)
        return df, csv_path
    except Exception as e:
        print(f"\n❌ Error loading CSV: {e}")
        sys.exit(1)


def main():
    """Run backend demo"""

    print_banner("🤖 AI Data Analyst - Backend Demo")

    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("\n❌ Error: GEMINI_API_KEY not found in .env file")
        print("\nPlease set your API key:")
        print("  echo 'GEMINI_API_KEY=your-key-here' > .env")
        sys.exit(1)

    print(f"\n✓ Using API key: {api_key[:10]}...")

    # Setup
    BASE_DIR = "demo_data"
    print(f"✓ Using data directory: {BASE_DIR}/")

    pm = ProjectManager(BASE_DIR)
    cm = ChatManager(BASE_DIR)
    vm = VersionManager(BASE_DIR)

    # Load user data
    print("\n📊 Loading user journey dataset...")
    df, csv_path = load_user_data()
    print(f"   {len(df)} rows, {len(df.columns)} columns")
    print(f"   Columns: {', '.join(df.columns[:10].tolist())}...")  # Show first 10 columns

    # Create project
    print("\n🗂️  Creating project...")
    project = pm.create_project(df, "sample_data.csv", "User Journey Analysis Demo")
    if not project:
        print("❌ Failed to create project")
        sys.exit(1)

    print(f"   Project: {project.name}")
    print(f"   Project ID: {project.id}")

    # Load dataframe and generate context
    df = vm.load_current_dataframe(project.id)
    eda_context = generate_eda_context(df)
    print(f"   EDA context: {len(eda_context)} chars")

    # Initialize AI agent
    print("\n🤖 Initializing AI agent...")
    agent = AIAgent(api_key=api_key, base_dir=BASE_DIR)

    # Get active chat
    chat_result = cm.get_chat(project.id, project.active_chat_id)
    if not chat_result:
        print("❌ Failed to get chat")
        sys.exit(1)

    chat, messages = chat_result
    print(f"   Chat ID: {chat.id}")

    # Start chat session
    success = agent.start_chat_session(
        project.id,
        chat.id,
        df,
        eda_context
    )

    if not success:
        print("❌ Failed to start chat session")
        sys.exit(1)

    print("   ✓ Chat session started")

    # Interactive query loop
    print_banner("💬 Interactive Query Mode")
    print("\nYou can now ask questions about the user journey data!")
    print("\nExamples:")
    print("  - How many users are in the dataset?")
    print("  - What are the most common journey names?")
    print("  - Show me users from the abha_journey")
    print("  - Create a bar chart of journey types")
    print("  - Give me users with health insurance data that I can download")
    print("\nType 'quit' to exit\n")

    query_count = 0

    while True:
        try:
            # Get user input
            user_query = input("\n🔍 Your question: ").strip()

            if not user_query:
                continue

            if user_query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            query_count += 1
            print(f"\n⏳ Processing query #{query_count}...")

            # Process query
            result = agent.process_query(user_query, save_to_chat=True)

            # Print result
            print_result(result)

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

    # Cleanup
    agent.close_session()
    print("\n✓ Session closed")

    # Show summary
    print_banner("📈 Session Summary")
    chat_result = cm.get_chat(project.id, chat.id)
    if chat_result:
        chat, messages = chat_result
        user_msgs = [m for m in messages if m.role == "user"]
        assistant_msgs = [m for m in messages if m.role == "assistant"]
        print(f"\n  Total queries: {len(user_msgs)}")
        print(f"  Responses: {len(assistant_msgs)}")
        print(f"  Chat history saved to: {BASE_DIR}/projects/{project.id}/chats/{chat.id}.json")


if __name__ == "__main__":
    main()
