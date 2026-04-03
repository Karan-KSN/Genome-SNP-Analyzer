import streamlit as st
import os

st.title("🧬 Personal Nutrigenetics Risk Analyzer")
st.markdown("### Upload your genetic data to discover your unique risks.")

# User-Friendly File Uploaders
uploaded_vcf = st.file_uploader("Upload your VCF (.gz)", type=["gz"])
uploaded_tbi = st.file_uploader("Upload your Index (.tbi)", type=["tbi"])

if uploaded_vcf and uploaded_tbi:
    # Save the uploaded files to the /tmp directory so cyvcf2 can read them
    with open("temp_user.vcf.gz", "wb") as f:
        f.write(uploaded_vcf.getbuffer())
    with open("temp_user.vcf.gz.tbi", "wb") as f:
        f.write(uploaded_tbi.getbuffer())
        
    st.success("Data Loaded! Select your Gene of Interest below.")
