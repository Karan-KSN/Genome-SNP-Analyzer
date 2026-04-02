import re
import requests
from cyvcf2 import VCF

def get_gdrive_direct_link(url):
    """Converts a Google Drive 'Share' link into a 'Direct Download' link."""
    if "drive.google.com" in url:
        file_id = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        if file_id:
            return f"https://drive.google.com/uc?export=download&id={file_id.group(1)}"
    return url

def parse_remote_genome(vcf_url, tbi_url, region="17:63477061-63500000"):
    """
    Specifically handles the 'Two-Link' system for Google Drive.
    """
    try:
        vcf_direct = get_gdrive_direct_link(vcf_url)
        tbi_direct = get_gdrive_direct_link(tbi_url)
        
        # We tell cyvcf2 exactly where the index is 
        # (This is the secret to making GDrive work!)
        vcf = VCF(vcf_direct, index_url=tbi_direct) 
        
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
        return f"Access Denied: Ensure both files are set to 'Anyone with the link'. {str(e)}"
