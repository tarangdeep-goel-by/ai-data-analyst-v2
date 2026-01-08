# AI Data Analyst v2.0 - Multi-File Architecture Implementation Plan

**Status:** Planning Complete - Ready for Implementation
**Date:** January 6, 2026
**Estimated Duration:** 3-4 weeks

---

## Executive Summary

Transform the current single-file, session-based AI Data Analyst into a robust multi-file system supporting:
- Multiple CSV projects
- Multiple chat sessions per project
- Full persistence to disk (survives app restarts)
- CSV version control with revert capability
- Project-based navigation UI (like ChatGPT/Claude)
- CSV modification & download
- Optional judge agent for code validation

---

## User Requirements & Decisions

### Key Requirements
1. **Multi-file support** - Users can upload and manage multiple CSVs
2. **Multi-chat per file** - Each CSV (project) has multiple independent chats
3. **State persistence** - Files, chats, metadata persist to disk
4. **Version control** - Track all CSV modifications, allow reversion
5. **File/chat navigation** - Sidebar UI with projects list
6. **File management** - Delete files (removes chats/versions)
7. **CSV modification & download** - Agent modifies CSV, user downloads
8. **Judge agent (P2)** - Secondary agent validates code quality

### Architectural Decisions Made
- **Persistence:** Save to disk (files, chats, metadata survive restart)
- **File versions:** Full version history with revert capability
- **UI layout:** Sidebar with projects list (ChatGPT/Claude style)
- **Judge agent:** Configurable threshold (not every query, only when needed)

---

## Current State (v1.0)

### What Works
- ✅ Single CSV upload and analysis
- ✅ Natural language chat interface
- ✅ Smart output types (table/plot/metric)
- ✅ AI queries full DataFrame (not just sample)
- ✅ Code generation and execution
- ✅ Gemini AI integration
- ✅ Clean UI with compact sidebar

### Current Limitations
- ❌ Only one file at a time
- ❌ Only one chat conversation per file
- ❌ No persistence (data lost on refresh)
- ❌ No version control for modifications
- ❌ No file management
- ❌ No code validation/review

### Current Architecture
```
chat_analyst_ui.py (main app)
├── Session state storage (volatile)
├── Single DataFrame
├── Single chat history
├── Gemini chat session
└── auto_eda.py (EDA utilities)
```

---

## New Architecture (v2.0)

### Directory Structure
```
ai_data_analyst/
├── chat_analyst_ui.py              # Main app (refactored)
├── auto_eda.py                     # EDA utilities (minor updates)
├── requirements.txt                # Updated
├── .env.example
├── start_ui.sh
├── README.md                       # Updated documentation
│
├── src/                            # NEW: Modular source code
│   ├── __init__.py
│   ├── models.py                   # Data models (Project, Chat, Message, Version)
│   ├── state_manager.py            # Persistence & disk I/O
│   ├── project_manager.py          # Project CRUD operations
│   ├── chat_manager.py             # Chat CRUD operations
│   ├── version_manager.py          # CSV version control
│   ├── ai_agent.py                 # Refactored AI logic
│   ├── judge_agent.py              # P2: Code validation agent
│   ├── ui_components.py            # Reusable UI components
│   └── utils.py                    # Helper functions
│
└── data/                           # NEW: Persistent storage
    ├── projects/
    │   ├── {project-uuid-1}/
    │   │   ├── metadata.json       # Project info
    │   │   ├── current.csv         # Current CSV version
    │   │   ├── eda_context.json    # Cached EDA analysis
    │   │   ├── chats/
    │   │   │   ├── {chat-uuid-1}.json
    │   │   │   └── {chat-uuid-2}.json
    │   │   └── versions/
    │   │       ├── v1_{timestamp}.csv
    │   │       ├── v2_{timestamp}.csv
    │   │       └── version_log.json
    │   └── {project-uuid-2}/
    │       └── ...
    ├── plots/
    │   └── {plot-uuid}.png
    └── config.json                 # Global app config
```

### Data Models

#### Project
```python
@dataclass
class Project:
    id: str                     # UUID
    name: str                   # User-friendly name
    original_filename: str      # Original CSV name
    created_at: datetime
    updated_at: datetime
    current_version: int        # Current version number
    total_rows: int
    total_columns: int
    file_size_mb: float
    active_chat_id: str | None
```

#### Chat
```python
@dataclass
class Chat:
    id: str                     # UUID
    project_id: str             # Parent project
    name: str                   # Chat name
    created_at: datetime
    updated_at: datetime
    message_count: int
    gemini_chat_history: list   # For Gemini session
```

