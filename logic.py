from cyvcf2 import VCF
import requests

def parse_remote_genome(vcf_url, tbi_url, region="17:63477061-63500000"):
    """
    Final Hardened Version for GitHub Release Streaming.
    Accepts two separate URLs for VCF and TBI.
    """
    try:
        # CRITICAL: We pass both URLs as positional arguments
        vcf = VCF(vcf_url, tbi_url) 
        
        results = []
        # This performs the HTTP Range Request (Streaming)
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

def fetch_snp_wisdom(rsid):
    """Clinical significance from MyVariant.info."""
    try:
        url = f"https://myvariant.info/v1/variant/{rsid}"
        res = requests.get(url, timeout=5).json()
        clinvar = res.get('clinvar', {})
        if isinstance(clinvar, list): clinvar = clinvar[0]
        return clinvar.get('rcv', [{}])[0].get('clinical_significance', 'No Data')
    except:
        return "API Timeout"
