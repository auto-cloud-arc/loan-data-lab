-- ============================================================
-- Seed: branch_reference
-- Reference data for branch validation and enrichment
-- ============================================================

USE loan_db;
GO

INSERT INTO dbo.branch_reference (branch_code, branch_name, region, state_code, is_active)
VALUES
('BR-01', 'Los Angeles Downtown',  'West',      'CA', 1),
('BR-02', 'Chicago North Side',    'Midwest',   'IL', 1),
('BR-03', 'Boston Back Bay',       'Northeast', 'MA', 1),
('BR-04', 'Houston Energy Corridor','South',    'TX', 1),
('BR-05', 'New York Midtown',      'Northeast', 'NY', 0); -- inactive branch
GO