#### Message
```python
@dataclass
class Message:
    id: str
    chat_id: str
    role: str                   # "user" | "assistant"
    content: str
    timestamp: datetime

    # Assistant-specific
    code: str | None
    output_type: str | None     # "table" | "plot" | "metric" | "text"
    output: str | None
    result: Any | None
    plot_path: str | None
    explanation: str | None
    thinking: str | None

    # Judge validation (P2)
    judge_score: float | None
    judge_feedback: str | None
```

#### Version
```python
@dataclass
class Version:
    version_number: int
    project_id: str
    created_at: datetime
    created_by_chat_id: str
    created_by_message_id: str
    file_path: str
    file_size_mb: float
    change_description: str
    row_count: int
    column_count: int
```

### JSON File Schemas

#### config.json (Global)
```json
{
  "version": "2.0.0",
  "last_active_project_id": "uuid",
  "judge_settings": {
    "enabled": true,
    "threshold_trigger": "user_request",
    "quality_threshold": 70
  }
}
```

#### metadata.json (Per Project)
```json
{
  "id": "project-uuid",
  "name": "Sales Analysis Q4 2025",
  "original_filename": "sales_data.csv",
  "created_at": "2026-01-06T12:00:00Z",
  "updated_at": "2026-01-06T15:30:00Z",
  "current_version": 3,
  "total_rows": 15000,
  "total_columns": 25,
  "file_size_mb": 2.3,
  "active_chat_id": "chat-uuid-1",
  "chat_ids": ["chat-uuid-1", "chat-uuid-2"]
}
```

#### {chat-uuid}.json (Per Chat)
```json
{
  "id": "chat-uuid-1",
  "project_id": "project-uuid-1",
  "name": "Revenue Analysis",
  "created_at": "2026-01-06T12:00:00Z",
  "updated_at": "2026-01-06T15:30:00Z",
  "message_count": 12,
  "gemini_chat_history": [],
  "messages": [...]
}
```

#### version_log.json (Per Project)
```json
{
  "project_id": "project-uuid-1",
  "versions": [
    {
      "version_number": 1,
      "created_at": "2026-01-06T12:00:00Z",
      "created_by_chat_id": null,
      "created_by_message_id": null,
      "file_path": "versions/v1_20260106_120000.csv",
      "file_size_mb": 2.3,
      "change_description": "Initial upload",
      "row_count": 15000,
      "column_count": 25
    }
  ]
}
```

---

## UI Design

### Sidebar Layout
```
┌─────────────────────────────────┐
│ 📊 PROJECTS                     │
├─────────────────────────────────┤
│ [+ New Project]                 │
│                                 │
│ ▼ Sales Analysis Q4 2025        │ ← Active/Expanded
│   📈 Revenue Analysis           │ ← Active chat (bold)
│   📊 Customer Segmentation      │
│   [+ New Chat]                  │
│                                 │
│ ▶ Marketing Campaign Data       │ ← Collapsed
│ ▶ Product Inventory             │
│                                 │
└─────────────────────────────────┘
```

### Main Area
```
┌────────────────────────────────────────────────────────────┐
│ 💬 Revenue Analysis                   [Rename] [Delete]    │
├────────────────────────────────────────────────────────────┤
│ 📊 15,000 rows  │  📋 25 cols  │  💾 2.3 MB  │  🔄 v3      │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  👤 What's the average revenue?                           │
│                                                            │
│  🤖 Calculating average revenue...                        │
│      📊 Result: $45,234.56                                │
│      [View Code ▼]                                        │
│      Explanation: Calculates mean of revenue column       │
│      ✅ Judge Score: 95/100 - Code is correct             │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  💬 Ask a question...                            [Send]   │
└────────────────────────────────────────────────────────────┘
```

