-- MySQL Schema for Clinical Genomics Database
-- Version 1.0

-- Drop existing tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS clinical_tests;
DROP TABLE IF EXISTS samples;
DROP TABLE IF EXISTS patients;

-- Create patients table
CREATE TABLE patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    sex ENUM('Male', 'Female', 'Other', 'Unknown') NOT NULL,
    medical_record_number VARCHAR(20) UNIQUE,
    contact_phone VARCHAR(20),
    contact_email VARCHAR(100),
    address_line1 VARCHAR(100),
    address_line2 VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(50),
    postal_code VARCHAR(20),
    country VARCHAR(50) DEFAULT 'United States',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_patient_name (last_name, first_name),
    INDEX idx_patient_dob (date_of_birth)
) ENGINE=InnoDB;

-- Create samples table
CREATE TABLE samples (
    sample_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    sample_type ENUM('Blood', 'Saliva', 'Tissue', 'Buccal', 'Other') NOT NULL,
    collection_date DATE NOT NULL,
    received_date DATE NOT NULL,
    status ENUM('Received', 'Processing', 'Completed', 'Failed', 'Canceled') NOT NULL DEFAULT 'Received',
    external_sample_id VARCHAR(50),
    collection_method VARCHAR(100),
    collection_site VARCHAR(100),
    specimen_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_sample_patient (patient_id),
    INDEX idx_sample_dates (collection_date, received_date)
) ENGINE=InnoDB;

-- Create clinical tests table
CREATE TABLE clinical_tests (
    test_id INT AUTO_INCREMENT PRIMARY KEY,
    sample_id INT NOT NULL,
    test_type ENUM('WGS', 'WES', 'Panel', 'SNP', 'RNA-seq', 'Other') NOT NULL,
    test_date DATE NOT NULL,
    test_code VARCHAR(50) NOT NULL,
    test_name VARCHAR(100) NOT NULL,
    ordering_physician VARCHAR(100),
    result_summary TEXT,
    result_status ENUM('Pending', 'Preliminary', 'Final', 'Amended', 'Canceled', 'Failed') NOT NULL DEFAULT 'Pending',
    report_date DATE,
    report_version INT DEFAULT 1,
    report_file_path VARCHAR(255),
    turnaround_time INT COMMENT 'TAT in days',
    test_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sample_id) REFERENCES samples(sample_id) ON DELETE CASCADE,
    INDEX idx_test_sample (sample_id),
    INDEX idx_test_type (test_type),
    INDEX idx_test_status (result_status),
    INDEX idx_test_code (test_code)
) ENGINE=InnoDB;

-- Additional metadata tables

-- Panel information
CREATE TABLE test_panels (
    panel_id INT AUTO_INCREMENT PRIMARY KEY,
    panel_code VARCHAR(50) NOT NULL UNIQUE,
    panel_name VARCHAR(100) NOT NULL,
    panel_version VARCHAR(20) NOT NULL,
    genes_included INT NOT NULL COMMENT 'Number of genes in the panel',
    panel_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_panel_code (panel_code)
) ENGINE=InnoDB;

-- Link table between clinical_tests and test_panels
CREATE TABLE test_panel_assignment (
    test_id INT NOT NULL,
    panel_id INT NOT NULL,
    PRIMARY KEY (test_id, panel_id),
    FOREIGN KEY (test_id) REFERENCES clinical_tests(test_id) ON DELETE CASCADE,
    FOREIGN KEY (panel_id) REFERENCES test_panels(panel_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Quality metrics for clinical tests
CREATE TABLE test_quality_metrics (
    metric_id INT AUTO_INCREMENT PRIMARY KEY,
    test_id INT NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_unit VARCHAR(50),
    metric_pass BOOLEAN,
    threshold_value FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_id) REFERENCES clinical_tests(test_id) ON DELETE CASCADE,
    INDEX idx_metric_test (test_id),
    INDEX idx_metric_name (metric_name)
) ENGINE=InnoDB; 