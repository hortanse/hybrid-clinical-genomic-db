#!/usr/bin/env python3
"""
API for the Hybrid Clinical Genomics Database.

This module provides a FastAPI-based RESTful API for querying patient, sample, and variant data
from both MySQL and MongoDB databases. It serves as the interface for client applications.
"""

from typing import List, Dict, Any, Optional
from datetime import date
import logging
from fastapi import FastAPI, HTTPException, Query, Path, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import mysql_queries
import mongo_queries

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Hybrid Clinical Genomics Database API",
    description="API for querying patient, sample, and variant data from a hybrid MySQL/MongoDB database system",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Define Pydantic models for request/response validation

class PatientBase(BaseModel):
    patient_id: int
    first_name: str
    last_name: str
    date_of_birth: str
    sex: str
    medical_record_number: Optional[str] = None

class Patient(PatientBase):
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    created_at: str

class SampleBase(BaseModel):
    sample_id: int
    patient_id: int
    sample_type: str
    collection_date: str
    received_date: str
    status: str
    external_sample_id: Optional[str] = None

class Sample(SampleBase):
    collection_method: Optional[str] = None
    collection_site: Optional[str] = None
    specimen_notes: Optional[str] = None
    created_at: str
    # Optional patient info for joined queries
    patient_first_name: Optional[str] = None
    patient_last_name: Optional[str] = None

class TestBase(BaseModel):
    test_id: int
    sample_id: int
    test_type: str
    test_date: str
    test_code: str
    test_name: str
    result_status: str

class Test(TestBase):
    ordering_physician: Optional[str] = None
    result_summary: Optional[str] = None
    report_date: Optional[str] = None
    report_version: Optional[int] = None
    report_file_path: Optional[str] = None
    turnaround_time: Optional[int] = None
    test_notes: Optional[str] = None
    created_at: str
    # Optional sample info for joined queries
    sample_type: Optional[str] = None
    external_sample_id: Optional[str] = None
    patient_id: Optional[int] = None
    patient_first_name: Optional[str] = None
    patient_last_name: Optional[str] = None

class VariantBase(BaseModel):
    variant_id: str
    chromosome: str
    position: int
    reference_allele: str
    alternate_allele: str
    gene: str
    clinical_significance: str

class Variant(VariantBase):
    transcript: Optional[str] = None
    hgvs_c: Optional[str] = None
    hgvs_p: Optional[str] = None
    variant_type: str
    zygosity: str
    coverage: Optional[int] = None
    quality: Optional[float] = None
    allele_frequency: Optional[float] = None
    annotations: Optional[Dict[str, Any]] = None
    phenotypes: Optional[List[str]] = None
    citations: Optional[List[str]] = None

class VariantResult(BaseModel):
    sample_id: str
    mysql_sample_id: int
    mysql_patient_id: int
    reference_genome: Optional[str] = None
    variant: Variant

class CNV(BaseModel):
    cnv_id: str
    chromosome: str
    start: int
    end: int
    type: str
    copy_number: int
    genes_affected: List[str]
    size: int
    confidence: str
    clinical_significance: str

class CNVResult(BaseModel):
    sample_id: str
    mysql_sample_id: int
    mysql_patient_id: int
    cnv: CNV

class SV(BaseModel):
    sv_id: str
    type: str
    chromosomes: List[str]
    breakpoints: List[int]
    genes_affected: List[str]
    fusion: Optional[str] = None
    clinical_significance: str
    phenotypes: Optional[List[str]] = None

class SVResult(BaseModel):
    sample_id: str
    mysql_sample_id: int
    mysql_patient_id: int
    sv: SV

class PatientSummary(BaseModel):
    patient: Patient
    samples: List[Dict[str, Any]]
    total_samples: int
    total_tests: int

class VariantStats(BaseModel):
    total_samples: int
    total_variants: int
    significance_counts: Dict[str, int]
    type_counts: Dict[str, int]
    total_cnvs: int
    total_svs: int

# Define API routes

@app.get("/", response_model=Dict[str, str])
async def root():
    """Get API information."""
    return {
        "name": "Hybrid Clinical Genomics Database API",
        "version": "1.0.0",
        "description": "API for querying patient, sample, and variant data"
    }