### Version History Modal
```
┌────────────────────────────────────────────────────────────┐
│ 📚 VERSION HISTORY                                   [✕]  │
├────────────────────────────────────────────────────────────┤
│  ● v3 - Current                       Jan 6, 2026 3:00 PM │
│    Added profit_margin column                             │
│    15,000 rows × 26 cols                                  │
│    [Download]                                             │
│                                                            │
│  ○ v2                                 Jan 6, 2026 1:00 PM │
│    Added calculated columns                               │
│    15,000 rows × 26 cols                                  │
│    [Download] [Revert to This]                            │
│                                                            │
│  ○ v1 - Original                      Jan 6, 2026 12:00 PM│
│    Initial upload                                         │
│    15,000 rows × 25 cols                                  │
│    [Download] [Revert to This]                            │
└────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1) - Priority P0

**Goal:** Set up data models, persistence layer, basic state management

**Tasks:**
1. Create `src/` directory structure
2. Implement `src/models.py` with all dataclasses
3. Implement `src/state_manager.py` for file I/O
4. Implement `src/project_manager.py` for project CRUD
5. Implement `src/version_manager.py` for version control
6. Create `src/utils.py` with helper functions

**Deliverables:**
- All model classes with serialization
- ProjectManager can create/read/update/delete projects
- VersionManager can create versions and revert
- StateManager can save/load from disk
- Data directory structure created

**Files to Create:**
- `src/__init__.py`
- `src/models.py`
- `src/state_manager.py`
- `src/project_manager.py`
- `src/version_manager.py`
- `src/utils.py`

---

### Phase 2: Multi-Chat Support (Week 1-2) - Priority P0

**Goal:** Enable multiple chat sessions per project

**Tasks:**
1. Implement `src/chat_manager.py` for chat CRUD
2. Update Message model for full chat history
3. Modify AI agent to work with chat-specific context
4. Implement chat switching logic
5. Update state management for chat persistence

**Deliverables:**
- ChatManager can create/read/update/delete chats
- Messages properly associated with chats
- Chat switching maintains state correctly
- Gemini chat history managed per chat

**Files to Create:**
- `src/chat_manager.py`

---

### Phase 3: UI Refactoring (Week 2) - Priority P0

**Goal:** Redesign UI for multi-file/multi-chat navigation

**Tasks:**
1. Create `src/ui_components.py` with reusable components
2. Implement sidebar project tree navigation
3. Implement chat view component
4. Implement version history modal
5. Implement new project dialog
6. Refactor `chat_analyst_ui.py` to use new architecture

**Deliverables:**
- Functional sidebar with project/chat tree
- Main area shows active chat
- Version history accessible
- Can create new projects/chats from UI
- All actions persist to disk

**Files to Create:**
- `src/ui_components.py`

**Files to Modify:**
- `chat_analyst_ui.py` (major refactoring)

---

### Phase 4: CSV Modification & Download (Week 2-3) - Priority P0

**Goal:** Enable CSV modifications and version downloads

**Tasks:**
1. Implement DataFrame modification detection
2. Auto-create versions when DataFrame changes
3. Add download buttons for current & historical versions
4. Implement version revert functionality
5. Update EDA context when reverting versions

**Deliverables:**
- Modifications automatically versioned
- Download any version as CSV
- Revert to previous version
- EDA re-runs on version change
- Version metadata tracked properly

**Files to Modify:**
- `src/ai_agent.py`
- `src/version_manager.py`
- `src/ui_components.py`

---

### Phase 5: Judge Agent (Week 3) - Priority P2 (Optional)

**Goal:** Add secondary validation agent

**Tasks:**
1. Implement `src/judge_agent.py`
2. Create judge prompt for code evaluation
3. Add configurable threshold settings
4. Integrate judge into message flow
5. Display judge feedback in UI

**Deliverables:**
- Judge agent evaluates code quality
- Configurable trigger threshold
- Judge feedback shown in chat
- Scores stored in message metadata

**Files to Create:**
- `src/judge_agent.py`

**Files to Modify:**
- `src/ai_agent.py`
- `src/ui_components.py`
- `data/config.json` (add judge settings)

---

### Phase 6: Polish & Testing (Week 4) - Priority P1

**Goal:** Finalize UX, fix bugs, optimize performance

**Tasks:**
1. Add loading states and progress indicators
2. Implement error handling and recovery
3. Add confirmation dialogs for destructive actions
4. Optimize large file handling
5. Write comprehensive tests
6. Update documentation
7. Create migration guide

**Deliverables:**
- Smooth UX with proper feedback
- Robust error handling
- Safe destructive operations
- Performance optimized
- Full documentation
- Migration guide from v1 to v2

**Files to Modify:**
- All src/ files (error handling)
- `README.md`
- Create `MIGRATION_GUIDE.md`

---

## Key Workflows

### 1. Create New Project
```
1. Click "+ New Project"
2. Upload CSV file
3. Enter project name (default: filename)
4. System creates:
   - Project directory with UUID
   - metadata.json
   - v1_{timestamp}.csv (initial version)
   - current.csv (copy)
   - eda_context.json
   - Default first chat
