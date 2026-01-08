# Phase 3: Streamlit UI Design Specification

## Design Philosophy

Inspired by Claude AI's 2025 interface and modern data analysis tools (ChatGPT Advanced Data Analysis, Julius AI), with emphasis on:
- Clean, conversational interface
- Clear separation of projects and chats
- Context-aware data interactions
- Output-specific UI experiences
- Modern SaaS aesthetics

---

## UI Architecture

### Three-Level Navigation Hierarchy

```
App Level → Project Level → Chat Level
   ↓            ↓              ↓
Sidebar      Home Page      Chat Interface
(Projects)   (Chats List)   (Conversation)
```

---

## 1. App-Level Layout

### Sidebar (Left - Always Visible)
**Purpose**: Project management and navigation

**Components**:
- **Header**
  - App logo/title: "AI Data Analyst"
  - "+ New Project" button (primary CTA)

- **Projects List**
  - Card-based project items:
    ```
    📊 [Project Name]
    [Dataset filename] • [X rows]
    Last active: [timestamp]
    ```
  - Active project highlighted
  - Hover effects with subtle shadow
  - Click to switch projects

- **Footer**
  - Settings icon
  - Dark/Light mode toggle
  - Help/Documentation link

**Design Notes**:
- Width: 280px
- Glass effect with backdrop-blur
- Scroll if many projects
- Minimalist, Claude-style aesthetics

### Main Content Area (Right)
Dynamically shows:
- Project Home Page (when project selected, no chat active)
- Chat Interface (when chat active)

---

## 2. Project Home Page

**Triggered**: When user clicks a project in sidebar

**Layout**:

### Header Section
```
┌─────────────────────────────────────────────────────┐
│ 📊 [Project Name]                    [View Data ↗️] │
│ [Dataset filename] • [X rows, Y columns]            │
└─────────────────────────────────────────────────────┘
```

**"View Data" Button**: Opens data context popup (see section 4)

### Chats Section

**New Chat Card** (Always first):
```
┌────────────────────────────────┐
│ ➕ Start New Chat               │
│ Begin analyzing your data       │
└────────────────────────────────┘
```

**Existing Chats** (Grid layout, 2-3 columns):
```
┌────────────────────────────────┐
│ 💬 Chat 1                       │
│ "What is the average salary?"   │
│ 5 messages • 2 hours ago        │
└────────────────────────────────┘
```

Each chat card shows:
- Chat name (auto-generated from first query)
- Preview of first query
- Message count
- Last activity timestamp
- Hover: subtle shadow + "Continue" overlay

**Design Notes**:
- Card-based layout with 16px spacing
- Subtle shadows and hover effects
- Empty state: "No chats yet. Start your first analysis!"

---

## 3. Chat Interface

**Triggered**: When user starts new chat or clicks existing chat

### Layout Structure

```
┌────────────────────────────────────────────────────────┐
│ Header: [← Back to Project] [Project Name] [View Data ↗️]│
├────────────────────────────────────────────────────────┤
│                                                         │
│  Message Thread (Scrollable)                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 👤 User: "How many employees are there?"       │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🤖 Assistant:                                   │   │
│  │ [Response varies by output_type - see below]    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
├────────────────────────────────────────────────────────┤
│ Input Area:                                            │
│ [Text input: "Ask a question about your data..."]      │
│ [Send Button]                                          │
└────────────────────────────────────────────────────────┘
```

### Output Type-Specific UI

#### A. Exploratory Query Response
```
┌─────────────────────────────────────────────────────┐
│ 🤖 Assistant                                         │
│                                                      │
│ 📝 Explanation:                                      │
│ This code counts the number of rows in the          │
│ DataFrame, which corresponds to the number of       │
│ employees.                                           │
│                                                      │
│ 💻 Code: [View Code ▼]                              │
│ ┌───────────────────────────────┐                   │
│ │ print(len(df))                │ [Copy Code]       │
│ └───────────────────────────────┘                   │
│                                                      │
│ 📊 Output:                                           │
│ 8                                                    │
└─────────────────────────────────────────────────────┘
```

**Features**:
- Collapsible code section (default: collapsed)
- Copy code button
- Clean text output
- Syntax highlighting for code

