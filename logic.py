import os
import requests
from cyvcf2 import VCF
from fpdf import FPDF

def parse_remote_genome(vcf_path, tbi_path, region):
    """
    Bioinformatics Engine: Optimized for ClinVar and GIAB datasets.
    Handles 'Site-Only' VCFs by providing a fallback for genotypes.
    """
    try:
        if not os.path.exists(vcf_path):
            return f"Error: VCF file not found at {vcf_path}"
        
        vcf = VCF(vcf_path)
        
        # 1. Safety Check: Verify file readability
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
                final_id = f"{variant.CHROM}:{pos}"

            # GENOTYPE LOGIC: Safe extraction for ClinVar (which may have 0 samples)
            try:
                # If sample data exists (GIAB), get it. Otherwise, show Ref/Alt for ClinVar.
                if len(vcf.samples) > 0:
                    gt = variant.gt_bases[0] if variant.gt_bases else "./."
                else:
                    gt = f"{variant.REF}/{variant.ALT[0]}" # Database view
            except:
                gt = "Data N/A"

            results.append({
                "RSID": final_id,
                "Chr": variant.CHROM,
                "Pos": pos,
                "Genotype": gt
            })
            
        return results if results else f"No variants found in {region}."

    except Exception as e:
        return f"Bioinformatics Engine Error: {str(e)}"

def fetch_snp_wisdom(rsid):
    """Clinical Annotation: Fetches significance from MyVariant.info."""
    try:
        clean_id = str(rsid).split(" ")[0].lower()
        if ":" in clean_id:
            chrom, pos = clean_id.split(":")
            api_query = f"{chrom}:g.{pos}"
        else:
            api_query = clean_id

        url = f"https://myvariant.info/v1/variant/{api_query}"
        res = requests.get(url, timeout=5).json()
        clinvar = res.get('clinvar', {})
        if isinstance(clinvar, list): clinvar = clinvar[0]
        
        rcv = clinvar.get('rcv', [{}])
        if isinstance(rcv, list) and len(rcv) > 0:
            return rcv[0].get('clinical_significance', 'Likely Benign/VUS')
        return 'Unannotated Variation'
    except:
        return "Database Record Not Found"

def generate_pdf_report(results):
    """Reporting Engine: Creates professional PDF bytes."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Genomic Risk Report", ln=True, align='C')
    
    pdf.set_font("Arial", size=10)
    for row in results:
        pdf.ln(5)
        wisdom = fetch_snp_wisdom(row['RSID'])
        pdf.multi_cell(0, 10, f"RSID: {row['RSID']} | Genotype: {row['Genotype']}\nInterpretation: {wisdom}", border=1)
        
    return bytes(pdf.output())
