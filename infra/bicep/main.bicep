targetScope = 'resourceGroup'

@description('Environment name (dev or prod)')
@allowed(['dev', 'prod'])
param environmentName string = 'dev'

@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Contoso project name prefix')
param projectName string = 'contoso-loan'

@description('Microsoft Entra object ID for the deployment administrator')
param adminObjectId string

@description('Microsoft Entra user or service principal name for SQL administrator')
param adminPrincipalName string

@description('Microsoft Entra principal type for the deployment administrator')
@allowed(['User', 'Group', 'Application'])
param adminPrincipalType string = 'User'

var projectToken = toLower(replace(projectName, '-', ''))
var resourceToken = uniqueString(subscription().id, resourceGroup().id, location, environmentName)
var resourcePrefix = 'az${substring(projectToken, 0, min(length(projectToken), 3))}${resourceToken}'

module keyVault 'keyvault.bicep' = {
  name: 'keyVaultDeploy'
  params: {
    environmentName: environmentName
    location: location
    resourcePrefix: resourcePrefix
    adminObjectId: adminObjectId
    adminPrincipalType: adminPrincipalType
  }
}

module sqlServer 'sql.bicep' = {
  name: 'sqlServerDeploy'
  params: {
    environmentName: environmentName
    location: location
    resourcePrefix: resourcePrefix
    keyVaultName: keyVault.outputs.keyVaultName
    sqlAdminEntraObjectId: adminObjectId
    sqlAdminEntraLogin: adminPrincipalName
    sqlAdminEntraPrincipalType: adminPrincipalType
  }
}

module storage 'storage.bicep' = {
  name: 'storageDeploy'
  params: {
    environmentName: environmentName
    location: location
    resourcePrefix: resourcePrefix
  }
}

output sqlServerFqdn string = sqlServer.outputs.sqlServerFqdn
output keyVaultUri string = keyVault.outputs.keyVaultUri
output storageAccountName string = storage.outputs.storageAccountName
