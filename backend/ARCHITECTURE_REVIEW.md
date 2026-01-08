# AI Data Analyst v2.0 - Architecture Deep Dive

**Purpose:** Understand the complete architecture before building the UI

---

## 🏗️ Architecture Overview

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE (Phase 3)                    │
│                         (Streamlit UI)                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    ORCHESTRATION LAYER                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ ProjectManager  │  │  ChatManager    │  │    AIAgent      │ │
│  │                 │  │                 │  │                 │ │
│  │ - Create/delete │  │ - Create chats  │  │ - Gemini API    │ │
│  │ - List projects │  │ - Add messages  │  │ - Code gen      │ │
│  │ - Search        │  │ - Search msgs   │  │ - Execution     │ │
│  │ - Stats         │  │ - Stats         │  │ - Context mgmt  │ │
│  └────────┬────────┘  └────────┬────────┘  └─────────────────┘ │
└───────────┼────────────────────┼──────────────────────────────┘
            │                    │
┌───────────▼────────┐  ┌────────▼────────┐
│  VersionManager    │  │  StateManager   │
│                    │  │                 │
│ - Create versions  │  │ - Save/load     │
│ - Track changes    │  │ - JSON I/O      │
│ - Revert versions  │  │ - File mgmt     │
│ - Load CSV         │  │ - Atomic writes │
└───────────┬────────┘  └────────┬────────┘
            │                    │
            └──────────┬─────────┘
                       │
┌──────────────────────▼──────────────────────┐
│           PERSISTENCE LAYER                 │
│                                             │
│  data/                                      │
│  ├── config.json (app config)              │
│  ├── projects/                             │
│  │   └── {project-uuid}/                   │
│  │       ├── metadata.json (project info)  │
│  │       ├── current.csv (active version)  │
│  │       ├── eda_context.json (cached EDA) │
│  │       ├── chats/                        │
│  │       │   └── {chat-uuid}.json          │
│  │       └── versions/                     │
│  │           ├── v1_timestamp.csv          │
│  │           ├── v2_timestamp.csv          │
│  │           └── version_log.json          │
│  └── plots/                                │
│      └── {plot-uuid}.png                   │
└─────────────────────────────────────────────┘
```

---

## 📦 Component Breakdown

### 1. Data Models (`src/models.py`)

**Purpose:** Define core data structures with serialization

```python
# Core entities
- Project: Represents a CSV file with metadata
- Chat: A conversation about a project
- Message: User or assistant message in a chat
- Version: A snapshot of the CSV at a point in time
- AppConfig: Global app configuration
```

**Key Features:**
- ✅ JSON serialization (to_dict/from_dict)
- ✅ Factory methods (create_new)
- ✅ Datetime handling
- ✅ UUID generation

**Example:**
```python
# Create a project
project = Project.create_new(
    name="Sales Analysis",
    filename="sales.csv",
    rows=10000,
    cols=25,
    size_mb=2.5
)

# Serialize to JSON
project_dict = project.to_dict()
# Save to file, send over network, etc.

# Deserialize back
project_restored = Project.from_dict(project_dict)
```

### 2. Utilities (`src/utils.py`)

**Purpose:** Helper functions for file I/O, CSV operations, etc.

**Key Functions:**
- `safe_write_json()` - Atomic writes (no corruption)
- `safe_read_json()` - Safe reads with defaults
- `get_csv_info()` - Extract CSV metadata
- `detect_dataframe_changes()` - Compare DataFrames
- `validate_csv_file()` - Check CSV validity
- Path helpers for consistent file locations

**Why Atomic Writes?**
```python
# Old way (dangerous):
with open('file.json', 'w') as f:
    json.dump(data, f)
# If crash happens during write → corrupted file

# Our way (safe):
# 1. Write to temp file
# 2. If successful, rename temp → real file
# 3. Rename is atomic operation (instant)
```

### 3. State Manager (`src/state_manager.py`)

**Purpose:** Handle all disk I/O and persistence

**Responsibilities:**
- Save/load projects (metadata.json)
- Save/load chats ({chat-uuid}.json)
- Save/load app config (config.json)
- Cache EDA context (eda_context.json)
- List/search operations
- Directory management

**Key Methods:**
```python
state = StateManager("data")

