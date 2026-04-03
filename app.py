import streamlit as st
import os

st.title("🧬 Personal Nutrigenetics Risk Analyzer")
st.markdown("### Upload your genetic data to discover your unique risks.")

# User-Friendly File Uploaders
uploaded_vcf = st.file_uploader("Upload your VCF (.gz)", type=["gz"])
uploaded_tbi = st.file_uploader("Upload your Index (.tbi)", type=["tbi"])

import streamlit as st
import os
from logic import parse_remote_genome, fetch_snp_wisdom, generate_pdf_report

st.title("🧬 Personal Nutrigenetics Risk Analyzer")
st.markdown("### Upload your genetic data to discover your unique risks.")

# 1. User-Friendly File Uploaders
uploaded_vcf = st.file_uploader("Upload your VCF (.gz)", type=["gz"])
uploaded_tbi = st.file_uploader("Upload your Index (.tbi)", type=["tbi"])

if uploaded_vcf and uploaded_tbi:
    # Save the uploaded files to the /tmp directory so cyvcf2 can read them locally
    vcf_path = "temp_user.vcf.gz"
    tbi_path = "temp_user.vcf.gz.tbi"
    
    with open(vcf_path, "wb") as f:
        f.write(uploaded_vcf.getbuffer())
    with open(tbi_path, "wb") as f:
        f.write(uploaded_tbi.getbuffer())
        
    st.success("Data Loaded! Now, pick your focus area.")
    
    # 2. The Gene Dropdown Menu
    GENE_MAP = {
        "ACE (Endurance & Hypertension Risk)": "chr17:63477061-63500000",
        "MTHFR (Folate & DNA Repair)": "chr1:11785729-11785731",
        "CYP1A2 (Caffeine Metabolism Speed)": "chr15:74719543-74750000",
        "LCT (Lactose Tolerance)": "chr2:135787840-135837170"
    }

    selected_label = st.selectbox("Which gene would you like to analyze?", list(GENE_MAP.keys()))
    target_region = GENE_MAP[selected_label]

    # 3. Execution Button
    if st.button("Generate My Risk Profile"):
        with st.spinner(f"Analyzing {selected_label}..."):
            # Note: We pass the LOCAL file paths now, not URLs
            results = parse_remote_genome(vcf_path, tbi_path, target_region)
            
            if isinstance(results, str):
                st.error(results)
            else:
                st.success(f"Found {len(results)} variants in the {selected_label} region!")
                st.table(results)
                
                # 4. PDF Generation
                pdf_bytes = generate_pdf_report(results)
                st.download_button(
                    label="📥 Download My Clinical PDF Report",
                    data=pdf_bytes,
                    file_name="My_Nutrigenetics_Report.pdf",
                    mime="application/pdf"
                )
