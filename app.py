import streamlit as st
import os
from logic import parse_remote_genome, fetch_snp_wisdom, generate_pdf_report

# Set page config for a professional look
st.set_page_config(page_title="Iron Primer: Genomic Risk", page_icon="🧬")

st.title("🧬 Personal Nutrigenetics Risk Analyzer")
st.markdown("### Upload your genetic data to discover your unique risks.")

# 1. User-Friendly File Uploaders (With Unique Keys to fix Duplicate ID error)
uploaded_vcf = st.file_uploader(
    "Upload your Genomic VCF (.gz)", 
    type=["gz"], 
    key="vcf_main"
)
uploaded_tbi = st.file_uploader(
    "Upload your Index (.tbi)", 
    type=["tbi"], 
    key="tbi_main"
)

if uploaded_vcf and uploaded_tbi:
    # Save to local /tmp directory
    vcf_path = "temp_user.vcf.gz"
    tbi_path = "temp_user.vcf.gz.tbi"
    
    with open(vcf_path, "wb") as f:
        f.write(uploaded_vcf.getbuffer())
        f.flush()
        os.fsync(f.fileno()) # Forces the OS to write the bits to the disk immediately
    with open(tbi_path, "wb") as f:
        f.write(uploaded_tbi.getbuffer())
        
    st.success("✅ Genetic Data Streamed Successfully!")
    
    # 2. Gene Selection Menu
    GENE_MAP = {
        "ACE (Broad Scan)": "chr17:63470000-63600000", # 130kb window
        "MTHFR (Broad Scan)": "chr1:11780000-11800000", # 20kb window
        "LCT (Broad Scan)": "chr2:135700000-135900000", # 200kb window
        "Caffeine (Broad Scan)": "chr15:74700000-74800000" # 100kb window
    }

    selected_label = st.selectbox("Which gene would you like to analyze?", list(GENE_MAP.keys()))
    target_region = GENE_MAP[selected_label]

    # 3. Execution
    if st.button("Generate My Risk Profile"):
        with st.spinner(f"Scanning {selected_label} locus..."):
            results = parse_remote_genome(vcf_path, tbi_path, target_region)
            
            if isinstance(results, str):
                st.error(results)
            else:
                st.success(f"Found {len(results)} variants!")
                st.table(results)
                
                # 4. Clinical PDF Generation
                pdf_bytes = generate_pdf_report(results)
                st.download_button(
                    label="📥 Download My Clinical PDF Report",
                    data=pdf_bytes,
                    file_name=f"{selected_label}_Risk_Report.pdf",
                    mime="application/pdf"
                )
