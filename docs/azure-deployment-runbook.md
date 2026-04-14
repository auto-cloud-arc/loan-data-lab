# Azure Deployment Runbook

This runbook captures the Azure deployment configuration that is currently working for this repository.

## Scope

- Subscription: `976c53b8-965c-4f97-ab51-993195a8623c`
- Resource group: `loan-data-rg`
- Environment: `dev`
- Region: `centralus`

## Live Azure Resources

- Azure SQL logical server: `azconkizafydob4k3msql`
- Azure SQL database: `loan_db`
- Key Vault: `azconkizafydob4k3mkv`
- Key Vault URI: `https://azconkizafydob4k3mkv.vault.azure.net/`
- Storage account: `azconkizafydob4k3msa000`
- Blob containers:
  - `loan-raw-extracts`
  - `loan-cleaned`

## Authentication Model

- Azure SQL is configured for Microsoft Entra-only authentication.
- The `SqlConnectionString` secret in Key Vault uses `Authentication=Active Directory Default`.
- GitHub Actions uses a dedicated service principal as both the deployment identity and the Azure SQL Entra administrator.

## GitHub Environment Secrets

Environment: `dev`

Required secrets:

- `AZURE_CREDENTIALS`
- `AZURE_RG`
- `AZURE_SQL_ADMIN_OBJECT_ID`
- `AZURE_SQL_ADMIN_LOGIN`
- `AZURE_SQL_ADMIN_PRINCIPAL_TYPE`

Expected values:

- `AZURE_RG=loan-data-rg`
- `AZURE_SQL_ADMIN_LOGIN=loan-data-lab-gh-dev`
- `AZURE_SQL_ADMIN_PRINCIPAL_TYPE=Application`

## Workflow

Workflow file: `.github/workflows/deploy-azure-sql-and-config.yml`

What it does:

1. Deploys Bicep infrastructure.
2. Resolves the deployed SQL server FQDN from the ARM deployment outputs.
3. Installs the `SQLServer` PowerShell module.
4. Runs SQL scripts against Azure SQL with an Entra access token.

## SQL Files Applied By Workflow

The SQL deployment job currently applies files in this order:

1. `src/sqlserver/schema/01_create_tables.sql`
2. `src/sqlserver/seed/02_seed_loan_application_raw.sql`
3. `src/sqlserver/seed/03_seed_customer_raw.sql`
4. `src/sqlserver/seed/04_seed_collateral_raw.sql`
5. `src/sqlserver/seed/05_seed_branch_reference.sql`

## Manual Rerun

To rerun the workflow from GitHub:

1. Open the repository Actions tab.
2. Select `Deploy Azure SQL & Config`.
3. Choose `Run workflow`.
4. Select `dev`.

To rerun from CLI:

```bash
gh workflow run deploy-azure-sql-and-config.yml --repo auto-cloud-arc/loan-data-lab -f environment=dev
```

To inspect the latest run from CLI:

```bash
gh run list --repo auto-cloud-arc/loan-data-lab --workflow deploy-azure-sql-and-config.yml --limit 5
```

## Manual SQL Script Execution

After `az login`, use the helper script:

```powershell
$sqlFiles = @(
  'src/sqlserver/schema/01_create_tables.sql'
  'src/sqlserver/seed/02_seed_loan_application_raw.sql'
  'src/sqlserver/seed/03_seed_customer_raw.sql'
  'src/sqlserver/seed/04_seed_collateral_raw.sql'
  'src/sqlserver/seed/05_seed_branch_reference.sql'
)

pwsh ./src/sqlserver/scripts/apply_sql_files.ps1 `
  -ServerInstance azconkizafydob4k3msql.database.windows.net `
  -Database loan_db `
  -SqlFiles $sqlFiles
```

## Notes

- `infra/parameters/dev.parameters.json` must remain on `centralus` for this subscription because SQL provisioning in `eastus` is restricted.
- If the GitHub workflow fails in the SQL job at `Azure Login`, confirm the job is attached to the `dev` environment so it can access environment-scoped secrets.
- If the Bicep deployment fails on Azure SQL policy, verify the SQL server template still sets the inline `administrators` block with `azureADOnlyAuthentication: true`.