# Projects
state.save_project_metadata(project)
project = state.load_project_metadata(project_id)
projects = state.load_all_projects()

# Chats
state.save_chat(chat, messages)
chat, messages = state.load_chat(project_id, chat_id)

# Config
config = state.load_config()
state.save_config(config)
```

### 4. Version Manager (`src/version_manager.py`)

**Purpose:** CSV version control (like Git for data)

**Workflow:**
```
1. User uploads CSV
   → create_initial_version() → v1_timestamp.csv

2. AI modifies DataFrame (adds column)
   → create_new_version() → v2_timestamp.csv
   → Auto-detects changes: "Added profit_margin column"

3. User wants old data back
   → revert_to_version(1) → v3_timestamp.csv (copy of v1)
```

**Key Features:**
- Auto-detect changes (new columns, removed rows, etc.)
- Full version history (never delete old versions)
- Revert creates new version (preserves history)
- Each version has metadata (who, when, what changed)

**Example:**
```python
vm = VersionManager("data")

# Create first version
version1 = vm.create_initial_version(
    project_id="abc123",
    csv_dataframe=df,
    original_filename="data.csv"
)
# Creates: data/projects/abc123/versions/v1_20260106_120000.csv

# User modifies data, create new version
df['profit'] = df['revenue'] - df['cost']
version2 = vm.create_new_version(
    project_id="abc123",
    csv_dataframe=df,
    change_description="Added profit column"  # Optional, auto-detected
)
# Creates: v2_20260106_130000.csv

# Revert to v1
version3 = vm.revert_to_version("abc123", version_number=1)
# Creates: v3_20260106_140000.csv (copy of v1 data)
```

### 5. Project Manager (`src/project_manager.py`)

**Purpose:** High-level project orchestration

**Responsibilities:**
- Create projects (CSV → Project + Version + Default Chat)
- Coordinate StateManager + VersionManager
- CRUD operations
- Search and statistics

**Why This Layer?**
- Simplifies UI code (one interface for everything)
- Handles complex multi-step operations
- Maintains consistency between managers

**Example Flow - Create Project:**
```python
pm = ProjectManager("data")

# One call does:
# 1. Create project object
# 2. Create v1 version of CSV
# 3. Save CSV files
# 4. Create default chat
# 5. Save metadata
project = pm.create_project(
    csv_dataframe=df,
    original_filename="sales.csv",
    project_name="Sales Analysis"
)

# Behind the scenes:
# VersionManager.create_initial_version()
# StateManager.save_chat() (default chat)
# StateManager.save_project_metadata()
```

### 6. Chat Manager (`src/chat_manager.py`)

**Purpose:** Manage chats and messages

**Key Features:**
- Multiple chats per project (independent conversations)
- Full message history (user + assistant)
- Gemini chat history (for conversation context)
- Search within chat or across all chats
- Statistics (message counts, etc.)

**Example:**
```python
cm = ChatManager("data")

# Create chat
chat = cm.create_chat(project_id, "Revenue Analysis")

# Add user message
cm.add_user_message(project_id, chat.id, "What's the average revenue?")

# Add assistant response
cm.add_assistant_message(
    project_id,
    chat.id,
    content="The average revenue is $45,234",
    code="df['revenue'].mean()",
    output_type="metric",
    result=45234.0
)

# Get all messages
messages = cm.get_messages(project_id, chat.id)

# Search
results = cm.search_messages(project_id, chat.id, "revenue")
```

### 7. AI Agent (`src/ai_agent.py`)

**Purpose:** Integrate with Gemini for code generation

**Workflow:**
```
1. User asks: "Show me products with price > $100"
2. AIAgent.process_query()
   a. Detect output type (table)
   b. Build prompt with dataset context
   c. Send to Gemini
   d. Extract code from response
   e. Execute code safely
   f. Return results
3. Save message to chat history
```

**Key Features:**
- Auto-detect output type (table, plot, metric, text)
- Safe code execution (sandboxed environment)
- Gemini chat history (maintains conversation context)
- DataFrame always available as 'df' in code

**Example:**
```python
agent = AIAgent(api_key="...")

