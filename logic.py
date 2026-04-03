import os
import requests
from cyvcf2 import VCF
from fpdf import FPDF

def get_vcf_chrom_prefix(vcf, target_num):
    """
    Detects if the VCF uses 'chr17', '17', or Accession numbers (NC_000017).
    Essential for compatibility across GIAB and ClinVar datasets.
    """
    vcf_chroms = vcf.seqnames
    patterns = [f"chr{target_num}", str(target_num), f"NC_0000{target_num.zfill(2)}"]
    
    for p in patterns:
        for actual in vcf_chroms:
            if actual.startswith(p):
                return actual
    return f"chr{target_num}" 

def parse_remote_genome(vcf_path, tbi_path, region_data):
    """
    Bioinformatics Engine: Optimized for GIAB (Personal) and ClinVar (Database).
    Prevents 'list index out of range' by checking sample availability.
    """
    try:
        if not os.path.exists(vcf_path):
            return f"Error: VCF file not found at {vcf_path}"
        
        vcf = VCF(vcf_path)
        
        # 1. Coordinate Parsing & Auto-Prefix Detection
        raw_chrom = region_data.split(":")[0].replace("chr", "")
        coords = region_data.split(":")[1]
        correct_chrom = get_vcf_chrom_prefix(vcf, raw_chrom)
        final_query = f"{correct_chrom}:{coords}"
        
        # 2. Safety Check to ensure file integrity
        try:
            test_vcf = VCF(vcf_path)
            next(test_vcf()) 
        except StopIteration:
            return "Error: The uploaded VCF appears to be empty."

        # 3. Master Nutrigenetics Registry (GRCh38)
        NUTRIGENETICS_REGISTRY = {
            63477061: "rs4646994 (ACE)",
            11785729: "rs1801133 (MTHFR)",
            74749576: "rs762551 (CYP1A2)",
            135837170: "rs4988235 (LCT)"
        }

        results = []
        
        # 4. Regional Scan
        for variant in vcf(final_query):
            pos = int(variant.POS)
            file_id = str(variant.ID) if variant.ID else "."
            
            # Identity Logic: Prioritize Registry for PhD-relevant SNPs
            if pos in NUTRIGENETICS_REGISTRY:
                final_id = NUTRIGENETICS_REGISTRY[pos]
            elif file_id not in [".", "None", "nan", ""]:
                final_id = file_id
            else:
                final_id = f"{variant.CHROM}:{pos}"

            # UNIVERSAL GENOTYPE LOGIC
            # If file has samples (GIAB), show the person's result.
            # If 0 samples (ClinVar), show the REF/ALT alleles.
            if len(vcf.samples) > 0:
                gt = variant.gt_bases[0] if variant.gt_bases is not None and len(variant.gt_bases) > 0 else "./."
            else:
                alt_allele = variant.ALT[0] if len(variant.ALT) > 0 else "."
                gt = f"{variant.REF}/{alt_allele} (Database)" 

            results.append({
                "RSID": final_id,
                "Chr": variant.CHROM,
                "Pos": pos,
                "Genotype": gt
            })
            
        return results if results else f"No variants found in {final_query}."

    except Exception as e:
        return f"Bioinformatics Engine Error: {str(e)}"

def fetch_snp_wisdom(rsid):
    """Clinical Resolver for both RSIDs and Genomic Coordinates."""
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
        return "Record Not Found"

def generate_pdf_report(results):
    """Generates the final PDF report with Clinical Wisdom."""
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
