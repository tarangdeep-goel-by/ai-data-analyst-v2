# Backend API Testing - Postman/Curl Commands

Base URL: `http://localhost:8000`

## 1. Health Check

**Check if backend is running and Gemini is configured**

```bash
curl -X GET "http://localhost:8000/health"
```

**Expected Response:**
```json
{
  "status": "healthy",
  "gemini_configured": true
}
```

---

## 2. List All Projects

**Get all existing projects**

```bash
curl -X GET "http://localhost:8000/api/projects/"
```

**Expected Response:**
```json
[
  {
    "id": "uuid-here",
    "name": "Sales Data",
    "original_filename": "sales.csv",
    "total_rows": 1000,
    "total_columns": 5,
    "created_at": "2026-01-08T08:00:00",
    "updated_at": "2026-01-08T08:00:00",
    "current_version": 1
  }
]
```

---

## 3. Upload CSV and Create Project

**Upload a CSV file to create a new project**

```bash
curl -X POST "http://localhost:8000/api/projects/upload" \
  -F "file=@/path/to/your/data.csv" \
  -F "project_name=My Data Analysis"
```

**Postman Instructions:**
- Method: POST
- URL: `http://localhost:8000/api/projects/upload`
- Body: form-data
  - Key: `file` (type: File) → Select your CSV file
  - Key: `project_name` (type: Text) → "My Data Analysis"

**Expected Response:**
```json
{
  "success": true,
  "message": "Project created successfully",
  "project_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## 4. Get Project Details

**Get details of a specific project**

```bash
curl -X GET "http://localhost:8000/api/projects/{project_id}"
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/projects/550e8400-e29b-41d4-a716-446655440000"
```

**Expected Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Data Analysis",
  "original_filename": "data.csv",
  "total_rows": 1000,
  "total_columns": 10,
  "created_at": "2026-01-08T08:00:00",
  "updated_at": "2026-01-08T08:00:00",
  "current_version": 1
}
```

---

## 5. Get Project EDA Context

**Get exploratory data analysis context for a project**

```bash
curl -X GET "http://localhost:8000/api/projects/{project_id}/context"
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/projects/550e8400-e29b-41d4-a716-446655440000/context"
```

**Expected Response:**
```json
{
  "dataset_name": "data.csv",
  "total_rows": 1000,
  "total_columns": 10,
  "columns": [
    {
      "name": "age",
      "dtype": "int64",
      "non_null": 950,
      "unique": 80,
      "min": 18,
      "max": 90
    },
    {
      "name": "name",
      "dtype": "object",
      "non_null": 1000,
      "unique": 856,
      "values": [
        {"value": "John", "count": 15},
        {"value": "Jane", "count": 12}
      ]
    }
  ],
  "sample_data": [
    {"age": 25, "name": "John", "salary": 50000},
    {"age": 30, "name": "Jane", "salary": 60000}
  ]
}
```

---

## 6. Create New Chat

**Create a new chat session for a project**

```bash
curl -X POST "http://localhost:8000/api/chats/{project_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Analysis"
  }'
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/chats/550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales Analysis Chat"
  }'
```

**Postman Instructions:**
- Method: POST
- URL: `http://localhost:8000/api/chats/{project_id}`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "name": "Sales Analysis Chat"
}
```

**Expected Response:**
```json
{
  "id": "chat-uuid-here",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Sales Analysis Chat",
  "created_at": "2026-01-08T08:00:00",
  "updated_at": "2026-01-08T08:00:00",
  "message_count": 0
}
```

---

## 7. List Chats for a Project

**Get all chats for a specific project**

```bash
curl -X GET "http://localhost:8000/api/chats/{project_id}"
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/chats/550e8400-e29b-41d4-a716-446655440000"
```

**Expected Response:**
```json
[
  {
    "id": "chat-uuid-1",
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Sales Analysis Chat",
    "created_at": "2026-01-08T08:00:00",
    "updated_at": "2026-01-08T08:05:00",
    "message_count": 5
  }
]
```

---

## 8. Get Chat Messages

**Get all messages from a specific chat**

```bash
curl -X GET "http://localhost:8000/api/chats/{project_id}/{chat_id}/messages"
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/chats/550e8400-e29b-41d4-a716-446655440000/chat-uuid-1/messages"
```

**Expected Response:**
```json
[
  {
    "id": "msg-uuid-1",
    "chat_id": "chat-uuid-1",
    "role": "user",
    "content": "Show me the first 5 rows",
    "timestamp": "2026-01-08T08:01:00",
    "code": null,
    "output": null,
    "output_type": null,
    "plot_path": null,
    "modification_summary": null
  },
  {
    "id": "msg-uuid-2",
    "chat_id": "chat-uuid-1",
    "role": "assistant",
    "content": "Here are the first 5 rows of your dataset:",
    "timestamp": "2026-01-08T08:01:05",
    "code": "result = df.head(5).to_string()",
    "output": "   age  name  salary\n0   25  John   50000\n...",
    "output_type": "exploratory",
    "plot_path": null,
    "modification_summary": null
  }
]
```

---

## 9. Send AI Query

**Send a natural language query to analyze data**

```bash
curl -X POST "http://localhost:8000/api/ai/{project_id}/{chat_id}/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me the first 10 rows of the dataset"
  }'
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/ai/550e8400-e29b-41d4-a716-446655440000/chat-uuid-1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me the first 10 rows of the dataset"
  }'
