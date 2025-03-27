#!/usr/bin/env python3
"""
Unit tests for MySQL queries module.

This module contains tests for the functions in the mysql_queries module,
using pytest and mock objects to simulate database connections.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime
from typing import List, Dict, Any

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import mysql_queries

# Mock data for testing
MOCK_PATIENTS = [
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
        "address_line2": "",
        "city": "Somecity",
        "state": "NY",
        "postal_code": "54321",
        "country": "United States",
        "created_at": "2022-02-15 14:30:00"
    }
]

MOCK_SAMPLES = [
    {
        "sample_id": 1,
        "patient_id": 1,
        "sample_type": "Blood",
        "collection_date": "2022-03-10",
        "received_date": "2022-03-11",
        "status": "Completed",
        "external_sample_id": "EXT-123456",
        "collection_method": "Venipuncture",
        "collection_site": "Main Hospital",
        "specimen_notes": "Sample in good condition",
        "created_at": "2022-03-10 09:15:00"
    },
    {
        "sample_id": 2,
        "patient_id": 1,
        "sample_type": "Saliva",
        "collection_date": "2022-04-20",
        "received_date": "2022-04-21",
        "status": "Processing",
        "external_sample_id": "EXT-789012",
        "collection_method": "Swab",
        "collection_site": "Satellite Clinic",
        "specimen_notes": "",
        "created_at": "2022-04-20 14:45:00"
    },
    {
        "sample_id": 3,
        "patient_id": 2,
        "sample_type": "Blood",
        "collection_date": "2022-03-15",
        "received_date": "2022-03-16",
        "status": "Completed",
        "external_sample_id": "EXT-345678",
        "collection_method": "Venipuncture",
        "collection_site": "Reference Lab",
        "specimen_notes": "",
        "created_at": "2022-03-15 10:30:00"
    }
]

MOCK_TESTS = [
    {
        "test_id": 1,
        "sample_id": 1,
        "test_type": "WGS",
        "test_date": "2022-03-15",
        "test_code": "GNM-WGS",
        "test_name": "Whole Genome Sequencing",
        "ordering_physician": "Dr. Johnson",
        "result_summary": "No pathogenic variants detected",
        "result_status": "Final",
        "report_date": "2022-04-01",
        "report_version": 1,
        "report_file_path": "/reports/1/GNM-WGS_20220315_v1.pdf",
        "turnaround_time": 17,
        "test_notes": "",
        "created_at": "2022-03-15 08:00:00"
    },
    {
        "test_id": 2,
        "sample_id": 2,
        "test_type": "Panel",
        "test_date": "2022-04-25",
        "test_code": "PNL-BRCA",
        "test_name": "BRCA1/2 Panel",
        "ordering_physician": "Dr. Smith",
        "result_summary": "",
        "result_status": "Pending",
        "report_date": None,
        "report_version": None,
        "report_file_path": None,
        "turnaround_time": None,
        "test_notes": "Rush processing requested",
        "created_at": "2022-04-25 09:30:00"
    },
    {
        "test_id": 3,
        "sample_id": 3,
        "test_type": "WES",
        "test_date": "2022-03-20",
        "test_code": "GNM-WES",
        "test_name": "Whole Exome Sequencing",
        "ordering_physician": "Dr. Williams",
        "result_summary": "Pathogenic variant in BRCA1 detected",
        "result_status": "Final",
        "report_date": "2022-04-05",
        "report_version": 1,
        "report_file_path": "/reports/3/GNM-WES_20220320_v1.pdf",
        "turnaround_time": 16,
        "test_notes": "",
        "created_at": "2022-03-20 11:15:00"
    }
]

MOCK_QUALITY_METRICS = [
    {
        "metric_id": 1,
        "test_id": 1,
        "metric_name": "Mean Coverage",
        "metric_value": 35.6,
        "metric_unit": "X",
        "metric_pass": True,
        "threshold_value": 30.0,
        "created_at": "2022-03-15 08:00:00"
    },
    {
        "metric_id": 2,
        "test_id": 1,
        "metric_name": "Q30",
        "metric_value": 92.3,
        "metric_unit": "%",
        "metric_pass": True,
        "threshold_value": 80.0,
        "created_at": "2022-03-15 08:00:00"
    },
    {
        "metric_id": 3,
        "test_id": 3,
        "metric_name": "Mean Coverage",
        "metric_value": 45.2,
        "metric_unit": "X",
        "metric_pass": True,
        "threshold_value": 30.0,
        "created_at": "2022-03-20 11:15:00"
    }
]

MOCK_PANELS = [
    {
        "panel_id": 1,
        "panel_code": "BRCA-PANEL",
        "panel_name": "Hereditary Breast/Ovarian Cancer Panel",
        "panel_version": "v2.0",
        "genes_included": 25,
        "panel_description": "Panel targeting genes associated with Hereditary Breast/Ovarian Cancer",
        "created_at": "2021-01-15 10:00:00"
    }
]

MOCK_PANEL_ASSIGNMENTS = [
    {
        "test_id": 2,
        "panel_id": 1
    }
]


# Pytest fixtures
@pytest.fixture
def mock_db_connection():
    """Create a mock database connection."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock the fetchall method to return different results based on the query
    def mock_execute(query, params=None):
        # Store the query for later assertion
        mock_cursor.query = query
        mock_cursor.params = params
        
        # Setup different responses based on query content
        if "FROM patients WHERE patient_id" in query:
            patient_id = params[0] if params else None
            mock_cursor.fetchall.return_value = [p for p in MOCK_PATIENTS if p["patient_id"] == patient_id]
        
        elif "FROM patients" in query and "WHERE" in query:
            # Simplified filter for test purposes
            mock_cursor.fetchall.return_value = MOCK_PATIENTS
        
        elif "FROM patients" in query:
            mock_cursor.fetchall.return_value = MOCK_PATIENTS
        
        elif "FROM samples WHERE patient_id" in query:
            patient_id = params[0] if params else None
            mock_cursor.fetchall.return_value = [s for s in MOCK_SAMPLES if s["patient_id"] == patient_id]
        
        elif "FROM samples WHERE sample_id" in query:
            sample_id = params[0] if params else None
            mock_cursor.fetchall.return_value = [s for s in MOCK_SAMPLES if s["sample_id"] == sample_id]
        
        elif "FROM samples" in query:
            mock_cursor.fetchall.return_value = MOCK_SAMPLES
        
        elif "FROM clinical_tests WHERE sample_id" in query:
            sample_id = params[0] if params else None
            mock_cursor.fetchall.return_value = [t for t in MOCK_TESTS if t["sample_id"] == sample_id]
        
        elif "FROM clinical_tests WHERE test_id" in query:
            test_id = params[0] if params else None
            mock_cursor.fetchall.return_value = [t for t in MOCK_TESTS if t["test_id"] == test_id]
        
        elif "FROM clinical_tests" in query:
            mock_cursor.fetchall.return_value = MOCK_TESTS
        
        elif "FROM test_quality_metrics WHERE test_id" in query:
            test_id = params[0] if params else None
            mock_cursor.fetchall.return_value = [m for m in MOCK_QUALITY_METRICS if m["test_id"] == test_id]
        
        elif "FROM test_panels" in query:
            mock_cursor.fetchall.return_value = MOCK_PANELS
        
        elif "SELECT s.sample_id FROM samples s JOIN patients p" in query:
            # For get_sample_ids_by_patient_details
            mock_cursor.fetchall.return_value = [{"sample_id": s["sample_id"]} for s in MOCK_SAMPLES]
        
        else:
            # Default empty result
            mock_cursor.fetchall.return_value = []
    
    mock_cursor.execute.side_effect = mock_execute
    
    # For dictionary cursor
    mock_cursor.column_names = []
    
    return mock_conn


