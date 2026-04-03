import re

def convert_gdrive_link(url):
    """Converts a standard GDrive share link to a direct download link."""
    if "drive.google.com" in url:
        # Extract the ID between /d/ and /view
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        if match:
            file_id = match.group(1)
            return f"https://drive.google.com/uc?export=download&id={file_id}"
    return url

def parse_remote_genome(vcf_url, tbi_url, region="chr17:63477061-63498373"):
    # Apply the conversion before downloading
    vcf_direct = convert_gdrive_link(vcf_url)
    tbi_direct = convert_gdrive_link(tbi_url)
    
    # ... rest of your download_file and VCF(vcf_path) code ...
