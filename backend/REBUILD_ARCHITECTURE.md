# AI Data Analyst v2.0 - Complete Architecture Summary

> **Historical, as of 2026-11-01.** This is the January 2026 rebuild guide; it assumes a Streamlit frontend and describes a Gemini-history restore path that the current code does not have. Current state: see `../README.md` and `../docs/NOTES.md`.

**Date**: January 7, 2026
**Status**: Implementation guide for fresh rebuild with Git

---

## 🎯 Product Vision

A multi-project, multi-chat data analysis application where users can:
1. Upload CSV files and chat with AI about their data
2. Get three types of responses: exploratory answers, visualizations, or modified data
3. Download modified DataFrames as artifacts (like Claude)
4. Maintain full conversation context with Gemini
5. Track version history of data modifications

---

## 🏗️ Architecture Overview

### Core Principles

1. **Gemini-Driven Intelligence**: Let Gemini decide output types and formats via JSON responses
2. **Full Persistence**: Everything saves to disk (projects, chats, messages, versions)
3. **Manager Pattern**: Separation of concerns (ProjectManager, ChatManager, VersionManager, etc.)
4. **Conversation Context**: Gemini maintains full chat history (serialized to JSON)
5. **Downloadable Artifacts**: Modified DataFrames saved as CSV files for download

### Technology Stack

- **Frontend**: Streamlit
- **AI Model**: Google Gemini 2.0 Flash Exp
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib
- **Storage**: JSON files + CSV files (no database)
- **Version Control**: Git (NEW - critical for next implementation)

---

## 📁 File Structure

```
ai_data_analyst/
├── chat_analyst_ui.py           # Main Streamlit app
├── auto_eda.py                  # Automated EDA context generation
├── .env                         # API key storage (not committed)
├── requirements.txt
│
├── src/
│   ├── __init__.py
│   ├── models.py                # Data models (Project, Chat, Message, Version)
│   ├── utils.py                 # Atomic file writes, CSV operations
│   ├── state_manager.py         # Low-level disk persistence
│   ├── project_manager.py       # High-level project operations
│   ├── chat_manager.py          # Chat and message management
│   ├── version_manager.py       # CSV version control
│   ├── ai_agent.py              # Gemini integration & code execution
│   └── ui_components.py         # Reusable Streamlit components
│
├── data/                        # All user data (gitignored)
│   ├── config.json
│   ├── plots/
│   ├── temp_modifications/      # Temp storage for modified DataFrames
│   └── projects/
│       └── {project-uuid}/
│           ├── metadata.json
│           ├── current.csv
│           ├── chats/
│           │   └── {chat-uuid}.json
│           └── versions/
│               ├── v1.csv
│               ├── v2.csv
│               └── version_log.json
│
└── tests/
    ├── test_phase1.py           # 31 tests for core infrastructure
    └── test_phase2.py           # 35 tests for chat/AI integration
```

---

## 🔑 Critical Implementation Details

### 1. Data Models (`src/models.py`)

```python
@dataclass
class Message:
    id: str
    chat_id: str
    role: str  # "user" | "assistant"
    content: str
    timestamp: datetime

    # Assistant-specific
    code: Optional[str] = None
    output_type: Optional[str] = None  # "exploratory" | "visualization" | "modification"
    output: Optional[str] = None
    explanation: Optional[str] = None

    # For modifications
    modified_dataframe_path: Optional[str] = None
    modification_summary: Optional[dict] = None  # {rows_before, rows_after, cols_before, cols_after}

    # For visualizations
    plot_path: Optional[str] = None
```

### 2. Gemini History Serialization (`src/ai_agent.py`)

**CRITICAL**: Gemini's `Content` objects aren't JSON serializable.

**Solution**:
```python
def _save_gemini_history(self):
    """Save Gemini history in serializable format"""
    serializable_history = []
    for msg in self.active_chat_session.history:
        serializable_history.append({
            "role": msg.role,
            "parts": [{"text": part.text} for part in msg.parts]
        })

    self.chat_manager.update_gemini_history(
        self.current_project_id,
        self.current_chat_id,
        serializable_history
    )

def start_chat_session(self, ...):
    """Restore Gemini history on chat load"""
    history_data = self.chat_manager.get_gemini_history(project_id, chat_id)

    if history_data:
        from google.generativeai.types import content_types
        restored_history = [
            content_types.to_content(msg) for msg in history_data
        ]
        self.active_chat_session = self.model.start_chat(history=restored_history)
    else:
        # Fresh chat - send system instruction
        self.active_chat_session = self.model.start_chat()
        self.active_chat_session.send_message(system_instruction)
```

### 3. Gemini System Instruction

**Critical**: Must request JSON format explicitly:

