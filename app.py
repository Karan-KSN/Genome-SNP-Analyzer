import streamlit as st
import logic
import pandas as pd

st.set_page_config(page_title="The Iron Primer", page_icon="🧬")

st.title("🧬 The Iron Primer")
st.info("Ph.D. Research Tool: Gene-Lifestyle Interaction Analysis")

# Instructions for the User
with st.expander("How to get Google Drive Links?"):
    st.write("1. Upload `.vcf.gz` and `.vcf.gz.tbi` to Google Drive.")
    st.write("2. Right-click each -> Share -> Change to 'Anyone with the link'.")
    st.write("3. Copy and paste both links below.")

# The Two-Input System
vcf_link = st.text_input("Paste Genome Link (.vcf.gz)")
tbi_link = st.text_input("Paste Index Link (.tbi)")

target = st.text_input("Target Region", "17:63477061-63500000")

if st.button("Analyze ACE Gene", type="primary"):
    if vcf_link and tbi_link:
        with st.spinner("Streaming from Google Drive..."):
            data = logic.parse_remote_genome(vcf_link, tbi_link, target)
            
            if isinstance(data, list):
                # Add Significance (logic.fetch_snp_wisdom)
                for snp in data:
                    snp['Significance'] = logic.fetch_snp_wisdom(snp['RSID'])
                
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
            else:
                st.error(data)
    else:
        st.warning("Please provide both the VCF and the Index links.")
