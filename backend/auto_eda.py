#!/usr/bin/env python3
"""
Automated Exploratory Data Analysis (EDA) for CSV files
Performs standard data profiling and analysis tasks automatically
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime
from pathlib import Path


class AutoEDA:
    """Automated EDA class for CSV file analysis"""

    def __init__(self, csv_path, output_dir=None):
        """
        Initialize AutoEDA with CSV file path

        Args:
            csv_path: Path to CSV file
            output_dir: Directory to save analysis outputs (default: same as CSV)
        """
        self.csv_path = csv_path
        self.df = None
        self.output_dir = output_dir or os.path.dirname(csv_path)
        self.report_lines = []

    def load_data(self):
        """Load CSV file into pandas DataFrame"""
        print(f"Loading data from: {self.csv_path}")
        try:
            self.df = pd.read_csv(self.csv_path)
            print(f"✓ Data loaded successfully\n")
            return True
        except Exception as e:
            print(f"✗ Error loading file: {e}")
            return False

    def _add_section(self, title):
        """Add section header to report"""
        self.report_lines.append(f"\n{'='*80}")
        self.report_lines.append(f"{title}")
        self.report_lines.append(f"{'='*80}\n")

    def _add_line(self, text):
        """Add line to report"""
        self.report_lines.append(text)

    def basic_info(self):
        """Display basic dataset information"""
        self._add_section("BASIC DATASET INFORMATION")

        rows, cols = self.df.shape
        self._add_line(f"File: {os.path.basename(self.csv_path)}")
        self._add_line(f"Shape: {rows:,} rows × {cols} columns")
        self._add_line(f"Memory Usage: {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        self._add_line(f"Duplicates: {self.df.duplicated().sum():,} rows ({self.df.duplicated().sum()/len(self.df)*100:.2f}%)")

        print(f"Shape: {rows:,} rows × {cols} columns")
        print(f"Memory Usage: {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        print(f"Duplicates: {self.df.duplicated().sum():,} rows\n")

    def column_info(self):
        """Analyze column data types and properties"""
        self._add_section("COLUMN INFORMATION")

        # Data types summary
        dtype_counts = self.df.dtypes.value_counts()
        self._add_line("Data Types Summary:")
        for dtype, count in dtype_counts.items():
            self._add_line(f"  {dtype}: {count} columns")

        # Detailed column info
        self._add_line("\nDetailed Column Information:")
        self._add_line(f"{'Column Name':<40} {'Type':<15} {'Non-Null':<12} {'Null %':<10} {'Unique'}")
        self._add_line("-" * 100)

        for col in self.df.columns:
            non_null = self.df[col].notna().sum()
            null_pct = (self.df[col].isna().sum() / len(self.df)) * 100
            unique = self.df[col].nunique()
            dtype = str(self.df[col].dtype)

            self._add_line(f"{col:<40} {dtype:<15} {non_null:<12,} {null_pct:<10.2f} {unique:,}")

        print("✓ Column information analyzed")

    def missing_values_analysis(self):
        """Analyze missing values in dataset"""
        self._add_section("MISSING VALUES ANALYSIS")

        missing = self.df.isna().sum()
        missing_pct = (missing / len(self.df)) * 100

        missing_df = pd.DataFrame({
            'Column': missing.index,
            'Missing_Count': missing.values,
            'Missing_Percentage': missing_pct.values
        })
        missing_df = missing_df[missing_df['Missing_Count'] > 0].sort_values('Missing_Count', ascending=False)

        if len(missing_df) > 0:
            self._add_line(f"Columns with missing values: {len(missing_df)}\n")
            self._add_line(f"{'Column':<40} {'Missing Count':<15} {'Missing %'}")
            self._add_line("-" * 80)
            for _, row in missing_df.iterrows():
                self._add_line(f"{row['Column']:<40} {row['Missing_Count']:<15,.0f} {row['Missing_Percentage']:.2f}%")

            print(f"✓ Found {len(missing_df)} columns with missing values")
        else:
            self._add_line("No missing values found in dataset")
            print("✓ No missing values found")

    def numerical_analysis(self):
        """Analyze numerical columns"""
        self._add_section("NUMERICAL COLUMNS ANALYSIS")

        numerical_cols = self.df.select_dtypes(include=[np.number]).columns

        if len(numerical_cols) > 0:
            self._add_line(f"Found {len(numerical_cols)} numerical columns\n")

            # Basic statistics
            stats = self.df[numerical_cols].describe()
            self._add_line("Statistical Summary:")
            self._add_line(stats.to_string())

            # Check for potential issues
            self._add_line("\n\nPotential Issues:")
            for col in numerical_cols:
                issues = []

                # Check for negative values
                if (self.df[col] < 0).any():
                    neg_count = (self.df[col] < 0).sum()
                    issues.append(f"Has {neg_count:,} negative values")

                # Check for zeros
                zero_count = (self.df[col] == 0).sum()
                if zero_count > 0:
                    zero_pct = (zero_count / len(self.df)) * 100
                    issues.append(f"Has {zero_count:,} zeros ({zero_pct:.2f}%)")

                # Check for outliers (using IQR method)
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((self.df[col] < (Q1 - 1.5 * IQR)) | (self.df[col] > (Q3 + 1.5 * IQR))).sum()
                if outliers > 0:
                    outlier_pct = (outliers / len(self.df)) * 100
                    issues.append(f"Has {outliers:,} outliers ({outlier_pct:.2f}%)")

                if issues:
                    self._add_line(f"  {col}: {', '.join(issues)}")

            print(f"✓ Analyzed {len(numerical_cols)} numerical columns")
        else:
            self._add_line("No numerical columns found")
            print("✓ No numerical columns found")

    def categorical_analysis(self):
        """Analyze categorical columns"""
        self._add_section("CATEGORICAL COLUMNS ANALYSIS")

        # Consider object and category dtypes, plus low-cardinality numerics
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()

        # Add numerical columns with low cardinality (< 20 unique values)
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            if self.df[col].nunique() < 20:
                categorical_cols.append(col)

        if len(categorical_cols) > 0:
            self._add_line(f"Found {len(categorical_cols)} categorical/low-cardinality columns\n")

            for col in categorical_cols:
                unique_count = self.df[col].nunique()
                self._add_line(f"\n{col} ({unique_count} unique values):")
                self._add_line("-" * 60)

                # Show value counts
                value_counts = self.df[col].value_counts()

                # If too many unique values, show only top 10
                if unique_count > 10:
                    self._add_line(f"Top 10 values (out of {unique_count} total):")
                    value_counts = value_counts.head(10)

                for value, count in value_counts.items():
                    pct = (count / len(self.df)) * 100
                    self._add_line(f"  {str(value)[:50]:<50} {count:>10,} ({pct:>6.2f}%)")

                if unique_count > 10:
                    remaining = self.df[col].value_counts()[10:].sum()
                    self._add_line(f"  {'... (other values)':<50} {remaining:>10,}")

            print(f"✓ Analyzed {len(categorical_cols)} categorical columns")
        else:
            self._add_line("No categorical columns found")
            print("✓ No categorical columns found")

    def date_column_detection(self):
        """Detect and analyze potential date columns"""
        self._add_section("DATE COLUMN DETECTION")

        date_columns = []

        # Check object columns for date patterns
        for col in self.df.select_dtypes(include=['object']).columns:
            # Try to convert to datetime
            try:
                sample = self.df[col].dropna().head(100)
                pd.to_datetime(sample, errors='raise')
                date_columns.append(col)
            except:
                # Check if column name suggests it's a date
                if any(keyword in col.lower() for keyword in ['date', 'time', 'dt', '_at', 'created', 'updated', 'timestamp']):
                    date_columns.append(col)

        if date_columns:
            self._add_line(f"Potential date columns found: {len(date_columns)}\n")
            for col in date_columns:
                self._add_line(f"  - {col}")
                # Try to show date range
                try:
                    dates = pd.to_datetime(self.df[col], errors='coerce')
                    if dates.notna().any():
                        self._add_line(f"    Range: {dates.min()} to {dates.max()}")
                        self._add_line(f"    Span: {(dates.max() - dates.min()).days} days")
                except:
                    pass
            print(f"✓ Found {len(date_columns)} potential date columns")
        else:
            self._add_line("No date columns detected")
            print("✓ No date columns detected")

    def sample_data(self):
        """Show sample rows from dataset"""
        self._add_section("SAMPLE DATA")

        self._add_line("First 5 rows:")
        self._add_line(self.df.head().to_string())

        self._add_line("\n\nLast 5 rows:")
        self._add_line(self.df.tail().to_string())

        print("✓ Sample data captured")

    def save_report(self):
        """Save analysis report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"eda_report_{Path(self.csv_path).stem}_{timestamp}.txt"
        output_path = os.path.join(self.output_dir, filename)

        with open(output_path, 'w') as f:
            f.write('\n'.join(self.report_lines))

        print(f"\n✓ Report saved to: {output_path}")
        return output_path

    def run_analysis(self, save_report=True):
        """Run complete EDA analysis"""
        if not self.load_data():
            return False

        print("Running automated EDA...\n")

        self.basic_info()
        self.column_info()
        self.missing_values_analysis()
        self.numerical_analysis()
        self.categorical_analysis()
        self.date_column_detection()
        self.sample_data()

        if save_report:
            report_path = self.save_report()
            return report_path

        return True

    def get_context_as_json(self):
        """
        Get EDA context as JSON-serializable dict
        This is used for caching and AI context

        Returns:
            Dict with complete EDA context
        """
        if self.df is None:
            return None

        # Basic info
        rows, cols = self.df.shape
        context = {
            "filename": os.path.basename(self.csv_path),
            "rows": int(rows),
            "columns": int(cols),
            "memory_mb": float(self.df.memory_usage(deep=True).sum() / 1024**2),
            "duplicates": int(self.df.duplicated().sum()),
            "column_list": self.df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in self.df.dtypes.items()},
        }

        # Column details
        column_details = {}
        for col in self.df.columns:
            col_info = {
                "dtype": str(self.df[col].dtype),
                "non_null": int(self.df[col].notna().sum()),
                "null_count": int(self.df[col].isna().sum()),
                "null_pct": float((self.df[col].isna().sum() / len(self.df)) * 100),
                "unique": int(self.df[col].nunique())
            }

            # Add numerical stats if applicable
            if pd.api.types.is_numeric_dtype(self.df[col]):
                col_info["stats"] = {
                    "mean": float(self.df[col].mean()) if not pd.isna(self.df[col].mean()) else None,
                    "std": float(self.df[col].std()) if not pd.isna(self.df[col].std()) else None,
                    "min": float(self.df[col].min()) if not pd.isna(self.df[col].min()) else None,
                    "max": float(self.df[col].max()) if not pd.isna(self.df[col].max()) else None,
                    "median": float(self.df[col].median()) if not pd.isna(self.df[col].median()) else None
                }

            # Add top values for categorical or low-cardinality columns
            if col_info["unique"] < 50:
                value_counts = self.df[col].value_counts().head(10)
                col_info["top_values"] = {
                    str(k): int(v) for k, v in value_counts.items()
                }

            column_details[col] = col_info

        context["column_details"] = column_details

        # Sample data (first 5 rows)
        context["sample_data"] = self.df.head(5).to_dict(orient='records')

        return context

    def generate_context_string(self):
        """
        Generate a concise string representation of the dataset for AI context
        This is what gets sent to the AI model

        Returns:
            String with dataset context
        """
        if self.df is None:
            return "No dataset loaded"

        context_parts = []

        # Basic info
        rows, cols = self.df.shape
        context_parts.append(f"Dataset: {os.path.basename(self.csv_path)}")
        context_parts.append(f"Shape: {rows:,} rows × {cols} columns")
        context_parts.append(f"\nColumns and Data Types:")

        # Column info with types
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            non_null = self.df[col].notna().sum()
            unique = self.df[col].nunique()

            col_str = f"  - {col} ({dtype}): {non_null:,} non-null, {unique:,} unique"

            # Add range for numerical
            if pd.api.types.is_numeric_dtype(self.df[col]):
                min_val = self.df[col].min()
                max_val = self.df[col].max()
                col_str += f", range: [{min_val:.2f}, {max_val:.2f}]"

            # Add top values for categorical
            elif unique < 20:
                top_vals = self.df[col].value_counts().head(3).index.tolist()
                top_vals_str = ", ".join(str(v)[:20] for v in top_vals)
                col_str += f", top values: {top_vals_str}"

            context_parts.append(col_str)

        # Sample data
        context_parts.append(f"\nFirst 3 rows preview:")
        context_parts.append(self.df.head(3).to_string(index=False))

        return "\n".join(context_parts)


def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python auto_eda.py <csv_file_path> [output_dir]")
        print("\nExample:")
        print("  python auto_eda.py data.csv")
        print("  python auto_eda.py data.csv ./reports")
        sys.exit(1)

    csv_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(csv_path):
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)

    print(f"\n{'='*80}")
    print("AUTOMATED EDA TOOL")
    print(f"{'='*80}\n")

    eda = AutoEDA(csv_path, output_dir)
    eda.run_analysis(save_report=True)

    print(f"\n{'='*80}")
    print("Analysis complete!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
