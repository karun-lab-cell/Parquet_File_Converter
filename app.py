import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os

# Get the uploaded filename
input_file = list(uploaded.keys())[0]

# ==========================================
# AUTO-DETECT FILE TYPE AND READ
# ==========================================

file_extension = os.path.splitext(input_file)[1].lower()

if file_extension == ".xlsx":
    print("Excel file detected")
    df = pd.read_excel(input_file, dtype=str)

elif file_extension == ".csv":
    print("CSV file detected")
    df = pd.read_csv(input_file, dtype=str)

else:
    raise ValueError(
        f"Unsupported file type: {file_extension}. "
        "Please upload a CSV or XLSX file."
    )


# ==========================================
# BASIC INFORMATION
# ==========================================

# Remove spaces from column names
df.columns = df.columns.str.strip()

print("File:", input_file)
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nColumns:")
print(df.columns.tolist())


# ==========================================
# DATE COLUMN
# ==========================================

if "Date" in df.columns:

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
        dayfirst=True
    ).dt.strftime("%d-%m-%Y")

    print("\nDate converted to dd-mm-yyyy STRING")


# ==========================================
# NUMERIC COLUMNS
# ==========================================

numeric_columns = [
    "Clicks",
    "Revenue",
    "Payout",
    "GMV"
]

for col in numeric_columns:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


# ==========================================
# CREATE PARQUET
# ==========================================

output_file = os.path.splitext(input_file)[0] + ".parquet"

table = pa.Table.from_pandas(
    df,
    preserve_index=False
)

pq.write_table(
    table,
    output_file,
    compression="snappy"
)


# ==========================================
# OUTPUT
# ==========================================

print("\n================================")
print("Parquet created successfully!")
print("================================")
print("Output file:", output_file)

print("\nData types:")
print(df.dtypes)
