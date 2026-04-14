-- ============================================================
-- Seed: customer_raw
-- Includes intentional duplicate (CUST-001 loaded twice)
-- ============================================================

USE loan_db;
GO

INSERT INTO dbo.customer_raw
    (customer_id, first_name, last_name, date_of_birth, ssn_hash, email_hash,
     phone_number, address_line1, city, state_code, zip_code, credit_score, load_timestamp)
VALUES
-- CUST-001 appears twice — duplicate customer scenario for workshop
('CUST-001', 'John',  'Doe',    '1980-05-15',
 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3',
 'b94f6f125179b4d18a7a39b876c7233da3d7a20bb76a7e6a7c33ad17bb3f2a47',
 '5555551234', '123 Main St',  'Los Angeles', 'CA', '90210', 720,
 '2024-01-01T00:00:00Z'),

('CUST-001', 'John',  'Doe',    '1980-05-15',
 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3',
 'b94f6f125179b4d18a7a39b876c7233da3d7a20bb76a7e6a7c33ad17bb3f2a47',
 '5555551234', '123 Main St',  'Los Angeles', 'CA', '90210', 720,
 '2024-01-15T00:00:00Z'),

('CUST-002', 'Jane',  'Smith',  '1975-08-22',
 'c3499c2729730a7f807efb8676a92dcb6f8a3f8f1c33aee5db76c22df63e1b1c',
 'd7a8fbb307d7809469d49e4a0d5c14b4d5c1ab5e13e29c0b3c7d1e56d7e3f2a1',
 '5559876543', '456 Oak Ave',  'Chicago',     'IL', '60601', 680,
 '2024-01-01T00:00:00Z'),

('CUST-003', 'Bob',   'Jones',  '1992-11-30',
 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
 'f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2',
 '5554441234', '789 Pine Rd',  'Houston',     'TX', '77001', 590,
 '2024-01-01T00:00:00Z'),

('CUST-004', 'Alice', 'Brown',  '1988-03-14',
 'd4e0f3b2a1c8e9f7d6b5a4c3e2f1d0b9a8c7e6f5d4b3a2c1e0f9d8b7a6c5e4f3',
 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2',
 '5552221234', '100 Corp Blvd','New York',    'NY', '10001', 780,
 '2024-01-01T00:00:00Z'),

('CUST-005', 'Diana', 'Prince', '1985-07-04',
 'd3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4',
 'e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5',
 '5554441234', '555 Hero Ave', 'Seattle',     'WA', '98101', 810,
 '2024-01-01T00:00:00Z'),

('CUST-006', 'Eve',   'Adams',  '1990-12-25',
 'f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6',
 'a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7',
 '5556661234', '777 Garden St','Boston',      'MA', '02101', 740,
 '2024-01-01T00:00:00Z'),

('CUST-007', 'Frank', 'Castle', '1978-09-09',
 'b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8',
 'c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9',
 '5557771234', '888 Punisher Rd','Miami',     'FL', '33101', 650,
 '2024-01-01T00:00:00Z'),

('CUST-008', 'Grace', 'Hopper', '1906-12-09',
 'd9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0',
 'e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1',
 '5558881234', '999 Navy Pier', 'Annapolis',  'MD', '21401', 760,
 '2024-01-01T00:00:00Z');
GO
