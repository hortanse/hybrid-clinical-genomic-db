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

## Setup and Installation

### Prerequisites

- Python 3.9+
- MySQL 8.0+
- MongoDB 5.0+
- Git (optional)

### Environment Setup

1. Clone or download the repository (if using Git):
   ```bash
   git clone https://github.com/hortanse/hybrid-clinical-genomic-db.git
   cd hybrid_clinical_genomic_db
   ```

2. Create and activate a virtual environment:
   ```bash
   # Create a virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Database Configuration

1. Configure environment variables:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your database credentials
   # Use your favorite text editor to modify connection parameters
   ```

2. Set up MySQL:
   - Create a MySQL database with the name specified in your `.env` file
   - The database schema will be created automatically when running the data loading script

3. Set up MongoDB:
   - Ensure MongoDB service is running
   - A database will be created automatically with the name specified in your `.env` file

### Generate and Load Data

1. Generate synthetic data:
   ```bash
   python scripts/generate_synthetic_data.py
   ```
   This will create CSV and JSON files in the `data/` directory.

2. Load data into MySQL:
   ```bash
   python scripts/load_mysql_data.py
   ```

3. Load data into MongoDB:
   ```bash
   python scripts/load_mongo_data.py
   ```

### Running the Application

1. Start the API server:
   ```bash
   python run.py
   ```

2. The API will be available at:
   - API endpoints: `http://localhost:8000/`
   - Swagger UI documentation: `http://localhost:8000/docs`
   - ReDoc alternative documentation: `http://localhost:8000/redoc`

### Running Tests

Execute the test suite:
```bash
pytest tests/
```

For specific test files:
```bash
pytest tests/test_mysql_queries.py
pytest tests/test_mongo_queries.py
```

## Usage Examples

Here are some example API queries and their expected responses:

### Getting a List of Patients

**Request:**
```bash
curl -X 'GET' 'http://localhost:8000/patients?limit=2' -H 'accept: application/json'
```

**Response:**
```json
[
  {
    "patient_id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1980-01-15",
    "sex": "Male",
    "medical_record_number": "MRN12345678",
    "contact_phone": "555-123-4567",
    "contact_email": "john.doe@example.com",
    "address_line1": "123 Main St",
    "address_line2": "Apt 4B",
    "city": "Anytown",
    "state": "CA",
    "postal_code": "12345",
    "country": "United States",
    "created_at": "2022-01-01 10:00:00"
  },
  {
    "patient_id": 2,
    "first_name": "Jane",
    "last_name": "Smith",
    "date_of_birth": "1992-05-23",
    "sex": "Female",
    "medical_record_number": "MRN87654321",
    "contact_phone": "555-987-6543",
    "contact_email": "jane.smith@example.com",
    "address_line1": "456 Oak Ave",
    "address_line2": null,
    "city": "Somecity",
    "state": "NY",
    "postal_code": "54321",
    "country": "United States",
    "created_at": "2022-02-15 14:30:00"
  }
]
```

### Retrieving Pathogenic Variants

**Request:**
```bash
curl -X 'GET' 'http://localhost:8000/variants/pathogenic?limit=1' -H 'accept: application/json'
```

**Response:**
```json
[
  {
    "sample_id": "12345",
    "mysql_sample_id": 1,
    "mysql_patient_id": 1,
    "reference_genome": "GRCh38",
    "variant": {
      "variant_id": "chr1_12345_A_G",
      "chromosome": "chr1",
      "position": 12345,
      "reference_allele": "A",
      "alternate_allele": "G",
      "gene": "BRCA1",
      "clinical_significance": "Pathogenic",
      "transcript": "NM_007294.4",
      "hgvs_c": "c.123A>G",
      "hgvs_p": "p.Lys41Arg",
      "variant_type": "SNV",
      "zygosity": "heterozygous",
      "coverage": 32,
      "quality": 99.8,
      "allele_frequency": 0.48,
      "annotations": {
        "sift": {
          "score": 0.01,
          "prediction": "Deleterious"
        },
        "polyphen": {
          "score": 0.98,
          "prediction": "Probably Damaging"
        },
        "cadd": 25.6,
        "gnomad": {
          "allele_frequency": 0.0001,
          "homozygous": 0,
          "heterozygous": 15
        }
      },
      "phenotypes": ["Hereditary Breast and Ovarian Cancer Syndrome"],
      "citations": ["PMID:12345678", "PMID:87654321"]
    }
  }
]
```

### Combined Query (MySQL + MongoDB)

**Request:**
```bash
curl -X 'GET' 'http://localhost:8000/variants/combined-query?gene=BRCA1&significance=Pathogenic&age_min=30&sex=Female' -H 'accept: application/json'
```

This query finds pathogenic BRCA1 variants in female patients aged 30 or older, demonstrating the hybrid database approach.

### Using Swagger UI

You can explore all API endpoints interactively using the Swagger UI at `http://localhost:8000/docs`:

1. Open the Swagger UI in your browser
2. Select an endpoint (e.g., `/patients/{patient_id}/summary`)
3. Click "Try it out"
4. Enter the required parameters
5. Click "Execute" to see the result

## License

[License information to be determined]
