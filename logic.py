import os
import requests
from cyvcf2 import VCF
from fpdf import FPDF

def parse_remote_genome(vcf_path, tbi_path, region):
    """
    Bioinformatics Engine: Direct Local Processing.
    Fixes the 'chrchr' prefix and prioritizes the RSID Registry.
    """
    try:
        if not os.path.exists(vcf_path):
            return f"Error: VCF file not found at {vcf_path}"
        
        vcf = VCF(vcf_path)
        
        # 1. Safety Check
        try:
            test_vcf = VCF(vcf_path)
            next(test_vcf()) 
        except StopIteration:
            return "Error: The uploaded VCF appears to be empty."
        except Exception as e:
            return f"VCF Format Error: {str(e)}"

        # 2. Master Registry (GRCh38)
        NUTRIGENETICS_REGISTRY = {
            63477061: "rs4646994 (ACE)",
            11785729: "rs1801133 (MTHFR)",
            74749576: "rs762551 (CYP1A2)",
            135837170: "rs4988235 (LCT)"
        }

        results = []
        
        # 3. Regional Scan
        for variant in vcf(region):
            pos = int(variant.POS)
            file_id = str(variant.ID) if variant.ID else "."
            
            # IDENTITY LOGIC: Prioritize Registry -> File ID -> Coordinate
            if pos in NUTRIGENETICS_REGISTRY:
                final_id = NUTRIGENETICS_REGISTRY[pos]
            elif file_id not in [".", "None", "nan", ""]:
                final_id = file_id
            else:
                # FIX: Removed manual 'chr' to prevent 'chrchr'
                final_id = f"{variant.CHROM}:{pos}"

            results.append({
                "RSID": final_id,
                "Chr": variant.CHROM,
                "Pos": pos,
                "Genotype": variant.gt_bases[0] if variant.gt_bases else "./."
            })
            
        return results if results else f"No variants found in {region}."

    except Exception as e:
        return f"Bioinformatics Engine Error: {str(e)}"

def fetch_snp_wisdom(rsid):
    """
    Clinical Annotation: Resolves both RSIDs and Coordinates via MyVariant.info.
    Essential for PhD-level Nutrigenetics reporting.
    """
    try:
        clean_id = str(rsid).split(" ")[0].lower()
        
        # If it is a coordinate, format it as chrom:g.pos for the API
        if ":" in clean_id:
            chrom, pos = clean_id.split(":")
            api_query = f"{chrom}:g.{pos}"
        else:
            api_query = clean_id

        url = f"https://myvariant.info/v1/variant/{api_query}"
        res = requests.get(url, timeout=5).json()
        
        clinvar = res.get('clinvar', {})
        if isinstance(clinvar, list): 
            clinvar = clinvar[0]
        
        # Pull clinical significance or provide a professional fallback
        rcv = clinvar.get('rcv', [{}])
        if isinstance(rcv, list) and len(rcv) > 0:
            significance = rcv[0].get('clinical_significance', 'Likely Benign/VUS')
        else:
            significance = 'Unannotated / Common Variation'
            
        return significance
    except:
        return "Clinical Database Offline or No Record Found"

def generate_pdf_report(results):
    """Reporting Engine: Creates the final PDF bytes for the download button."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Nutrigenetics Analysis Report", ln=True, align='C')
    
    pdf.set_font("Arial", size=10)
    for row in results:
        pdf.ln(5)
        # We call fetch_snp_wisdom during PDF generation to populate data
        wisdom = fetch_snp_wisdom(row['RSID'])
        pdf.multi_cell(0, 10, f"RSID: {row['RSID']} | Genotype: {row['Genotype']}\nInterpretation: {wisdom}", border=1)
        
    return bytes(pdf.output())
