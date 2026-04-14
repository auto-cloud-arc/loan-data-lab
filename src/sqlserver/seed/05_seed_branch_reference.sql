-- ============================================================
-- Seed: branch_reference
-- Reference data for branch validation and enrichment
-- ============================================================

USE loan_db;
GO

MERGE dbo.branch_reference AS target
USING (VALUES
('BR-01', 'Los Angeles Downtown',  'West',      'CA', 1),
('BR-02', 'Chicago North Side',    'Midwest',   'IL', 1),
('BR-03', 'Boston Back Bay',       'Northeast', 'MA', 1),
('BR-04', 'Houston Energy Corridor','South',    'TX', 1),
('BR-05', 'New York Midtown',      'Northeast', 'NY', 0)
) AS source (branch_code, branch_name, region, state_code, is_active)
ON target.branch_code = source.branch_code
WHEN MATCHED THEN
	UPDATE SET
		branch_name = source.branch_name,
		region = source.region,
		state_code = source.state_code,
		is_active = source.is_active
WHEN NOT MATCHED THEN
	INSERT (branch_code, branch_name, region, state_code, is_active)
	VALUES (source.branch_code, source.branch_name, source.region, source.state_code, source.is_active);
GO