```

**More Query Examples:**

```bash
# Exploratory query
curl -X POST "http://localhost:8000/api/ai/{project_id}/{chat_id}/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the summary statistics for numeric columns?"
  }'

# Visualization query
curl -X POST "http://localhost:8000/api/ai/{project_id}/{chat_id}/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Create a bar chart showing the distribution of ages"
  }'

# Data modification query
curl -X POST "http://localhost:8000/api/ai/{project_id}/{chat_id}/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Remove all rows where age is null"
  }'
```

**Expected Response (Exploratory):**
```json
{
  "success": true,
  "message": "Query processed successfully",
  "output_type": "exploratory",
  "result": "   age  name  salary\n0   25  John   50000\n1   30  Jane   60000\n...",
  "code_executed": "result = df.head(10).to_string()",
  "plot_url": null,
  "modification_summary": null
}
```

**Expected Response (Visualization):**
```json
{
  "success": true,
  "message": "Query processed successfully",
  "output_type": "visualization",
  "result": "Created bar chart showing age distribution",
  "code_executed": "plt.figure(figsize=(10,6))\ndf['age'].value_counts().plot(kind='bar')\n...",
  "plot_url": "/static/plots/plot-uuid.png",
  "modification_summary": null
}
```

**Expected Response (Modification):**
```json
{
  "success": true,
  "message": "Query processed successfully",
  "output_type": "modification",
  "result": "Removed 50 rows with null age values",
  "code_executed": "df = df.dropna(subset=['age'])\nresult = f'Removed rows...'",
  "plot_url": null,
  "modification_summary": {
    "before_rows": 1000,
    "after_rows": 950,
    "before_columns": 10,
    "after_columns": 10,
    "preview": [
      {"age": 25, "name": "John"},
      {"age": 30, "name": "Jane"}
    ]
  }
}
```

---

## 10. Delete Chat

**Delete a specific chat and all its messages**

```bash
curl -X DELETE "http://localhost:8000/api/chats/{project_id}/{chat_id}"
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/chats/550e8400-e29b-41d4-a716-446655440000/chat-uuid-1"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Chat deleted successfully"
}
```

---

## 11. Delete Project

**Delete a project and all associated data**

```bash
curl -X DELETE "http://localhost:8000/api/projects/{project_id}"
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/projects/550e8400-e29b-41d4-a716-446655440000"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Project deleted successfully"
}
```

---

## 12. Clear AI Session

**Clear the AI conversation context for a chat**

```bash
curl -X DELETE "http://localhost:8000/api/ai/{project_id}/session"
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/ai/550e8400-e29b-41d4-a716-446655440000/session"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "AI session cleared"
}
```

---

## 13. Access Generated Plots

**View a generated visualization**

```bash
# In browser or curl
http://localhost:8000/static/plots/{plot_filename}
```

**Example:**
```bash
curl -o chart.png "http://localhost:8000/static/plots/abc123-plot.png"
```

---

## 14. Download Modified Dataset

**Download a modified CSV file**

```bash
curl -o modified_data.csv "http://localhost:8000/static/downloads/{filename}"
```

---

## Complete Testing Flow

Here's a complete workflow to test the entire system:

```bash
# 1. Check health
curl -X GET "http://localhost:8000/health"

# 2. Upload a CSV file (replace path with your CSV)
curl -X POST "http://localhost:8000/api/projects/upload" \
  -F "file=@/path/to/your/data.csv" \
  -F "project_name=Test Project"
# Save the project_id from response

# 3. Get project details
PROJECT_ID="your-project-id-here"
curl -X GET "http://localhost:8000/api/projects/$PROJECT_ID"

# 4. Get EDA context
curl -X GET "http://localhost:8000/api/projects/$PROJECT_ID/context"

# 5. Create a chat
curl -X POST "http://localhost:8000/api/chats/$PROJECT_ID" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Chat"}'
# Save the chat_id from response

# 6. Send a query
CHAT_ID="your-chat-id-here"
curl -X POST "http://localhost:8000/api/ai/$PROJECT_ID/$CHAT_ID/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me the first 5 rows"}'

# 7. Get messages
curl -X GET "http://localhost:8000/api/chats/$PROJECT_ID/$CHAT_ID/messages"

# 8. Clean up - delete chat
curl -X DELETE "http://localhost:8000/api/chats/$PROJECT_ID/$CHAT_ID"

# 9. Clean up - delete project
curl -X DELETE "http://localhost:8000/api/projects/$PROJECT_ID"
```

---

## Postman Collection Tips

### Setting Variables
1. Create environment variables in Postman:
   - `base_url` = `http://localhost:8000`
   - `project_id` = (set after creating project)
   - `chat_id` = (set after creating chat)

2. Use variables in requests:
   - URL: `{{base_url}}/api/projects/{{project_id}}`

### Extracting IDs from Responses
Add this to "Tests" tab in Postman:

```javascript
// After project upload
const response = pm.response.json();
pm.environment.set("project_id", response.project_id);

// After chat creation
const response = pm.response.json();
pm.environment.set("chat_id", response.id);
```

---

## Sample CSV for Testing

Create a file `test_data.csv`:

```csv
name,age,salary,department,years_experience
John Doe,28,65000,Engineering,3
Jane Smith,35,85000,Marketing,8
Bob Johnson,42,95000,Engineering,15
Alice Brown,29,70000,Sales,4
Charlie Wilson,31,75000,Marketing,6
```

Then upload it:
```bash
curl -X POST "http://localhost:8000/api/projects/upload" \
  -F "file=@test_data.csv" \
  -F "project_name=Employee Data"
```
