from cyvcf2 import VCF
import requests
import re

def get_gdrive_direct_link(url):
    """Converts a Google Drive 'Share' link into a 'Direct Download' link."""
    if "drive.google.com" in url:
        file_id = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        if file_id:
            return f"https://drive.google.com/uc?export=download&id={file_id.group(1)}"
    return url

def parse_remote_genome(vcf_url, tbi_url, region="17:63477061-63500000"):
    try:
        vcf_direct = get_gdrive_direct_link(vcf_url)
        tbi_direct = get_gdrive_direct_link(tbi_url)
        
        # New approach: Some versions of cyvcf2 prefer the index 
        # to be passed as the second positional argument, not a keyword.
        vcf = VCF(vcf_direct, tbi_direct) 
        
        results = []
        # 'vcf(region)' is the magic command that streams the data
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
        # This will tell us if it's still a link issue or a code issue
        return f"Bioinformatics Engine Error: {str(e)}"
                })
        return results
    except Exception as e:
        return f"Access Denied: Ensure both files are set to 'Anyone with the link'. {str(e)}"
