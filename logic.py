from cyvcf2 import VCF
import requests

def parse_remote_genome(url, region="17:63477061-63500000"):
    """Streams specific genomic regions from a remote URL."""
    try:
        # cyvcf2/htslib handles the remote streaming automatically
        vcf = VCF(url) 
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
        return f"Error: {str(e)}"

def fetch_snp_wisdom(rsid):
    """Queries MyVariant.info (dbSNP/ClinVar) for clinical significance."""
    try:
        url = f"https://myvariant.info/v1/variant/{rsid}"
        res = requests.get(url, timeout=5).json()
        clinvar = res.get('clinvar', {})
        if isinstance(clinvar, list): clinvar = clinvar[0]
        return clinvar.get('rcv', [{}])[0].get('clinical_significance', 'No Data')
    except:
        return "API Timeout"
