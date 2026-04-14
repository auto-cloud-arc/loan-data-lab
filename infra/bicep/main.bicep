targetScope = 'resourceGroup'

@description('Environment name (dev or prod)')
@allowed(['dev', 'prod'])
param environmentName string = 'dev'

@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Contoso project name prefix')
param projectName string = 'contoso-loan'

var resourcePrefix = '${projectName}-${environmentName}'

module keyVault 'keyvault.bicep' = {
  name: 'keyVaultDeploy'
  params: {
    environmentName: environmentName
    location: location
    resourcePrefix: resourcePrefix
  }
}

module sqlServer 'sql.bicep' = {
  name: 'sqlServerDeploy'
  params: {
    environmentName: environmentName
    location: location
    resourcePrefix: resourcePrefix
    keyVaultName: keyVault.outputs.keyVaultName
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
