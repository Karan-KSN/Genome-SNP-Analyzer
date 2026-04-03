import streamlit as st
import os
from logic import parse_remote_genome, generate_pdf_report

st.set_page_config(page_title="Iron Primer: Clinical Analyzer", page_icon="🧬")
st.title("🧬 High-Impact Nutrigenetics Analyzer")
st.markdown("---")

uploaded_vcf = st.file_uploader("Upload VCF (.gz)", type=["gz"], key="vcf_v5")
uploaded_tbi = st.file_uploader("Upload Index (.tbi)", type=["tbi"], key="tbi_v5")

if uploaded_vcf and uploaded_tbi:
    vcf_path, tbi_path = "temp.vcf.gz", "temp.vcf.gz.tbi"
    with open(vcf_path, "wb") as f:
        f.write(uploaded_vcf.getbuffer())
        os.fsync(f.fileno())
    with open(tbi_path, "wb") as f:
        f.write(uploaded_tbi.getbuffer())
        os.fsync(f.fileno())
        
    st.success("✅ Ready for High-Impact Scan.")
    GENE_MAP = {
        "ACE (Endurance)": "chr17:63470000-63600000",
        "MTHFR (Folate)": "chr1:11780000-11800000",
        "LCT (Lactose)": "chr2:135700000-135840000",
        "CYP1A2 (Caffeine)": "chr15:74700000-74800000"
    }
    selected = st.selectbox("Gene Selection:", list(GENE_MAP.keys()))
    
    if st.button("Filter & Analyze"):
        with st.spinner("Extracting High-Impact Variants..."):
            results = parse_remote_genome(vcf_path, tbi_path, GENE_MAP[selected])
            if isinstance(results, str):
                st.warning(results)
            else:
                st.table(results)
                pdf_bytes = generate_pdf_report(results)
                st.download_button("📥 Download Filtered Report", data=pdf_bytes, file_name="High_Impact_Report.pdf")