# Start session
agent.start_chat_session(
    project_id=project.id,
    chat_id=chat.id,
    dataframe=df,
    dataset_context=eda_context
)

# Process query
result = agent.process_query("Show top 10 products by revenue")
# Returns:
# {
#   "success": True,
#   "output_type": "table",
#   "code": "df.nlargest(10, 'revenue')[['product', 'revenue']]",
#   "output": "... table output ...",
#   "explanation": "Showing top 10 products sorted by revenue"
# }
```

---

## 🔄 Data Flow Examples

### Example 1: Creating a New Project

```
User uploads CSV → UI calls ProjectManager.create_project()
                    │
                    ├─→ Create Project object
                    │   └─→ Generate UUID, timestamps
                    │
                    ├─→ VersionManager.create_initial_version()
                    │   ├─→ Save to versions/v1_timestamp.csv
                    │   ├─→ Save to current.csv
                    │   └─→ Create version_log.json
                    │
                    ├─→ ChatManager.create_chat()
                    │   └─→ Create default "Chat 1"
                    │
                    ├─→ Run EDA (AutoEDA)
                    │   └─→ Cache to eda_context.json
                    │
                    └─→ StateManager.save_project_metadata()
                        └─→ Save metadata.json

Result: Project ready with v1 CSV, default chat, cached EDA
```

### Example 2: User Asks Question

```
User: "What's the average price?"
  │
  ├─→ ChatManager.add_user_message() → Save to chat JSON
  │
  ├─→ AIAgent.process_query()
  │   ├─→ Detect output type: "metric"
  │   ├─→ Build prompt with dataset context
  │   ├─→ Send to Gemini
  │   ├─→ Extract code: "df['price'].mean()"
  │   ├─→ Execute code
  │   └─→ Return: {"result": 45.23, "code": "...", "output": "45.23"}
  │
  ├─→ ChatManager.add_assistant_message() → Save response
  │
  └─→ UI displays result

Result: Question answered, full conversation saved
```

### Example 3: DataFrame Modified

```
User: "Add a profit margin column"
  │
  ├─→ AIAgent executes: df['profit_margin'] = ...
  │
  ├─→ VersionManager.detect_modification()
  │   └─→ Compare current.csv with new DataFrame
  │   └─→ Changes detected!
  │
  ├─→ VersionManager.create_new_version()
  │   ├─→ Auto-describe: "Added profit_margin column"
  │   ├─→ Save to versions/v2_timestamp.csv
  │   ├─→ Update current.csv
  │   └─→ Update version_log.json
  │
  ├─→ ProjectManager.refresh_project_stats()
  │   └─→ Update rows/cols/size in metadata
  │
  └─→ StateManager.delete_eda_context()
      └─→ Force EDA re-run (data changed)

Result: New version created, project stats updated
```

---

## 🎯 Key Design Patterns

### 1. Factory Methods
```python
# Instead of:
project = Project(id=uuid4(), created_at=datetime.now(), ...)  # Error-prone

