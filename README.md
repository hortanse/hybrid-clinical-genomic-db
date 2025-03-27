# Hybrid Clinical Genomics Database

A combined SQL/NoSQL database system for clinical genomics that leverages the strengths of relational databases (MySQL) for structured patient/sample data and document databases (MongoDB) for flexible variant storage.

## Project Overview

This project implements a hybrid database approach to clinical genomics data storage and retrieval:

- **MySQL**: Stores normalized patient demographics, sample metadata, and clinical test information
- **MongoDB**: Stores flexible genomic variant data with JSON documents per sample

The system demonstrates how to effectively bridge relational and document databases in a bioinformatics context.

## Technologies Used

- Python 3.9+
- MySQL 8.0+
- MongoDB 5.0+
- FastAPI
- Direct database connections using:
  - mysql-connector-python: For direct MySQL database access
  - pymongo: Official MongoDB Python driver for database operations

## Project Structure

```
hybrid_clinical_genomic_db/
├── README.md
├── requirements.txt           # Python dependencies
├── mysql_schema.sql
├── mongo_sample_data.json
├── data/                      # Generated synthetic data
├── scripts/
│   ├── generate_synthetic_data.py
│   ├── load_mysql_data.py
│   └── load_mongo_data.py
├── app/
│   ├── mysql_queries.py
│   ├── mongo_queries.py  
│   └── api.py
└── tests/
    ├── test_mysql_queries.py
    └── test_mongo_queries.py
```

## Implementation Plan

### Step 1: Define Data Model

- Design normalized MySQL tables for patients, samples, and clinical tests
- Create JSON document schema for MongoDB variant storage
- Files: `mysql_schema.sql`, `mongo_sample_data.json`

### Step 2: Generate Synthetic Data

- Create Python script to generate realistic but synthetic patient data
- Generate 50 patients with demographics (names, DOBs, sex)
- Generate 100 samples linked to patients
- Generate 100-500 test records linked to samples
- Generate JSON MongoDB variant data (10-100 variants per sample)
- Files: `scripts/generate_synthetic_data.py`
- Output: Files in `/data/` directory

### Step 3: Load Data into Databases

- Develop scripts to load synthetic data into both databases
- Ensure referential integrity in MySQL
- Maintain document consistency in MongoDB
- Files: `scripts/load_mysql_data.py`, `scripts/load_mongo_data.py`

### Step 4: Query Logic Implementation

- Create modular functions for MySQL queries (patients, samples)
- Create modular functions for MongoDB variant queries
- Implement combined queries that filter variants based on patient metadata
- Files: `app/mysql_queries.py`, `app/mongo_queries.py`

### Step 5: API Development

- Build RESTful API using FastAPI
- Implement endpoints:
  - `/variants/by-gene`: Filter variants by gene name
  - `/samples/with-pathogenic`: Find samples with pathogenic variants
  - `/patients/summary`: Generate patient summaries
- Support filtering by patient age, gene symbol, variant impact
- Files: `app/api.py`
- Include Swagger UI for API testing

### Step 6: Testing

- Develop unit tests for SQL queries
- Develop unit tests for MongoDB queries
- Test combined query functionality
- Implement mock database connections for testing
- Files: `tests/test_mysql_queries.py`, `tests/test_mongo_queries.py`

## Dependencies

The project requires the following main dependencies (to be detailed in `requirements.txt`):
- fastapi: For building the API layer
- uvicorn: ASGI server for FastAPI
- mysql-connector-python: MySQL database driver
- pymongo: MongoDB Python driver
- faker: For generating synthetic data
- pytest: For unit testing

## Setup and Installation (TBD)

Instructions for setting up the development environment, including:
- Python environment setup
- MySQL and MongoDB installation
- Database initialization
- Running the application

## Usage Examples (TBD)

Example API queries and responses will be documented here.

## License

[License information to be determined]
