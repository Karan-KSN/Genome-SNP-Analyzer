import streamlit as st
import os
from logic import parse_remote_genome, generate_pdf_report

st.set_page_config(page_title="Iron Primer: Clinical Analyzer", page_icon="🧬")
st.title("🧬 Targeted Nutrigenetics Analyzer")
st.markdown("---")

uploaded_vcf = st.file_uploader("Upload VCF (.gz)", type=["gz"], key="vcf_target")
uploaded_tbi = st.file_uploader("Upload Index (.tbi)", type=["tbi"], key="tbi_target")

if uploaded_vcf and uploaded_tbi:
    vcf_path, tbi_path = "temp.vcf.gz", "temp.vcf.gz.tbi"
    with open(vcf_path, "wb") as f:
        f.write(uploaded_vcf.getbuffer())
        os.fsync(f.fileno())
    with open(tbi_path, "wb") as f:
        f.write(uploaded_tbi.getbuffer())
        os.fsync(f.fileno())
        
    st.success("✅ Genomic Data Synced.")
    
    # EXACT GRCh38 Loci Windows
    GENE_MAP = {
        "ACE (Endurance/Hypertension)": "chr17:63488000-63489000", 
        "MTHFR (Folate/Energy)": "chr1:11796000-11797000",   
        "LCT (Lactose Tolerance)": "chr2:135850000-135852000",
        "CYP1A2 (Caffeine Metabolism)": "chr15:74749000-74750000"
    }
    selected = st.selectbox("Select Target Gene Panel:", list(GENE_MAP.keys()))
    
    if st.button("Execute Targeted Panel Scan"):
        with st.spinner(f"Scanning precise locus for {selected.split(' ')[0]}..."):
            results = parse_remote_genome(vcf_path, tbi_path, GENE_MAP[selected])
            if isinstance(results, str):
                st.info(results)
            else:
                st.table(results)
                pdf_bytes = generate_pdf_report(results)
                st.download_button("📥 Download Clinical Panel Report", data=pdf_bytes, file_name="Targeted_Panel_Report.pdf")
