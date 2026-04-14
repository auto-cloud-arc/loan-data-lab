param(
    [Parameter(Mandatory = $true)]
    [string]$ServerInstance,

    [Parameter(Mandatory = $true)]
    [string]$Database,

    [Parameter(Mandatory = $true)]
    [string[]]$SqlFiles
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Module -ListAvailable -Name SQLServer)) {
    throw 'SQLServer PowerShell module is required. Install-Module SQLServer -Scope CurrentUser'
}

Import-Module SQLServer

$accessToken = az account get-access-token --resource https://database.windows.net/ --query accessToken -o tsv

if ([string]::IsNullOrWhiteSpace($accessToken)) {
    throw 'Failed to acquire an Azure SQL access token from Azure CLI.'
}

foreach ($sqlFile in $SqlFiles) {
    if (-not (Test-Path $sqlFile)) {
        throw "SQL file not found: $sqlFile"
    }

    Write-Host "Applying $sqlFile to $ServerInstance/$Database"
    Invoke-Sqlcmd -ServerInstance $ServerInstance -Database $Database -AccessToken $accessToken -InputFile $sqlFile -EncryptConnection
}