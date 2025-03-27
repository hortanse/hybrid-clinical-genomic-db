#!/usr/bin/env python3
"""
MongoDB query functions for the Hybrid Clinical Genomics Database.

This module provides functions to query genomic variant data from MongoDB.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB connection parameters
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DATABASE", "genomics_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "variants")


def get_mongo_client() -> MongoClient:
    """
    Create and return a MongoDB client.
    """
    try:
        client = MongoClient(MONGO_URI)
        # Check connection
        client.admin.command('ismaster')
        return client
    except ConnectionFailure as e:
        logger.error(f"MongoDB connection error: {e}")
        raise


def get_mongo_collection():
    """
    Get the MongoDB collection object.
    """
    client = get_mongo_client()
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    return collection, client


def find_variants_by_sample_id(sample_id: Union[int, str]) -> Optional[Dict[str, Any]]:
    """
    Find variants for a specific sample.
    
    Args:
        sample_id: The sample ID
        
    Returns:
        Dictionary with sample variant data or None if not found
    """
    collection, client = get_mongo_collection()
    
    try:
        # Convert sample_id to string if it's an integer
        if isinstance(sample_id, int):
            sample_id = str(sample_id)
        
        result = collection.find_one({"sample_id": sample_id})
        return result
    
    except Exception as e:
        logger.error(f"Error querying MongoDB for sample_id {sample_id}: {e}")
        return None
    
    finally:
        client.close()


def find_variants_by_mysql_sample_id(mysql_sample_id: int) -> Optional[Dict[str, Any]]:
    """
    Find variants using the MySQL sample ID reference.
    
    Args:
        mysql_sample_id: The MySQL sample ID
        
    Returns:
        Dictionary with sample variant data or None if not found
    """
    collection, client = get_mongo_collection()
    
    try:
        result = collection.find_one({"mysql_sample_id": mysql_sample_id})
        return result
    
    except Exception as e:
        logger.error(f"Error querying MongoDB for mysql_sample_id {mysql_sample_id}: {e}")
        return None
    
    finally:
        client.close()


def find_variants_by_mysql_patient_id(mysql_patient_id: int) -> List[Dict[str, Any]]:
    """
    Find all variant documents for a MySQL patient ID.
    
    Args:
        mysql_patient_id: The MySQL patient ID
        
    Returns:
        List of dictionaries with sample variant data
    """
    collection, client = get_mongo_collection()
    
    try:
        cursor = collection.find({"mysql_patient_id": mysql_patient_id})
        results = list(cursor)
        return results
    
    except Exception as e:
        logger.error(f"Error querying MongoDB for mysql_patient_id {mysql_patient_id}: {e}")
        return []
    
    finally:
        client.close()


def find_variants_by_gene(gene: str) -> List[Dict[str, Any]]:
    """
    Find all variants associated with a specific gene.
    
    Args:
        gene: Gene symbol
        
    Returns:
        List of dictionaries with variant data
    """
    collection, client = get_mongo_collection()
    
    try:
        # Use aggregation to unwrap the variants array
        pipeline = [
            {"$match": {"variants.gene": gene}},
            {"$unwind": "$variants"},
            {"$match": {"variants.gene": gene}},
            {"$project": {
                "sample_id": 1,
                "mysql_sample_id": 1,
                "mysql_patient_id": 1,
                "variant": "$variants"
            }}
        ]
        
        cursor = collection.aggregate(pipeline)
        results = list(cursor)
        return results
    
    except Exception as e:
        logger.error(f"Error querying MongoDB for gene {gene}: {e}")
        return []
    
    finally:
        client.close()


def find_pathogenic_variants(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Find pathogenic variants across all samples.
    
    Args:
        limit: Maximum number of results
        
    Returns:
        List of dictionaries with pathogenic variant data
    """
    collection, client = get_mongo_collection()
    
    try:
        # Use aggregation to unwrap the variants array
        pipeline = [
            {"$match": {"variants.clinical_significance": "Pathogenic"}},
            {"$unwind": "$variants"},
            {"$match": {"variants.clinical_significance": "Pathogenic"}},
            {"$project": {
                "sample_id": 1,
                "mysql_sample_id": 1,
                "mysql_patient_id": 1,
                "variant": "$variants"
            }},
            {"$limit": limit}
        ]
        
        cursor = collection.aggregate(pipeline)
        results = list(cursor)
        return results
    
    except Exception as e:
        logger.error(f"Error querying MongoDB for pathogenic variants: {e}")
        return []
    
    finally:
        client.close()


