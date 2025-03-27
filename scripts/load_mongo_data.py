#!/usr/bin/env python3
"""
Load synthetic variant data into MongoDB.

This script reads the JSON variant documents from the data/ directory
and loads them into a MongoDB collection. It also creates appropriate
indexes for efficient querying.
"""

import os
import json
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

# Load environment variables
load_dotenv()

# Get database connection parameters from environment variables or use defaults
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DATABASE", "genomics_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "variants")

# Paths
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
VARIANT_JSON = DATA_DIR / "variant_documents.json"

def connect_to_mongodb() -> MongoClient:
    """
    Connect to MongoDB using the URI from environment variables.
    Returns a MongoDB client.
    """
    try:
        client = MongoClient(MONGO_URI)
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        return client
    except ConnectionFailure as e:
        print(f"Could not connect to MongoDB: {e}")
        sys.exit(1)

def read_json_file(file_path: Path) -> List[Dict[str, Any]]:
    """
    Read JSON file and return the data.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        sys.exit(1)

def create_mongodb_indexes(collection: pymongo.collection.Collection) -> None:
    """
    Create indexes for efficient querying of variants.
    """
    try:
        # Create index on sample_id
        collection.create_index("sample_id", background=True)
        print("Created index on sample_id")
        
        # Create index on mysql_sample_id and mysql_patient_id
        collection.create_index("mysql_sample_id", background=True)
        collection.create_index("mysql_patient_id", background=True)
        print("Created indexes on mysql_sample_id and mysql_patient_id")
        
        # Create compound index for variants.gene
        collection.create_index("variants.gene", background=True)
        print("Created index on variants.gene")
        
        # Create compound index for variants.clinical_significance
        collection.create_index("variants.clinical_significance", background=True)
        print("Created index on variants.clinical_significance")
        
        # Create indexes for CNVs and SVs
        collection.create_index("copy_number_variants.genes_affected", background=True)
        collection.create_index("structural_variants.genes_affected", background=True)
        print("Created indexes on copy_number_variants.genes_affected and structural_variants.genes_affected")
        
        # Create index for reference genome
        collection.create_index("reference_genome", background=True)
        print("Created index on reference_genome")
        
    except OperationFailure as e:
        print(f"Error creating MongoDB indexes: {e}")

def load_data_to_mongodb(client: MongoClient, data: List[Dict[str, Any]]) -> None:
    """
    Load data into MongoDB collection and create indexes.
    """
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    
    # Drop collection if it exists and user confirms
    if collection.count_documents({}) > 0:
        print(f"Collection '{MONGO_COLLECTION}' already contains data.")
        confirmation = input("Do you want to drop the existing collection? (y/n): ")
        if confirmation.lower() == 'y':
            collection.drop()
            print(f"Collection '{MONGO_COLLECTION}' dropped.")
        else:
            print("Aborting data load.")
            return
    
    # Insert data
    if data:
        collection.insert_many(data)
        print(f"Inserted {len(data)} documents into '{MONGO_COLLECTION}' collection")
    else:
        print("No data to insert")
    
    # Create indexes
    create_mongodb_indexes(collection)

def main():
    """
    Main function to load data into MongoDB.
    """
    parser = argparse.ArgumentParser(description='Load synthetic variant data into MongoDB.')
    parser.add_argument('--force', action='store_true', help='Force drop of existing collection without confirmation')
    args = parser.parse_args()
    
    # Connect to MongoDB
    print("Connecting to MongoDB...")
    client = connect_to_mongodb()
    
    # Read variant data from JSON file
    print(f"Reading variant data from {VARIANT_JSON}...")
    variant_data = read_json_file(VARIANT_JSON)
    
    # Get or create the database
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    
    # Check if collection exists and has data
    if collection.count_documents({}) > 0:
        if args.force:
            collection.drop()
            print(f"Collection '{MONGO_COLLECTION}' dropped (forced).")
        else:
            print(f"Collection '{MONGO_COLLECTION}' already contains data.")
            confirmation = input("Do you want to drop the existing collection? (y/n): ")
            if confirmation.lower() == 'y':
                collection.drop()
                print(f"Collection '{MONGO_COLLECTION}' dropped.")
            else:
                print("Aborting data load.")
                client.close()
                return
    
    # Insert data
    if variant_data:
        print(f"Loading {len(variant_data)} variant documents into MongoDB...")
        result = collection.insert_many(variant_data)
        print(f"Inserted {len(result.inserted_ids)} documents into '{MONGO_COLLECTION}' collection")
    else:
        print("No variant data to insert")
    
    # Create indexes
    print("Creating MongoDB indexes...")
    create_mongodb_indexes(collection)
    
    # Print some stats
    print("\nMongoDB Data Summary:")
    print(f"Total variant documents: {collection.count_documents({})}")
    print(f"Distinct genes: {len(collection.distinct('variants.gene'))}")
    
    # Count pathogenic variants
    pathogenic_pipeline = [
        {"$unwind": "$variants"},
        {"$match": {"variants.clinical_significance": "Pathogenic"}},
        {"$count": "pathogenic_count"}
    ]
    pathogenic_count = list(collection.aggregate(pathogenic_pipeline))
    
    if pathogenic_count:
        print(f"Pathogenic variants: {pathogenic_count[0]['pathogenic_count']}")
    else:
        print("Pathogenic variants: 0")
    
    # Close the connection
    client.close()
    print("Data loading complete!")

if __name__ == "__main__":
    main() 