"""
AI Agent for AI Data Analyst v2.0
Handles Gemini integration, code generation, and execution
"""

import os
import io
import sys
import json
import uuid
import shutil
import traceback
from typing import Optional, Any
import pandas as pd
import matplotlib.pyplot as plt
import google.generativeai as genai

from .chat_manager import ChatManager
from .models import Message


class AIAgent:
    """
    AI agent that handles natural language queries and code generation
    Integrates with Gemini API and manages chat context
    """

    def __init__(
        self,
        api_key: str,
        base_dir: str = "data",
        model_name: str = "gemini-2.0-flash-exp"
    ):
        """
        Initialize AI agent

        Args:
            api_key: Google Gemini API key
            base_dir: Base directory for data storage
            model_name: Gemini model to use
        """
        self.base_dir = base_dir
        self.chat_manager = ChatManager(base_dir)
        self.model_name = model_name

        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

        # Active chat session
        self.active_chat_session = None
        self.current_project_id = None
        self.current_chat_id = None
        self.current_dataframe = None
        self.dataset_context = None

    # ===== Session Management =====

    def start_chat_session(
        self,
        project_id: str,
        chat_id: str,
        dataframe: pd.DataFrame,
        dataset_context: str,
        business_context: Optional[str] = None
    ) -> bool:
        """
        Start or resume a chat session

        Args:
            project_id: Project UUID
            chat_id: Chat UUID
            dataframe: Current DataFrame
            dataset_context: EDA context string
            business_context: Optional business context

        Returns:
            True if successful, False otherwise
        """
        try:
            self.current_project_id = project_id
            self.current_chat_id = chat_id
            self.current_dataframe = dataframe
            self.dataset_context = dataset_context

            # Build system instruction
            system_instruction = self._build_system_instruction(
                dataset_context,
                business_context
            )

            # Start fresh chat session
            self.active_chat_session = self.model.start_chat()

            # Send initial system message with instructions
            initial_msg = f"{system_instruction}\n\nDataset loaded and ready for analysis."
            self.active_chat_session.send_message(initial_msg)

            return True

        except Exception as e:
            print(f"Error starting chat session: {e}")
            traceback.print_exc()
            return False

    def _build_system_instruction(
        self,
        dataset_context: str,
        business_context: Optional[str] = None
    ) -> str:
        """Build system instruction for Gemini with JSON response format"""
        instruction = f"""You are an expert data analyst assistant. You help users analyze CSV data by generating Python code using pandas.

DATASET CONTEXT:
{dataset_context}

RESPONSE FORMAT (CRITICAL):
You MUST respond with valid JSON in this exact structure:
{{
  "output_type": "exploratory" | "visualization" | "modification",
  "code": "Python code here",
  "explanation": "Brief explanation of what the code does"
}}

OUTPUT TYPES:
1. **exploratory**: Answering questions, showing data, calculating metrics, statistical analysis
   - Use this when: User wants to SEE/UNDERSTAND data (not download modified data)
   - Examples: "What's the average?", "Show first 10 rows", "Count unique values", "Show correlations", "Calculate statistics"
   - Code should PRINT results using print()
   - Return computed values, statistics, correlations, summaries
   - Example code: print(df['column'].mean())
   - Example code: print(df.groupby('category').size())
   - Example code: print(df[['col1', 'col2']].corr())

2. **visualization**: Creating plots/charts
   - Use this when: User wants to see a visual representation (chart, graph, heatmap)
   - Examples: "Plot distribution", "Show trends over time", "Create correlation heatmap", "Bar chart of categories"
   - Code MUST save plot: plt.savefig('plot.png', bbox_inches='tight', dpi=100)
   - Code MUST call: plt.close()
   - Example code:
     import matplotlib.pyplot as plt
     import seaborn as sns
     df['column'].hist()
     plt.savefig('plot.png', bbox_inches='tight', dpi=100)
     plt.close()

3. **modification**: Creating a NEW/MODIFIED dataset that user wants to DOWNLOAD
   - Use this ONLY when: User explicitly wants to create/download a filtered/transformed dataset
   - Examples: "Give me users from NYC that I can download", "Create a subset with only 2024 data", "Add calculated column and let me download"
   - Code MUST assign result to 'result' variable
   - Example code: result = df[df['state'] == 'CA']
   - This creates a downloadable CSV file
   - DO NOT use this for calculations, correlations, or statistics - those are exploratory!

IMPORTANT RULES:
1. The DataFrame is available as variable 'df' - DO NOT try to load it
2. For modifications, ALWAYS assign to 'result' variable
3. Use pandas, numpy, matplotlib, seaborn as needed
4. Keep code concise and efficient
5. Handle missing values and errors gracefully
6. Return ONLY valid JSON, no extra text before or after
7. DO NOT wrap JSON in markdown code blocks - return raw JSON only

CODE QUALITY BEST PRACTICES:
- Use vectorized pandas operations (avoid loops when possible)
- Use appropriate pandas methods: .value_counts(), .groupby(), .agg(), .query(), .corr(), .describe()
- Compute statistics directly on the data - don't transform data unless user explicitly requests transformation
- Handle null values appropriately: .dropna(), .fillna(), .isna()
- Use descriptive variable names
- Keep code clean and readable
- Reference the dataset context above for column names, types, and ranges
- For numeric columns, use the provided range information to validate filters
- For categorical columns, use the provided top values to guide analysis

CRITICAL PRINCIPLES:
- When asked to analyze or calculate, work with the ORIGINAL data values
- Only transform/modify data when output_type is "modification" (user wants downloadable result)
- For exploratory analysis: Calculate statistics, correlations, aggregations directly - then PRINT results
- Don't create intermediate transformed columns unless that's what the user explicitly requested
- Example: For correlation → use df.corr(), NOT df with binary flags
- Example: For group statistics → use df.groupby().agg(), NOT create new filtered dataframes
"""

        if business_context:
            instruction += f"\n\nBUSINESS CONTEXT:\n{business_context}"

        return instruction

    # ===== Query Processing =====

    def process_query(
        self,
        user_query: str,
        save_to_chat: bool = True
    ) -> dict:
        """
        Process user query and generate response

        Args:
            user_query: User's natural language query
            save_to_chat: Whether to save to chat history

        Returns:
            Dict with response data (code, output, result, etc.)
        """
        try:
            if self.active_chat_session is None:
                return {
                    "success": False,
                    "error": "No active chat session"
                }

            # Save user message if requested
            if save_to_chat:
                self.chat_manager.add_user_message(
                    self.current_project_id,
                    self.current_chat_id,
                    user_query
                )

            # Send query to Gemini
            print(f"[DEBUG] Sending query to Gemini: {user_query}")
            response = self.active_chat_session.send_message(user_query)
            ai_response = response.text
            print(f"[DEBUG] Gemini response (first 500 chars): {ai_response[:500]}")

            # Parse JSON response from Gemini (with markdown stripping)
            try:
                # Strip markdown code blocks if present (FIX for previous issue)
                clean_response = ai_response.strip()
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:]  # Remove ```json
                elif clean_response.startswith("```"):
                    clean_response = clean_response[3:]  # Remove ```

                if clean_response.endswith("```"):
                    clean_response = clean_response[:-3]  # Remove trailing ```

                clean_response = clean_response.strip()

                # Try to parse as JSON
                response_json = json.loads(clean_response)
                output_type = response_json.get("output_type", "exploratory")
                code = response_json.get("code", "")
                explanation = response_json.get("explanation", "")
                print(f"[DEBUG] Successfully parsed JSON - output_type: {output_type}")
            except json.JSONDecodeError as e:
                # Fallback: if JSON parsing fails, try to extract from markdown
                print(f"[WARNING] Gemini didn't return valid JSON: {e}")
                print(f"[DEBUG] Response after stripping: {clean_response[:200]}")
                return {
                    "success": False,
                    "error": f"Failed to parse Gemini response as JSON: {e}\n\nResponse: {ai_response[:500]}"
                }

            # Execute code
            execution_result = self._execute_code(code, output_type)

            # Build response dict
            response_data = {
                "success": execution_result["success"],
                "output_type": output_type,
                "code": code,
                "output": execution_result.get("output"),
                "result": execution_result.get("result"),
                "plot_path": execution_result.get("plot_path"),
                "modified_dataframe_path": execution_result.get("modified_dataframe_path"),
                "modification_summary": execution_result.get("modification_summary"),
                "error": execution_result.get("error"),
                "explanation": explanation
            }

            # Save assistant message if requested and successful
            if save_to_chat and response_data["success"]:
                self.chat_manager.add_assistant_message(
                    self.current_project_id,
                    self.current_chat_id,
                    content=explanation,
                    code=code,
                    output_type=output_type,
                    output=execution_result.get("output"),
                    result=execution_result.get("result"),
                    plot_path=execution_result.get("plot_path"),
                    modified_dataframe_path=execution_result.get("modified_dataframe_path"),
                    modification_summary=execution_result.get("modification_summary"),
                    explanation=explanation
                )

                # Update Gemini history in storage
                self._save_gemini_history()

            return response_data

        except Exception as e:
            error_msg = f"Error processing query: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    def _execute_code(self, code: str, output_type: str) -> dict:
        """Execute Python code safely"""
        try:
            # Prepare execution environment
            exec_globals = {
                'df': self.current_dataframe,
                'pd': pd,
                'plt': plt,
                'np': __import__('numpy'),
                'sns': __import__('seaborn')
            }

            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()

            # Execute code
            exec(code, exec_globals)

            # Restore stdout
            sys.stdout = old_stdout
            output = captured_output.getvalue()

            # Process result based on output type
            result_data = {
                "success": True,
                "output": output
            }

            if output_type == "visualization":
                # Check if plot was saved
                plot_path = os.path.join(self.base_dir, "plots", f"plot_{self.current_chat_id}.png")
                if os.path.exists("plot.png"):
                    # Move plot to proper location
                    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
                    shutil.move("plot.png", plot_path)
                    result_data["plot_path"] = plot_path
                else:
                    result_data["success"] = False
                    result_data["error"] = "Code executed but no plot was saved. Make sure to use plt.savefig('plot.png')"

            elif output_type == "modification":
                # Check if 'result' variable exists
                if 'result' in exec_globals:
                    modified_df = exec_globals['result']

                    # Validate it's a DataFrame
                    if isinstance(modified_df, pd.DataFrame):
                        # Save modified DataFrame to temp location
                        temp_dir = os.path.join(self.base_dir, "temp_modifications")
                        os.makedirs(temp_dir, exist_ok=True)

                        temp_filename = f"{self.current_chat_id}_{uuid.uuid4().hex[:8]}.csv"
                        temp_path = os.path.join(temp_dir, temp_filename)

                        modified_df.to_csv(temp_path, index=False)
                        result_data["modified_dataframe_path"] = temp_path

                        # Generate modification summary
                        result_data["modification_summary"] = {
                            "rows_before": len(self.current_dataframe),
                            "rows_after": len(modified_df),
                            "cols_before": len(self.current_dataframe.columns),
                            "cols_after": len(modified_df.columns),
                            "new_columns": list(set(modified_df.columns) - set(self.current_dataframe.columns)),
                            "removed_columns": list(set(self.current_dataframe.columns) - set(modified_df.columns))
                        }
                    else:
                        result_data["success"] = False
                        result_data["error"] = f"'result' variable is not a DataFrame (type: {type(modified_df).__name__})"
                else:
                    result_data["success"] = False
                    result_data["error"] = "Modification query must assign output to 'result' variable"

            elif output_type == "exploratory":
                # Just use the printed output
                result_data["result"] = output

            return result_data

        except Exception as e:
            sys.stdout = old_stdout
            error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            return {
                "success": False,
                "error": error_msg
            }

    def _save_gemini_history(self):
        """
        Save current Gemini chat history in serializable format
        Extracts role and text from Gemini's Content objects
        """
        if not self.active_chat_session or not self.current_project_id or not self.current_chat_id:
            return

        try:
            # Serialize Gemini history to JSON-safe format
            serializable_history = []
            for msg in self.active_chat_session.history:
                serializable_history.append({
                    "role": msg.role,
                    "parts": [{"text": part.text} for part in msg.parts]
                })

            # Save to chat manager
            self.chat_manager.update_gemini_history(
                self.current_project_id,
                self.current_chat_id,
                serializable_history
            )
        except Exception as e:
            print(f"Error saving Gemini history: {e}")
            traceback.print_exc()

    # ===== Utility Methods =====

    def update_dataframe(self, new_dataframe: pd.DataFrame):
        """
        Update the active DataFrame
        Used when DataFrame is modified (e.g., new version)
        """
        self.current_dataframe = new_dataframe

    def update_context(self, new_context: str):
        """Update the dataset context"""
        self.dataset_context = new_context

    def close_session(self):
        """Close current chat session"""
        self._save_gemini_history()
        self.active_chat_session = None
        self.current_project_id = None
        self.current_chat_id = None
        self.current_dataframe = None
        self.dataset_context = None
