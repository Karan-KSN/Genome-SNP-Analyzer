from cyvcf2 import VCF

def parse_remote_genome(vcf_url, tbi_url, region="17:63477061-63500000"):
    """
    Directly passes both the VCF and the TBI URLs to the engine.
    This is required for GitHub Release streaming.
    """
    try:
        # The magic happens here: we pass the TBI as the second argument
        vcf = VCF(vcf_url, tbi_url) 
        
        results = []
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
