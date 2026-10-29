import streamlit as st
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os

st.title("CSV / Excel to Parquet Converter")

# ==========================================
# FILE UPLOAD
# ==========================================

uploaded_file = st.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    input_file = uploaded_file.name
    file_extension = os.path.splitext(input_file)[1].lower()

    # ==========================================
    # AUTO-DETECT FILE TYPE
    # ==========================================

    try:

        if file_extension == ".xlsx":

            st.info("Excel file detected")
            df = pd.read_excel(
                uploaded_file,
                dtype=str
            )

        elif file_extension == ".csv":

            st.info("CSV file detected")
            df = pd.read_csv(
                uploaded_file,
                dtype=str
            )

        else:

            st.error(
                "Unsupported file type. Please upload CSV or XLSX."
            )
            st.stop()

        # ==========================================
        # BASIC INFORMATION
        # ==========================================

        df.columns = df.columns.str.strip()

        st.success("File loaded successfully!")

        st.write("**File:**", input_file)
        st.write("**Rows:**", len(df))
        st.write("**Columns:**", len(df.columns))

        st.write("### Columns")
        st.write(df.columns.tolist())


        # ==========================================
        # DATE COLUMN
        # ==========================================

        if "Date" in df.columns:

            df["Date"] = pd.to_datetime(
                df["Date"],
                errors="coerce",
                dayfirst=True
            ).dt.strftime("%d-%m-%Y")

            st.success(
                "Date column converted to DD-MM-YYYY."
            )


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

        output_file = (
            os.path.splitext(input_file)[0]
            + ".parquet"
        )

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
        # SUCCESS
        # ==========================================

        st.success(
            f"Parquet created successfully: {output_file}"
        )

        # ==========================================
        # DOWNLOAD BUTTON
        # ==========================================

        with open(output_file, "rb") as f:

            st.download_button(
                label="Download Parquet File",
                data=f,
                file_name=output_file,
                mime="application/octet-stream"
            )


        # ==========================================
        # PREVIEW
        # ==========================================

        st.write("### Data Preview")

        st.dataframe(
            df.head(10),
            use_container_width=True
        )

        # ==========================================
        # DATA TYPES
        # ==========================================

        st.write("### Data Types")

        st.dataframe(
            df.dtypes.astype(str).to_frame("Data Type"),
            use_container_width=True
        )


    except Exception as e:

        st.error(
            f"Error while processing the file: {str(e)}"
        )