5. Project appears in sidebar (expanded)
6. Default chat selected and ready
```

### 2. Switch Chat
```
1. Click different chat in sidebar
2. System:
   - Saves current chat state (if modified)
   - Loads target chat's messages
   - Loads Gemini chat history
   - Re-initializes Gemini session
3. UI updates with new chat messages
4. Chat input enabled
```

### 3. CSV Modification & Versioning
```
1. User asks: "Add a profit_margin column"
2. AI generates code: df['profit_margin'] = (revenue - cost) / revenue
3. Code executes, modifies DataFrame
4. System detects modification:
   - Compare DataFrame with current version
   - Create new version entry
   - Save as v{N}_{timestamp}.csv
   - Update current.csv
   - Update metadata
5. UI shows: "✨ Created new version (v3)"
6. Download button available for v3
```

### 4. Revert to Previous Version
```
1. Click "View Version History"
2. Click "Revert to This" on older version
3. Confirm: "This will create new version with old data"
4. System:
   - Loads old version CSV
   - Creates new version (copy of old)
   - Updates current.csv
   - Re-runs EDA
   - Invalidates chat history (data changed)
5. UI shows: "🔄 Reverted to v1 (created as v4)"
```

### 5. Delete Project
```
1. Click delete icon on project
2. Confirm: "Delete project + all chats/versions?"
3. System:
   - Removes entire project directory
   - Updates config.json
4. UI:
   - Removes from sidebar
   - Switches to next project or welcome screen