#### B. Visualization Response
```
┌─────────────────────────────────────────────────────┐
│ 🤖 Assistant                                         │
│                                                      │
│ 📝 Explanation:                                      │
│ This chart shows the average salary by department.  │
│                                                      │
│ 💻 Code: [View Code ▼]                              │
│                                                      │
│ 🎨 Visualization:                                    │
│ ┌───────────────────────────────┐                   │
│ │                                │                   │
│ │     [Chart Image Display]      │                   │
│ │                                │                   │
│ └───────────────────────────────┘                   │
│ [📥 Download PNG]                                    │
└─────────────────────────────────────────────────────┘
```

**Features**:
- Image displayed inline
- Download button with icon
- "View Code" to see matplotlib code
- Responsive image sizing

#### C. Modification Response
```
┌─────────────────────────────────────────────────────┐
│ 🤖 Assistant                                         │
│                                                      │
│ 📝 Explanation:                                      │
│ Filtered data to include only employees from NYC.   │
│                                                      │
│ 💻 Code: [View Code ▼]                              │
│                                                      │
│ 💾 Modified Data:                                    │
│ Rows: 8 → 3                                          │
│ Columns: 5 → 5                                       │
│ [📥 Download CSV]                                    │
│                                                      │
│ Preview (first 5 rows):                              │
│ ┌───────────────────────────────┐                   │
│ │ name    | age | city | salary │                   │
│ │ Alice   | 25  | NYC  | 50000  │                   │
│ │ Charlie | 35  | NYC  | 75000  │                   │
│ │ ...                            │                   │
│ └───────────────────────────────┘                   │
└─────────────────────────────────────────────────────┘
```

**Features**:
- Summary stats (rows/columns before → after)
- Download CSV button
- Data preview table (first 5 rows)
- "View Code" to see transformation logic

---

## 4. Data Context Popup

**Triggered**: Clicking "View Data" button (in header)

**Modal Design**:
```
┌─────────────────────────────────────────────────────┐
│ Dataset Context                          [✕ Close]  │
├─────────────────────────────────────────────────────┤
│                                                      │
│ 📊 Dataset Overview                                  │
│ File: sample_data.csv                              │
│ Size: 58,245 rows × 17 columns                      │
│                                                      │
│ 📋 Columns:                                          │
│ ┌─────────────────────────────────────┐             │
│ │ Column Name           Type    Nulls │             │
│ │ user_id              object   0%    │             │
│ │ created_at           object   0%    │             │
│ │ journey_name         object   5%    │             │
│ │ marital_status       object   89%   │             │
│ │ ...                                 │             │
│ └─────────────────────────────────────┘             │
│                                                      │
│ 📈 Sample Data (first 5 rows):                       │
│ [Interactive table - sortable, scrollable]          │
│                                                      │
│ 📝 Statistics:                                       │
│ - Numeric columns: 2                                │
│ - Categorical columns: 15                           │
│ - Missing values: 45%                               │
│                                                      │
│ [📥 Download Full Dataset]                           │
└─────────────────────────────────────────────────────┘
```

**Features**:
- Semi-transparent backdrop (blur background)
- Scrollable content
- Interactive data preview
- Column statistics
- Download original dataset option

---

## 5. Color Scheme & Design Tokens

### Light Mode
```
Background:       #FFFFFF
Surface:          #F7F7F8
Sidebar:          rgba(255, 255, 255, 0.8) with backdrop-blur
Text Primary:     #1A1A1A
Text Secondary:   #6B6B6B
Accent (Primary): #2563EB (Blue)
Success:          #10B981 (Green)
Border:           #E5E5E5
Shadow:           0 1px 3px rgba(0,0,0,0.1)
```

### Dark Mode
```
Background:       #1A1A1A
Surface:          #2D2D2D
Sidebar:          rgba(45, 45, 45, 0.8) with backdrop-blur
Text Primary:     #FFFFFF
Text Secondary:   #A3A3A3
Accent (Primary): #3B82F6 (Blue)
Success:          #10B981 (Green)
Border:           #404040
Shadow:           0 1px 3px rgba(0,0,0,0.3)
```

