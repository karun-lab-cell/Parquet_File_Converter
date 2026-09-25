import streamlit as st
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os
import tempfile

st.set_page_config(
    page_title="Excel to Parquet Converter",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Excel to Parquet Converter")
st.write("Upload an Excel file, clean the data, convert selected columns, and download the Parquet file.")

uploaded_file = st.file_uploader(
    "Upload Excel file",
    type=["xlsx", "xls"],
    help="Upload an Excel workbook containing your data."
)

if uploaded_file is not None:

    try:
        # Read Excel as text first
        df = pd.read_excel(uploaded_file, dtype=str)

        # Remove spaces from column names
        df.columns = df.columns.str.strip()

        st.success(f"File uploaded: {uploaded_file.name}")

        # Basic information
        col1, col2 = st.columns(2)
        col1.metric("Rows", len(df))
        col2.metric("Columns", len(df.columns))

        with st.expander("View column names"):
            st.write(df.columns.tolist())

        # ============================
        # DATE COLUMN
        # ============================
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(
                df["Date"],
                errors="coerce",
                dayfirst=True
            ).dt.strftime("%d-%m-%Y")

        # ============================
        # NUMERIC COLUMNS
        # ============================
        numeric_columns = [
            "Clicks",
            "Revenue",
            "Payout",
            "GMV"
        ]

        converted_columns = []

        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )
                converted_columns.append(col)

        # ============================
        # CREATE PARQUET
        # ============================
        base_name = os.path.splitext(uploaded_file.name)[0]
        output_file = f"{base_name}.parquet"

        table = pa.Table.from_pandas(
            df,
            preserve_index=False
        )

        # Save to a temporary file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".parquet"
        ) as temp_file:
            temp_path = temp_file.name

        pq.write_table(
            table,
            temp_path,
            compression="snappy"
        )

        # ============================
        # BASIC CHECK
        # ============================
        check = pd.read_parquet(temp_path)

        st.subheader("✅ Conversion Summary")

        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", len(check))
        c2.metric("Columns", len(check.columns))
        c3.metric("File Size", f"{os.path.getsize(temp_path) / 1024 / 1024:.2f} MB")

        if converted_columns:
            st.write("**Numeric columns converted:**", ", ".join(converted_columns))

        # ============================
        # DATE CHECK
        # ============================
        if "Date" in check.columns:
            parsed_dates = pd.to_datetime(
                check["Date"],
                format="%d-%m-%Y",
                errors="coerce"
            )

            invalid_dates = parsed_dates.isna().sum()

            st.subheader("📅 Date Check")

            d1, d2, d3, d4 = st.columns(4)
            d1.metric("Invalid Dates", int(invalid_dates))
            d2.metric("First Date", str(parsed_dates.min())[:10])
            d3.metric("Last Date", str(parsed_dates.max())[:10])
            d4.metric("Unique Dates", int(parsed_dates.nunique()))

        # ============================
        # NULL CHECK
        # ============================
        st.subheader("🔎 Null Check")

        null_check = check.isna().sum().reset_index()
        null_check.columns = ["Column", "Null Count"]

        st.dataframe(
            null_check,
            use_container_width=True,
            hide_index=True
        )

        # ============================
        # DATA TYPES
        # ============================
        with st.expander("View Data Types"):
            dtype_df = pd.DataFrame({
                "Column": check.columns,
                "Data Type": check.dtypes.astype(str).values
            })
            st.dataframe(
                dtype_df,
                use_container_width=True,
                hide_index=True
            )

        # ============================
        # SAMPLE DATA
        # ============================
        st.subheader("👀 Sample Data")
        st.dataframe(
            check.head(10),
            use_container_width=True,
            hide_index=True
        )

        # ============================
        # DOWNLOAD
        # ============================
        with open(temp_path, "rb") as f:
            parquet_bytes = f.read()

        st.download_button(
            label="⬇️ Download Parquet File",
            data=parquet_bytes,
            file_name=output_file,
            mime="application/octet-stream"
        )

        # Clean temporary file
        try:
            os.remove(temp_path)
        except OSError:
            pass

    except Exception as e:
        st.error("An error occurred while processing the file.")
        st.exception(e)

else:
    st.info("👆 Upload an Excel file to begin.")
