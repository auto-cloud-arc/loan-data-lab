@description('Environment name')
param environmentName string

@description('Azure region')
param location string

@description('Resource prefix for naming')
param resourcePrefix string

var storageAccountName = '${resourcePrefix}sa000'
var rawExtractContainerName = 'loan-raw-extracts'
var cleanedContainerName = 'loan-cleaned'

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: length(storageAccountName) > 24 ? substring(storageAccountName, 0, 24) : storageAccountName
  location: location
  sku: {
    name: environmentName == 'prod' ? 'Standard_GRS' : 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    accessTier: 'Hot'
    encryption: {
      services: {
        blob: {
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
  tags: {
    environment: environmentName
    project: 'contoso-loan'
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
  properties: {
    deleteRetentionPolicy: {
      enabled: true
      days: environmentName == 'prod' ? 30 : 7
    }
  }
}

resource rawExtractContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: rawExtractContainerName
  properties: {
    publicAccess: 'None'
  }
}

resource cleanedContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: cleanedContainerName
  properties: {
    publicAccess: 'None'
  }
}

output storageAccountName string = storageAccount.name
output storageAccountId string = storageAccount.id
output rawExtractContainerName string = rawExtractContainerName
output cleanedContainerName string = cleanedContainerName