### Typography
```
Font Family:   'Inter', -apple-system, sans-serif
Headings:      600 weight, 1.5rem - 2rem
Body:          400 weight, 1rem
Code:          'Fira Code', monospace
Line Height:   1.6
```

---

## 6. Interaction Patterns

### Animations
- **Page Transitions**: 200ms ease-out
- **Hover Effects**: Scale(1.02) + shadow increase (150ms)
- **Loading States**: Skeleton screens + spinner for AI responses
- **Message Appearance**: Fade-in from bottom (300ms)

### Responsive Behavior
- **Desktop (>1024px)**: Full sidebar + main content
- **Tablet (768-1024px)**: Collapsible sidebar
- **Mobile (<768px)**: Bottom navigation + full-width content

### Loading States
- **AI Processing**:
  ```
  🤖 Assistant is thinking...
  [Animated dots or spinner]
  ```
- **Data Upload**: Progress bar with percentage
- **Code Execution**: "Running code..." with code snippet preview

---

## 7. Technical Implementation Notes

### Streamlit Components Required
- `st.sidebar` - Project navigation
- `st.columns` - Layout grids
- `st.container` - Message grouping
- `st.expander` - Collapsible code sections
- `st.download_button` - CSV/PNG downloads
- `st.modal` / `st.dialog` - Data context popup
- `st.chat_message` - Message formatting
- Custom CSS injection for glass effects

### Session State Management
```python
st.session_state = {
    'active_project_id': str,
    'active_chat_id': str,
    'show_data_modal': bool,
    'theme': 'light' | 'dark',
    'messages': List[dict]
}
```

### Custom CSS Additions
- Glass sidebar effect
- Hover animations
- Card shadows
- Code syntax highlighting
- Responsive breakpoints

---

## 8. User Flows

### Flow 1: New User First Visit
1. See empty sidebar with "+ New Project" button
2. Click "+ New Project"
3. Upload CSV dialog appears
4. Enter project name
5. Project created → Navigate to Project Home
6. Click "Start New Chat"
7. Begin asking questions

### Flow 2: Returning User
1. See sidebar with existing projects
2. Click on project → Navigate to Project Home
3. See existing chats + "Start New Chat"
4. Click existing chat → Continue conversation
5. OR click "View Data" to see dataset context

### Flow 3: Analyzing Data
1. In chat interface, type query
2. Press Send
3. See "Assistant is thinking..." loader
4. Response appears with appropriate UI:
   - Exploratory: Explanation + Code + Output
   - Visualization: Explanation + Chart + Download
   - Modification: Explanation + Stats + Preview + Download
5. Can "View Code" to see Python
6. Can download outputs if applicable

---

## 9. Accessibility Considerations

- **Keyboard Navigation**: Tab through all interactive elements
- **Screen Reader Support**: ARIA labels on all buttons/inputs
- **High Contrast Mode**: Ensure 4.5:1 contrast ratio
- **Focus Indicators**: Visible focus states on all clickable items
- **Alt Text**: All visualizations have descriptive alt text

---

## 10. Phase 3 Implementation Plan

### Stage 1: Core Layout (Week 1)
- [ ] Sidebar with projects list
- [ ] Project Home page
- [ ] Basic chat interface
- [ ] Navigation between views

### Stage 2: Chat Functionality (Week 1)
- [ ] Message display (user/assistant)
- [ ] Input area with send button
- [ ] Integration with AIAgent
- [ ] Loading states

### Stage 3: Output Types (Week 2)
- [ ] Exploratory query UI
- [ ] Visualization display + download
- [ ] Modification display + download + preview
- [ ] Code reveal/collapse

### Stage 4: Polish & Features (Week 2)
- [ ] Data context popup
- [ ] Custom CSS styling
- [ ] Dark mode
- [ ] Animations
- [ ] Responsive design

---

## Design Inspiration Sources

- **Claude AI**: Sidebar projects, clean chat interface, artifacts panel
- **ChatGPT Advanced Data Analysis**: Code execution UI, "View Analysis" pattern
- **Julius AI**: Automated visualizations, conversational analytics
- **2025 UI Trends**: Glass effects, card layouts, minimalist components

---

**Next Step**: Begin implementation with Stage 1 (Core Layout)
