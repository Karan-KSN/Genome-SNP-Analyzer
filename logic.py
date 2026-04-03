import os
import requests
from cyvcf2 import VCF
from fpdf import FPDF
def parse_remote_genome(vcf_path, tbi_path, region):
    """
    Bioinformatics Engine: Direct Local Processing.
    Includes a 'Safety Check' to ensure the 1.1 GB file is readable.
    """
    try:
        # 1. Initialize Engine
        vcf = VCF(vcf_path)
        
        # --- THE CHUNK STARTS HERE ---
        # Test if the file is even readable/contains data
        try:
            # We use a temporary iterator so we don't 'exhaust' the main one
            test_vcf = VCF(vcf_path)
            first_variant = next(test_vcf())
            # If this succeeds, the file is 'Live'
        except StopIteration:
            return "Error: The uploaded VCF appears to be empty or contains no mutations."
        except Exception as e:
            return f"VCF Format Error: {str(e)}"
        # --- THE CHUNK ENDS HERE ---

        results = []
        
        # 2. Now perform the actual regional scan
        # 'region' comes from your GENE_MAP in app.py
        for variant in vcf(region):
            results.append({
                "RSID": variant.ID if variant.ID != "." else f"chr{variant.CHROM}:{variant.POS}",
                "Chr": variant.CHROM,
                "Pos": variant.POS,
                "Genotype": variant.gt_bases[0] if variant.gt_bases else "./."
            })
        
        # 3. Handle 'No Variants' logically
        if not results:
            return f"No variants found in {region}. (User matches Reference Genome at this locus)."
            
        return results

    except Exception as e:
        return f"Bioinformatics Engine Error: {str(e)}"
