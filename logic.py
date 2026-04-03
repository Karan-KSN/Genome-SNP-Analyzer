import os
import requests
from cyvcf2 import VCF
from fpdf import FPDF

def parse_remote_genome(vcf_path, tbi_path, region):
    """
    Bioinformatics Engine: Direct Local Processing.
    Includes a 'Safety Check' to ensure the 1.1 GB file is readable.
    """
    try:
        # 1. Initialize Engine
        if not os.path.exists(vcf_path):
            return f"Error: VCF file not found at {vcf_path}"
        
        vcf = VCF(vcf_path)
        
        # 2. Safety Check (The Chunk)
        try:
            test_vcf = VCF(vcf_path)
            next(test_vcf()) # Peeks at the first variant
        except StopIteration:
            return "Error: The uploaded VCF appears to be empty or contains no mutations."
        except Exception as e:
            return f"VCF Format Error: {str(e)}"

        results = []
        
        # 3. Regional Scan
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
    """Clinical Annotation for the PhD/Portfolio."""
    try:
        if "rs" not in str(rsid).lower():
            return "Custom Coordinate: Clinical data not in database."
        url = f"https://myvariant.info/v1/variant/{rsid}"
        res = requests.get(url, timeout=5).json()
        clinvar = res.get('clinvar', {})
        if isinstance(clinvar, list): clinvar = clinvar[0]
        return clinvar.get('rcv', [{}])[0].get('clinical_significance', 'No Data Found')
    except:
        return "SNP Database Timeout"

def generate_pdf_report(results):
    """Reporting Engine for the final portfolio piece."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Nutrigenetics Analysis Report", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    for row in results:
        pdf.ln(5)
        pdf.cell(0, 10, f"RSID: {row['RSID']} | Genotype: {row['Genotype']}", ln=True)
    return bytes(pdf.output())
