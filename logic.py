from cyvcf2 import VCF
import requests

def parse_remote_genome(vcf_url, tbi_url, region="17:63477061-63500000"):
    """
    Handles remote streaming by passing VCF and TBI as direct positions.
    This bypasses the 'unexpected keyword' error.
    """
    try:
        # We pass the index link as the second piece of information
        # no 'index_url=' label is needed here.
        vcf = VCF(vcf_url, tbi_url) 
        
        results = []
        # The engine now 'jumps' to the ACE gene region instantly
        for variant in vcf(region):
            if variant.ID and "rs" in variant.ID:
                results.append({
                    "RSID": variant.ID,
                    "Chr": variant.CHROM,
                    "Pos": variant.POS,
                    "Genotype": variant.gt_bases[0]
                })
        return results
    except Exception as e:
        return f"Bioinformatics Engine Error: {str(e)}"
