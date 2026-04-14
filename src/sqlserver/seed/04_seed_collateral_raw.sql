-- ============================================================
-- Seed: collateral_raw
-- Collateral records linked to secured loan applications
-- ============================================================

USE loan_db;
GO

INSERT INTO dbo.collateral_raw
    (collateral_id, application_id, collateral_type, collateral_value,
     appraisal_date, appraisal_company, load_timestamp)
VALUES
('COL-001', 'APP-001', 'REAL_ESTATE', 300000.00, '2024-01-10',
 'Apex Appraisal Inc',        '2024-01-15T00:00:00'),
('COL-002', 'APP-002', 'VEHICLE',      18000.00, '2024-02-05',
 'Blue Book Auto Valuations', '2024-02-10T00:00:00'),
('COL-003', 'APP-004', 'REAL_ESTATE', 220000.00, '2024-03-10',
 'Apex Appraisal Inc',        '2024-03-15T00:00:00'),
('COL-004', 'APP-008', 'REAL_ESTATE', 150000.00, '2024-04-05',
 'Prime Property Valuers',    '2024-04-11T00:00:00'),
('COL-005', 'APP-009', 'VEHICLE',      14000.00, '2024-04-10',
 'Blue Book Auto Valuations', '2024-04-13T00:00:00');
GO
