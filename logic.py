import streamlit as st
import requests
import tempfile
import os
from cyvcf2 import VCF

def parse_remote_genome(vcf_url, tbi_url, region="17:63477061-63500000"):
    """
    Ph.D. Grade Streaming Logic:
    Uses a temporary local buffer to bypass GitHub redirect/header issues.
    """
    try:
        # 1. Create a temporary directory that Streamlit will clean up later
        with tempfile.TemporaryDirectory() as tmpdir:
            vcf_path = os.path.join(tmpdir, "remote.vcf.gz")
            tbi_path = os.path.join(tmpdir, "remote.vcf.gz.tbi")

            # 2. Use 'requests' to stream the files into the temp buffer
            # This handles the GitHub -> Amazon S3 redirect automatically
            def download_file(url, dest):
                r = requests.get(url, stream=True, timeout=15)
                r.raise_for_status()
                with open(dest, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            download_file(vcf_url, vcf_path)
            download_file(tbi_url, tbi_path)

            # 3. Now the engine reads from the local 'temp' path
            vcf = VCF(vcf_path) # It finds the .tbi automatically now
            
            results = []
            for variant in vcf(region):
                if variant.ID and "rs" in variant.ID:
                    results.append({
                        "RSID": variant.ID,
                        "Chr": variant.CHROM,
                        "Pos": variant.POS,
                        "Genotype": variant.gt_bases[0]
                    })
            return results
    except Exception as e:
        return f"Bioinformatics Engine Error: {str(e)}"
