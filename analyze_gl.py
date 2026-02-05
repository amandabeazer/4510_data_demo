import pandas as pd
import numpy as np
import os
import sys

# Configuration
INPUT_FILE = "je_samples (1).xlsx"
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "analysis_report.txt")

def calculate_benford_stats(series):
    """
    Calculates Benford's Law statistics for a given pandas Series.
    Returns a DataFrame with Observed Count, Observed %, and Expected %.
    """
    # Filter out 0 and NaN
    series = series.dropna()
    series = series[series != 0]

    if series.empty:
        return None

    # Get first digit using string manipulation
    def get_leading_digit(x):
        try:
            s = str(float(abs(x))).replace('.', '').lstrip('0')
            return int(s[0]) if s else 0
        except:
            return 0

    first_digits = series.apply(get_leading_digit)
    # Filter out any 0s that might have slipped through
    first_digits = first_digits[first_digits != 0]

    if first_digits.empty:
        return None

    # Count frequencies
    counts = first_digits.value_counts().sort_index()

    # Ensure all digits 1-9 are present
    for i in range(1, 10):
        if i not in counts:
            counts[i] = 0

    counts = counts.sort_index()

    # Calculate percentages
    total_count = counts.sum()
    observed_pct = (counts / total_count) * 100

    # Expected Benford percentages
    digits = np.arange(1, 10)
    expected_pct = np.log10(1 + 1/digits) * 100

    # Create DataFrame
    df_res = pd.DataFrame({
        'Digit': digits,
        'Observed Count': counts.values,
        'Observed %': observed_pct.values,
        'Expected %': expected_pct
    })

    df_res.set_index('Digit', inplace=True)
    return df_res

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

        # Benford Analysis
        f.write("Benford Analysis (Column: Amount):\n")
        f.write("-" * 20 + "\n")

        if 'Amount' in df.columns:
            benford_stats = calculate_benford_stats(df['Amount'])
            if benford_stats is not None:
                 f.write(benford_stats.to_string(float_format="%.2f"))
                 f.write("\n\n")

                 # Basic check for concern
                 benford_stats['Deviation'] = (benford_stats['Observed %'] - benford_stats['Expected %']).abs()
                 max_dev = benford_stats['Deviation'].max()
                 f.write(f"Maximum deviation from expected: {max_dev:.2f}%\n")

                 significant_digits = benford_stats[benford_stats['Deviation'] > 2.0]
                 if not significant_digits.empty:
                     f.write("WARNING: The following digits show significant deviation (>2.0%):\n")
                     for digit, row in significant_digits.iterrows():
                         f.write(f"  Digit {digit}: Observed {row['Observed %']:.2f}% vs Expected {row['Expected %']:.2f}% (Diff: {row['Observed %'] - row['Expected %']:.2f}%)\n")
                     f.write("Further investigation recommended.\n")
                 else:
                     f.write("No significant deviation (>2.0%) detected.\n")
            else:
                f.write("Could not perform Benford analysis (no valid data).\n")
        else:
             f.write("Column 'Amount' not found.\n")
        f.write("\n")

    print(f"Analysis complete. Report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    analyze_file()
