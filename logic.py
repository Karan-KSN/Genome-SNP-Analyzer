from cyvcf2 import VCF
import os

def parse_remote_genome(vcf_url, tbi_url, region="17:63477061-63500000"):
    """
    Hardened streaming logic for Ph.D. Research.
    Uses htslib's environment configuration to handle GitHub redirects.
    """
    try:
        # We set an environment variable so htslib (the engine) 
        # knows how to handle the secure GitHub connection.
        os.environ["HTS_ALLOW_GDRIVE_REUSE"] = "1" 
        
        # We pass the index URL explicitly. 
        # If this fails, it's usually a header/redirect issue.
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
        # Detailed error reporting for troubleshooting
        return f"Bioinformatics Engine Error: {str(e)}"
