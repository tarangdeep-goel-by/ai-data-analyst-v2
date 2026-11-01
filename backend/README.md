# AI Data Analyst v2.0

A multi-project AI-powered data analysis tool with conversational interface, built with Gemini API. This directory holds the FastAPI backend (`api/`, run with `python3 run_api.py`) used by the React app in `../frontend`, plus the older Streamlit UI described below. See the root `README.md` and `docs/NOTES.md` for the current, code-checked description.

## 🎯 Features

- **Multi-Project Support**: Manage multiple data analysis projects with full isolation
- **Multi-Chat Interface**: Multiple conversation threads per project
- **Version Manager**: Git-like versioning for CSV data with auto-change detection. Only the initial snapshot on upload is wired up; AI modifications do not create new versions, and revert is not exposed in any UI or API route
- **AI-Powered Analysis**: Natural language queries powered by Google Gemini
- **Three Query Types**:
  - **Exploratory**: Answer questions, calculate metrics
  - **Visualization**: Generate plots and charts
  - **Modification**: Transform data with downloadable results
- **Atomic JSON writes**: temp file, then rename (CSV writes are plain `to_csv`)

## 📦 Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd ai_data_analyst_v2

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

## 🚀 Quick Start

### Run the Streamlit UI

```bash
# Start the web application
streamlit run chat_analyst_ui.py

# The app will open at http://localhost:8501
```

### Run Backend Demo (CLI)

```bash
# Run interactive command-line demo
python3 demo_backend.py
```

### Run Tests

```bash
# Run Phase 1 tests (Core infrastructure)
python3 test_phase1.py

# Run Phase 2 tests (AI agent integration)
python3 test_phase2.py
```

## 📚 Documentation

- `IMPLEMENTATION_PLAN_V2.md` - Complete implementation roadmap
- `REBUILD_ARCHITECTURE.md` - Detailed architecture guide
- `ARCHITECTURE_REVIEW.md` - Architecture review and best practices

## 🏗️ Project Structure

```
ai_data_analyst_v2/
├── src/
│   ├── models.py              # Data models (Project, Chat, Message, Version)
│   ├── state_manager.py       # File I/O and persistence
│   ├── project_manager.py     # Project operations
│   ├── chat_manager.py        # Chat operations
│   ├── version_manager.py     # Version control for data
│   ├── ai_agent.py            # Gemini session, prompt, exec()
│   ├── eda_utils.py           # Dataset profile sent to the model
│   └── utils.py               # Atomic writes and utilities
├── api/                       # FastAPI app and routers
├── run_api.py                 # Starts the API on 0.0.0.0:8000
├── test_phase1.py             # Phase 1 comprehensive tests
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## ✅ Development Phases

- [x] **Phase 1**: Core Infrastructure (Complete)
  - Multi-project architecture
  - Data models and managers
  - Version control system
  - Comprehensive testing
- [x] **Phase 2**: AI Agent Integration (Complete)
  - Gemini API integration with JSON responses
  - Code generation and execution (plain `exec()` in the backend process, not sandboxed)
  - Three query types (exploratory, visualization, modification)
  - Markdown stripping and robust JSON parsing
  - Chat history persistence (Gemini history is saved per chat but not restored when a session restarts)
- [x] **Phase 3**: Streamlit UI (Complete)
  - Modern Claude-inspired interface with glass effects
  - Three-level navigation (App → Project → Chat)
  - Sidebar with projects list
  - Project Home with chats grid
  - Chat interface with AI agent integration
  - Data context popup modal
  - Output-specific UIs:
    - Exploratory: Explanation + Code + Text Output
    - Visualization: Chart + Download PNG
    - Modification: Stats + Preview Table + Download CSV
  - Custom CSS with animations and hover effects
- [ ] **Phase 4**: Advanced Features
  - Dark mode toggle
  - Export capabilities
  - Sharing and collaboration
  - Analytics dashboard

## 🧪 Testing

**Phase 1 Tests** - Core infrastructure:
- All data models
- StateManager operations
- VersionManager version control
- ProjectManager multi-project support
- ChatManager multi-chat support
- Integrated workflows

**Phase 2 Tests** - AI Agent integration:
- Gemini API integration
- JSON response parsing
- Exploratory queries
- Visualization generation
- Data modification with downloads
- Chat history persistence

Run tests:
```bash
python3 test_phase1.py   # Core infrastructure tests
python3 test_phase2.py   # AI agent tests (requires GEMINI_API_KEY exported in the shell; it does not read .env)
```

## 🔒 Data Safety

- Atomic JSON writes (temp + rename pattern)
- Initial CSV snapshot kept in `versions/` on upload
- Safe file operations with error handling
- Data directory excluded from Git

## 📝 License

MIT License

## 🤝 Contributing

This project is being built incrementally with full test coverage at each phase.

---

Built with ❤️ using Claude Code
