import streamlit as st
from logic import parse_remote_genome, fetch_snp_wisdom

st.set_page_config(page_title="The Iron Primer: Genomic Analyzer", page_icon="🧬")

st.title("🧬 Genomic SNP Analyzer")
st.markdown("---")

# 1. Inputs
vcf_link = st.text_input("Enter VCF Link (.vcf.gz)")
tbi_link = st.text_input("Enter Index Link (.vcf.gz.tbi)")
region = st.text_input("Enter Genomic Region (e.g., chr2:135787840-135837170)", value="chr2:135787840-135837170")

if st.button("Analyze Genotype"):
    if vcf_link and tbi_link:
        with st.spinner("Streaming & Indexing 1.1 GB Data..."):
            # Call your logic.py function
            results = parse_remote_genome(vcf_link, tbi_link, region)
            
            # 2. Check if results is a string (Error) or a list (Success)
            if isinstance(results, str):
                st.error(results)
            else:
                st.success(f"Found {len(results)} variants in this region!")
                
                # 3. Display the Table
                st.table(results)
                
                # 4. Deep Dive into the first SNP for wisdom
                if results:
                    first_rsid = results[0]['RSID']
                    st.info(f"Clinical Wisdom for {first_rsid}: {fetch_snp_wisdom(first_rsid)}")
    else:
        st.warning("Please provide both the VCF and TBI links.")
