import os
import requests
from cyvcf2 import VCF
from fpdf import FPDF

def get_vcf_chrom_prefix(vcf, target_num):
    """Detects chromosome naming convention (e.g., chr17, 17, NC_000017)."""
    vcf_chroms = vcf.seqnames
    patterns = [f"chr{target_num}", str(target_num), f"NC_0000{target_num.zfill(2)}"]
    for p in patterns:
        for actual in vcf_chroms:
            if actual.startswith(p): return actual
    return f"chr{target_num}" 

def fetch_snp_wisdom(rsid):
    """Fetches clinical significance from MyVariant.info API."""
    try:
        clean_id = str(rsid).split(" ")[0].lower()
        api_query = f"{clean_id.split(':')[0]}:g.{clean_id.split(':')[1]}" if ":" in clean_id else clean_id
        
        url = f"https://myvariant.info/v1/variant/{api_query}"
        res = requests.get(url, timeout=5).json()
        clinvar = res.get('clinvar', {})
        if isinstance(clinvar, list): clinvar = clinvar[0]
        
        rcv = clinvar.get('rcv', [{}])
        if isinstance(rcv, list) and len(rcv) > 0:
            return rcv[0].get('clinical_significance', 'Unannotated')
        return 'Unannotated'
    except:
        return "Record Not Found"

def parse_remote_genome(vcf_path, tbi_path, region_data):
    """
    Bioinformatics Engine with Positive Clinical Filtering.
    Targeting exact GRCh38 coordinates for panel precision.
    """
    try:
        vcf = VCF(vcf_path)
        raw_chrom = region_data.split(":")[0].replace("chr", "")
        coords = region_data.split(":")[1]
        correct_chrom = get_vcf_chrom_prefix(vcf, raw_chrom)
        final_query = f"{correct_chrom}:{coords}"
        
        # EXACT GRCh38 Coordinates
        NUTRIGENETICS_REGISTRY = {
            63488539: "rs4646994 (ACE)",
            11796321: "rs1801133 (MTHFR)",
            74749576: "rs762551 (CYP1A2)",
            135851076: "rs4988235 (LCT)"
        }

        results = []
        for variant in vcf(final_query):
            pos = int(variant.POS)
            file_id = str(variant.ID) if variant.ID else "."
            final_id = NUTRIGENETICS_REGISTRY.get(pos, file_id if file_id not in [".", "None"] else f"{variant.CHROM}:{pos}")

            wisdom = fetch_snp_wisdom(final_id)
            
            # THE POSITIVE FILTER
            is_master_snp = pos in NUTRIGENETICS_REGISTRY
            wisdom_lower = wisdom.lower()
            is_risk = any(keyword in wisdom_lower for keyword in ["pathogenic", "risk factor", "drug response", "protective"])

            if not (is_master_snp or is_risk):
                continue 

            if len(vcf.samples) > 0:
                gt = variant.gt_bases[0] if variant.gt_bases is not None else "./."
            else:
                gt = f"{variant.REF}/{variant.ALT[0]} (Database)" 

            results.append({
                "RSID": final_id,
                "Chr": variant.CHROM,
                "Pos": pos,
                "Genotype": gt,
                "Interpretation": wisdom
            })
            
        return results if results else f"Target loci analyzed in {final_query}. No pathogenic or panel variants detected (Wild-Type/Healthy)."
    except Exception as e:
        return f"Bioinformatics Engine Error: {str(e)}"

def generate_pdf_report(results):
    """Compiles the filtered data into a focused clinical PDF."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Clinical Nutrigenetics Risk Panel", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    for row in results:
        pdf.ln(5)
        pdf.multi_cell(0, 10, f"RSID: {row['RSID']} | Genotype: {row['Genotype']}\nInterpretation: {row['Interpretation']}", border=1)
    return bytes(pdf.output())
