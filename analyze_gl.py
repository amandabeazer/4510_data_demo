import pandas as pd
import os
import sys

# Configuration
INPUT_FILE = "je_samples (1).xlsx"
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "analysis_report.txt")

def analyze_file():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: File '{INPUT_FILE}' not found.")
        sys.exit(1)

    print(f"Loading {INPUT_FILE}...")
    try:
        df = pd.read_excel(INPUT_FILE)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        sys.exit(1)

    # Create output directory
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(OUTPUT_FILE, "w") as f:
        f.write(f"Analysis Report for {INPUT_FILE}\n")
        f.write("=" * 40 + "\n\n")

        # Row Count
        row_count = len(df)
        f.write(f"Total Row Count: {row_count}\n\n")

        # Columns
        f.write(f"Columns: {', '.join(map(str, df.columns))}\n\n")

        # Date Analysis
        f.write("Date Analysis:\n")
        f.write("-" * 20 + "\n")

        date_cols = []
        # First check for already datetime columns
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                date_cols.append(col)

        # If no dates found, or to be thorough, try converting object columns that look like dates
        for col in df.select_dtypes(include=['object']):
             if col not in date_cols:
                 try:
                     # Try converting, if it fails, it's not a date.
                     if 'date' in str(col).lower():
                        df[col] = pd.to_datetime(df[col])
                        if pd.api.types.is_datetime64_any_dtype(df[col]):
                            date_cols.append(col)
                 except (ValueError, TypeError):
                     pass

        if date_cols:
            for col in date_cols:
                min_date = df[col].min()
                max_date = df[col].max()
                f.write(f"Column: {col}\n")
                f.write(f"  Range: {min_date} to {max_date}\n")
        else:
            f.write("No date columns identified.\n")
        f.write("\n")

        # Descriptive Statistics
        f.write("Descriptive Statistics (Numerical Columns):\n")
        f.write("-" * 20 + "\n")

        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            stats = df[numeric_cols].describe()
            f.write(stats.to_string())
        else:
            f.write("No numerical columns found.\n")
        f.write("\n")

    print(f"Analysis complete. Report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    analyze_file()
