#!/usr/bin/env python3
"""
Generate synthetic data for the Hybrid Clinical Genomics Database.

This script generates:
1. 50 patients with demographic information
2. 100 samples linked to patients
3. 100-500 test records linked to samples
4. MongoDB variant JSON documents (10-100 variants per sample)

Output files are stored in the data/ directory.
"""

import os
import json
import random
import datetime
import csv
from typing import Dict, List, Any
from faker import Faker
import pandas as pd
import numpy as np
from pathlib import Path

# Initialize faker
fake = Faker()
Faker.seed(42)  # For reproducibility
random.seed(42)
np.random.seed(42)

# Constants
NUM_PATIENTS = 50
NUM_SAMPLES = 100
MIN_TESTS = 100
MAX_TESTS = 500
MIN_VARIANTS_PER_SAMPLE = 10
MAX_VARIANTS_PER_SAMPLE = 100

# Paths
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Lists for realistic data generation
SAMPLE_TYPES = ["Blood", "Saliva", "Tissue", "Buccal", "Other"]
TEST_TYPES = ["WGS", "WES", "Panel", "SNP", "RNA-seq", "Other"]
TEST_CODES = ["GNM-WGS", "GNM-WES", "PNL-BRCA", "PNL-HEART", "SNP-ARRAY", "RNA-1"]
TEST_NAMES = [
    "Whole Genome Sequencing", 
    "Whole Exome Sequencing", 
    "BRCA1/2 Panel", 
    "Cardiomyopathy Panel", 
    "SNP Array", 
    "RNA Sequencing"
]
VARIANT_TYPES = ["SNV", "Insertion", "Deletion", "Duplication", "CNV", "Indel"]
CHROMOSOMES = [f"chr{i}" for i in range(1, 23)] + ["chrX", "chrY"]
GENES = [
    "BRCA1", "BRCA2", "TP53", "MLH1", "MSH2", "KRAS", "EGFR", "BRAF", "PIK3CA", 
    "APC", "PTEN", "RB1", "CDKN2A", "MYC", "MYCN", "AR", "FOXP1", "CDH1", 
    "NOTCH1", "JAK2", "STAT3", "ALK", "IDH1", "IDH2", "CTNNB1", "DNMT3A", 
    "RUNX1", "ABL1", "BCR"
]
CLINICAL_SIGNIFICANCE = [
    "Pathogenic", "Likely Pathogenic", "Uncertain Significance", 
    "Likely Benign", "Benign"
]
PHENOTYPES = [
    "Hereditary Breast and Ovarian Cancer", "Lynch Syndrome", "Cystic Fibrosis",
    "Huntington's Disease", "Marfan Syndrome", "Neurofibromatosis", 
    "Hemochromatosis", "Sickle Cell Anemia", "Beta-Thalassemia",
    "Chronic Myeloid Leukemia", "Acute Lymphoblastic Leukemia"
]
SIFT_PREDICTIONS = ["Tolerated", "Deleterious"]
POLYPHEN_PREDICTIONS = ["Benign", "Possibly Damaging", "Probably Damaging"]
PANEL_CODES = ["BRCA-PANEL", "CARDIO-PANEL", "NEURO-PANEL", "HEMAT-PANEL", "METAB-PANEL"]
PANEL_NAMES = [
    "Hereditary Breast/Ovarian Cancer Panel", 
    "Cardiomyopathy Panel", 
    "Neurological Disorders Panel",
    "Hematological Malignancies Panel",
    "Metabolic Disorders Panel"
]
PANEL_VERSIONS = ["v1.0", "v2.0", "v3.0", "v2.1", "v1.5"]
PHYSICIANS = [
    f"Dr. {fake.last_name()}" for _ in range(10)
]


def generate_patients(num_patients: int) -> List[Dict[str, Any]]:
    """Generate synthetic patient data."""
    patients = []
    
    for i in range(1, num_patients + 1):
        sex = random.choice(["Male", "Female"])
        first_name = fake.first_name_male() if sex == "Male" else fake.first_name_female()
        
        # Generate date of birth (between 1 and 90 years old)
        dob = fake.date_of_birth(minimum_age=1, maximum_age=90)
        
        patient = {
            "patient_id": i,
            "first_name": first_name,
            "last_name": fake.last_name(),
            "date_of_birth": dob.strftime("%Y-%m-%d"),
            "sex": sex,
            "medical_record_number": f"MRN{fake.random_number(digits=8)}",
            "contact_phone": fake.phone_number(),
            "contact_email": fake.email(),
            "address_line1": fake.street_address(),
            "address_line2": fake.secondary_address() if random.random() > 0.7 else "",
            "city": fake.city(),
            "state": fake.state(),
            "postal_code": fake.zipcode(),
            "country": "United States",
            "created_at": fake.date_time_between(start_date="-3y", end_date="now").strftime("%Y-%m-%d %H:%M:%S")
        }
        patients.append(patient)
    
    return patients


