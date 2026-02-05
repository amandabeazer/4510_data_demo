import pandas as pd
import os
import sys

# Configuration
INPUT_FILE = "je_samples (1).xlsx"
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "analysis_report.xlsx")

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

    # 1. Summary Data
    row_count = len(df)
    summary_data = {
        'Metric': ['File Name', 'Total Row Count'],
        'Value': [INPUT_FILE, row_count]
    }
    summary_df = pd.DataFrame(summary_data)

    # Column list
    columns_df = pd.DataFrame({'Columns': df.columns})

    # 2. Date Analysis
    date_analysis_list = []

    date_cols = []
    # Check for already datetime columns
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            date_cols.append(col)

    # Try converting object columns
    for col in df.select_dtypes(include=['object']):
         if col not in date_cols:
             try:
                 if 'date' in str(col).lower():
                    # Create a copy to avoid SettingWithCopy warning if it were a slice,
                    # though here it is the main df.
                    # Converting effectively.
                    converted = pd.to_datetime(df[col], errors='coerce')
                    # Check if we got valid dates
                    if not converted.isna().all():
                        df[col] = converted
                        date_cols.append(col)
             except (ValueError, TypeError):
                 pass

    if date_cols:
        for col in date_cols:
            min_date = df[col].min()
            max_date = df[col].max()
            date_analysis_list.append({
                'Column': col,
                'Min Date': min_date,
                'Max Date': max_date
            })
        date_analysis_df = pd.DataFrame(date_analysis_list)
    else:
        date_analysis_df = pd.DataFrame({'Message': ['No date columns identified']})

    # 3. Descriptive Statistics
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        stats_df = df[numeric_cols].describe()
        # Transpose for better readability in Excel usually, but standard describe is row-based stats.
        # Let's keep standard orientation but include the index (count, mean, etc) as a column?
        # ExcelWriter writes the index by default, which is good.
    else:
        stats_df = pd.DataFrame({'Message': ['No numerical columns found']})


    print(f"Writing results to {OUTPUT_FILE}...")
    try:
        with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            columns_df.to_excel(writer, sheet_name='Columns', index=False)
            date_analysis_df.to_excel(writer, sheet_name='Date Analysis', index=False)
            stats_df.to_excel(writer, sheet_name='Statistics') # Keep index for describe()
    except Exception as e:
         print(f"Error writing to Excel: {e}")
         sys.exit(1)

    print(f"Analysis complete. Report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    analyze_file()
