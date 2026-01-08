#!/usr/bin/env python3
"""
AI Data Analyst - Streamlit UI
Phase 3: Modern conversational data analysis interface
"""

import os
import sys
from datetime import datetime
from io import BytesIO
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import backend modules
from src.project_manager import ProjectManager
from src.chat_manager import ChatManager
from src.version_manager import VersionManager
from src.ai_agent import AIAgent
from src.eda_utils import generate_eda_context

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - Glass Effect, Cards, Animations
# ============================================================================

def inject_custom_css():
    """Inject custom CSS for modern UI styling"""
    st.markdown("""
    <style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Fira+Code&display=swap');

    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* Sidebar styling - Glass effect */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-right: 1px solid #E5E5E5;
    }

    /* Dark mode sidebar */
    [data-theme="dark"] [data-testid="stSidebar"] {
        background: rgba(45, 45, 45, 0.8);
        border-right: 1px solid #404040;
    }

    /* Project cards */
    .project-card {
        background: #F7F7F8;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        border: 1px solid #E5E5E5;
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .project-card:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .project-card.active {
        background: #2563EB;
        color: white;
        border-color: #2563EB;
    }

    /* Dark mode project cards */
    [data-theme="dark"] .project-card {
        background: #2D2D2D;
        border-color: #404040;
    }

    [data-theme="dark"] .project-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    /* Chat cards */
    .chat-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        margin: 12px;
        border: 1px solid #E5E5E5;
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .chat-card:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    [data-theme="dark"] .chat-card {
        background: #2D2D2D;
        border-color: #404040;
    }

    /* Buttons */
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.15s ease;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }

    /* Message containers */
    .user-message {
        background: #F7F7F8;
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
    }

    .assistant-message {
        background: #FFFFFF;
        border: 1px solid #E5E5E5;
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
    }

    [data-theme="dark"] .user-message {
        background: #2D2D2D;
    }

    [data-theme="dark"] .assistant-message {
        background: #1A1A1A;
        border-color: #404040;
    }

    /* Code blocks */
    .stCodeBlock {
        border-radius: 8px;
    }

    /* Sticky header for chat interface */
    .sticky-header {
        position: sticky;
        top: 0;
        z-index: 999;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 16px 0;
        margin: -16px 0 16px 0;
        border-bottom: 1px solid #E5E5E5;
    }

    [data-theme="dark"] .sticky-header {
        background: rgba(26, 26, 26, 0.95);
        border-bottom: 1px solid #404040;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Smooth animations */
    .element-container {
        animation: fadeIn 0.3s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize Streamlit session state variables"""

    # Navigation state
    if 'view' not in st.session_state:
        st.session_state.view = 'project_home'  # 'project_home' or 'chat'

    if 'active_project_id' not in st.session_state:
        st.session_state.active_project_id = None

    if 'active_chat_id' not in st.session_state:
        st.session_state.active_chat_id = None

    # UI state
    if 'show_data_modal' not in st.session_state:
        st.session_state.show_data_modal = False

    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'

    # Backend managers (initialized once)
    if 'pm' not in st.session_state:
        base_dir = os.getenv('DATA_DIR', 'data')
        st.session_state.pm = ProjectManager(base_dir)
        st.session_state.cm = ChatManager(base_dir)
        st.session_state.vm = VersionManager(base_dir)
        st.session_state.base_dir = base_dir

    # AI Agent (initialized per chat session)
    if 'agent' not in st.session_state:
        st.session_state.agent = None

    # Messages for current chat
    if 'messages' not in st.session_state:
        st.session_state.messages = []

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_timestamp(dt):
    """Format datetime for display"""
    now = datetime.now()
    delta = now - dt

    if delta.days == 0:
        if delta.seconds < 3600:
            mins = delta.seconds // 60
            return f"{mins} minute{'s' if mins != 1 else ''} ago"
        else:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif delta.days == 1:
        return "Yesterday"
    elif delta.days < 7:
        return f"{delta.days} days ago"
    else:
        return dt.strftime("%b %d, %Y")

def safe_get_project(project_id):
    """Safely get project with error handling"""
    try:
        return st.session_state.pm.get_project(project_id)
    except Exception as e:
        st.error(f"Error loading project: {e}")
        return None

def safe_get_chat(project_id, chat_id):
    """Safely get chat with error handling"""
    try:
        return st.session_state.cm.get_chat(project_id, chat_id)
    except Exception as e:
        st.error(f"Error loading chat: {e}")
        return None

# ============================================================================
# SIDEBAR - Projects List
# ============================================================================

def render_sidebar():
    """Render sidebar with projects list"""

    with st.sidebar:
        # Header
        st.markdown("### 📊 AI Data Analyst")

        # New Project button
        if st.button("➕ New Project", use_container_width=True, type="primary"):
            st.session_state.view = 'new_project'
            st.rerun()

        st.markdown("---")

        # Projects list
        st.markdown("**Your Projects**")

        projects = st.session_state.pm.list_all_projects()

        if not projects:
            st.info("No projects yet. Create your first project!")
        else:
            for project in projects:
                # Project card
                is_active = st.session_state.active_project_id == project.id

                button_label = f"{'📌' if is_active else '📊'} {project.name}"

                if st.button(
                    button_label,
                    key=f"project_{project.id}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary"
                ):
                    st.session_state.active_project_id = project.id
                    st.session_state.active_chat_id = project.active_chat_id
                    st.session_state.view = 'project_home'
                    st.session_state.messages = []
                    st.rerun()

                # Project metadata
                st.caption(f"{project.original_filename} • {project.total_rows:,} rows")
                st.caption(f"Updated {format_timestamp(project.updated_at)}")
                st.markdown("")  # Spacing

        # Footer
        st.markdown("---")

        # Dark mode toggle (placeholder for now)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚙️ Settings"):
                st.info("Settings coming soon!")
        with col2:
            if st.button("❓ Help"):
                st.info("Help documentation coming soon!")

# ============================================================================
# NEW PROJECT VIEW
# ============================================================================

def render_new_project_view():
    """Render new project creation view"""

    st.markdown("## 📊 Create New Project")
    st.markdown("Upload a CSV file to start analyzing your data")

    # Project name
    project_name = st.text_input(
        "Project Name",
        placeholder="e.g., Sales Analysis Q4 2024"
    )

    # File upload
    uploaded_file = st.file_uploader(
        "Upload CSV File",
        type=['csv'],
        help="Upload a CSV file containing your data"
    )

    if uploaded_file is not None:
        # Show preview
        try:
            df = pd.read_csv(uploaded_file)

            st.success(f"✓ File loaded: {len(df):,} rows × {len(df.columns)} columns")

            # Preview
            with st.expander("Preview data (first 5 rows)"):
                st.dataframe(df.head(), use_container_width=True)

            # Create project button
            col1, col2 = st.columns([1, 3])

            with col1:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.view = 'project_home'
                    st.rerun()

            with col2:
                if st.button("Create Project", type="primary", use_container_width=True):
                    if not project_name:
                        st.error("Please enter a project name")
                    else:
                        with st.spinner("Creating project..."):
                            # Create project
                            project = st.session_state.pm.create_project(
                                csv_dataframe=df,
                                original_filename=uploaded_file.name,
                                project_name=project_name
                            )

                            if project:
                                st.success(f"✓ Project '{project.name}' created!")
                                st.session_state.active_project_id = project.id
                                st.session_state.active_chat_id = project.active_chat_id
                                st.session_state.view = 'project_home'
                                st.rerun()
                            else:
                                st.error("Failed to create project. Please try again.")

        except Exception as e:
            st.error(f"Error reading CSV file: {e}")

# ============================================================================
# PROJECT HOME VIEW - Chats List
# ============================================================================

def render_project_home():
    """Render project home page with chats list"""

    project = safe_get_project(st.session_state.active_project_id)

    if not project:
        st.warning("No project selected. Please select a project from the sidebar.")
        return

    # Header
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f"## 📊 {project.name}")
        st.caption(f"{project.original_filename} • {project.total_rows:,} rows, {project.total_columns} columns")

    with col2:
        if st.button("👁️ View Data", use_container_width=True):
            st.session_state.show_data_modal = True
            st.rerun()

    st.markdown("---")

    # New Chat card
    st.markdown("### 💬 Chats")

    if st.button("➕ Start New Chat", use_container_width=True, type="primary"):
        # Create new chat
        with st.spinner("Creating new chat..."):
            new_chat = st.session_state.cm.create_chat(project.id)
            if new_chat:
                st.session_state.active_chat_id = new_chat.id
                st.session_state.view = 'chat'
                st.session_state.messages = []
                st.rerun()

    st.markdown("")  # Spacing

    # Existing chats
    chats = st.session_state.cm.list_chats(project.id)

    if chats:
        # Display in grid (3 columns)
        cols_per_row = 3

        for i in range(0, len(chats), cols_per_row):
            cols = st.columns(cols_per_row)

            for j, chat in enumerate(chats[i:i+cols_per_row]):
                with cols[j]:
                    # Chat card
                    st.markdown(f"""
                    <div class="chat-card">
                        <h4>💬 {chat.name}</h4>
                        <p style="color: #6B6B6B; font-size: 14px;">
                            {chat.message_count} message{'s' if chat.message_count != 1 else ''} •
                            {format_timestamp(chat.updated_at)}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("Continue", key=f"chat_{chat.id}", use_container_width=True):
                        st.session_state.active_chat_id = chat.id
                        st.session_state.view = 'chat'
                        st.rerun()
    else:
        st.info("No chats yet. Start your first analysis!")

# ============================================================================
# DATA CONTEXT MODAL
# ============================================================================

@st.dialog("📊 Dataset Context", width="large")
def show_data_context_modal():
    """Show data context in a modal"""

    project = safe_get_project(st.session_state.active_project_id)

    if not project:
        st.error("Project not found")
        return

    # Load dataframe
    try:
        df = st.session_state.vm.load_current_dataframe(project.id)

        # Overview
        st.markdown("### 📊 Dataset Overview")
        st.markdown(f"**File:** {project.original_filename}")
        st.markdown(f"**Size:** {len(df):,} rows × {len(df.columns)} columns")

        st.markdown("---")

        # Columns info
        st.markdown("### 📋 Columns")

        col_info = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_pct = (df[col].isnull().sum() / len(df) * 100)
            col_info.append({
                "Column": col,
                "Type": dtype,
                "Nulls": f"{null_pct:.1f}%"
            })

        st.dataframe(
            pd.DataFrame(col_info),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # Value Distributions for Low-Cardinality Columns
        st.markdown("### 📊 Value Distributions")

        low_cardinality_cols = [col for col in df.columns if df[col].nunique() <= 20 and df[col].nunique() > 1]

        if low_cardinality_cols:
            # Show distributions in tabs
            tabs = st.tabs([col[:20] for col in low_cardinality_cols[:10]])  # Limit to 10 tabs

            for i, col in enumerate(low_cardinality_cols[:10]):
                with tabs[i]:
                    value_counts = df[col].value_counts()

                    # Show as bar chart
                    st.bar_chart(value_counts)

                    # Show as table with counts and percentages
                    dist_df = pd.DataFrame({
                        'Value': value_counts.index.astype(str),
                        'Count': value_counts.values,
                        'Percentage': (value_counts.values / len(df) * 100).round(2)
                    })
                    st.dataframe(dist_df, use_container_width=True, hide_index=True)
        else:
            st.info("No low-cardinality columns found (columns with ≤20 unique values)")

        st.markdown("---")

        # Sample data
        st.markdown("### 📈 Sample Data (first 10 rows)")
        st.dataframe(df.head(10), use_container_width=True)

        st.markdown("---")

        # Statistics
        st.markdown("### 📝 Statistics")
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object']).columns

        st.markdown(f"- Numeric columns: {len(numeric_cols)}")
        st.markdown(f"- Categorical columns: {len(categorical_cols)}")
        st.markdown(f"- Low-cardinality columns (≤20 unique): {len(low_cardinality_cols)}")
        st.markdown(f"- Missing values: {(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100):.1f}%")

        st.markdown("---")

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Dataset",
            data=csv,
            file_name=project.original_filename,
            mime="text/csv",
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Error loading data: {e}")

# ============================================================================
# MESSAGE RENDERING - Output Type-Specific UI
# ============================================================================

def render_assistant_message(msg):
    """Render assistant message with output type-specific UI"""

    output_type = msg.output_type

    # Show explanation if available
    if msg.explanation:
        st.markdown(f"**📝 Explanation:**")
        st.markdown(msg.explanation)
        st.markdown("")

    # === EXPLORATORY QUERY UI ===
    if output_type == "exploratory":
        # Collapsible code section
        if msg.code:
            with st.expander("💻 View Code"):
                st.code(msg.code, language="python")
                st.button("📋 Copy Code", key=f"copy_{msg.id}")

        # Output
        if msg.output:
            st.markdown("**📊 Output:**")
            st.text(msg.output)

    # === VISUALIZATION UI ===
    elif output_type == "visualization":
        # Collapsible code section
        if msg.code:
            with st.expander("💻 View Code"):
                st.code(msg.code, language="python")

        # Visualization
        if msg.plot_path and os.path.exists(msg.plot_path):
            st.markdown("**🎨 Visualization:**")
            st.image(msg.plot_path, use_container_width=True)

            # Download button
            with open(msg.plot_path, "rb") as file:
                st.download_button(
                    label="📥 Download PNG",
                    data=file,
                    file_name=os.path.basename(msg.plot_path),
                    mime="image/png",
                    key=f"download_plot_{msg.id}"
                )

    # === MODIFICATION UI ===
    elif output_type == "modification":
        # Collapsible code section
        if msg.code:
            with st.expander("💻 View Code"):
                st.code(msg.code, language="python")

        # Modification summary
        if msg.modification_summary:
            st.markdown("**💾 Modified Data:**")
            summary = msg.modification_summary

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Rows", f"{summary['rows_after']:,}",
                         delta=f"{summary['rows_after'] - summary['rows_before']:,}")
            with col2:
                st.metric("Columns", f"{summary['cols_after']}",
                         delta=f"{summary['cols_after'] - summary['cols_before']}")

        # Download modified data
        if msg.modified_dataframe_path and os.path.exists(msg.modified_dataframe_path):
            with open(msg.modified_dataframe_path, "rb") as file:
                st.download_button(
                    label="📥 Download CSV",
                    data=file,
                    file_name=os.path.basename(msg.modified_dataframe_path),
                    mime="text/csv",
                    key=f"download_csv_{msg.id}"
                )

            # Preview
            try:
                df_preview = pd.read_csv(msg.modified_dataframe_path)
                st.markdown("**Preview (first 5 rows):**")
                st.dataframe(df_preview.head(), use_container_width=True)
            except Exception as e:
                st.error(f"Error loading preview: {e}")

    # === FALLBACK (for messages without type or unknown type) ===
    else:
        if msg.content:
            st.markdown(msg.content)

        if msg.code:
            with st.expander("💻 View Code"):
                st.code(msg.code, language="python")

        if msg.output:
            st.text(msg.output)

        if msg.plot_path and os.path.exists(msg.plot_path):
            st.image(msg.plot_path)

        if msg.modified_dataframe_path and os.path.exists(msg.modified_dataframe_path):
            with open(msg.modified_dataframe_path, "rb") as file:
                st.download_button(
                    label="📥 Download File",
                    data=file,
                    file_name=os.path.basename(msg.modified_dataframe_path),
                    mime="text/csv",
                    key=f"download_{msg.id}"
                )

# ============================================================================
# AI AGENT INITIALIZATION
# ============================================================================

def init_ai_agent_for_chat(project_id, chat_id):
    """Initialize AI agent for the current chat session"""

    try:
        # Get API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            st.error("GEMINI_API_KEY not found in environment variables")
            return False

        # Initialize agent if not already done
        if st.session_state.agent is None:
            st.session_state.agent = AIAgent(
                api_key=api_key,
                base_dir=st.session_state.base_dir
            )

        # Load dataframe and EDA context
        df = st.session_state.vm.load_current_dataframe(project_id)
        eda_context = generate_eda_context(df)

        # Start chat session
        success = st.session_state.agent.start_chat_session(
            project_id,
            chat_id,
            df,
            eda_context
        )

        return success

    except Exception as e:
        st.error(f"Error initializing AI agent: {e}")
        return False

# ============================================================================
# CHAT INTERFACE
# ============================================================================

def render_chat_interface():
    """Render chat interface"""

    project = safe_get_project(st.session_state.active_project_id)
    chat_result = safe_get_chat(st.session_state.active_project_id, st.session_state.active_chat_id)

    if not project or not chat_result:
        st.warning("Chat not found. Please select a chat from the project home.")
        return

    chat, messages = chat_result

    # Initialize AI agent if needed (only when switching chats/projects)
    if st.session_state.agent is None or \
       st.session_state.agent.current_project_id != project.id or \
       st.session_state.agent.current_chat_id != chat.id:

        with st.spinner("Initializing AI agent..."):
            if not init_ai_agent_for_chat(project.id, chat.id):
                st.error("Failed to initialize AI agent. Please check your GEMINI_API_KEY.")
                return

    # Sticky Header
    st.markdown('<div class="sticky-header">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.view = 'project_home'
            st.session_state.messages = []
            st.rerun()

    with col2:
        st.markdown(f"### 💬 {chat.name}")
        st.caption(f"{project.name} • {project.original_filename}")

    with col3:
        if st.button("👁️ View Data", use_container_width=True):
            st.session_state.show_data_modal = True
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Messages container
    message_container = st.container()

    with message_container:
        if not messages:
            st.info("No messages yet. Start by asking a question about your data!")
        else:
            for msg in messages:
                if msg.role == "user":
                    with st.chat_message("user"):
                        st.markdown(msg.content)
                else:
                    with st.chat_message("assistant"):
                        # Render based on output type
                        render_assistant_message(msg)

    # Input area
    st.markdown("---")

    user_input = st.chat_input("Ask a question about your data...")

    if user_input:
        # Process query with AI agent
        with st.spinner("AI is thinking..."):
            try:
                # Process query (saves to chat automatically)
                result = st.session_state.agent.process_query(
                    user_input,
                    save_to_chat=True
                )

                if not result.get("success", False):
                    st.error(f"Error processing query: {result.get('error', 'Unknown error')}")

            except Exception as e:
                st.error(f"Error processing query: {e}")
                import traceback
                st.error(traceback.format_exc())

            st.rerun()

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application entry point"""

    # Initialize
    init_session_state()
    inject_custom_css()

    # Render sidebar (always visible)
    render_sidebar()

    # Show data modal if requested
    if st.session_state.show_data_modal:
        st.session_state.show_data_modal = False
        show_data_context_modal()

    # Main content based on view
    if st.session_state.view == 'new_project':
        render_new_project_view()

    elif st.session_state.view == 'project_home':
        if st.session_state.active_project_id:
            render_project_home()
        else:
            st.info("👈 Select a project from the sidebar or create a new one!")

    elif st.session_state.view == 'chat':
        if st.session_state.active_chat_id:
            render_chat_interface()
        else:
            st.warning("No chat selected. Please select a chat from the project home.")
            if st.button("Go to Project Home"):
                st.session_state.view = 'project_home'
                st.rerun()


if __name__ == "__main__":
    main()
