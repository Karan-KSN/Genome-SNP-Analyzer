import streamlit as st
import requests
import tempfile
import os
import re
from cyvcf2 import VCF

def convert_gdrive_link(url):
    """Converts a standard GDrive share link to a direct download link."""
    if "drive.google.com" in url:
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        if match:
            file_id = match.group(1)
            return f"https://drive.google.com/uc?export=download&id={file_id}"
    return url

def parse_remote_genome(vcf_url, tbi_url, region="chr2:135787840-135837170"):
    # 1. Convert Links
    vcf_direct = convert_gdrive_link(vcf_url)
    tbi_direct = convert_gdrive_link(tbi_url)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            vcf_path = os.path.join(tmpdir, "remote.vcf.gz")
            tbi_path = os.path.join(tmpdir, "remote.vcf.gz.tbi")

            # 2. Download with high-speed streaming
            def download_file(url, dest):
                r = requests.get(url, stream=True, timeout=30)
                r.raise_for_status()
                with open(dest, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024*1024):
                        f.write(chunk)
            
            download_file(vcf_direct, vcf_path)
            download_file(tbi_direct, tbi_path)

            # 3. Initialize Engine
            vcf = VCF(vcf_path)
            results = []

            # 4. Query the region
            for variant in vcf(region):
                results.append({
                    "RSID": variant.ID if variant.ID != "." else f"chr{variant.CHROM}:{variant.POS}",
                    "Chr": variant.CHROM,
                    "Pos": variant.POS,
                    "Genotype": variant.gt_bases[0] if variant.gt_bases else "./."
                })
            
            if not results:
                return f"No variants found in {region}. Check prefix or gene presence."
            
            return results

    except Exception as e:
        return f"Bioinformatics Engine Error: {str(e)}"

# --- THIS MUST BE AT THE LEFT MARGIN ---
def fetch_snp_wisdom(rsid):
    """
    Connects to MyVariant.info to fetch clinical significance for your PhD.
    """
    try:
        if "rs" not in str(rsid).lower():
            return "Custom Coordinate: Clinical data not available in SNP database."
            
        url = f"https://myvariant.info/v1/variant/{rsid}"
        res = requests.get(url, timeout=5).json()
        
        clinvar = res.get('clinvar', {})
        if isinstance(clinvar, list): 
            clinvar = clinvar[0]
            
        significance = clinvar.get('rcv', [{}])[0].get('clinical_significance', 'No Data Found')
        return significance
    except Exception:
        return "SNP Database Timeout or No Clinical Data"
