#!/usr/bin/env python3
"""
Unit tests for MongoDB queries module.

This module contains tests for the functions in the mongo_queries module,
using pytest and mock objects to simulate MongoDB connections.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from typing import List, Dict, Any

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import mongo_queries

# Mock data for testing
MOCK_VARIANT_DOC_1 = {
    "sample_id": "1",
    "external_id": "EXT-123456",
    "mysql_sample_id": 1,
    "mysql_patient_id": 1,
    "analysis_date": "2022-03-20T10:30:45Z",
    "analysis_pipeline": "GenomicsCore v2.0",
    "reference_genome": "GRCh38",
    "sequencing_stats": {
        "total_reads": 150000000,
        "mapped_reads": 148500000,
        "percent_mapped": 99.0,
        "mean_coverage": 30.5,
        "percent_bases_over_20x": 95.2
    },
    "variants": [
        {
            "variant_id": "chr1_12345_A_G",
            "chromosome": "chr1",
            "position": 12345,
            "reference_allele": "A",
            "alternate_allele": "G",
            "gene": "BRCA1",
            "transcript": "NM_007294.4",
            "hgvs_c": "c.123A>G",
            "hgvs_p": "p.Lys41Arg",
            "variant_type": "SNV",
            "zygosity": "heterozygous",
            "coverage": 32,
            "quality": 99.8,
            "allele_frequency": 0.48,
            "clinical_significance": "Pathogenic",
            "annotations": {
                "sift": {
                    "score": 0.01,
                    "prediction": "Deleterious"
                },
                "polyphen": {
                    "score": 0.98,
                    "prediction": "Probably Damaging"
                }
            },
            "phenotypes": ["Hereditary Breast and Ovarian Cancer Syndrome"],
            "citations": ["PMID:12345678"]
        },
        {
            "variant_id": "chr17_41245466_G_A",
            "chromosome": "chr17",
            "position": 41245466,
            "reference_allele": "G",
            "alternate_allele": "A",
            "gene": "BRCA1",
            "transcript": "NM_007294.4",
            "hgvs_c": "c.5516G>A",
            "hgvs_p": "p.Val1839Met",
            "variant_type": "SNV",
            "zygosity": "heterozygous",
            "coverage": 28,
            "quality": 99.5,
            "allele_frequency": 0.51,
            "clinical_significance": "Uncertain Significance",
            "annotations": {
                "sift": {
                    "score": 0.08,
                    "prediction": "Tolerated"
                },
                "polyphen": {
                    "score": 0.45,
                    "prediction": "Possibly Damaging"
                }
            }
        }
    ],
    "copy_number_variants": [
        {
            "cnv_id": "cnv_chr3_12345678_12400000",
            "chromosome": "chr3",
            "start": 12345678,
            "end": 12400000,
            "type": "Deletion",
            "copy_number": 1,
            "genes_affected": ["FOXP1"],
            "size": 54322,
            "confidence": "High",
            "clinical_significance": "Likely Pathogenic"
        }
    ],
    "structural_variants": []
}

MOCK_VARIANT_DOC_2 = {
    "sample_id": "2",
    "external_id": "EXT-789012",
    "mysql_sample_id": 2,
    "mysql_patient_id": 1,
    "analysis_date": "2022-04-25T15:20:30Z",
    "analysis_pipeline": "GenomicsCore v2.0",
    "reference_genome": "GRCh38",
    "sequencing_stats": {
        "total_reads": 180000000,
        "mapped_reads": 177300000,
        "percent_mapped": 98.5,
        "mean_coverage": 35.2,
        "percent_bases_over_20x": 97.1
    },
    "variants": [
        {
            "variant_id": "chr13_32915047_C_T",
            "chromosome": "chr13",
            "position": 32915047,
            "reference_allele": "C",
            "alternate_allele": "T",
            "gene": "BRCA2",
            "transcript": "NM_000059.3",
            "hgvs_c": "c.6275C>T",
            "hgvs_p": "p.Thr2092Ile",
            "variant_type": "SNV",
            "zygosity": "heterozygous",
            "coverage": 42,
            "quality": 99.9,
            "allele_frequency": 0.53,
            "clinical_significance": "Likely Benign",
            "annotations": {
                "sift": {
                    "score": 0.42,
                    "prediction": "Tolerated"
                },
                "polyphen": {
                    "score": 0.22,
                    "prediction": "Benign"
                }
            }
        }
    ],
    "copy_number_variants": [],
    "structural_variants": [
        {
            "sv_id": "sv_chr9_chr22_34567890_12345678",
            "type": "Translocation",
            "chromosomes": ["chr9", "chr22"],
            "breakpoints": [34567890, 12345678],
            "genes_affected": ["ABL1", "BCR"],
            "fusion": "BCR-ABL1",
            "clinical_significance": "Pathogenic",
            "phenotypes": ["Chronic Myeloid Leukemia"]
        }
    ]
}

MOCK_VARIANT_DOC_3 = {
    "sample_id": "3",
    "external_id": "EXT-345678",
    "mysql_sample_id": 3,
    "mysql_patient_id": 2,
    "analysis_date": "2022-03-25T09:45:15Z",
    "analysis_pipeline": "GenomicsCore v2.1",
    "reference_genome": "GRCh37",
    "sequencing_stats": {
        "total_reads": 160000000,
        "mapped_reads": 158400000,
        "percent_mapped": 99.0,
        "mean_coverage": 32.8,
        "percent_bases_over_20x": 96.3
    },
    "variants": [
        {
            "variant_id": "chr17_41234451_A_G",
            "chromosome": "chr17",
            "position": 41234451,
            "reference_allele": "A",
            "alternate_allele": "G",
            "gene": "BRCA1",
            "transcript": "NM_007294.4",
            "hgvs_c": "c.4837A>G",
            "hgvs_p": "p.Ser1613Gly",
            "variant_type": "SNV",
            "zygosity": "homozygous",
            "coverage": 30,
            "quality": 99.7,
            "allele_frequency": 0.98,
            "clinical_significance": "Benign",
            "annotations": {
                "sift": {
                    "score": 0.85,
                    "prediction": "Tolerated"
                },
                "polyphen": {
                    "score": 0.05,
                    "prediction": "Benign"
                }
            }
        },
        {
            "variant_id": "chr17_41245067_G_T",
            "chromosome": "chr17",
            "position": 41245067,
            "reference_allele": "G",
            "alternate_allele": "T",
            "gene": "BRCA1",
            "transcript": "NM_007294.4",
            "hgvs_c": "c.5117G>T",
            "hgvs_p": "p.Gly1706Val",
            "variant_type": "SNV",
            "zygosity": "heterozygous",
            "coverage": 25,
            "quality": 95.2,
            "allele_frequency": 0.45,
            "clinical_significance": "Pathogenic",
            "annotations": {
                "sift": {
                    "score": 0.001,
                    "prediction": "Deleterious"
                },
                "polyphen": {
                    "score": 0.99,
                    "prediction": "Probably Damaging"
                }
            },
            "phenotypes": ["Hereditary Breast and Ovarian Cancer Syndrome"],
            "citations": ["PMID:23535732", "PMID:29420474"]
        }
    ],
    "copy_number_variants": [],
    "structural_variants": []
}

MOCK_VARIANT_DOCUMENTS = [MOCK_VARIANT_DOC_1, MOCK_VARIANT_DOC_2, MOCK_VARIANT_DOC_3]


# Helper functions for mocks
def filter_variants_by_gene(docs, gene):
    """Filter variant results by gene."""
    results = []
    for doc in docs:
        for variant in doc["variants"]:
            if variant["gene"] == gene:
                results.append({
                    "sample_id": doc["sample_id"],
                    "mysql_sample_id": doc["mysql_sample_id"],
                    "mysql_patient_id": doc["mysql_patient_id"],
                    "variant": variant
                })
    return results


def filter_variants_by_significance(docs, significance):
    """Filter variant results by clinical significance."""
    results = []
    for doc in docs:
        for variant in doc["variants"]:
            if variant["clinical_significance"] == significance:
                results.append({
                    "sample_id": doc["sample_id"],
                    "mysql_sample_id": doc["mysql_sample_id"],
                    "mysql_patient_id": doc["mysql_patient_id"],
                    "variant": variant
                })
    return results


def find_samples_with_pathogenic(docs):
    """Find samples with pathogenic variants."""
    results = []
    for doc in docs:
        pathogenic_count = 0
        for variant in doc["variants"]:
            if variant["clinical_significance"] == "Pathogenic":
                pathogenic_count += 1
        
        if pathogenic_count > 0:
            results.append({
                "sample_id": doc["sample_id"],
                "mysql_sample_id": doc["mysql_sample_id"],
                "mysql_patient_id": doc["mysql_patient_id"],
                "external_id": doc["external_id"],
                "reference_genome": doc["reference_genome"],
                "analysis_date": doc["analysis_date"],
                "pathogenic_count": pathogenic_count
            })
    
    return results


def filter_cnvs_by_gene(docs, gene):
    """Filter CNV results by affected gene."""
    results = []
    for doc in docs:
        for cnv in doc.get("copy_number_variants", []):
            if gene in cnv["genes_affected"]:
                results.append({
                    "sample_id": doc["sample_id"],
                    "mysql_sample_id": doc["mysql_sample_id"],
                    "mysql_patient_id": doc["mysql_patient_id"],
                    "cnv": cnv
                })
    return results


def filter_svs_by_gene(docs, gene):
    """Filter SV results by affected gene."""
    results = []
    for doc in docs:
        for sv in doc.get("structural_variants", []):
            if gene in sv["genes_affected"]:
                results.append({
                    "sample_id": doc["sample_id"],
                    "mysql_sample_id": doc["mysql_sample_id"],
                    "mysql_patient_id": doc["mysql_patient_id"],
                    "sv": sv
                })
    return results


# Mock mongodb client and collection classes
class MockCollection:
    def __init__(self):
        self.data = MOCK_VARIANT_DOCUMENTS
    
    def find_one(self, query):
        """Mock find_one method."""
        # Handle sample_id query
        if "sample_id" in query:
            sample_id = query["sample_id"]
            for doc in self.data:
                if doc["sample_id"] == sample_id:
                    return doc
        
        # Handle mysql_sample_id query
        if "mysql_sample_id" in query:
            mysql_sample_id = query["mysql_sample_id"]
            for doc in self.data:
                if doc["mysql_sample_id"] == mysql_sample_id:
                    return doc
        
        return None
    
    def find(self, query):
        """Mock find method."""
        # Handle mysql_patient_id query
        if "mysql_patient_id" in query:
            mysql_patient_id = query["mysql_patient_id"]
            return [doc for doc in self.data if doc["mysql_patient_id"] == mysql_patient_id]
        
        return []
    
    def aggregate(self, pipeline):
        """Mock aggregate method with simplified logic."""
        # For variants by gene query
        for stage in pipeline:
            if "$match" in stage and "variants.gene" in stage["$match"]:
                gene = stage["$match"]["variants.gene"]
                return filter_variants_by_gene(self.data, gene)
            
            # For pathogenic variants query
            if "$match" in stage and "variants.clinical_significance" in stage["$match"]:
                significance = stage["$match"]["variants.clinical_significance"]
                if "variants.gene" in stage["$match"]:
                    # Both gene and significance
                    gene = stage["$match"]["variants.gene"]
                    gene_variants = filter_variants_by_gene(self.data, gene)
                    return [v for v in gene_variants if v["variant"]["clinical_significance"] == significance]
                else:
                    # Just significance
                    return filter_variants_by_significance(self.data, significance)
            
            # For samples with pathogenic variants
            if "$project" in stage and "pathogenic_count" in stage["$project"]:
                return find_samples_with_pathogenic(self.data)
            
            # For CNVs by gene
            if "$match" in stage and "copy_number_variants.genes_affected" in stage["$match"]:
                gene = stage["$match"]["copy_number_variants.genes_affected"]
                return filter_cnvs_by_gene(self.data, gene)
            
            # For SVs by gene
            if "$match" in stage and "structural_variants.genes_affected" in stage["$match"]:
                gene = stage["$match"]["structural_variants.genes_affected"]
                return filter_svs_by_gene(self.data, gene)
        
        return []
    
    def distinct(self, field):
        """Mock distinct method."""
        if field == "variants.gene":
            genes = set()
            for doc in self.data:
                for variant in doc["variants"]:
                    genes.add(variant["gene"])
            return sorted(list(genes))
        return []
    
    def count_documents(self, query):
        """Mock count_documents method."""
        if not query:  # Empty query counts all documents
            return len(self.data)
        return 0


class MockDatabase:
    def __init__(self, collection_name=None):
        self.collection = MockCollection()
    
    def __getitem__(self, collection_name):
        return self.collection


class MockMongoClient:
    def __init__(self, uri=None):
        self.db = MockDatabase()
    
    def __getitem__(self, db_name):
        return self.db
    
    def close(self):
        pass
    
    def admin(self):
        return self
    
    def command(self, cmd):
        return {"ok": 1.0, "ismaster": True}


# Pytest fixtures
@pytest.fixture
def mock_mongo_client():
    """Create a mock MongoDB client."""
    return MockMongoClient()


# Tests for mongo_queries.py functions

@patch('pymongo.MongoClient')
def test_get_mongo_client(mock_client_class):
    """Test getting a MongoDB client."""
    mock_client = MockMongoClient()
    mock_client_class.return_value = mock_client
    
    client = mongo_queries.get_mongo_client()
    
    assert client == mock_client
    mock_client_class.assert_called_once_with(mongo_queries.MONGO_URI)


@patch('app.mongo_queries.get_mongo_client')
def test_get_mongo_collection(mock_get_client):
    """Test getting a MongoDB collection."""
    mock_client = MockMongoClient()
    mock_get_client.return_value = mock_client
    
    collection, client = mongo_queries.get_mongo_collection()
    
    assert client == mock_client
    assert isinstance(collection, MockCollection)
    mock_get_client.assert_called_once()


@patch('app.mongo_queries.get_mongo_collection')
def test_find_variants_by_sample_id(mock_get_collection):
    """Test finding variants by sample ID."""
    mock_collection = MockCollection()
    mock_client = MockMongoClient()
    mock_get_collection.return_value = (mock_collection, mock_client)
    
    # Call with string sample_id
    result = mongo_queries.find_variants_by_sample_id("1")
    
    # Assertions
    assert result is not None
    assert result["sample_id"] == "1"
    assert result["mysql_sample_id"] == 1
    assert len(result["variants"]) == 2
    mock_get_collection.assert_called_once()
    
    # Reset mock
    mock_get_collection.reset_mock()
    
    # Call with integer sample_id
    result = mongo_queries.find_variants_by_sample_id(1)
    
    # Assertions
    assert result is not None
    assert result["sample_id"] == "1"
    assert result["mysql_sample_id"] == 1
    assert len(result["variants"]) == 2
    mock_get_collection.assert_called_once()


@patch('app.mongo_queries.get_mongo_collection')
def test_find_variants_by_mysql_sample_id(mock_get_collection):
    """Test finding variants by MySQL sample ID."""
    mock_collection = MockCollection()
    mock_client = MockMongoClient()
    mock_get_collection.return_value = (mock_collection, mock_client)
    
    # Call the function
    result = mongo_queries.find_variants_by_mysql_sample_id(2)
    
    # Assertions
    assert result is not None
    assert result["mysql_sample_id"] == 2
    assert result["mysql_patient_id"] == 1
    assert len(result["variants"]) == 1
    assert result["variants"][0]["gene"] == "BRCA2"
    mock_get_collection.assert_called_once()


@patch('app.mongo_queries.get_mongo_collection')
def test_find_variants_by_mysql_patient_id(mock_get_collection):
    """Test finding variants by MySQL patient ID."""
    mock_collection = MockCollection()
    mock_client = MockMongoClient()
    mock_get_collection.return_value = (mock_collection, mock_client)
    
    # Call the function
    results = mongo_queries.find_variants_by_mysql_patient_id(1)
    
    # Assertions
    assert len(results) == 2
    assert results[0]["mysql_patient_id"] == 1
    assert results[1]["mysql_patient_id"] == 1
    mock_get_collection.assert_called_once()


@patch('app.mongo_queries.get_mongo_collection')
def test_find_variants_by_gene(mock_get_collection):
    """Test finding variants by gene."""
    mock_collection = MockCollection()
    mock_client = MockMongoClient()
    mock_get_collection.return_value = (mock_collection, mock_client)
    
    # Call the function
    results = mongo_queries.find_variants_by_gene("BRCA1")
    
    # Assertions
    assert len(results) > 0
    for result in results:
        assert result["variant"]["gene"] == "BRCA1"
    mock_get_collection.assert_called_once()


@patch('app.mongo_queries.get_mongo_collection')
def test_find_pathogenic_variants(mock_get_collection):
    """Test finding pathogenic variants."""
    mock_collection = MockCollection()
    mock_client = MockMongoClient()
    mock_get_collection.return_value = (mock_collection, mock_client)
    
    # Call the function
    results = mongo_queries.find_pathogenic_variants()
    
    # Assertions
    assert len(results) > 0
    for result in results:
        assert result["variant"]["clinical_significance"] == "Pathogenic"
    mock_get_collection.assert_called_once()


@patch('app.mongo_queries.get_mongo_collection')
def test_find_samples_with_pathogenic_variants(mock_get_collection):
    """Test finding samples with pathogenic variants."""
    mock_collection = MockCollection()
    mock_client = MockMongoClient()
    mock_get_collection.return_value = (mock_collection, mock_client)
    
    # Call the function
    results = mongo_queries.find_samples_with_pathogenic_variants()
    
    # Assertions
    assert len(results) > 0
    for result in results:
        assert result["pathogenic_count"] > 0
    mock_get_collection.assert_called_once()


@patch('app.mongo_queries.get_mongo_collection')
def test_find_variants_by_clinical_significance(mock_get_collection):
    """Test finding variants by clinical significance."""
    mock_collection = MockCollection()
    mock_client = MockMongoClient()
    mock_get_collection.return_value = (mock_collection, mock_client)
    
    # Call the function
    results = mongo_queries.find_variants_by_clinical_significance("Uncertain Significance")
    
    # Assertions
    assert len(results) > 0
    for result in results:
        assert result["variant"]["clinical_significance"] == "Uncertain Significance"
    mock_get_collection.assert_called_once()


@patch('app.mongo_queries.get_mongo_collection')
def test_find_variants_by_gene_and_significance(mock_get_collection):
    """Test finding variants by gene and clinical significance."""
    mock_collection = MockCollection()
    mock_client = MockMongoClient()
    mock_get_collection.return_value = (mock_collection, mock_client)
    
    # Call the function
    results = mongo_queries.find_variants_by_gene_and_significance("BRCA1", "Pathogenic")
    
    # Assertions
    assert len(results) > 0
    for result in results:
        assert result["variant"]["gene"] == "BRCA1"
        assert result["variant"]["clinical_significance"] == "Pathogenic"
    mock_get_collection.assert_called_once()


@patch('app.mongo_queries.get_mongo_collection')
def test_find_copy_number_variants_by_gene(mock_get_collection):
    """Test finding CNVs by affected gene."""
    mock_collection = MockCollection()
    mock_client = MockMongoClient()
    mock_get_collection.return_value = (mock_collection, mock_client)
    
    # Call the function
    results = mongo_queries.find_copy_number_variants_by_gene("FOXP1")
    
    # Assertions
    assert len(results) > 0
    for result in results:
        assert "FOXP1" in result["cnv"]["genes_affected"]
    mock_get_collection.assert_called_once()


@patch('app.mongo_queries.get_mongo_collection')
def test_find_structural_variants_by_gene(mock_get_collection):
    """Test finding SVs by affected gene."""
    mock_collection = MockCollection()
    mock_client = MockMongoClient()
    mock_get_collection.return_value = (mock_collection, mock_client)
    
    # Call the function
    results = mongo_queries.find_structural_variants_by_gene("BCR")
    
    # Assertions
    assert len(results) > 0
    for result in results:
        assert "BCR" in result["sv"]["genes_affected"]
    mock_get_collection.assert_called_once()


@patch('app.mongo_queries.get_mongo_collection')
def test_get_available_genes(mock_get_collection):
    """Test getting available genes."""
    mock_collection = MockCollection()
    mock_client = MockMongoClient()
    mock_get_collection.return_value = (mock_collection, mock_client)
    
    # Call the function
    genes = mongo_queries.get_available_genes()
    
    # Assertions
    assert len(genes) > 0
    assert "BRCA1" in genes
    assert "BRCA2" in genes
    mock_get_collection.assert_called_once()


if __name__ == "__main__":
    pytest.main(['-xvs', __file__]) 