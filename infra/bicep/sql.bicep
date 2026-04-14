@description('Environment name')
param environmentName string

@description('Azure region')
param location string

@description('Resource prefix for naming')
param resourcePrefix string

@description('Key Vault name for storing secrets')
param keyVaultName string

@description('Microsoft Entra object ID for the SQL administrator')
param sqlAdminEntraObjectId string

@description('Microsoft Entra login name for the SQL administrator')
param sqlAdminEntraLogin string

@description('Microsoft Entra principal type for the SQL administrator')
@allowed(['User', 'Group', 'Application'])
param sqlAdminEntraPrincipalType string = 'User'

var sqlServerName = '${resourcePrefix}sql'
var sqlDatabaseName = 'loan_db'

resource sqlServer 'Microsoft.Sql/servers@2024-11-01-preview' = {
  name: sqlServerName
  location: location
  properties: {
    administrators: {
      administratorType: 'ActiveDirectory'
      azureADOnlyAuthentication: true
      login: sqlAdminEntraLogin
      principalType: sqlAdminEntraPrincipalType
      sid: sqlAdminEntraObjectId
      tenantId: subscription().tenantId
    }
    version: '12.0'
    minimalTlsVersion: '1.2'
    publicNetworkAccess: environmentName == 'dev' ? 'Enabled' : 'Disabled'
  }
  tags: {
    environment: environmentName
    project: 'contoso-loan'
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2023-05-01-preview' = {
  parent: sqlServer
  name: sqlDatabaseName
  location: location
  sku: {
    name: environmentName == 'prod' ? 'S2' : 'Basic'
    tier: environmentName == 'prod' ? 'Standard' : 'Basic'
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    maxSizeBytes: environmentName == 'prod' ? 10737418240 : 2147483648
    zoneRedundant: false
  }
  tags: {
    environment: environmentName
    project: 'contoso-loan'
  }
}

resource allowAzureServices 'Microsoft.Sql/servers/firewallRules@2023-05-01-preview' = {
  parent: sqlServer
  name: 'AllowAllWindowsAzureIps'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

resource sqlConnectionStringSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'SqlConnectionString'
  properties: {
    value: 'Server=tcp:${sqlServer.properties.fullyQualifiedDomainName},1433;Initial Catalog=${sqlDatabaseName};Authentication=Active Directory Default;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;'
  }
}

output sqlServerFqdn string = sqlServer.properties.fullyQualifiedDomainName
output sqlDatabaseName string = sqlDatabaseName
output sqlServerName string = sqlServerName