```

---

## Technical Decisions

### State Management Strategy
- **Single source of truth:** File system (data/ directory)
- **Session state:** Only for UI state & active data (DataFrame, current chat)
- **Lazy loading:** Load projects on demand, not all at startup
- **Atomic writes:** Write to temp file, then rename (prevents corruption)

### Performance Optimizations
- Cache EDA context (don't regenerate unless CSV changes)
- Load only active project's DataFrame into memory
- Paginate version history (show last 10, load more on demand)
- Compress old plots, limit total storage

### Error Handling
- Graceful degradation for corrupted JSON
- Retry logic for API failures
- Timeout protection for code execution (30s)
- Validation for all user inputs

### Security
- Code execution sandboxed (no file system access)
- API keys in .env file (never logged)
- File paths validated (prevent directory traversal)
- No network access from executed code

---

## Files to Create (Summary)

### New Source Files (9 files)
1. `src/__init__.py`
2. `src/models.py` - Data models
3. `src/state_manager.py` - Persistence layer
4. `src/project_manager.py` - Project operations
5. `src/chat_manager.py` - Chat operations
6. `src/version_manager.py` - Version control
7. `src/ai_agent.py` - Refactored AI logic
8. `src/judge_agent.py` - Code validation (P2)
9. `src/ui_components.py` - UI components
10. `src/utils.py` - Helper functions

### Documentation Files
1. `MIGRATION_GUIDE.md` - v1 to v2 migration instructions
2. `CHANGELOG.md` - Version history

---

## Files to Modify

1. **chat_analyst_ui.py** - Major refactoring
   - Remove inline logic, use managers
   - Use UI components from ui_components.py
   - Handle project/chat switching
   - Initialize from disk on startup

2. **auto_eda.py** - Minor updates
   - Add method to return context as JSON
   - Add method to load cached context

3. **README.md** - Update documentation
   - Add v2.0 features
   - Update screenshots
   - Add usage examples

4. **requirements.txt** - No changes needed
   - All dependencies already present

---

## Migration from v1 to v2

### Breaking Changes
- Complete architectural rewrite
- Existing session state won't transfer
- Users must re-upload CSV files

### Migration Process
1. Create `data/` directory structure
2. Initialize config.json with defaults
3. Show welcome screen: "Welcome to v2.0"
4. Guide user to create first project

### Migration Script (Optional)
- Could create script to import from session state if file exists
- Low priority - most users will just re-upload

---

## Testing Strategy

### Unit Tests
- Test all data model serialization
- Test CRUD operations (projects, chats, versions)
- Test state persistence (save/load cycles)
- Test version control logic

### Integration Tests
- Test full workflows (create project → chat → modify → revert)
- Test persistence across app restarts
- Test multi-project/multi-chat scenarios

### Manual Testing
- UI flows (navigation, dialogs, confirmations)
- Error scenarios (disk full, corrupted data)
- Performance with large files (>100 MB)

---

## Timeline & Priorities

### Week 1: Foundation (Phases 1-2)
- **Days 1-3:** Core infrastructure (models, managers, persistence)
- **Days 4-5:** Multi-chat support

### Week 2: UI & Features (Phases 3-4)
- **Days 1-3:** UI refactoring (sidebar, chat view, dialogs)
- **Days 4-5:** CSV modification & versioning

### Week 3: Optional Features (Phase 5)
- **Days 1-3:** Judge agent (P2 - can be skipped if time constrained)
- **Days 4-5:** Buffer for catch-up

### Week 4: Polish (Phase 6)
- **Days 1-2:** Error handling, edge cases
- **Days 3-4:** Testing & bug fixes
- **Day 5:** Documentation & release

**Total: 3-4 weeks**

---

## Success Criteria

### Must Have (P0)
- ✅ Multiple CSV projects supported
- ✅ Multiple chats per project
- ✅ Full persistence to disk
- ✅ Version control with revert
- ✅ Project/chat navigation UI
- ✅ CSV download (all versions)
- ✅ Delete projects/chats

### Should Have (P1)
- ✅ Smooth UX with loading states
- ✅ Error handling & recovery
- ✅ Confirmation dialogs
- ✅ Performance optimized
- ✅ Documentation updated

### Nice to Have (P2)
- ✅ Judge agent for validation
- ✅ Search across chats
- ✅ Export project as ZIP

---

## Risk Mitigation

### Technical Risks
1. **State corruption** - Mitigate: Atomic writes, validation, recovery
2. **Performance with large files** - Mitigate: Lazy loading, caching, warnings
3. **Gemini API issues** - Mitigate: Retry logic, error messages, offline mode

### UX Risks
1. **Complex navigation** - Mitigate: Intuitive UI, clear labels, help text
2. **Data loss fear** - Mitigate: Confirmation dialogs, version history, backups
3. **Learning curve** - Mitigate: Onboarding guide, tooltips, examples

---

## Next Steps

### Immediate Actions
1. ✅ Review and approve this plan
2. Create `src/` directory
3. Start Phase 1: Implement data models
4. Set up testing framework

### First Week Goals
- Complete Phases 1 & 2
- Have basic multi-file/multi-chat working
- Persistence functional

### Decision Points
- After Phase 4: Evaluate if judge agent (Phase 5) is needed
- After Phase 5: Decide on additional P2 features
- Week 3: Review progress, adjust timeline if needed

---

## Questions to Resolve

### Before Starting Implementation
- ✅ All architectural decisions confirmed by user
- ✅ UI mockups approved
- ✅ Priorities set (P0/P1/P2)

### During Implementation
- How to handle very large files (>1 GB)?
- Should we add undo/redo for non-CSV actions?
- Export/import project as ZIP for sharing?

---

## Appendix: Code Examples

### Example: Create Project
```python
# In project_manager.py
def create_project(self, name: str, csv_file) -> Project:
    project_id = generate_uuid()
    project_dir = f"data/projects/{project_id}"

    # Create directory structure
    ensure_directory(project_dir)
    ensure_directory(f"{project_dir}/chats")
    ensure_directory(f"{project_dir}/versions")

    # Save CSV
    df = pd.read_csv(csv_file)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    version_path = f"{project_dir}/versions/v1_{timestamp}.csv"
    current_path = f"{project_dir}/current.csv"
    df.to_csv(version_path, index=False)
    df.to_csv(current_path, index=False)

    # Create project
    project = Project(
        id=project_id,
        name=name,
        original_filename=csv_file.name,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        current_version=1,
        total_rows=len(df),
        total_columns=len(df.columns),
        file_size_mb=os.path.getsize(current_path) / 1024**2
    )

    # Save metadata
    self.state_manager.save_project_metadata(project)

    # Create default chat
    self.chat_manager.create_chat(project_id, "Chat 1")

    return project
```

### Example: Switch Chat
```python
# In chat_manager.py
def switch_chat(self, chat_id: str):
    # Save current chat if modified
    if st.session_state.get('current_chat_modified'):
        self.save_chat(st.session_state.current_chat)

    # Load new chat
    chat = self.get_chat(chat_id)
    messages = self.get_messages(chat_id)

    # Update session state
    st.session_state.current_chat = chat
    st.session_state.current_messages = messages

    # Re-initialize Gemini with history
    if chat.gemini_chat_history:
        self.ai_agent.restore_chat_history(chat.gemini_chat_history)
```

---

## Contact & Support

For questions during implementation:
- Review this document
- Check inline code comments
- Refer to original requirements
- Test incrementally

**End of Implementation Plan**
