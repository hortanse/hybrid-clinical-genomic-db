# Testing Guide for Hybrid Clinical Genomics Database

This document provides detailed instructions for testing the Hybrid Clinical Genomics Database system, including both manual and automated testing approaches.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Setting Up the Test Environment](#setting-up-the-test-environment)
- [Automated Testing](#automated-testing)
- [Manual API Testing](#manual-api-testing)
- [Database Validation](#database-validation)
- [Performance Testing](#performance-testing)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before beginning testing, ensure you have:
1. Completed the installation steps in README.md
2. Access to both MySQL and MongoDB databases
3. Generated and loaded synthetic data

## Setting Up the Test Environment

### 1. Create a Testing Configuration

Create a `.env.test` file specifically for testing:

```bash
cp .env.example .env.test
```

Modify `.env.test` to use test databases:
```
MYSQL_DATABASE=genomics_test_db
MONGO_DATABASE=genomics_test_db
```

### 2. Create Test Databases

Create separate databases for testing:

```bash
# MySQL
mysql -u root -p -e "CREATE DATABASE genomics_test_db;"

# MongoDB is created automatically when you run the tests
```

### 3. Set Up Test Data

Generate a smaller dataset for faster testing:

```bash
# Use environment variable to specify smaller test dataset
TEST_DATA=1 python scripts/generate_synthetic_data.py
```

## Automated Testing

### Running the Unit Tests

The project includes unit tests for both MySQL and MongoDB query functions:

```bash
# Run all tests
pytest tests/

# Run specific test files
pytest tests/test_mysql_queries.py
pytest tests/test_mongo_queries.py

# Run tests with verbose output
pytest -v tests/

# Run tests and show coverage report
pytest --cov=app tests/
```

### Running the API Tests

You can create and run API tests using pytest and the HTTP client:

```bash
# First, start the API server in test mode
TEST_MODE=1 python run.py

# In another terminal, run the API tests
pytest tests/test_api.py
```

## Manual API Testing

### Using Swagger UI

The easiest way to manually test the API is through Swagger UI:

1. Start the server: `python run.py`
2. Open a browser and navigate to `http://localhost:8000/docs`
3. Test each endpoint using the interactive UI

### Using curl

You can also test with curl commands:

#### Get Patient List

```bash
curl -X 'GET' 'http://localhost:8000/patients' -H 'accept: application/json'
```

#### Get Patient by ID

```bash
curl -X 'GET' 'http://localhost:8000/patients/1' -H 'accept: application/json'
```

#### Search Patients by Name

```bash
curl -X 'GET' 'http://localhost:8000/patients?name=Smith' -H 'accept: application/json'
```

#### Get Variants by Gene

```bash
curl -X 'GET' 'http://localhost:8000/variants/by-gene/BRCA1' -H 'accept: application/json'
```

#### Get Pathogenic Variants

```bash
curl -X 'GET' 'http://localhost:8000/variants/pathogenic' -H 'accept: application/json'
```

#### Combined Query

```bash
curl -X 'GET' 'http://localhost:8000/variants/combined-query?gene=BRCA1&sex=Female&age_min=30' -H 'accept: application/json'
```

## Database Validation

### Validate MySQL Data

Connect to MySQL and run these validation queries:

```sql
-- Check patient count
SELECT COUNT(*) FROM patients;

-- Check sample distribution
SELECT COUNT(*), patient_id FROM samples GROUP BY patient_id ORDER BY COUNT(*) DESC;

-- Check test distribution
SELECT COUNT(*), sample_id FROM clinical_tests GROUP BY sample_id ORDER BY COUNT(*) DESC;

-- Verify referential integrity
SELECT s.sample_id FROM samples s LEFT JOIN patients p ON s.patient_id = p.patient_id WHERE p.patient_id IS NULL;
SELECT t.test_id FROM clinical_tests t LEFT JOIN samples s ON t.sample_id = s.sample_id WHERE s.sample_id IS NULL;
```

### Validate MongoDB Data

Connect to MongoDB and run these validation queries:

```javascript
// Check document count
db.variants.count()

// Check distribution of pathogenic variants
db.variants.aggregate([
  {$unwind: "$variants"},
  {$match: {"variants.clinical_significance": "Pathogenic"}},
  {$group: {_id: "$mysql_patient_id", count: {$sum: 1}}},
  {$sort: {count: -1}}
])

// Check gene distribution
db.variants.aggregate([
  {$unwind: "$variants"},
  {$group: {_id: "$variants.gene", count: {$sum: 1}}},
  {$sort: {count: -1}},
  {$limit: 10}
])
```

## Performance Testing

For basic performance testing:

```bash
# Install Apache Bench
# On Ubuntu/Debian:
sudo apt-get install apache2-utils
# On macOS (included with macOS)

# Test the API performance (100 requests, 10 concurrent)
ab -n 100 -c 10 http://localhost:8000/patients

# Test a more complex endpoint
ab -n 50 -c 5 http://localhost:8000/variants/pathogenic
```

## Troubleshooting

### Common Issues

1. **Database Connection Problems**
   - Verify the database credentials in your `.env` file
   - Check that both MySQL and MongoDB servers are running
   - Test connections manually:
     ```bash
     # MySQL
     mysql -u root -p -h localhost
     # MongoDB
     mongo
     ```

2. **Missing Data**
   - Check that you've generated and loaded the data
   - Verify data paths in the configuration
   - Run the data generation and loading scripts again

3. **API Errors**
   - Check the server logs for detailed error messages
   - Verify the API is running on the expected port
   - Check if another service is using the same port

4. **Test Failures**
   - Check that the test database configurations are correct
   - Ensure test data is properly loaded
   - Look for specific assertion errors in the test output

For any persistent issues, please check the project issues page or contact the development team. 