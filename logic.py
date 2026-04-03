import os
import requests
from cyvcf2 import VCF
from fpdf import FPDF

def parse_remote_genome(vcf_path, tbi_path, region):
    """
    Bioinformatics Engine: Processes local files saved in the /tmp directory.
    Uses Tabix-indexing for sub-second random access of large genomic files.
    """
    try:
        if not os.path.exists(vcf_path):
            return f"Error: VCF file not found at {vcf_path}"
        
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
    """
    Clinical Annotation: Connects to MyVariant.info to fetch 
    ClinVar significance for the user's report.
    """
    try:
        if "rs" not in str(rsid).lower():
            return "Custom Coordinate: Specific clinical data not in SNP database."
            
        url = f"https://myvariant.info/v1/variant/{rsid}"
        res = requests.get(url, timeout=5).json()
        
        clinvar = res.get('clinvar', {})
        if isinstance(clinvar, list): clinvar = clinvar[0]
            
        significance = clinvar.get('rcv', [{}])[0].get('clinical_significance', 'No Data Found')
        return significance
    except:
        return "SNP Database Timeout or No Clinical Data"

def generate_pdf_report(results):
    """
    Reporting Engine: Generates a professional PDF for the user's records.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(200, 10, txt="Nutrigenetics Analysis Report", ln=True, align='C')
    pdf.ln(10)
    
    # Table Content
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(60, 10, "RSID", 1)
    pdf.cell(40, 10, "Genotype", 1)
    pdf.cell(90, 10, "Interpretation", 1, 1)
    
    pdf.set_font("Arial", size=9)
    for row in results:
        wisdom = fetch_snp_wisdom(row['RSID'])
        pdf.cell(60, 10, str(row['RSID']), 1)
        pdf.cell(40, 10, str(row['Genotype']), 1)
        pdf.multi_cell(90, 10, str(wisdom), 1)
        
    return pdf.output(dest='S')
