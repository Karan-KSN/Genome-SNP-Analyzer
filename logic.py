import streamlit as st
import os
from cyvcf2 import VCF

def parse_remote_genome(vcf_path, tbi_path, region="chr2:135787840-135837170"):
    """
    Bioinformatics Engine: Direct Local Processing.
    Accepts local file paths created by the Streamlit uploader.
    """
    try:
        # 1. Verification: Ensure the files actually exist in /tmp
        if not os.path.exists(vcf_path) or not os.path.exists(tbi_path):
            return "Error: Local genomic files not found. Please re-upload."

        # 2. Initialize Engine directly from the file path
        # No 'requests.get' needed here!
        vcf = VCF(vcf_path)
        results = []

        # 3. Query the region
        for variant in vcf(region):
            results.append({
                "RSID": variant.ID if variant.ID != "." else f"chr{variant.CHROM}:{variant.POS}",
                "Chr": variant.CHROM,
                "Pos": variant.POS,
                "Genotype": variant.gt_bases[0] if variant.gt_bases else "./."
            })
        
        if not results:
            return f"No variants found in {region}. The user might be Wild Type (Reference) here."
        
        return results

    except Exception as e:
        # This will catch things like 'index file not found' or 'invalid vcf'
        return f"Bioinformatics Engine Error: {str(e)}"