def generate_samples(num_samples: int, patients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate synthetic sample data linked to patients."""
    samples = []
    
    for i in range(1, num_samples + 1):
        # Randomly select a patient
        patient = random.choice(patients)
        
        # Generate collection date (within past 3 years)
        collection_date = fake.date_time_between(start_date="-3y", end_date="now")
        
        # Generate received date (0-5 days after collection)
        received_date = collection_date + datetime.timedelta(days=random.randint(0, 5))
        
        sample = {
            "sample_id": i,
            "patient_id": patient["patient_id"],
            "sample_type": random.choice(SAMPLE_TYPES),
            "collection_date": collection_date.strftime("%Y-%m-%d"),
            "received_date": received_date.strftime("%Y-%m-%d"),
            "status": random.choice(["Received", "Processing", "Completed", "Failed", "Canceled"]),
            "external_sample_id": f"EXT-{fake.random_number(digits=6)}",
            "collection_method": random.choice(["Venipuncture", "Swab", "Biopsy", "FNA", "Bone Marrow Aspiration"]),
            "collection_site": random.choice(["Main Hospital", "Satellite Clinic", "Primary Care Office", "Reference Lab"]),
            "specimen_notes": fake.text(max_nb_chars=100) if random.random() > 0.7 else "",
            "created_at": collection_date.strftime("%Y-%m-%d %H:%M:%S")
        }
        samples.append(sample)
    
    return samples


def generate_tests(min_tests: int, max_tests: int, samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate synthetic clinical test data linked to samples."""
    num_tests = random.randint(min_tests, max_tests)
    tests = []
    
    # Generate panel data
    panels = []
    for i, (code, name, version) in enumerate(zip(PANEL_CODES, PANEL_NAMES, PANEL_VERSIONS), 1):
        panels.append({
            "panel_id": i,
            "panel_code": code,
            "panel_name": name,
            "panel_version": version,
            "genes_included": random.randint(10, 200),
            "panel_description": f"Panel targeting genes associated with {name.split(' Panel')[0]}",
            "created_at": fake.date_time_between(start_date="-2y", end_date="-1y").strftime("%Y-%m-%d %H:%M:%S")
        })
    
    # Generate test data
    for i in range(1, num_tests + 1):
        # Randomly select a sample
        sample = random.choice(samples)
        
        # Generate test date (after sample received date)
        received_date = datetime.datetime.strptime(sample["received_date"], "%Y-%m-%d")
        test_date = received_date + datetime.timedelta(days=random.randint(1, 30))
        
        # Generate result status
        result_status = random.choice(["Pending", "Preliminary", "Final", "Amended", "Canceled", "Failed"])
        
        # Generate report date if results are available
        report_date = None
        if result_status in ["Preliminary", "Final", "Amended"]:
            report_date = test_date + datetime.timedelta(days=random.randint(5, 45))
        
        # Choose test type and associated code/name
        test_index = random.randint(0, len(TEST_TYPES) - 1)
        test_type = TEST_TYPES[min(test_index, len(TEST_TYPES) - 1)]
        test_code = TEST_CODES[min(test_index, len(TEST_CODES) - 1)]
        test_name = TEST_NAMES[min(test_index, len(TEST_NAMES) - 1)]
        
        test = {
            "test_id": i,
            "sample_id": sample["sample_id"],
            "test_type": test_type,
            "test_date": test_date.strftime("%Y-%m-%d"),
            "test_code": test_code,
            "test_name": test_name,
            "ordering_physician": random.choice(PHYSICIANS),
            "result_summary": fake.text(max_nb_chars=200) if result_status in ["Preliminary", "Final", "Amended"] else "",
            "result_status": result_status,
            "report_date": report_date.strftime("%Y-%m-%d") if report_date else None,
            "report_version": random.randint(1, 3) if result_status in ["Amended"] else 1,
            "report_file_path": f"/reports/{sample['sample_id']}/{test_code}_{test_date.strftime('%Y%m%d')}_v1.pdf" if result_status in ["Preliminary", "Final", "Amended"] else None,
            "turnaround_time": (report_date - test_date).days if report_date else None,
            "test_notes": fake.text(max_nb_chars=100) if random.random() > 0.7 else "",
            "created_at": test_date.strftime("%Y-%m-%d %H:%M:%S")
        }
        tests.append(test)
    
    # Generate test quality metrics
    quality_metrics = []
    metric_id = 1
    for test in tests:
        # Generate 3-10 quality metrics per test
        num_metrics = random.randint(3, 10)
        for _ in range(num_metrics):
            metric_name = random.choice([
                "Q30", "Mean Coverage", "Uniformity", "Duplication Rate", 
                "Mapping Rate", "GC Bias", "Fragment Length", "Call Rate"
            ])
            metric_value = round(random.uniform(10, 100), 2)
            threshold_value = 30 if metric_name == "Mean Coverage" else 80 if metric_name in ["Q30", "Uniformity", "Mapping Rate", "Call Rate"] else 20
            metric_pass = metric_value >= threshold_value if metric_name not in ["Duplication Rate", "GC Bias"] else metric_value <= threshold_value
            
            quality_metrics.append({
                "metric_id": metric_id,
                "test_id": test["test_id"],
                "metric_name": metric_name,
                "metric_value": metric_value,
                "metric_unit": "%" if metric_name in ["Q30", "Uniformity", "Mapping Rate", "Call Rate"] else "X" if metric_name == "Mean Coverage" else "",
                "metric_pass": metric_pass,
                "threshold_value": threshold_value,
                "created_at": test["created_at"]
            })
            metric_id += 1
    
    # Generate panel assignments for panel tests
    panel_assignments = []
    for test in tests:
        if test["test_type"] == "Panel":
            panel = random.choice(panels)
            panel_assignments.append({
                "test_id": test["test_id"],
                "panel_id": panel["panel_id"]
            })
    
    return {
        "tests": tests,
        "panels": panels,
        "quality_metrics": quality_metrics,
        "panel_assignments": panel_assignments
    }


def generate_variant(sample_id: int, variant_index: int) -> Dict[str, Any]:
    """Generate a random genomic variant."""
    chromosome = random.choice(CHROMOSOMES)
    position = random.randint(1, 250000000)
    ref_allele = random.choice(["A", "C", "G", "T"])
    alt_bases = [b for b in "ACGT" if b != ref_allele]
    alt_allele = random.choice(alt_bases)
    
    # Generate variant ID
    variant_id = f"{chromosome}_{position}_{ref_allele}_{alt_allele}"
    
    # Select a random gene
    gene = random.choice(GENES)
    
    # Generate transcript ID
    transcript = f"NM_{random.randint(100000, 999999)}.{random.randint(1, 9)}"
    
    # Generate HGVS nomenclature
    position_in_gene = random.randint(1, 10000)
    hgvs_c = f"c.{position_in_gene}{ref_allele}>{alt_allele}"
    
    # Generate amino acid change
    aa_ref = random.choice(["Ala", "Arg", "Asn", "Asp", "Cys", "Gln", "Glu", "Gly", "His", "Ile", "Leu", "Lys", "Met", "Phe", "Pro", "Ser", "Thr", "Trp", "Tyr", "Val"])
    aa_alt = random.choice(["Ala", "Arg", "Asn", "Asp", "Cys", "Gln", "Glu", "Gly", "His", "Ile", "Leu", "Lys", "Met", "Phe", "Pro", "Ser", "Thr", "Trp", "Tyr", "Val", "Ter"])
    aa_pos = random.randint(1, 1000)
    hgvs_p = f"p.{aa_ref}{aa_pos}{aa_alt}"
    
    # Clinical significance - weight towards VUS
    clin_sig_weights = [15, 10, 50, 15, 10]  # Pathogenic, Likely Path, VUS, Likely Benign, Benign
    clin_sig = random.choices(CLINICAL_SIGNIFICANCE, weights=clin_sig_weights, k=1)[0]
    
    # Generate phenotypes if pathogenic
    phenotypes = []
    if clin_sig in ["Pathogenic", "Likely Pathogenic"] and random.random() > 0.3:
        num_phenotypes = random.randint(1, 3)
        phenotypes = random.sample(PHENOTYPES, num_phenotypes)
    
    # Generate citations if pathogenic or VUS
    citations = []
    if clin_sig in ["Pathogenic", "Likely Pathogenic", "Uncertain Significance"] and random.random() > 0.5:
        num_citations = random.randint(1, 5)
        citations = [f"PMID:{random.randint(10000000, 40000000)}" for _ in range(num_citations)]
    
    # Create the variant
    variant = {
        "variant_id": variant_id,
        "chromosome": chromosome,
        "position": position,
        "reference_allele": ref_allele,
        "alternate_allele": alt_allele,
        "gene": gene,
        "transcript": transcript,
        "hgvs_c": hgvs_c,
        "hgvs_p": hgvs_p,
        "variant_type": random.choice(VARIANT_TYPES),
        "zygosity": random.choice(["heterozygous", "homozygous"]),
        "coverage": random.randint(10, 100),
        "quality": round(random.uniform(20, 100), 1),
        "allele_frequency": round(random.uniform(0.3, 0.7), 2),
        "clinical_significance": clin_sig,
        "annotations": {
            "sift": {
                "score": round(random.uniform(0, 1), 3),
                "prediction": random.choice(SIFT_PREDICTIONS)
            },
            "polyphen": {
                "score": round(random.uniform(0, 1), 3),
                "prediction": random.choice(POLYPHEN_PREDICTIONS)
            },
            "cadd": round(random.uniform(0, 35), 1),
            "gnomad": {
                "allele_frequency": round(random.uniform(0, 0.1), 5),
                "homozygous": random.randint(0, 100),
                "heterozygous": random.randint(0, 1000)
            }
        },
        "phenotypes": phenotypes,
        "citations": citations
    }
    
    return variant


def generate_mongo_documents(samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate MongoDB variant documents for each sample."""
    mongo_docs = []
    
    for sample in samples:
        sample_id = sample["sample_id"]
        
        # Find the patient for this sample
        patient_id = sample["patient_id"]
        
        # Generate number of variants for this sample
        num_variants = random.randint(MIN_VARIANTS_PER_SAMPLE, MAX_VARIANTS_PER_SAMPLE)
        
        # Generate variants
        variants = [generate_variant(sample_id, i) for i in range(num_variants)]
        
        # Add some copy number variants (CNVs) for ~20% of samples
        cnvs = []
        if random.random() < 0.2:
            num_cnvs = random.randint(1, 3)
            for i in range(num_cnvs):
                chromosome = random.choice(CHROMOSOMES)
                start = random.randint(1, 240000000)
                end = start + random.randint(1000, 5000000)
                cnv_type = random.choice(["Deletion", "Duplication", "Amplification"])
                copy_number = 1 if cnv_type == "Deletion" else random.randint(3, 10) if cnv_type == "Amplification" else 3
                
                # Choose random genes that might be affected
                num_genes = random.randint(1, 5)
                genes_affected = random.sample(GENES, num_genes)
                
                cnvs.append({
                    "cnv_id": f"cnv_{chromosome}_{start}_{end}",
                    "chromosome": chromosome,
                    "start": start,
                    "end": end,
                    "type": cnv_type,
                    "copy_number": copy_number,
                    "genes_affected": genes_affected,
                    "size": end - start,
                    "confidence": random.choice(["Low", "Medium", "High"]),
                    "clinical_significance": random.choice(CLINICAL_SIGNIFICANCE)
                })
        
        # Add structural variants (SVs) for ~10% of samples
        svs = []
        if random.random() < 0.1:
            num_svs = random.randint(1, 2)
            for i in range(num_svs):
                sv_type = random.choice(["Translocation", "Inversion", "Complex Rearrangement"])
                chromosomes = random.sample(CHROMOSOMES, 2)
                breakpoints = [random.randint(1, 240000000) for _ in range(2)]
                
                # Choose random genes that might be affected
                genes_affected = random.sample(GENES, 2)
                
                # For translocations, create a fusion
                fusion = None
                if sv_type == "Translocation":
                    fusion = f"{genes_affected[0]}-{genes_affected[1]}"
                
                svs.append({
                    "sv_id": f"sv_{chromosomes[0]}_{chromosomes[1]}_{breakpoints[0]}_{breakpoints[1]}",
                    "type": sv_type,
                    "chromosomes": chromosomes,
                    "breakpoints": breakpoints,
                    "genes_affected": genes_affected,
                    "fusion": fusion,
                    "clinical_significance": random.choice(CLINICAL_SIGNIFICANCE),
                    "phenotypes": random.sample(PHENOTYPES, 1) if random.random() < 0.5 else []
                })
        
        # Create the MongoDB document
        doc = {
            "sample_id": str(sample_id),
            "external_id": sample["external_sample_id"],
            "mysql_sample_id": sample_id,
            "mysql_patient_id": patient_id,
            "analysis_date": (datetime.datetime.strptime(sample["received_date"], "%Y-%m-%d") + 
                            datetime.timedelta(days=random.randint(7, 30))).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "analysis_pipeline": f"GenomicsCore v{random.choice(['1.0', '2.0', '2.1', '3.0'])}",
            "reference_genome": random.choice(["GRCh37", "GRCh38"]),
            "sequencing_stats": {
                "total_reads": random.randint(50000000, 500000000),
                "mapped_reads": random.randint(45000000, 495000000),
                "percent_mapped": round(random.uniform(85, 99.9), 1),
                "mean_coverage": round(random.uniform(20, 100), 1),
                "percent_bases_over_20x": round(random.uniform(70, 99), 1)
            },
            "variants": variants,
            "copy_number_variants": cnvs,
            "structural_variants": svs,
            "metainfo": {
                "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "created_by": "generate_synthetic_data.py",
                "version": 1
            }
        }
        
        mongo_docs.append(doc)
    
    return mongo_docs


def write_to_csv(data: List[Dict[str, Any]], file_path: str):
    """Write data to a CSV file."""
    if not data:
        return
    
    with open(file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Wrote {len(data)} records to {file_path}")


def write_to_json(data: List[Dict[str, Any]], file_path: str):
    """Write data to a JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Wrote {len(data)} records to {file_path}")


def main():
    """Generate all synthetic data and save to files."""
    print("Generating synthetic data...")
    
    # Generate patients
    print(f"Generating {NUM_PATIENTS} patients...")
    patients = generate_patients(NUM_PATIENTS)
    
    # Generate samples
    print(f"Generating {NUM_SAMPLES} samples...")
    samples = generate_samples(NUM_SAMPLES, patients)
    
    # Generate tests and related data
    print(f"Generating clinical tests...")
    test_data = generate_tests(MIN_TESTS, MAX_TESTS, samples)
    tests = test_data["tests"]
    panels = test_data["panels"]
    quality_metrics = test_data["quality_metrics"]
    panel_assignments = test_data["panel_assignments"]
    
    # Generate MongoDB documents
    print("Generating MongoDB variant documents...")
    mongo_docs = generate_mongo_documents(samples)
    
    # Save data to CSV files
    write_to_csv(patients, str(DATA_DIR / "patients.csv"))
    write_to_csv(samples, str(DATA_DIR / "samples.csv"))
    write_to_csv(tests, str(DATA_DIR / "clinical_tests.csv"))
    write_to_csv(panels, str(DATA_DIR / "test_panels.csv"))
    write_to_csv(quality_metrics, str(DATA_DIR / "test_quality_metrics.csv"))
    write_to_csv(panel_assignments, str(DATA_DIR / "test_panel_assignments.csv"))
    
    # Save MongoDB documents to JSON files
    write_to_json(mongo_docs, str(DATA_DIR / "variant_documents.json"))
    
    # Also save a sample document structure to the root directory
    sample_doc = mongo_docs[0] if mongo_docs else {}
    with open(str(PROJECT_ROOT / "mongo_sample_data.json"), 'w') as f:
        json.dump(sample_doc, f, indent=2)
    
    print("Data generation complete!")
    print(f"Generated:")
    print(f"- {len(patients)} patients")
    print(f"- {len(samples)} samples")
    print(f"- {len(tests)} clinical tests")
    print(f"- {len(panels)} test panels")
    print(f"- {len(quality_metrics)} quality metrics")
    print(f"- {len(panel_assignments)} panel assignments")
    print(f"- {len(mongo_docs)} MongoDB variant documents")
    print(f"- {sum(len(doc['variants']) for doc in mongo_docs)} total variants")
    print(f"- {sum(len(doc['copy_number_variants']) for doc in mongo_docs)} total CNVs")
    print(f"- {sum(len(doc['structural_variants']) for doc in mongo_docs)} total SVs")


if __name__ == "__main__":
    main() 