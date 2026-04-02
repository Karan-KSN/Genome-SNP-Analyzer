import streamlit as st
import logic
import pandas as pd

st.set_page_config(page_title="The Iron Primer", page_icon="🧬")

st.title("🧬 The Iron Primer")
st.caption("Nutrigenetics Analysis Portal | Ph.D. Candidate Project")

# The 'Ease of Access' Input
vcf_url = st.text_input("Paste Genome Direct Link", placeholder="https://dropbox.com/s/sample.vcf.gz?dl=1")
target = st.text_input("Target Region", "17:63477061-63500000") # ACE gene focus

if st.button("Analyze Now", type="primary", use_container_width=True):
    with st.spinner("Streaming data from cloud..."):
        data = logic.parse_remote_genome(vcf_url, target)
        
        if isinstance(data, list) and len(data) > 0:
            for snp in data:
                snp['Significance'] = logic.fetch_snp_wisdom(snp['RSID'])
            
            st.success("Analysis Complete!")
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.error("Check your link. Ensure the .tbi index is in the same folder as the .vcf.gz.")