# Tests for mysql_queries.py functions

@patch('mysql.connector.connect')
def test_get_mysql_connection(mock_connect):
    """Test getting a MySQL connection."""
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    
    conn = mysql_queries.get_mysql_connection()
    
    assert conn == mock_conn
    mock_connect.assert_called_once()


@patch('app.mysql_queries.get_mysql_connection')
def test_execute_query(mock_get_conn, mock_db_connection):
    """Test executing a SQL query."""
    mock_get_conn.return_value = mock_db_connection
    
    # Call the function
    query = "SELECT * FROM patients"
    results = mysql_queries.execute_query(query)
    
    # Assertions
    mock_get_conn.assert_called_once()
    mock_db_connection.cursor.assert_called_once()
    mock_db_connection.cursor().execute.assert_called_once_with(query)
    assert results == MOCK_PATIENTS


@patch('app.mysql_queries.execute_query')
def test_get_patient_by_id(mock_execute_query):
    """Test retrieving a patient by ID."""
    # Mock the execute_query function to return a single patient
    mock_execute_query.return_value = [MOCK_PATIENTS[0]]
    
    # Call the function
    patient = mysql_queries.get_patient_by_id(1)
    
    # Assertions
    assert patient == MOCK_PATIENTS[0]
    mock_execute_query.assert_called_once()
    # Check that the query includes the patient ID
    assert "WHERE patient_id = %s" in mock_execute_query.call_args[0][0]
    assert mock_execute_query.call_args[0][1] == (1,)


