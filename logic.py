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
from fpdf import FPDF
import io

def generate_pdf_report(results):
    """
    Generates a professional Nutrigenetics PDF report.
    This is the 'Executive Summary' for the user.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # 1. Header & Branding
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(30, 70, 140) # Professional Deep Blue
    pdf.cell(200, 15, txt="Nutrigenetics Analysis Report", ln=True, align='C')
    
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(200, 10, txt="Powered by The Iron Primer Bioinformatics Engine", ln=True, align='C')
    pdf.ln(10)
    
    # 2. Results Table
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.set_text_color(0, 0, 0)
    
    # Table Column Headers
    pdf.cell(60, 10, "RSID / Coordinate", 1, 0, 'C', True)
    pdf.cell(40, 10, "Chr", 1, 0, 'C', True)
    pdf.cell(40, 10, "Pos", 1, 0, 'C', True)
    pdf.cell(50, 10, "Genotype", 1, 1, 'C', True)
    
    # Table Data Rows
    pdf.set_font("Arial", size=10)
    for row in results:
        pdf.cell(60, 10, str(row['RSID']), 1)
        pdf.cell(40, 10, str(row['Chr']), 1)
        pdf.cell(40, 10, str(row['Pos']), 1)
        pdf.cell(50, 10, str(row['Genotype']), 1, 1, 'C')
        
    # 3. Footer & Legal
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, "Scientific Interpretation:", ln=True)
    pdf.set_font("Arial", size=9)
    pdf.multi_cell(0, 5, "This report identifies specific genetic variants. Clinical significance is based on the MyVariant.info database and relevant literature (e.g., Rigat et al., 1990 for ACE; Sayed-Tabatabaei et al., 2006).")
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 5, "DISCLAIMER: For research use only. This is not a clinical diagnostic tool. Consult a certified genetic counselor for medical advice.")

    # Return as bytes for Streamlit
    return pdf.output(dest='S')
