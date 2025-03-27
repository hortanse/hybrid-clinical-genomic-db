#!/usr/bin/env python3
"""
MySQL query functions for the Hybrid Clinical Genomics Database.

This module provides functions to query patient and sample data from MySQL database.
"""

import os
import mysql.connector
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_PORT = int(os.getenv("MYSQL_PORT", "3306"))
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = os.getenv("MYSQL_DATABASE", "genomics_db")


def get_mysql_connection():
    """
    Create and return a MySQL database connection.
    """
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except mysql.connector.Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        raise


def dict_factory(cursor, row):
    """
    Convert database row objects to dictionaries.
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def execute_query(query: str, params: Tuple = None) -> List[Dict[str, Any]]:
    """
    Execute a MySQL query and return results as a list of dictionaries.
    
    Args:
        query: SQL query string
        params: Query parameters as tuple
        
    Returns:
        List of dictionaries containing the query results
    """
    conn = None
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        results = cursor.fetchall()
        
        # Convert any datetime objects to string
        for row in results:
            for key, value in row.items():
                if isinstance(value, (datetime, date)):
                    row[key] = value.isoformat()
                    
        return results
    
    except mysql.connector.Error as e:
        logger.error(f"MySQL query error: {e}")
        logger.error(f"Query: {query}")
        if params:
            logger.error(f"Params: {params}")
        raise
    
    finally:
        if conn and conn.is_connected():
            conn.close()


def get_patient_by_id(patient_id: int) -> Optional[Dict[str, Any]]:
    """
    Get patient information by ID.
    
    Args:
        patient_id: Patient ID
        
    Returns:
        Dictionary with patient data or None if not found
    """
    query = """
    SELECT *
    FROM patients
    WHERE patient_id = %s
    """
    
    results = execute_query(query, (patient_id,))
    
    if results:
        return results[0]
    return None


def search_patients(
    name: Optional[str] = None,
    dob: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    sex: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Search patients based on filters.
    
    Args:
        name: Patient name (searches first_name and last_name)
        dob: Date of birth (YYYY-MM-DD)
        min_age: Minimum age in years
        max_age: Maximum age in years
        sex: Patient sex
        limit: Maximum number of results
        
    Returns:
        List of patient dictionaries
    """
    params = []
    conditions = []
    
    # Build WHERE clause based on provided parameters
    if name:
        conditions.append("(first_name LIKE %s OR last_name LIKE %s)")
        params.extend([f"%{name}%", f"%{name}%"])
    
    if dob:
        conditions.append("date_of_birth = %s")
        params.append(dob)
    
    if min_age is not None:
        min_dob = datetime.now().date().replace(year=datetime.now().year - min_age)
        conditions.append("date_of_birth <= %s")
        params.append(min_dob)
    
    if max_age is not None:
        max_dob = datetime.now().date().replace(year=datetime.now().year - max_age - 1)
        conditions.append("date_of_birth >= %s")
        params.append(max_dob)
    
    if sex:
        conditions.append("sex = %s")
        params.append(sex)
    
    # Construct the query
    query = "SELECT * FROM patients"
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += f" LIMIT {limit}"
    
    return execute_query(query, tuple(params))


def get_samples_by_patient_id(patient_id: int) -> List[Dict[str, Any]]:
    """
    Get all samples for a patient.
    
    Args:
        patient_id: Patient ID
        
    Returns:
        List of sample dictionaries
    """
    query = """
    SELECT *
    FROM samples
    WHERE patient_id = %s
    ORDER BY collection_date DESC
    """
    
    return execute_query(query, (patient_id,))


def get_sample_by_id(sample_id: int) -> Optional[Dict[str, Any]]:
    """
    Get sample information by ID.
    
    Args:
        sample_id: Sample ID
        
    Returns:
        Dictionary with sample data or None if not found
    """
    query = """
    SELECT *
    FROM samples
    WHERE sample_id = %s
    """
    
    results = execute_query(query, (sample_id,))
    
    if results:
        return results[0]
    return None


