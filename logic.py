import streamlit as st
import requests
import tempfile
import os
import re
from cyvcf2 import VCF

def get_confirm_token(response):
    """Extracts the Google Drive virus scan confirmation token."""
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def download_large_file(url, dest):
    """Universal downloader for GitHub or GDrive."""
    session = requests.Session()
    # Try GDrive logic first
    if "drive.google.com" in url or "docs.google.com" in url:
        file_id = re.search(r'/d/([a-zA-Z0-9-_]+)', url).group(1)
        download_url = "https://docs.google.com/uc?export=download"
        response = session.get(download_url, params={'id': file_id}, stream=True)
        token = get_confirm_token(response)
        if token:
            response = session.get(download_url, params={'id': file_id, 'confirm': token}, stream=True)
    else:
        # Standard GitHub/Direct link logic
        response = session.get(url, stream=True, timeout=30)
    
    response.raise_for_status()
    with open(dest, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
    
    # First attempt to get the token
    response = session.get(url, params={'id': file_id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(url, params=params, stream=True)
    
    response.raise_for_status()
    with open(dest, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)

def parse_remote_genome(vcf_url, tbi_url, region="chr2:135787840-135837170"):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            vcf_path = os.path.join(tmpdir, "remote.vcf.gz")
            tbi_path = os.path.join(tmpdir, "remote.vcf.gz.tbi")
            for variant in vcf(region):
                # Clean up the RSID logic
                raw_id = variant.ID if variant.ID and variant.ID != "." else None
                display_id = raw_id if raw_id else f"chr{variant.CHROM}:{variant.POS}"
                
                results.append({
                    "RSID": display_id,
                    "Chr": variant.CHROM,
                    "Pos": variant.POS,
                    "Genotype": variant.gt_bases[0] if variant.gt_bases else "./."
                })

            # UNIVERSAL DOWNLOADER
            def download_universal(url, dest):
                session = requests.Session()
                # Check if it's Google Drive
                if "drive.google.com" in url or "docs.google.com" in url:
                    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
                    if not match: raise ValueError("Invalid GDrive Link")
                    file_id = match.group(1)
                    confirm_url = "https://docs.google.com/uc?export=download"
                    res = session.get(confirm_url, params={'id': file_id}, stream=True)
                    token = get_confirm_token(res)
                    if token:
                        res = session.get(confirm_url, params={'id': file_id, 'confirm': token}, stream=True)
                else:
                    # It's a Direct Link (GitHub)
                    res = session.get(url, stream=True, timeout=30)
                
                res.raise_for_status()
                with open(dest, 'wb') as f:
                    for chunk in res.iter_content(chunk_size=1024*1024):
                        if chunk: f.write(chunk)

            # Execution
            download_universal(vcf_url, vcf_path)
            download_universal(tbi_url, tbi_path)

            # Initialize VCF engine
            vcf = VCF(vcf_path)
            results = []
            for variant in vcf(region):
                results.append({
                    "RSID": variant.ID if variant.ID != "." else f"chr{variant.CHROM}:{variant.POS}",
                    "Chr": variant.CHROM,
                    "Pos": variant.POS,
                    "Genotype": variant.gt_bases[0] if variant.gt_bases else "./."
                })
            
            return results if results else f"No variants found in {region}."

    except Exception as e:
        return f"Bioinformatics Engine Error: {str(e)}"

def fetch_snp_wisdom(rsid):
    try:
        if "rs" not in str(rsid).lower():
            return "Custom Coordinate: Clinical data not available."
        url = f"https://myvariant.info/v1/variant/{rsid}"
        res = requests.get(url, timeout=5).json()
        clinvar = res.get('clinvar', {})
        if isinstance(clinvar, list): clinvar = clinvar[0]
        return clinvar.get('rcv', [{}])[0].get('clinical_significance', 'No Data Found')
    except:
        return "SNP Database Timeout"