```python
def _build_system_instruction(self, dataset_context, business_context=None):
    return f"""You are an expert data analyst assistant.

DATASET CONTEXT:
{dataset_context}

RESPONSE FORMAT (CRITICAL):
You MUST respond with valid JSON in this exact structure:
{{
  "output_type": "exploratory" | "visualization" | "modification",
  "code": "Python code here",
  "explanation": "Brief explanation"
}}

OUTPUT TYPES:

1. **exploratory**: Answering questions, showing data
   - Code should print results
   - Example: print(df['column'].mean())

2. **visualization**: Creating plots/charts
   - Code MUST save plot: plt.savefig('plot.png', bbox_inches='tight', dpi=100)
   - Code MUST call: plt.close()

3. **modification**: Transforming/filtering the DataFrame
   - Code MUST assign result to 'result' variable
   - Example: result = df[df['state'] == 'CA']
   - User will download this modified DataFrame

RULES:
- DataFrame is available as 'df' - DO NOT load it
- For modifications, ALWAYS assign to 'result' variable
- Return ONLY valid JSON, no extra text
"""
```

### 4. Processing Queries (`src/ai_agent.py`)

```python
def process_query(self, user_query: str, save_to_chat: bool = True):
    # Send query to Gemini
    response = self.active_chat_session.send_message(user_query)
    ai_response = response.text

    # Parse JSON response
    try:
        response_json = json.loads(ai_response)
        output_type = response_json.get("output_type", "exploratory")
        code = response_json.get("code", "")
        explanation = response_json.get("explanation", "")
    except json.JSONDecodeError:
        # Fallback to code extraction
        code = self._extract_code(ai_response)
        output_type = self._detect_output_type(user_query)
        explanation = self._extract_explanation(ai_response)

    # Execute code
    execution_result = self._execute_code(code, output_type)

    # Save message with all metadata
    self.chat_manager.add_assistant_message(
        project_id, chat_id,
        content=explanation,
        code=code,
        output_type=output_type,
        output=execution_result.get("output"),
        modified_dataframe_path=execution_result.get("modified_dataframe_path"),
        modification_summary=execution_result.get("modification_summary"),
        plot_path=execution_result.get("plot_path"),
        explanation=explanation
    )

    # Save Gemini history
    self._save_gemini_history()
```

### 5. Code Execution with 'result' Variable

```python
def _execute_code(self, code: str, output_type: str) -> dict:
    exec_globals = {
        'df': self.current_dataframe.copy(),
        'pd': pd, 'plt': plt, 'np': np, 'sns': sns
    }

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    exec(code, exec_globals)

    sys.stdout = old_stdout
    output = captured_output.getvalue()

    result_data = {"success": True, "output": output}

    if output_type == "modification":
        # Check for 'result' variable
        if 'result' in exec_globals:
            modified_df = exec_globals['result']

            if isinstance(modified_df, pd.DataFrame):
                # Save to temp location
                temp_path = os.path.join(
                    self.base_dir, "temp_modifications",
                    f"{self.current_chat_id}_{uuid.uuid4().hex[:8]}.csv"
                )
                modified_df.to_csv(temp_path, index=False)
                result_data["modified_dataframe_path"] = temp_path

                # Generate summary
                result_data["modification_summary"] = {
                    "rows_before": len(self.current_dataframe),
                    "rows_after": len(modified_df),
                    "cols_before": len(self.current_dataframe.columns),
                    "cols_after": len(modified_df.columns),
                    "new_columns": list(set(modified_df.columns) - set(self.current_dataframe.columns)),
                    "removed_columns": list(set(self.current_dataframe.columns) - set(modified_df.columns))
                }

    elif output_type == "visualization":
        if os.path.exists("plot.png"):
            plot_path = os.path.join(self.base_dir, "plots", f"plot_{self.current_chat_id}.png")
            shutil.move("plot.png", plot_path)
            result_data["plot_path"] = plot_path

    return result_data
```

### 6. UI Rendering (`src/ui_components.py`)

```python
def render_assistant_message(msg: Message):
    with st.chat_message("assistant"):
        # Explanation
        if msg.explanation:
            st.write(msg.explanation)

        # Code (collapsible)
        if msg.code:
            with st.expander("📝 Code", expanded=False):
                st.code(msg.code, language="python")

        # Output based on type
        if msg.output_type == "exploratory":
            if msg.output:
                st.info(msg.output)

        elif msg.output_type == "visualization":
            if msg.plot_path and os.path.exists(msg.plot_path):
                st.image(msg.plot_path)

        elif msg.output_type == "modification":
            if msg.modified_dataframe_path and os.path.exists(msg.modified_dataframe_path):
                modified_df = pd.read_csv(msg.modified_dataframe_path)

                # Show summary
                if msg.modification_summary:
                    s = msg.modification_summary
                    st.success(f"""
✨ **Data Modified**
- Rows: {s['rows_before']:,} → {s['rows_after']:,}
- Columns: {s['cols_before']} → {s['cols_after']}
                    """)

                # Preview
                with st.expander("👁️ Preview Modified Data", expanded=True):
                    st.dataframe(modified_df.head(10))

                # Download button
                csv_data = modified_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Download Modified Data ({len(modified_df):,} rows)",
                    data=csv_data,
                    file_name=f"modified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
```

