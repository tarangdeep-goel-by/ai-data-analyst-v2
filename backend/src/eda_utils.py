"""
Utility functions for exploratory data analysis (EDA)
Ported from auto_eda.py generate_context_string for better AI context
"""

import os
import pandas as pd
from typing import Optional


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

        # Add unique values for categorical columns
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
