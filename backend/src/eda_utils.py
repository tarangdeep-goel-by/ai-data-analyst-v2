"""
Utility functions for exploratory data analysis (EDA)
Ported from auto_eda.py generate_context_string for better AI context
"""

import os
import pandas as pd
import ast
from typing import Optional


def _detect_data_format(sample_values):
    """
    Detect if column contains serialized collections (sets, lists, dicts)
    Returns format hint for AI agent
    """
    for val in sample_values:
        if pd.isna(val):
            continue
        val_str = str(val).strip()

        # Check if it looks like a set (with or without proper quoting)
        if val_str.startswith('{') and val_str.endswith('}') and ':' not in val_str:
            try:
                ast.literal_eval(val_str)
                return "set_string_valid", val_str
            except:
                # It LOOKS like a set but has invalid syntax (missing quotes)
                # Example: {Bike} instead of {'Bike'}
                return "set_string_invalid", val_str

        # Check if it looks like a list
        if val_str.startswith('[') and val_str.endswith(']'):
            try:
                ast.literal_eval(val_str)
                return "list_string_valid", val_str
            except:
                return "list_string_invalid", val_str

        # Check if it looks like a dict
        if val_str.startswith('{') and val_str.endswith('}') and ':' in val_str:
            try:
                ast.literal_eval(val_str)
                return "dict_string_valid", val_str
            except:
                return "dict_string_invalid", val_str

    return None, None


def generate_eda_context(df: pd.DataFrame, dataset_name: str = "Dataset") -> str:
    """
    Generate a concise string representation of the dataset for AI context
    This format gives the AI agent better understanding of data structure and ranges

    Args:
        df: Input DataFrame
        dataset_name: Name of the dataset (for context)

    Returns:
        Formatted EDA context string optimized for AI agent
    """
    context_parts = []

    # Basic info
    rows, cols = df.shape
    context_parts.append(f"Dataset: {dataset_name}")
    context_parts.append(f"Shape: {rows:,} rows × {cols} columns")
    context_parts.append(f"\nColumns and Data Types:")

    # Column info with types, nulls, unique counts, and ranges/top values
    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null = df[col].notna().sum()
        unique = df[col].nunique()

        col_str = f"  - {col} ({dtype}): {non_null:,} non-null, {unique:,} unique"

        # Add range for numerical columns - CRITICAL for AI to understand data bounds
        if pd.api.types.is_numeric_dtype(df[col]) and non_null > 0:
            min_val = df[col].min()
            max_val = df[col].max()
            col_str += f", range: [{min_val:.2f}, {max_val:.2f}]"

        # Check if column contains serialized collections FIRST (before categorical check)
        elif non_null > 0:
            sample_vals = df[col].dropna().head(5).tolist()
            data_format, example = _detect_data_format(sample_vals)

            if data_format:
                # Add format hint for AI
                format_hints = {
                    "set_string_valid": "⚠️ STORED AS STRING - Contains valid Python sets",
                    "set_string_invalid": "⚠️ STORED AS STRING - Contains set-like data (NOT valid Python syntax)",
                    "list_string_valid": "⚠️ STORED AS STRING - Contains valid Python lists",
                    "list_string_invalid": "⚠️ STORED AS STRING - Contains list-like data (NOT valid Python syntax)",
                    "dict_string_valid": "⚠️ STORED AS STRING - Contains valid Python dicts",
                    "dict_string_invalid": "⚠️ STORED AS STRING - Contains dict-like data (NOT valid Python syntax)"
                }

                # Still show the values for low cardinality
                if unique <= 10:
                    value_counts = df[col].value_counts()
                    vals_with_counts = [f"{str(v)[:30]}({c})" for v, c in value_counts.items()]
                    col_str += f"\n    {format_hints[data_format]}, values: {', '.join(vals_with_counts)}"
                elif unique <= 50:
                    value_counts = df[col].value_counts().head(10)
                    vals_with_counts = [f"{str(v)[:30]}({c})" for v, c in value_counts.items()]
                    col_str += f"\n    {format_hints[data_format]}, top 10: {', '.join(vals_with_counts)}"
                else:
                    col_str += f"\n    {format_hints[data_format]} - example: {example}"

                # Add appropriate parsing instructions
                if "invalid" in data_format:
                    col_str += f"\n    ➜ Use .str.contains() or string methods - DO NOT use ast.literal_eval() or eval()"
                    col_str += f"\n    ➜ Example: df[col].str.contains('Car', na=False) to check if 'Car' is in the set"
                else:
                    col_str += f"\n    ➜ To parse: import ast; parsed = ast.literal_eval(value_str)"

            # Add unique values for regular categorical columns (not serialized collections)
            elif unique > 0 and unique <= 10:
                # For very low cardinality, show ALL unique values with counts
                value_counts = df[col].value_counts()
                vals_with_counts = [f"{str(v)[:30]}({c})" for v, c in value_counts.items()]
                col_str += f", values: {', '.join(vals_with_counts)}"
            elif unique <= 50:
                # For moderate cardinality, show top 10 with counts
                value_counts = df[col].value_counts().head(10)
                vals_with_counts = [f"{str(v)[:30]}({c})" for v, c in value_counts.items()]
                col_str += f", top 10: {', '.join(vals_with_counts)}"

        context_parts.append(col_str)

    # Sample data - show first 3 rows for conciseness
    context_parts.append(f"\nFirst 3 rows preview:")
    context_parts.append(df.head(3).to_string(index=False))

    return "\n".join(context_parts)
