import streamlit as st
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os
import time

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Parquet File Converter",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS - LIGHT + DARK MODE COMPATIBLE
# ============================================================

st.markdown("""
<style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }

    /* ========================================================
       MAIN TITLE
       ======================================================== */

    .main-title {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 5px;
        color: var(--text-color);
    }

    .subtitle {
        font-size: 16px;
        color: var(--secondary-text-color);
        margin-bottom: 25px;
    }

    /* ========================================================
       KPI CARDS
       ======================================================== */

    .kpi-card {
        background-color: var(--secondary-background-color);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
        min-height: 105px;
    }

    .kpi-title {
        font-size: 14px;
        color: var(--secondary-text-color);
        margin-bottom: 5px;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--text-color);
        word-break: break-word;
    }

    /* ========================================================
       SECTION HEADERS
       ======================================================== */

    .section-title {
        font-size: 22px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
        color: var(--text-color);
    }

    /* ========================================================
       UPLOAD BOX
       ======================================================== */

    [data-testid="stFileUploader"] {
        background-color: var(--secondary-background-color);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid var(--border-color);
    }

    /* File uploader text */
    [data-testid="stFileUploader"] label {
        color: var(--text-color) !important;
    }

    [data-testid="stFileUploader"] section {
        background-color: var(--secondary-background-color);
        border-color: var(--border-color);
    }

    [data-testid="stFileUploader"] small {
        color: var(--secondary-text-color) !important;
    }

    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {
        background-color: var(--secondary-background-color);
    }

    [data-testid="stSidebar"] * {
        color: var(--text-color);
    }

    /* ========================================================
       BUTTONS
       ======================================================== */

    .stDownloadButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }

    /* ========================================================
       METRICS
       ======================================================== */

    [data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid var(--border-color);
    }

    [data-testid="stMetricLabel"] {
        color: var(--secondary-text-color) !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--text-color) !important;
    }

    [data-testid="stMetricDelta"] {
        color: var(--text-color) !important;
    }

    /* ========================================================
       DATAFRAME
       ======================================================== */

    [data-testid="stDataFrame"] {
        border: 1px solid var(--border-color);
        border-radius: 8px;
    }

    /* ========================================================
       TABS
       ======================================================== */

    button[data-baseweb="tab"] {
        color: var(--text-color) !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--text-color) !important;
    }

    /* ========================================================
       SLIDER
       ======================================================== */

    [data-testid="stSlider"] {
        color: var(--text-color);
    }

    /* ========================================================
       ALERTS / INFO BOXES
       ======================================================== */

    [data-testid="stAlert"] {
        border-radius: 8px;
    }

    /* ========================================================
       MARKDOWN / TEXT
       ======================================================== */

    .stMarkdown,
    .stText,
    p,
    span,
    label {
        color: var(--text-color);
    }

    /* Don't override icons */
    svg {
        color: inherit;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">📦 CSV / Excel → Parquet Converter</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Convert your CSV or Excel files into optimized Parquet format in seconds.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Converter Settings")

    st.markdown("---")

    st.markdown("### Supported Files")

    st.markdown("""
    **CSV**

    `.csv`

    **Excel**

    `.xlsx`
    """)

    st.markdown("---")

    st.markdown("### Automatic Processing")

    st.write("✅ Column name cleanup")
    st.write("✅ Date formatting")
    st.write("✅ Numeric conversion")
    st.write("✅ Snappy compression")
    st.write("✅ Parquet generation")

    st.markdown("---")

    st.caption("Parquet Converter v1.0")


# ============================================================
# FILE UPLOAD
# ============================================================

st.markdown(
    '<div class="section-title">📤 Upload Your File</div>',
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Drag and drop your file here",
    type=["csv", "xlsx"],
    help="Supported formats: CSV and XLSX"
)


# ============================================================
# MAIN PROCESSING
# ============================================================

if uploaded_file is not None:

    input_file = uploaded_file.name
    file_extension = os.path.splitext(input_file)[1].lower()

    try:

        # ----------------------------------------------------
        # FILE INFORMATION
        # ----------------------------------------------------

        file_size_mb = uploaded_file.size / (1024 * 1024)

        # ----------------------------------------------------
        # READ FILE
        # ----------------------------------------------------

        with st.spinner("Reading your file..."):

            if file_extension == ".xlsx":

                st.info("📗 Excel file detected")

                df = pd.read_excel(
                    uploaded_file,
                    dtype=str
                )

            elif file_extension == ".csv":

                st.info("📄 CSV file detected")

                df = pd.read_csv(
                    uploaded_file,
                    dtype=str
                )

            else:

                st.error(
                    "Unsupported file type. Please upload CSV or XLSX."
                )

                st.stop()

        # ----------------------------------------------------
        # CLEAN COLUMN NAMES
        # ----------------------------------------------------

        df.columns = df.columns.str.strip()

        # ----------------------------------------------------
        # BASIC FILE INFORMATION
        # ----------------------------------------------------

        st.success("✅ File loaded successfully!")

        st.markdown(
            '<div class="section-title">📊 File Overview</div>',
            unsafe_allow_html=True
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">File Name</div>
                    <div class="kpi-value" style="font-size:18px;">
                        {input_file}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:

            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Rows</div>
                    <div class="kpi-value">
                        {len(df):,}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:

            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Columns</div>
                    <div class="kpi-value">
                        {len(df.columns):,}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col4:

            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">File Size</div>
                    <div class="kpi-value">
                        {file_size_mb:.2f} MB
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


        # ====================================================
        # PROCESSING
        # ====================================================

        st.markdown(
            '<div class="section-title">🧹 Data Processing</div>',
            unsafe_allow_html=True
        )

        progress_bar = st.progress(0)

        status_text = st.empty()


        # ----------------------------------------------------
        # STEP 1
        # ----------------------------------------------------

        status_text.info(
            "Step 1/4 — Cleaning column names..."
        )

        progress_bar.progress(25)

        df.columns = df.columns.str.strip()

        time.sleep(0.2)


        # ----------------------------------------------------
        # STEP 2 - DATE
        # ----------------------------------------------------

        status_text.info(
            "Step 2/4 — Processing date columns..."
        )

        progress_bar.progress(50)

        if "Date" in df.columns:

            df["Date"] = pd.to_datetime(
                df["Date"],
                errors="coerce",
                dayfirst=True
            ).dt.strftime("%d-%m-%Y")

        time.sleep(0.2)


        # ----------------------------------------------------
        # STEP 3 - NUMERIC COLUMNS
        # ----------------------------------------------------

        status_text.info(
            "Step 3/4 — Converting numeric columns..."
        )

        progress_bar.progress(75)

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

        time.sleep(0.2)


        # ----------------------------------------------------
        # STEP 4 - PARQUET
        # ----------------------------------------------------

        status_text.info(
            "Step 4/4 — Creating Parquet file..."
        )

        progress_bar.progress(90)

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

        progress_bar.progress(100)

        status_text.success(
            "🎉 Processing completed!"
        )


        # ====================================================
        # RESULTS
        # ====================================================

        st.markdown(
            '<div class="section-title">📦 Parquet File Ready</div>',
            unsafe_allow_html=True
        )

        output_size_mb = (
            os.path.getsize(output_file)
            / (1024 * 1024)
        )

        result_col1, result_col2, result_col3 = st.columns(3)

        with result_col1:

            st.metric(
                "Original Size",
                f"{file_size_mb:.2f} MB"
            )

        with result_col2:

            st.metric(
                "Parquet Size",
                f"{output_size_mb:.2f} MB"
            )

        with result_col3:

            if file_size_mb > 0:

                reduction = (
                    (file_size_mb - output_size_mb)
                    / file_size_mb
                ) * 100

                st.metric(
                    "Size Reduction",
                    f"{reduction:.1f}%"
                )


        # ====================================================
        # DOWNLOAD
        # ====================================================

        st.markdown(
            '<div class="section-title">⬇️ Download</div>',
            unsafe_allow_html=True
        )

        with open(output_file, "rb") as f:

            st.download_button(
                label="⬇️ Download Parquet File",
                data=f,
                file_name=output_file,
                mime="application/octet-stream"
            )


        # ====================================================
        # TABS
        # ====================================================

        st.markdown("---")

        tab1, tab2, tab3 = st.tabs(
            [
                "👀 Data Preview",
                "📋 Columns",
                "🔢 Data Types"
            ]
        )


        # ----------------------------------------------------
        # TAB 1 - DATA PREVIEW
        # ----------------------------------------------------

        with tab1:

            st.subheader("Data Preview")

            max_rows = max(5, min(100, len(df)))

            preview_rows = st.slider(
                "Number of rows to preview",
                min_value=5,
                max_value=max_rows,
                value=min(10, max_rows),
                step=5
            )

            st.dataframe(
                df.head(preview_rows),
                use_container_width=True,
                height=400
            )


        # ----------------------------------------------------
        # TAB 2 - COLUMNS
        # ----------------------------------------------------

        with tab2:

            st.subheader("Column Information")

            column_info = pd.DataFrame({

                "Column": df.columns,

                "Data Type": [
                    str(dtype)
                    for dtype in df.dtypes
                ],

                "Non-Null Values": [
                    df[col].notna().sum()
                    for col in df.columns
                ],

                "Null Values": [
                    df[col].isna().sum()
                    for col in df.columns
                ]

            })

            st.dataframe(
                column_info,
                use_container_width=True,
                height=400
            )


        # ----------------------------------------------------
        # TAB 3 - DATA TYPES
        # ----------------------------------------------------

        with tab3:

            st.subheader("Data Type Summary")

            dtype_summary = (
                df.dtypes
                .astype(str)
                .value_counts()
                .reset_index()
            )

            dtype_summary.columns = [
                "Data Type",
                "Number of Columns"
            ]

            st.dataframe(
                dtype_summary,
                use_container_width=True
            )


        # ====================================================
        # PROCESSING SUMMARY
        # ====================================================

        st.markdown("---")

        st.markdown(
            '<div class="section-title">✅ Processing Summary</div>',
            unsafe_allow_html=True
        )

        summary_col1, summary_col2 = st.columns(2)

        with summary_col1:

            st.write(
                "**File Type:**",
                file_extension.upper()
            )

            st.write(
                "**Output Format:**",
                "Parquet"
            )

            st.write(
                "**Compression:**",
                "Snappy"
            )

        with summary_col2:

            if "Date" in df.columns:

                st.write(
                    "📅 Date column converted to DD-MM-YYYY"
                )

            if converted_columns:

                st.write(
                    "🔢 Numeric columns converted:"
                )

                st.write(
                    ", ".join(converted_columns)
                )


    except Exception as e:

        st.error(
            f"❌ Error while processing the file: {str(e)}"
        )


else:

    # ========================================================
    # EMPTY STATE
    # ========================================================

    st.info(
        "👆 Upload a CSV or Excel file above to get started."
    )

    st.markdown("### How it works")

    step1, step2, step3 = st.columns(3)

    with step1:

        st.markdown(
            """
            ### 1️⃣ Upload

            Upload your `.csv` or `.xlsx` file.
            """
        )

    with step2:

        st.markdown(
            """
            ### 2️⃣ Process

            The tool automatically cleans and converts your data.
            """
        )

    with step3:

        st.markdown(
            """
            ### 3️⃣ Download

            Download the optimized `.parquet` file.
            """
        )