---

## 🚀 Implementation Order for Fresh Start

### Phase 0: Setup (30 min)

1. **Git initialization**
   ```bash
   git init
   git add .gitignore
   echo "data/" >> .gitignore
   echo ".env" >> .gitignore
   echo "__pycache__/" >> .gitignore
   git commit -m "Initial commit with gitignore"
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Basic file structure**
   - Create src/ directory with __init__.py
   - Create data/ directory (gitignored)
   - Create requirements.txt

### Phase 1: Core Infrastructure (2-3 hours)

**Commit after each file:**

1. `src/models.py` - All data models
   - Test: Can create, serialize, deserialize all models
   - Commit: "Add data models with JSON serialization"

2. `src/utils.py` - Atomic file operations
   - Test: safe_write_json, DataFrame comparison
   - Commit: "Add utility functions for file operations"

3. `src/state_manager.py` - Low-level persistence
   - Test: Save/load projects, chats
   - Commit: "Add state manager for disk persistence"

4. `src/version_manager.py` - Version control
   - Test: Create versions, revert, download
   - Commit: "Add version manager for CSV tracking"

5. `src/project_manager.py` - High-level orchestration
   - Test: Create project, add chats
   - Commit: "Add project manager"

6. Run test_phase1.py (31 tests)
   - Commit: "Phase 1 complete - all tests passing"

### Phase 2: AI Integration (2-3 hours)

**Commit after each file:**

1. `src/chat_manager.py` - Chat operations
   - Include Gemini history methods (even if not used yet)
   - Test: Create chat, add messages, search
   - Commit: "Add chat manager"

2. `auto_eda.py` - EDA context generation
   - Test: Generate context string from CSV
   - Commit: "Add automated EDA for dataset context"

3. `src/ai_agent.py` - Gemini integration
   - **CRITICAL**: Implement Gemini history serialization from start
   - **CRITICAL**: Use JSON response format
   - Test: Process query, execute code, save history
   - Commit: "Add AI agent with Gemini integration"

4. Run test_phase2.py (35 tests)
   - Commit: "Phase 2 complete - all tests passing"

### Phase 3: UI (2-3 hours)

**Commit after each component:**

1. `src/ui_components.py` - Reusable components
   - Start with simple components first
   - Test manually as you build
   - Commit after each major component:
     - "Add sidebar components"
     - "Add message rendering"
     - "Add modification UI with download"

2. `chat_analyst_ui.py` - Main app
   - **IMPORTANT**: Use @st.cache_resource for managers AND agent
   - Test: Create project, send queries, see responses
   - Commit: "Add Streamlit UI"

3. Manual testing session
   - Test all three output types
   - Test download functionality
   - Commit: "Phase 3 complete - UI working"

### Phase 4: Polish (1 hour)

1. Documentation
   - Update README.md
   - Create QUICK_START.md
   - Commit: "Add documentation"

2. Final testing
   - Run all automated tests
   - Manual E2E test
   - Commit: "Production ready"

---

## ⚠️ Critical Gotchas (Lessons Learned)

### 1. Gemini History Serialization

**Problem**: Gemini's `Content` objects can't be serialized to JSON
**Solution**: Extract only `role` and `text` parts
**When to implement**: From the very start in Phase 2

### 2. System Instruction Timing

**Problem**: If you restore history without sending system instruction, Gemini won't return JSON
**Solution**: Always send system instruction at chat start:
```python
if history_data:
    self.active_chat_session = self.model.start_chat(history=restored_history)
else:
    self.active_chat_session = self.model.start_chat()
    self.active_chat_session.send_message(system_instruction)
```

### 3. Agent Caching in Streamlit

**Problem**: Uncached agent gets recreated every rerun
**Solution**: Use `@st.cache_resource` decorator:
```python
@st.cache_resource
def get_ai_agent(api_key: str):
    return AIAgent(api_key=api_key, base_dir="data")
```

### 4. Download Button File Handles

**Problem**: Passing file handle to st.download_button closes before Streamlit reads
**Solution**: Read file content first:
```python
with open(path, 'rb') as f:
    file_data = f.read()
st.download_button(data=file_data, ...)
```

### 5. 'result' Variable Convention

**Problem**: Need predictable variable name for modified DataFrames
**Solution**: Always use `result = ...` in modification code:
```python
# Gemini generates:
result = df[df['column'] > 100]