@patch('app.mysql_queries.execute_query')
def test_get_patient_by_id_not_found(mock_execute_query):
    """Test retrieving a patient that doesn't exist."""
    # Mock the execute_query function to return an empty list
    mock_execute_query.return_value = []
    
    # Call the function
    patient = mysql_queries.get_patient_by_id(999)
    
    # Assertions
    assert patient is None
    mock_execute_query.assert_called_once()


@patch('app.mysql_queries.execute_query')
def test_search_patients(mock_execute_query):
    """Test searching for patients with filters."""
    # Mock the execute_query function to return all patients
    mock_execute_query.return_value = MOCK_PATIENTS
    
    # Call the function with some filters
    patients = mysql_queries.search_patients(
        name="Doe",
        min_age=30,
        sex="Male",
        limit=10
    )
    
    # Assertions
    assert patients == MOCK_PATIENTS
    mock_execute_query.assert_called_once()
    # Check that the query includes the filters
    query = mock_execute_query.call_args[0][0]
    assert "WHERE" in query
    assert "LIMIT 10" in query


@patch('app.mysql_queries.execute_query')
def test_get_samples_by_patient_id(mock_execute_query):
    """Test retrieving samples for a patient."""
    # Filter mock samples for patient 1
    patient_samples = [s for s in MOCK_SAMPLES if s["patient_id"] == 1]
    mock_execute_query.return_value = patient_samples
    
    # Call the function
    samples = mysql_queries.get_samples_by_patient_id(1)
    
    # Assertions
    assert samples == patient_samples
    mock_execute_query.assert_called_once()
    # Check that the query includes the patient ID
    assert "WHERE patient_id = %s" in mock_execute_query.call_args[0][0]
    assert mock_execute_query.call_args[0][1] == (1,)


@patch('app.mysql_queries.execute_query')
def test_get_sample_by_id(mock_execute_query):
    """Test retrieving a sample by ID."""
    # Mock the execute_query function to return a single sample
    mock_execute_query.return_value = [MOCK_SAMPLES[0]]
    
    # Call the function
    sample = mysql_queries.get_sample_by_id(1)
    
    # Assertions
    assert sample == MOCK_SAMPLES[0]
    mock_execute_query.assert_called_once()
    # Check that the query includes the sample ID
    assert "WHERE sample_id = %s" in mock_execute_query.call_args[0][0]
    assert mock_execute_query.call_args[0][1] == (1,)