# Use:
project = Project.create_new(name="Sales", filename="data.csv", ...)  # Safe
```

### 2. Manager Pattern
```python
# Each manager owns a domain:
ProjectManager   → Projects
ChatManager      → Chats & Messages
VersionManager   → CSV Versions
StateManager     → Disk I/O
AIAgent          → Gemini Integration
```

### 3. Separation of Concerns
```python
# ProjectManager doesn't know about file I/O
# StateManager doesn't know about business logic
# Each layer has one job
```

### 4. Atomic Operations
```python
# All writes are atomic (temp file → rename)
# Either fully succeeds or fully fails
# No partial corruption
```

---

## 💾 File Structure on Disk

### Real Example

```
data/
├── config.json
│   {
│     "version": "2.0.0",
│     "last_active_project_id": "abc-123",
│     "judge_settings": {...}
│   }
│
├── projects/
│   ├── abc-123/  ← Project UUID
│   │   ├── metadata.json
│   │   │   {
│   │   │     "id": "abc-123",
│   │   │     "name": "Sales Analysis Q4 2025",
│   │   │     "current_version": 2,
│   │   │     "total_rows": 15000,
│   │   │     "chat_ids": ["chat-1", "chat-2"]
│   │   │   }
│   │   │
│   │   ├── current.csv  ← Active CSV (version 2)
│   │   │
│   │   ├── eda_context.json  ← Cached EDA
│   │   │   {
│   │   │     "rows": 15000,
│   │   │     "columns": 25,
│   │   │     "column_details": {...}
│   │   │   }
│   │   │
│   │   ├── chats/
│   │   │   ├── chat-1.json
│   │   │   │   {
│   │   │   │     "id": "chat-1",
│   │   │   │     "name": "Revenue Analysis",
│   │   │   │     "message_count": 12,
│   │   │   │     "messages": [
│   │   │   │       {"role": "user", "content": "Show revenue"},
│   │   │   │       {"role": "assistant", "code": "df.head()", ...}
│   │   │   │     ]
│   │   │   │   }
│   │   │   └── chat-2.json
│   │   │
│   │   └── versions/
│   │       ├── v1_20260106_120000.csv  ← Original
│   │       ├── v2_20260106_130000.csv  ← After adding column
│   │       └── version_log.json
│   │           {
│   │             "versions": [
│   │               {"version_number": 1, "change_description": "Initial upload"},
│   │               {"version_number": 2, "change_description": "Added profit_margin"}
│   │             ]
│   │           }
│   │
│   └── xyz-789/  ← Another project
│       └── ...
│
└── plots/
    ├── plot-uuid-1.png
    └── plot-uuid-2.png
```

---

## 🧪 Testing Strategy

### Unit Tests (test_phase1.py)
- Test each model in isolation
- Test each manager independently
- Verify serialization/deserialization
- Test edge cases (missing files, corrupted data)

### Integration Tests (test_phase2.py)
- Test workflows across managers
- Test chat + messages + project
- Test search functionality
- Test statistics

### Why This Matters
```
✅ Confidence: 66 tests passing means core is solid
✅ Refactoring: Can change internals without breaking UI
✅ Debugging: If bug found, write test first, then fix
```

---

## 🔐 Security & Reliability

### 1. Safe Code Execution
```python
# Sandboxed environment (no file system access)
exec_globals = {
    'df': dataframe,  # Only DataFrame available
    'pd': pd,
    'plt': plt
    # NO: open, os, sys, subprocess, etc.
}
exec(code, exec_globals)
```

### 2. Atomic Writes
```python
# Never partially write files
# Either complete success or no change
```

### 3. Input Validation
```python
# Validate CSV before accepting
# Sanitize filenames (remove invalid chars)
# Check for empty DataFrames
```

### 4. Error Handling
```python
# All operations return success/failure
# Graceful degradation (corrupted JSON → recreate)
# User-friendly error messages
```

---

## 📊 Performance Optimizations

### 1. Lazy Loading
```python
# Don't load all projects on startup
# Load only when user navigates to project
```

### 2. EDA Caching
```python
# Run EDA once, save to eda_context.json
# Only re-run if CSV changes
# Saves ~5-10 seconds per project
```

### 3. Efficient Search
```python
# Search in memory (messages already loaded)
# Could add indexing for large histories (Phase 6)
```

---

## 🎓 Key Takeaways

### What Makes This Architecture Good?

1. **Separation of Concerns**
   - Each manager has ONE job
   - Easy to test, modify, extend

2. **Data Persistence**
   - Everything saved to disk
   - Survives crashes, restarts
   - No data loss

3. **Version Control**
   - Full history of CSV changes
   - Can always go back
   - Clear audit trail

4. **Flexibility**
   - Multiple projects, multiple chats
   - Independent conversations
   - Easy to add features

5. **Reliability**
   - Atomic operations
   - Comprehensive tests
   - Error handling

### What We'll Build in Phase 3 (UI)

```python
# Simple UI pseudocode:
sidebar:
    for project in project_manager.list_all_projects():
        if project.expanded:
            for chat in chat_manager.list_chats(project.id):
                if chat.is_active:
                    main_area:
                        show chat_manager.get_messages(...)
                        user_input → ai_agent.process_query(...)
```

---

**Next:** Run demo_backend.py to see it in action!