def find_samples_with_pathogenic_variants() -> List[Dict[str, Any]]:
    """
    Find samples that have pathogenic variants.
    
    Returns:
        List of dictionaries with sample info that have pathogenic variants
    """
    collection, client = get_mongo_collection()
    
    try:
        # Use aggregation to get distinct samples with pathogenic variants
        pipeline = [
            {"$match": {"variants.clinical_significance": "Pathogenic"}},
            {"$project": {
                "sample_id": 1,
                "mysql_sample_id": 1,
                "mysql_patient_id": 1,
                "external_id": 1,
                "reference_genome": 1,
                "analysis_date": 1,
                "pathogenic_count": {
                    "$size": {
                        "$filter": {
                            "input": "$variants",
                            "as": "variant",
                            "cond": {"$eq": ["$$variant.clinical_significance", "Pathogenic"]}
                        }
                    }
                }
            }}
        ]
        
        cursor = collection.aggregate(pipeline)
        results = list(cursor)
        return results
    
    except Exception as e:
        logger.error(f"Error querying MongoDB for samples with pathogenic variants: {e}")
        return []
    
    finally:
        client.close()


def find_variants_by_clinical_significance(significance: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Find variants with a specific clinical significance.
    
    Args:
        significance: Clinical significance value
        limit: Maximum number of results
        
    Returns:
        List of dictionaries with variant data
    """
    collection, client = get_mongo_collection()
    
    try:
        # Use aggregation to unwrap the variants array
        pipeline = [
            {"$match": {"variants.clinical_significance": significance}},
            {"$unwind": "$variants"},
            {"$match": {"variants.clinical_significance": significance}},
            {"$project": {
                "sample_id": 1,
                "mysql_sample_id": 1,
                "mysql_patient_id": 1,
                "variant": "$variants"
            }},
            {"$limit": limit}
        ]
        
        cursor = collection.aggregate(pipeline)
        results = list(cursor)
        return results
    
    except Exception as e:
        logger.error(f"Error querying MongoDB for {significance} variants: {e}")
        return []
    
    finally:
        client.close()


def find_variants_by_gene_and_significance(
    gene: str, 
    significance: str, 
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Find variants for a specific gene with a specific clinical significance.
    
    Args:
        gene: Gene symbol
        significance: Clinical significance value
        limit: Maximum number of results
        
    Returns:
        List of dictionaries with variant data
    """
    collection, client = get_mongo_collection()
    
    try:
        # Use aggregation to unwrap the variants array
        pipeline = [
            {"$match": {
                "variants.gene": gene,
                "variants.clinical_significance": significance
            }},
            {"$unwind": "$variants"},
            {"$match": {
                "variants.gene": gene,
                "variants.clinical_significance": significance
            }},
            {"$project": {
                "sample_id": 1,
                "mysql_sample_id": 1,
                "mysql_patient_id": 1,
                "variant": "$variants"
            }},
            {"$limit": limit}
        ]
        
        cursor = collection.aggregate(pipeline)
        results = list(cursor)
        return results
    
    except Exception as e:
        logger.error(f"Error querying MongoDB for gene {gene} with {significance} significance: {e}")
        return []
    
    finally:
        client.close()


def find_variants_by_position(
    chromosome: str, 
    position: int, 
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Find variants at a specific genomic position.
    
    Args:
        chromosome: Chromosome name
        position: Genomic position
        limit: Maximum number of results
        
    Returns:
        List of dictionaries with variant data
    """
    collection, client = get_mongo_collection()
    
    try:
        # Use aggregation to unwrap the variants array
        pipeline = [
            {"$match": {
                "variants.chromosome": chromosome,
                "variants.position": position
            }},
            {"$unwind": "$variants"},
            {"$match": {
                "variants.chromosome": chromosome,
                "variants.position": position
            }},
            {"$project": {
                "sample_id": 1,
                "mysql_sample_id": 1,
                "mysql_patient_id": 1,
                "variant": "$variants"
            }},
            {"$limit": limit}
        ]
        
        cursor = collection.aggregate(pipeline)
        results = list(cursor)
        return results
    
    except Exception as e:
        logger.error(f"Error querying MongoDB for position {chromosome}:{position}: {e}")
        return []
    
    finally:
        client.close()


def find_copy_number_variants_by_gene(gene: str) -> List[Dict[str, Any]]:
    """
    Find copy number variants affecting a specific gene.
    
    Args:
        gene: Gene symbol
        
    Returns:
        List of dictionaries with CNV data
    """
    collection, client = get_mongo_collection()
    
    try:
        # Use aggregation to unwrap the CNV array
        pipeline = [
            {"$match": {"copy_number_variants.genes_affected": gene}},
            {"$unwind": "$copy_number_variants"},
            {"$match": {"copy_number_variants.genes_affected": gene}},
            {"$project": {
                "sample_id": 1,
                "mysql_sample_id": 1,
                "mysql_patient_id": 1,
                "cnv": "$copy_number_variants"
            }}
        ]
        
        cursor = collection.aggregate(pipeline)
        results = list(cursor)
        return results
    
    except Exception as e:
        logger.error(f"Error querying MongoDB for CNVs affecting gene {gene}: {e}")
        return []
    
    finally:
        client.close()


def find_structural_variants_by_gene(gene: str) -> List[Dict[str, Any]]:
    """
    Find structural variants affecting a specific gene.
    
    Args:
        gene: Gene symbol
        
    Returns:
        List of dictionaries with SV data
    """
    collection, client = get_mongo_collection()
    
    try:
        # Use aggregation to unwrap the SV array
        pipeline = [
            {"$match": {"structural_variants.genes_affected": gene}},
            {"$unwind": "$structural_variants"},
            {"$match": {"structural_variants.genes_affected": gene}},
            {"$project": {
                "sample_id": 1,
                "mysql_sample_id": 1,
                "mysql_patient_id": 1,
                "sv": "$structural_variants"
            }}
        ]
        
        cursor = collection.aggregate(pipeline)
        results = list(cursor)
        return results
    
    except Exception as e:
        logger.error(f"Error querying MongoDB for SVs affecting gene {gene}: {e}")
        return []
    
    finally:
        client.close()


def get_available_genes() -> List[str]:
    """
    Get a list of all genes that have variants in the database.
    
    Returns:
        List of gene symbols
    """
    collection, client = get_mongo_collection()
    
    try:
        genes = collection.distinct("variants.gene")
        return sorted(genes)
    
    except Exception as e:
        logger.error(f"Error getting available genes from MongoDB: {e}")
        return []
    
    finally:
        client.close()


def get_variant_stats() -> Dict[str, Any]:
    """
    Get statistics about variants in the database.
    
    Returns:
        Dictionary with variant statistics
    """
    collection, client = get_mongo_collection()
    
    try:
        stats = {}
        
        # Total samples
        stats["total_samples"] = collection.count_documents({})
        
        # Total variants
        pipeline = [
            {"$project": {"variant_count": {"$size": "$variants"}}},
            {"$group": {"_id": None, "total_variants": {"$sum": "$variant_count"}}}
        ]
        result = list(collection.aggregate(pipeline))
        stats["total_variants"] = result[0]["total_variants"] if result else 0
        
        # Variants by clinical significance
        pipeline = [
            {"$unwind": "$variants"},
            {"$group": {
                "_id": "$variants.clinical_significance",
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        result = list(collection.aggregate(pipeline))
        stats["significance_counts"] = {item["_id"]: item["count"] for item in result}
        
        # Variants by type
        pipeline = [
            {"$unwind": "$variants"},
            {"$group": {
                "_id": "$variants.variant_type",
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        result = list(collection.aggregate(pipeline))
        stats["type_counts"] = {item["_id"]: item["count"] for item in result}
        
        # CNVs
        pipeline = [
            {"$project": {"cnv_count": {"$size": {"$ifNull": ["$copy_number_variants", []]}}}},
            {"$group": {"_id": None, "total_cnvs": {"$sum": "$cnv_count"}}}
        ]
        result = list(collection.aggregate(pipeline))
        stats["total_cnvs"] = result[0]["total_cnvs"] if result else 0
        
        # SVs
        pipeline = [
            {"$project": {"sv_count": {"$size": {"$ifNull": ["$structural_variants", []]}}}},
            {"$group": {"_id": None, "total_svs": {"$sum": "$sv_count"}}}
        ]
        result = list(collection.aggregate(pipeline))
        stats["total_svs"] = result[0]["total_svs"] if result else 0
        
        return stats
    
    except Exception as e:
        logger.error(f"Error getting variant stats from MongoDB: {e}")
        return {}
    
    finally:
        client.close()


def find_variants_by_multiple_filters(
    sample_ids: Optional[List[int]] = None,
    gene: Optional[str] = None,
    significance: Optional[str] = None,
    chromosome: Optional[str] = None,
    position_min: Optional[int] = None,
    position_max: Optional[int] = None,
    reference_genome: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Find variants that match multiple filter criteria.
    
    Args:
        sample_ids: List of MySQL sample IDs
        gene: Gene symbol
        significance: Clinical significance
        chromosome: Chromosome name
        position_min: Minimum genomic position
        position_max: Maximum genomic position
        reference_genome: Reference genome build
        limit: Maximum number of results
        
    Returns:
        List of dictionaries with variant data
    """
    collection, client = get_mongo_collection()
    
    try:
        # Build match conditions
        sample_match = {}
        variant_match = {}
        
        if sample_ids:
            sample_match["mysql_sample_id"] = {"$in": sample_ids}
        
        if gene:
            variant_match["variants.gene"] = gene
        
        if significance:
            variant_match["variants.clinical_significance"] = significance
        
        if chromosome:
            variant_match["variants.chromosome"] = chromosome
        
        if position_min is not None and position_max is not None:
            variant_match["variants.position"] = {"$gte": position_min, "$lte": position_max}
        elif position_min is not None:
            variant_match["variants.position"] = {"$gte": position_min}
        elif position_max is not None:
            variant_match["variants.position"] = {"$lte": position_max}
        
        if reference_genome:
            sample_match["reference_genome"] = reference_genome
        
        # Combine sample and variant match conditions
        match_condition = {**sample_match, **variant_match}
        
        # Use aggregation to unwrap the variants array
        pipeline = [
            {"$match": match_condition},
            {"$unwind": "$variants"},
            {"$match": variant_match},  # Apply variant-specific filters after unwinding
            {"$project": {
                "sample_id": 1,
                "mysql_sample_id": 1,
                "mysql_patient_id": 1,
                "reference_genome": 1,
                "variant": "$variants"
            }},
            {"$limit": limit}
        ]
        
        cursor = collection.aggregate(pipeline)
        results = list(cursor)
        return results
    
    except Exception as e:
        logger.error(f"Error querying MongoDB with multiple filters: {e}")
        return []
    
    finally:
        client.close() 