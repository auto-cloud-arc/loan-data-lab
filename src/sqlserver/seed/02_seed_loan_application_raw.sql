-- ============================================================
-- Seed: loan_application_raw
-- Includes intentional data quality issues for workshop use:
--   APP-005: future application date
--   APP-006: missing customer_id
--   APP-007: negative loan amount
--   APP-010: invalid application date string (handled by C# parser)
-- ============================================================

USE loan_db;
GO

MERGE dbo.loan_application_raw AS target
USING (VALUES
-- Clean records
('APP-001', 'CUST-001', 'BR-01', 250000.00, 'MORTGAGE',
 '2024-01-15', 'John', 'Doe', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3',
 '5555551234', '123 Main St', 'Los Angeles', 'ca', '90210',
 'b94f6f125179b4d18a7a39b876c7233da3d7a20bb76a7e6a7c33ad17bb3f2a47',
 300000.00, 'BRANCH_INTAKE_v2', GETUTCDATE()),

('APP-002', 'CUST-002', 'BR-02', 15000.00, 'AUTO',
 '2024-02-10', 'Jane', 'Smith', 'c3499c2729730a7f807efb8676a92dcb6f8a3f8f1c33aee5db76c22df63e1b1c',
 '555-555-9876', '456 Oak Ave', 'Chicago', 'IL', '60601',
 'd7a8fbb307d7809469d49e4a0d5c14b4d5c1ab5e13e29c0b3c7d1e56d7e3f2a1',
 18000.00, 'BRANCH_INTAKE_v2', GETUTCDATE()),

('APP-003', 'CUST-003', 'BR-01', 5000.00, 'PERSONAL',
 '2024-03-01', 'Bob', 'Jones', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
 '5554441234', '789 Pine Rd', 'Houston', 'tx', '77001',
 'f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2',
 NULL, 'BRANCH_INTAKE_v2', GETUTCDATE()),

('APP-004', 'CUST-001', 'BR-03', 180000.00, 'MORTGAGE',
 '2024-03-15', 'John', 'Doe', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3',
 '5555551234', '123 Main St', 'Los Angeles', 'CA', '90210',
 'b94f6f125179b4d18a7a39b876c7233da3d7a20bb76a7e6a7c33ad17bb3f2a47',
 220000.00, 'BRANCH_INTAKE_v2', GETUTCDATE()),

-- DQ Issue: future application date (2099)
('APP-005', 'CUST-004', 'BR-02', 750000.00, 'BUSINESS',
 '2099-04-01', 'Alice', 'Brown', 'd4e0f3b2a1c8e9f7d6b5a4c3e2f1d0b9a8c7e6f5d4b3a2c1e0f9d8b7a6c5e4f3',
 '5552221234', '100 Corp Blvd', 'New York', 'NY', '10001',
 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2',
 NULL, 'BRANCH_INTAKE_v2', GETUTCDATE()),

-- DQ Issue: missing customer_id
('APP-006', NULL, 'BR-01', 25000.00, 'AUTO',
 '2024-04-10', 'Charlie', 'Wilson', 'b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2',
 '5553331234', '321 Elm St', 'Phoenix', 'AZ', '85001',
 'c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3',
 28000.00, 'BRANCH_INTAKE_v2', GETUTCDATE()),

-- DQ Issue: negative loan amount
('APP-007', 'CUST-005', 'BR-99', -500.00, 'MORTGAGE',
 '2024-04-12', 'Diana', 'Prince', 'd3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4',
 '5554441234', '555 Hero Ave', 'Seattle', 'WA', '98101',
 'e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5',
 500000.00, 'BRANCH_INTAKE_v2', GETUTCDATE()),

-- Clean records
('APP-008', 'CUST-006', 'BR-03', 95000.00, 'HELOC',
 '2024-04-11', 'Eve', 'Adams', 'f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6',
 '5556661234', '777 Garden St', 'Boston', 'MA', '02101',
 'a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7',
 150000.00, 'BRANCH_INTAKE_v2', GETUTCDATE()),

('APP-009', 'CUST-007', 'BR-02', 12000.00, 'AUTO',
 '2024-04-13', 'Frank', 'Castle', 'b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8',
 '5557771234', '888 Punisher Rd', 'Miami', 'FL', '33101',
 'c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9',
 14000.00, 'BRANCH_INTAKE_v2', GETUTCDATE()),

-- DQ Issue: application_date is not a valid date value
('APP-010', 'CUST-008', 'BR-01', 30000.00, 'PERSONAL',
 NULL, 'Grace', 'Hopper', 'd9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0',
 '5558881234', '999 Navy Pier', 'Annapolis', 'MD', '21401',
 'e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1',
 NULL, 'BRANCH_INTAKE_v2', GETUTCDATE())
) AS source (
    application_id, customer_id, branch_code, loan_amount, loan_type,
    application_date, first_name, last_name, ssn_hash, phone_number,
    address_line1, city, state_code, zip_code, email_hash,
    collateral_value, source_system, load_timestamp
)
ON target.application_id = source.application_id
WHEN MATCHED THEN
    UPDATE SET
        customer_id = source.customer_id,
        branch_code = source.branch_code,
        loan_amount = source.loan_amount,
        loan_type = source.loan_type,
        application_date = source.application_date,
        first_name = source.first_name,
        last_name = source.last_name,
        ssn_hash = source.ssn_hash,
        phone_number = source.phone_number,
        address_line1 = source.address_line1,
        city = source.city,
        state_code = source.state_code,
        zip_code = source.zip_code,
        email_hash = source.email_hash,
        collateral_value = source.collateral_value,
        source_system = source.source_system,
        load_timestamp = source.load_timestamp
WHEN NOT MATCHED THEN
    INSERT (
        application_id, customer_id, branch_code, loan_amount, loan_type,
        application_date, first_name, last_name, ssn_hash, phone_number,
        address_line1, city, state_code, zip_code, email_hash,
        collateral_value, source_system, load_timestamp
    )
    VALUES (
        source.application_id, source.customer_id, source.branch_code, source.loan_amount, source.loan_type,
        source.application_date, source.first_name, source.last_name, source.ssn_hash, source.phone_number,
        source.address_line1, source.city, source.state_code, source.zip_code, source.email_hash,
        source.collateral_value, source.source_system, source.load_timestamp
    );
GO