def get_sample_with_patient_info(sample_id: int) -> Optional[Dict[str, Any]]:
    """
    Get sample with joined patient information.
    
    Args:
        sample_id: Sample ID
        
    Returns:
        Dictionary with sample and patient data or None if not found
    """
    query = """
    SELECT s.*, p.first_name, p.last_name, p.date_of_birth, p.sex, p.medical_record_number
    FROM samples s
    JOIN patients p ON s.patient_id = p.patient_id
    WHERE s.sample_id = %s
    """
    
    results = execute_query(query, (sample_id,))
    
    if results:
        return results[0]
    return None


def get_tests_by_sample_id(sample_id: int) -> List[Dict[str, Any]]:
    """
    Get all tests for a sample.
    
    Args:
        sample_id: Sample ID
        
    Returns:
        List of test dictionaries
    """
    query = """
    SELECT *
    FROM clinical_tests
    WHERE sample_id = %s
    ORDER BY test_date DESC
    """
    
    return execute_query(query, (sample_id,))


def get_test_by_id(test_id: int) -> Optional[Dict[str, Any]]:
    """
    Get test information by ID.
    
    Args:
        test_id: Test ID
        
    Returns:
        Dictionary with test data or None if not found
    """
    query = """
    SELECT *
    FROM clinical_tests
    WHERE test_id = %s
    """
    
    results = execute_query(query, (test_id,))
    
    if results:
        return results[0]
    return None


def get_test_with_details(test_id: int) -> Optional[Dict[str, Any]]:
    """
    Get test with joined sample, patient, and panel information.
    
    Args:
        test_id: Test ID
        
    Returns:
        Dictionary with test, sample, patient, and panel data or None if not found
    """
    # First get the test with basic info
    test_query = """
    SELECT ct.*, s.sample_type, s.collection_date, s.external_sample_id,
           p.first_name, p.last_name, p.date_of_birth, p.sex, p.medical_record_number
    FROM clinical_tests ct
    JOIN samples s ON ct.sample_id = s.sample_id
    JOIN patients p ON s.patient_id = p.patient_id
    WHERE ct.test_id = %s
    """
    
    test_results = execute_query(test_query, (test_id,))
    
    if not test_results:
        return None
    
    test_data = test_results[0]
    
    # Get quality metrics
    metrics_query = """
    SELECT metric_name, metric_value, metric_unit, metric_pass, threshold_value
    FROM test_quality_metrics
    WHERE test_id = %s
    """
    
    metrics_results = execute_query(metrics_query, (test_id,))
    test_data['quality_metrics'] = metrics_results
    
    # Get panel information if it's a panel test
    if test_data['test_type'] == 'Panel':
        panel_query = """
        SELECT tp.*
        FROM test_panels tp
        JOIN test_panel_assignment tpa ON tp.panel_id = tpa.panel_id
        WHERE tpa.test_id = %s
        """
        
        panel_results = execute_query(panel_query, (test_id,))
        if panel_results:
            test_data['panel'] = panel_results[0]
    
    return test_data


def get_patient_summary(patient_id: int) -> Dict[str, Any]:
    """
    Get a complete patient summary including demographics, samples, and tests.
    
    Args:
        patient_id: Patient ID
        
    Returns:
        Dictionary with patient summary
    """
    # Get patient demographics
    patient = get_patient_by_id(patient_id)
    
    if not patient:
        return {"error": "Patient not found"}
    
    # Get all samples for the patient
    samples = get_samples_by_patient_id(patient_id)
    
    # Get all tests for each sample
    for sample in samples:
        sample['tests'] = get_tests_by_sample_id(sample['sample_id'])
    
    # Construct the summary
    summary = {
        "patient": patient,
        "samples": samples,
        "total_samples": len(samples),
        "total_tests": sum(len(sample['tests']) for sample in samples)
    }
    
    return summary