# We check:
if 'result' in exec_globals:
    modified_df = exec_globals['result']
```

---

## 🧪 Testing Strategy

### Automated Tests

**test_phase1.py** (31 tests):
- Data model serialization
- Project creation/management
- Chat creation/management
- Version creation/revert
- State persistence

**test_phase2.py** (35 tests):
- Chat operations
- Message operations
- EDA generation
- AI agent initialization
- Code execution (mock)

### Manual Testing Checklist

**Exploratory Queries**:
- [ ] "How many rows?"
- [ ] "What's the average of column X?"
- [ ] "Show first 10 rows"

**Visualization Queries**:
- [ ] "Plot distribution of column X"
- [ ] "Show trends over time"

**Modification Queries**:
- [ ] "Filter to only rows where X > 100"
- [ ] "Add a new column Y = X * 2"
- [ ] "Create subset with only columns A, B, C"

**Download Testing**:
- [ ] Click download button
- [ ] Verify CSV downloads
- [ ] Verify correct data in CSV

**Context Testing**:
- [ ] Ask follow-up question ("Now show me the top 10")
- [ ] Verify Gemini remembers context

**Persistence Testing**:
- [ ] Refresh page
- [ ] Verify messages still there
- [ ] Verify download buttons still work

---

## 📦 Dependencies (requirements.txt)

```
streamlit==1.31.0
pandas==2.1.4
numpy==1.26.3
matplotlib==3.8.2
seaborn==0.13.1
python-dotenv==1.0.0
google-generativeai==0.3.2
```

---

## 🔐 Environment Variables (.env)

```bash
GEMINI_API_KEY=your_api_key_here
```

---

## 🎓 Key Architectural Decisions

### Why Manager Pattern?

- **Separation of Concerns**: Each manager has one responsibility
- **Testability**: Easy to test in isolation
- **Maintainability**: Changes to one component don't affect others

### Why JSON for Storage?

- **Human Readable**: Easy to debug
- **No Database Needed**: Simple deployment
- **Version Control Friendly**: Can track changes in Git (if needed)

### Why Streamlit?

- **Fast Development**: Built-in components for data apps
- **Python Native**: No frontend framework needed
- **Auto-reload**: See changes immediately

### Why Gemini?

- **JSON Output**: Can be instructed to return structured data
- **Context Window**: Large enough for full chat history
- **Cost Effective**: Flash model is fast and cheap

---

## 🚨 Known Limitations

1. **No Real Database**: All data in JSON files (okay for single user)
2. **No Authentication**: Anyone with URL can access
3. **No Concurrent Users**: Streamlit session-based
4. **File Size Limits**: Large CSVs (>100MB) may be slow
5. **No Plot Customization**: Uses Gemini's default plot styling

---

## 🎯 Success Criteria

**Minimum Viable Product**:
- ✅ Upload CSV
- ✅ Ask questions in natural language
- ✅ Get three types of responses (exploratory, visualization, modification)
- ✅ Download modified data
- ✅ Full conversation context
- ✅ Message history persists

**Nice to Have** (Future):
- [ ] Multiple file formats (Excel, JSON)
- [ ] Collaborative features (share projects)
- [ ] Advanced visualizations (Plotly)
- [ ] SQL database backend
- [ ] API mode

---

## 📝 Git Workflow for Next Implementation

```bash
# Initial setup
git init
git commit -m "Initial commit"

# Phase 1
git checkout -b phase1-core-infrastructure
# ... implement models.py
git add src/models.py
git commit -m "Add data models"
# ... continue with other files
git commit -m "Phase 1 complete - all tests passing"
git checkout main
git merge phase1-core-infrastructure

# Phase 2
git checkout -b phase2-ai-integration
# ... implement chat_manager.py, ai_agent.py
git commit -m "Phase 2 complete - all tests passing"
git checkout main
git merge phase2-ai-integration

# Phase 3
git checkout -b phase3-ui
# ... implement ui_components.py, chat_analyst_ui.py
git commit -m "Phase 3 complete - UI working"
git checkout main
git merge phase3-ui

# Production
git tag v1.0.0
```

---

## 🔄 Recovery Plan (If Something Breaks)

**With Git**:
```bash
git log --oneline  # Find last working commit
git checkout <commit-hash>  # Revert to working state
```

**Without Git** (Current Situation):
- No way to recover
- Must rebuild from scratch
- **THIS IS WHY GIT IS CRITICAL**

---

**END OF ARCHITECTURE SUMMARY**

This document contains everything needed to rebuild the AI Data Analyst v2.0 from scratch with proper version control. Follow the implementation order, commit frequently, and test at each step.
