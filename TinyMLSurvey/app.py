import streamlit as st
import pandas as pd
import os

# Page configuration
st.set_page_config(
    page_title="TinyML Corpus Explorer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling - FIXED parameter name here
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    /* Making metric cards look like professional dashboard tiles */
    [data-testid="stMetricValue"] { font-size: 28px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    if os.path.exists('papers_master.xlsx'):
        df = pd.read_excel('papers_master.xlsx')
    elif os.path.exists('papers_master.csv'):
        df = pd.read_csv('papers_master.csv')
    else:
        return None
    
    # Standardize data
    if 'include_core' in df.columns:
        df['include_core'] = df['include_core'].astype(str).str.strip().str.title()
    return df

def main():
    st.title("🔬 TinyML Systematic Review: Interactive Companion")
    st.markdown("---")

    df_raw = load_data()
    if df_raw is None:
        st.error("⚠️ Data file not found. Please ensure 'papers_master.xlsx' is in the folder.")
        return

    # Filter only Core Corpus (104 papers) for the explorer
    # Using the standardized inclusion labels from your project [cite: 1]
    df = df_raw[df_raw['include_core'].str.contains('Yes|In|Maybe', case=False, na=False)].copy()

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("🎯 Filter Corpus")
    
    with st.sidebar:
        search = st.text_input("🔍 Search by Title or Author")
        
        platforms = st.multiselect("Hardware Platform", 
                                   options=sorted(df['platform_class'].dropna().unique()),
                                   default=df['platform_class'].dropna().unique())
        
        domains = st.multiselect("IoT Domain", 
                                 options=sorted(df['iot_subdomain'].dropna().unique()),
                                 default=df['iot_subdomain'].dropna().unique())
        
        # Simple checkbox for open source
        show_only_code = st.checkbox("Only show papers with available code")

    # Apply Filtering Logic
    mask = (df['platform_class'].isin(platforms) | df['platform_class'].isna()) & \
       (df['iot_subdomain'].isin(domains) | df['iot_subdomain'].isna())

    if search:
        # Use na=False for the search string mask to avoid errors with empty cells
        mask = mask & (df['title'].str.contains(search, case=False, na=False) | 
                    df['authors'].str.contains(search, case=False, na=False))

    if show_only_code:
        mask = mask & (df['code_available'].astype(str).str.contains('Yes', case=False, na=False))

    filtered_df = df[mask]

    # --- MAIN LAYOUT TABS ---
    tab1, tab2, tab3 = st.tabs(["📊 Study Statistics", "🔍 Corpus Explorer", "📑 Search Documentation"])

    with tab1:
        st.header("Manuscript Statistical Artifacts")
        
        # KPI Cards based on your finalized manuscript data [cite: 1]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Core Corpus", "104 Papers")
        col2.metric("Real-World Eval", "56.7%")
        col3.metric("Energy Reporting", "38.5%")
        col4.metric("Agreement Rate", "92.7%")

        st.markdown("### 🗺️ System Taxonomy")
        # Ensure you saved the taxonomy figure as a PNG in your generate_artifacts script!
        if os.path.exists('fig_class_distribution.png'):
            st.image('fig_class_distribution.png', use_container_width=True, caption="Figure 2: Distribution of Core Papers by Taxonomy Class")
        else:
            st.info("💡 Run your 'generate_artifacts.py' script first to generate the 'fig_class_distribution.png' file.")

        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("### 📋 PRISMA Study Flow")
            if os.path.exists('table_prisma_flow.csv'):
                prisma = pd.read_csv('table_prisma_flow.csv')
                st.table(prisma)
            else:
                st.write("PRISMA CSV table data not found.")

        with col_right:
            st.markdown("### 📉 Reporting Gaps (Table 14)")
            if os.path.exists('table_14_reporting_gaps.csv'):
                gaps = pd.read_csv('table_14_reporting_gaps.csv')
                st.dataframe(gaps, use_container_width=True, hide_index=True)
            else:
                st.write("Reporting Gaps CSV table data not found.")

    with tab2:
        st.header("Searchable Database")
        st.write(f"Showing **{len(filtered_df)}** papers matching your current filters.")
        
        # Display clean view of the papers master
        display_cols = ['paper_id', 'title', 'authors', 'year', 'platform_class', 'iot_subdomain', 'task_primary', 'metrics_latency_ms', 'metrics_energy_mj']
        valid_cols = [c for c in display_cols if c in filtered_df.columns]
        
        st.dataframe(filtered_df[valid_cols].sort_values('year', ascending=False), use_container_width=True, hide_index=True)

        # Download Button for the filtered view
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Filtered Results as CSV", csv, "filtered_tinyml_corpus.csv", "text/csv")

    with tab3:
        st.header("Data Dictionary & Scope")
        st.markdown("""
        **Project Scope:** This systematic review synthesizes 104 core studies on TinyML deployments on MCU-class hardware (Cortex-M, ESP32, RISC-V) published between 2020 and 2026.
        
        **Taxonomy Class Definitions:**
        - **C01:** Wearable & IMU sensing (23 papers) 
        - **C02:** Audio & Acoustic systems (17 papers) 
        - **C03:** Urban & Outdoor distributed sensing (21 papers) 
        - **C04:** Industrial vibration & Anomaly detection (19 papers) 
        - **C05:** Indoor context-aware IoT (17 papers) 
        - **C06:** Benchmarking & Evaluation frameworks (16 papers) 
        """)

if __name__ == "__main__":
    main()