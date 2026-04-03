import os
import requests
from cyvcf2 import VCF
from fpdf import FPDF

def get_vcf_chrom_prefix(vcf, target_num):
    """
    Detects if the VCF uses 'chr17', '17', or Accession numbers.
    """
    # Check common patterns in the VCF's internal index (seqnames)
    vcf_chroms = vcf.seqnames
    patterns = [f"chr{target_num}", str(target_num), f"NC_0000{target_num.zfill(2)}"]
    
    for p in patterns:
        for actual in vcf_chroms:
            if actual.startswith(p):
                return actual
    return f"chr{target_num}" # Fallback

def parse_remote_genome(vcf_path, tbi_path, region_data):
    """
    Bioinformatics Engine: Direct Local Processing.
    Now with Auto-Chromosome Detection to fix 'No variants found'.
    """
    try:
        if not os.path.exists(vcf_path):
            return f"Error: VCF file not found at {vcf_path}"
        
        vcf = VCF(vcf_path)
        
        # 1. Extract Chrom, Start, End from our app's internal format (e.g. 'chr17:start-end')
        raw_chrom = region_data.split(":")[0].replace("chr", "")
        coords = region_data.split(":")[1]
        
        # 2. Auto-Detect the correct Chromosome name in the VCF
        correct_chrom = get_vcf_chrom_prefix(vcf, raw_chrom)
        final_query = f"{correct_chrom}:{coords}"
        
        # 3. Safety Check
        try:
            test_vcf = VCF(vcf_path)
            next(test_vcf()) 
        except StopIteration:
            return "Error: The uploaded VCF appears to be empty."

        # 4. Master Registry (GRCh38 Coordinates)
        NUTRIGENETICS_REGISTRY = {
            63477061: "rs4646994 (ACE)",
            11785729: "rs1801133 (MTHFR)",
            74749576: "rs762551 (CYP1A2)",
            135837170: "rs4988235 (LCT)"
        }

        results = []
        
        # 5. Regional Scan using the auto-detected 'final_query'
        for variant in vcf(final_query):
            pos = int(variant.POS)
            file_id = str(variant.ID) if variant.ID else "."
            
            if pos in NUTRIGENETICS_REGISTRY:
                final_id = NUTRIGENETICS_REGISTRY[pos]
            elif file_id not in [".", "None", "nan", ""]:
                final_id = file_id
            else:
                final_id = f"{variant.CHROM}:{pos}"

            # ClinVar-Safe Genotype Extraction
            if len(vcf.samples) > 0:
                gt = variant.gt_bases[0] if variant.gt_bases else "./."
            else:
                gt = f"{variant.REF}/{variant.ALT[0]}" 

            results.append({
                "RSID": final_id,
                "Chr": variant.CHROM,
                "Pos": pos,
                "Genotype": gt
            })
            
        return results if results else f"No variants found in {final_query}. Verify the Genome Build (GRCh38 required)."

    except Exception as e:
        return f"Bioinformatics Engine Error: {str(e)}"

def fetch_snp_wisdom(rsid):
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
        return rcv[0].get('clinical_significance', 'Likely Benign/VUS') if rcv else 'Unannotated'
    except:
        return "Clinical Record Not Found"

def generate_pdf_report(results):
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