@app.get("/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: int = Path(..., description="The patient ID")):
    """Get patient information by ID."""
    patient = mysql_queries.get_patient_by_id(patient_id)
    
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient with ID {patient_id} not found")
    
    return patient

@app.get("/patients", response_model=List[Patient])
async def search_patients(
    name: Optional[str] = Query(None, description="Patient name (first or last)"),
    dob: Optional[str] = Query(None, description="Date of birth (YYYY-MM-DD)"),
    min_age: Optional[int] = Query(None, ge=0, description="Minimum age in years"),
    max_age: Optional[int] = Query(None, ge=0, description="Maximum age in years"),
    sex: Optional[str] = Query(None, description="Patient sex"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results to return")
):
    """Search for patients based on filters."""
    patients = mysql_queries.search_patients(
        name=name, 
        dob=dob, 
        min_age=min_age, 
        max_age=max_age, 
        sex=sex, 
        limit=limit
    )
    
    return patients

@app.get("/patients/{patient_id}/samples", response_model=List[Sample])
async def get_patient_samples(patient_id: int = Path(..., description="The patient ID")):
    """Get all samples for a patient."""
    # Check if patient exists
    patient = mysql_queries.get_patient_by_id(patient_id)
    
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient with ID {patient_id} not found")
    
    samples = mysql_queries.get_samples_by_patient_id(patient_id)
    return samples

@app.get("/patients/{patient_id}/summary", response_model=PatientSummary)
async def get_patient_summary(patient_id: int = Path(..., description="The patient ID")):
    """Get a comprehensive patient summary including samples and tests."""
    summary = mysql_queries.get_patient_summary(patient_id)
    
    if "error" in summary:
        raise HTTPException(status_code=404, detail=summary["error"])
    
    return summary

@app.get("/samples/{sample_id}", response_model=Sample)
async def get_sample(sample_id: int = Path(..., description="The sample ID")):
    """Get sample information by ID."""
    sample = mysql_queries.get_sample_with_patient_info(sample_id)
    
    if not sample:
        raise HTTPException(status_code=404, detail=f"Sample with ID {sample_id} not found")
    
    return sample

@app.get("/samples", response_model=List[Sample])
async def search_samples(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    sample_type: Optional[str] = Query(None, description="Sample type"),
    status: Optional[str] = Query(None, description="Sample status"),
    collection_date_start: Optional[str] = Query(None, description="Collection date range start (YYYY-MM-DD)"),
    collection_date_end: Optional[str] = Query(None, description="Collection date range end (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results to return")
):
    """Search for samples based on filters."""
    samples = mysql_queries.search_samples(
        patient_id=patient_id,
        sample_type=sample_type,
        status=status,
        collection_date_start=collection_date_start,
        collection_date_end=collection_date_end,
        limit=limit
    )
    
    return samples

@app.get("/samples/{sample_id}/tests", response_model=List[Test])
async def get_sample_tests(sample_id: int = Path(..., description="The sample ID")):
    """Get all tests for a sample."""
    # Check if sample exists
    sample = mysql_queries.get_sample_by_id(sample_id)
    
    if not sample:
        raise HTTPException(status_code=404, detail=f"Sample with ID {sample_id} not found")
    
    tests = mysql_queries.get_tests_by_sample_id(sample_id)
    return tests

@app.get("/samples/{sample_id}/variants", response_model=Dict[str, Any])
async def get_sample_variants(sample_id: int = Path(..., description="The MySQL sample ID")):
    """Get all variants for a sample."""
    # Check if sample exists
    sample = mysql_queries.get_sample_by_id(sample_id)
    
    if not sample:
        raise HTTPException(status_code=404, detail=f"Sample with ID {sample_id} not found")
    
    # Get variants from MongoDB
    variants_doc = mongo_queries.find_variants_by_mysql_sample_id(sample_id)
    
    if not variants_doc:
        raise HTTPException(status_code=404, detail=f"No variants found for sample ID {sample_id}")
    
    return variants_doc

@app.get("/tests/{test_id}", response_model=Dict[str, Any])
async def get_test(test_id: int = Path(..., description="The test ID")):
    """Get test information with details by ID."""
    test = mysql_queries.get_test_with_details(test_id)
    
    if not test:
        raise HTTPException(status_code=404, detail=f"Test with ID {test_id} not found")
    
    return test

@app.get("/tests", response_model=List[Test])
async def search_tests(
    sample_id: Optional[int] = Query(None, description="Filter by sample ID"),
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    test_type: Optional[str] = Query(None, description="Test type"),
    result_status: Optional[str] = Query(None, description="Result status"),
    test_date_start: Optional[str] = Query(None, description="Test date range start (YYYY-MM-DD)"),
    test_date_end: Optional[str] = Query(None, description="Test date range end (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results to return")
):
    """Search for tests based on filters."""
    tests = mysql_queries.search_tests(
        sample_id=sample_id,
        patient_id=patient_id,
        test_type=test_type,
        result_status=result_status,
        test_date_start=test_date_start,
        test_date_end=test_date_end,
        limit=limit
    )
    
    return tests

@app.get("/variants/by-gene/{gene}", response_model=List[VariantResult])
async def get_variants_by_gene(
    gene: str = Path(..., description="Gene symbol"),
    significance: Optional[str] = Query(None, description="Clinical significance filter"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results to return")
):
    """Find variants by gene symbol, optionally filtered by clinical significance."""
    if significance:
        variants = mongo_queries.find_variants_by_gene_and_significance(gene, significance, limit)
    else:
        variants = mongo_queries.find_variants_by_gene(gene)
        if limit < len(variants):
            variants = variants[:limit]
    
    if not variants:
        raise HTTPException(status_code=404, detail=f"No variants found for gene {gene}")
    
    return variants

@app.get("/variants/pathogenic", response_model=List[VariantResult])
async def get_pathogenic_variants(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results to return")
):
    """Find pathogenic variants across all samples."""
    variants = mongo_queries.find_pathogenic_variants(limit)
    
    if not variants:
        raise HTTPException(status_code=404, detail="No pathogenic variants found")
    
    return variants

@app.get("/variants/by-significance/{significance}", response_model=List[VariantResult])
async def get_variants_by_significance(
    significance: str = Path(..., description="Clinical significance value"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results to return")
):
    """Find variants with a specific clinical significance."""
    variants = mongo_queries.find_variants_by_clinical_significance(significance, limit)
    
    if not variants:
        raise HTTPException(status_code=404, detail=f"No variants found with significance {significance}")
    
    return variants

@app.get("/samples/with-pathogenic", response_model=List[Dict[str, Any]])
async def get_samples_with_pathogenic_variants():
    """Find samples that have pathogenic variants."""
    samples = mongo_queries.find_samples_with_pathogenic_variants()
    
    if not samples:
        raise HTTPException(status_code=404, detail="No samples with pathogenic variants found")
    
    return samples

@app.get("/cnv/by-gene/{gene}", response_model=List[CNVResult])
async def get_cnvs_by_gene(gene: str = Path(..., description="Gene symbol")):
    """Find copy number variants affecting a specific gene."""
    cnvs = mongo_queries.find_copy_number_variants_by_gene(gene)
    
    if not cnvs:
        raise HTTPException(status_code=404, detail=f"No CNVs found for gene {gene}")
    
    return cnvs

@app.get("/sv/by-gene/{gene}", response_model=List[SVResult])
async def get_svs_by_gene(gene: str = Path(..., description="Gene symbol")):
    """Find structural variants affecting a specific gene."""
    svs = mongo_queries.find_structural_variants_by_gene(gene)
    
    if not svs:
        raise HTTPException(status_code=404, detail=f"No SVs found for gene {gene}")
    
    return svs

@app.get("/genes", response_model=List[str])
async def get_genes():
    """Get a list of all genes that have variants in the database."""
    genes = mongo_queries.get_available_genes()
    
    if not genes:
        raise HTTPException(status_code=404, detail="No genes found in the database")
    
    return genes

@app.get("/variant-stats", response_model=VariantStats)
async def get_variant_statistics():
    """Get statistics about variants in the database."""
    stats = mongo_queries.get_variant_stats()
    
    if not stats:
        raise HTTPException(status_code=500, detail="Error retrieving variant statistics")
    
    return stats

@app.get("/variants/combined-query", response_model=List[VariantResult])
async def combined_query(
    gene: Optional[str] = Query(None, description="Gene symbol"),
    significance: Optional[str] = Query(None, description="Clinical significance"),
    age_min: Optional[int] = Query(None, ge=0, description="Minimum patient age"),
    age_max: Optional[int] = Query(None, ge=0, description="Maximum patient age"),
    sex: Optional[str] = Query(None, description="Patient sex"),
    chromosome: Optional[str] = Query(None, description="Chromosome"),
    position_min: Optional[int] = Query(None, ge=0, description="Minimum position"),
    position_max: Optional[int] = Query(None, ge=0, description="Maximum position"),
    reference_genome: Optional[str] = Query(None, description="Reference genome"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results to return")
):
    """
    Perform a combined query across MySQL and MongoDB.
    Filter patients by demographics in MySQL, then find their variants in MongoDB.
    """
    # If we have patient demographic filters (age or sex), first get matching sample IDs from MySQL
    sample_ids = None
    if age_min is not None or age_max is not None or sex is not None:
        sample_ids = mysql_queries.get_sample_ids_by_patient_details(
            age_min=age_min,
            age_max=age_max,
            sex=sex
        )
        
        if not sample_ids:
            raise HTTPException(status_code=404, detail="No samples match the demographic criteria")
    
    # Now query MongoDB with all filters
    variants = mongo_queries.find_variants_by_multiple_filters(
        sample_ids=sample_ids,
        gene=gene,
        significance=significance,
        chromosome=chromosome,
        position_min=position_min,
        position_max=position_max,
        reference_genome=reference_genome,
        limit=limit
    )
    
    if not variants:
        raise HTTPException(status_code=404, detail="No variants match the combined criteria")
    
    return variants

# Run the app using Uvicorn if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 