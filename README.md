
# 🧬  WGS SNP Analyzer

### Ph.D. Research Project | Nutrigenetics & Hypertension
**Author:** Karan Singh Negi 
**Focus:** Gene-Lifestyle Interaction of ACE I/D polymorphism (North Indians)

---

## 📖 Overview
This tool is a high-performance **Bioinformatics Pipeline** designed to analyze Whole Genome Sequencing (WGS) data directly from cloud storage. It specifically targets polymorphisms related to hypertension, such as the **ACE I/D (rs4646994)**.

## 🚀 Key Features
* **Zero-Footprint Streaming:** Uses `htslib` and `cyvcf2` to stream specific genomic regions via HTTP Range Requests (No heavy (1GB+) uploads required).
* **Mobile-Friendly:** Accessible via any smartphone.
* **Clinical Annotation:** Real-time significance fetching from MyVariant.info (ClinVar/dbSNP).

## 🛠️ How to Use
1.  **Host your Data:** Upload your `.vcf.gz` and its `.tbi` index to a cloud provider (e.g., Dropbox).
2.  **Get Direct Link:** Ensure the link ends in `?dl=1` for direct streaming.
3.  **Analyze:** Paste the link into the app, specify your coordinates (default is ACE gene), and scan.

## 🔬 Scientific Basis
The analysis is backed by relevant scientific literature regarding the ACE I/D polymorphism and its prevalence in North Indian populations.
* *Reference: Cooper et al., "The Angiotensin-Converting Enzyme Insertion/Deletion Polymorphism," Hypertension, 1994.*