@patch('app.mysql_queries.execute_query')
def test_get_tests_by_sample_id(mock_execute_query):
    """Test retrieving tests for a sample."""
    # Filter mock tests for sample 1
    sample_tests = [t for t in MOCK_TESTS if t["sample_id"] == 1]
    mock_execute_query.return_value = sample_tests
    
    # Call the function
    tests = mysql_queries.get_tests_by_sample_id(1)
    
    # Assertions
    assert tests == sample_tests
    mock_execute_query.assert_called_once()
    # Check that the query includes the sample ID
    assert "WHERE sample_id = %s" in mock_execute_query.call_args[0][0]
    assert mock_execute_query.call_args[0][1] == (1,)


@patch('app.mysql_queries.get_patient_by_id')
@patch('app.mysql_queries.get_samples_by_patient_id')
@patch('app.mysql_queries.get_tests_by_sample_id')
def test_get_patient_summary(mock_get_tests, mock_get_samples, mock_get_patient):
    """Test retrieving a comprehensive patient summary."""
    # Setup mocks
    mock_get_patient.return_value = MOCK_PATIENTS[0]
    
    # Patient 1 samples
    patient_samples = [s for s in MOCK_SAMPLES if s["patient_id"] == 1]
    mock_get_samples.return_value = patient_samples
    
    # Tests for each sample
    mock_get_tests.side_effect = lambda sample_id: [t for t in MOCK_TESTS if t["sample_id"] == sample_id]
    
    # Call the function
    summary = mysql_queries.get_patient_summary(1)
    
    # Assertions
    assert summary["patient"] == MOCK_PATIENTS[0]
    assert summary["total_samples"] == len(patient_samples)
    assert "total_tests" in summary
    
    # Verify each sample has its tests
    for sample in summary["samples"]:
        assert "tests" in sample
        assert sample["tests"] == [t for t in MOCK_TESTS if t["sample_id"] == sample["sample_id"]]
    
    # Check function calls
    mock_get_patient.assert_called_once_with(1)
    mock_get_samples.assert_called_once_with(1)
    assert mock_get_tests.call_count == len(patient_samples)


@patch('app.mysql_queries.get_patient_by_id')
def test_get_patient_summary_not_found(mock_get_patient):
    """Test retrieving a summary for a patient that doesn't exist."""
    # Setup mocks
    mock_get_patient.return_value = None
    
    # Call the function
    summary = mysql_queries.get_patient_summary(999)
    
    # Assertions
    assert "error" in summary
    assert summary["error"] == "Patient not found"
    mock_get_patient.assert_called_once_with(999)


@patch('app.mysql_queries.execute_query')
def test_get_test_with_details(mock_execute_query):
    """Test retrieving detailed test information."""
    # First call gets the test with basic info
    mock_execute_query.side_effect = [
        # First call: test with joined sample and patient info
        [{
            **MOCK_TESTS[0],
            "sample_type": MOCK_SAMPLES[0]["sample_type"],
            "collection_date": MOCK_SAMPLES[0]["collection_date"],
            "external_sample_id": MOCK_SAMPLES[0]["external_sample_id"],
            "first_name": MOCK_PATIENTS[0]["first_name"],
            "last_name": MOCK_PATIENTS[0]["last_name"],
            "date_of_birth": MOCK_PATIENTS[0]["date_of_birth"],
            "sex": MOCK_PATIENTS[0]["sex"],
            "medical_record_number": MOCK_PATIENTS[0]["medical_record_number"]
        }],
        # Second call: quality metrics
        [m for m in MOCK_QUALITY_METRICS if m["test_id"] == 1]
    ]
    
    # Call the function
    test_details = mysql_queries.get_test_with_details(1)
    
    # Assertions
    assert test_details is not None
    assert test_details["test_id"] == 1
    assert "quality_metrics" in test_details
    assert len(test_details["quality_metrics"]) == 2  # Two metrics for test 1
    
    # Check that the query was called twice
    assert mock_execute_query.call_count == 2


if __name__ == "__main__":
    pytest.main(['-xvs', __file__]) 