def search_samples(
    patient_id: Optional[int] = None,
    sample_type: Optional[str] = None,
    status: Optional[str] = None,
    collection_date_start: Optional[str] = None,
    collection_date_end: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Search samples based on filters.
    
    Args:
        patient_id: Filter by patient ID
        sample_type: Sample type
        status: Sample status
        collection_date_start: Collection date range start (YYYY-MM-DD)
        collection_date_end: Collection date range end (YYYY-MM-DD)
        limit: Maximum number of results
        
    Returns:
        List of sample dictionaries
    """
    params = []
    conditions = []
    
    # Build WHERE clause based on provided parameters
    if patient_id is not None:
        conditions.append("patient_id = %s")
        params.append(patient_id)
    
    if sample_type:
        conditions.append("sample_type = %s")
        params.append(sample_type)
    
    if status:
        conditions.append("status = %s")
        params.append(status)
    
    if collection_date_start:
        conditions.append("collection_date >= %s")
        params.append(collection_date_start)
    
    if collection_date_end:
        conditions.append("collection_date <= %s")
        params.append(collection_date_end)
    
    # Construct the query
    query = """
    SELECT s.*, p.first_name, p.last_name
    FROM samples s
    JOIN patients p ON s.patient_id = p.patient_id
    """
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY s.collection_date DESC"
    query += f" LIMIT {limit}"
    
    return execute_query(query, tuple(params))


def search_tests(
    sample_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    test_type: Optional[str] = None,
    result_status: Optional[str] = None,
    test_date_start: Optional[str] = None,
    test_date_end: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Search clinical tests based on filters.
    
    Args:
        sample_id: Filter by sample ID
        patient_id: Filter by patient ID
        test_type: Test type
        result_status: Result status
        test_date_start: Test date range start (YYYY-MM-DD)
        test_date_end: Test date range end (YYYY-MM-DD)
        limit: Maximum number of results
        
    Returns:
        List of test dictionaries
    """
    params = []
    conditions = []
    
    # Build WHERE clause based on provided parameters
    if sample_id is not None:
        conditions.append("ct.sample_id = %s")
        params.append(sample_id)
    
    if patient_id is not None:
        conditions.append("s.patient_id = %s")
        params.append(patient_id)
    
    if test_type:
        conditions.append("ct.test_type = %s")
        params.append(test_type)
    
    if result_status:
        conditions.append("ct.result_status = %s")
        params.append(result_status)
    
    if test_date_start:
        conditions.append("ct.test_date >= %s")
        params.append(test_date_start)
    
    if test_date_end:
        conditions.append("ct.test_date <= %s")
        params.append(test_date_end)
    
    # Construct the query
    query = """
    SELECT ct.*, s.sample_type, s.external_sample_id,
           p.patient_id, p.first_name, p.last_name
    FROM clinical_tests ct
    JOIN samples s ON ct.sample_id = s.sample_id
    JOIN patients p ON s.patient_id = p.patient_id
    """
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY ct.test_date DESC"
    query += f" LIMIT {limit}"
    
    return execute_query(query, tuple(params))


def get_sample_ids_by_patient_details(
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    sex: Optional[str] = None
) -> List[int]:
    """
    Get sample IDs based on patient demographic filters.
    This is useful for cross-database queries.
    
    Args:
        age_min: Minimum patient age
        age_max: Maximum patient age
        sex: Patient sex
        
    Returns:
        List of sample IDs
    """
    params = []
    conditions = []
    
    # Build WHERE clause based on provided parameters
    if age_min is not None:
        min_dob = datetime.now().date().replace(year=datetime.now().year - age_min)
        conditions.append("p.date_of_birth <= %s")
        params.append(min_dob)
    
    if age_max is not None:
        max_dob = datetime.now().date().replace(year=datetime.now().year - age_max - 1)
        conditions.append("p.date_of_birth >= %s")
        params.append(max_dob)
    
    if sex:
        conditions.append("p.sex = %s")
        params.append(sex)
    
    # Construct the query
    query = """
    SELECT s.sample_id
    FROM samples s
    JOIN patients p ON s.patient_id = p.patient_id
    """
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    results = execute_query(query, tuple(params))
    return [result['sample_id'] for result in results] 