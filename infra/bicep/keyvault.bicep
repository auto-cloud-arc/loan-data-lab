@description('Environment name')
param environmentName string

@description('Azure region')
param location string

@description('Resource prefix for naming')
param resourcePrefix string

@description('Object ID of the principal (user or service principal) that receives admin access')
param adminObjectId string = ''

@description('Principal type of the admin object')
@allowed(['User', 'Group', 'Application'])
param adminPrincipalType string = 'User'

var keyVaultRolePrincipalType = adminPrincipalType == 'Application' ? 'ServicePrincipal' : adminPrincipalType

var rawKeyVaultName = '${resourcePrefix}kv'
// Key Vault names must be 3–24 characters; truncate if needed
var keyVaultName = length(rawKeyVaultName) > 24 ? substring(rawKeyVaultName, 0, 24) : rawKeyVaultName

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enabledForDeployment: false
    enabledForTemplateDeployment: true
    enabledForDiskEncryption: false
    enableSoftDelete: true
    softDeleteRetentionInDays: environmentName == 'prod' ? 90 : 7
    enableRbacAuthorization: true
    publicNetworkAccess: 'Enabled'
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

resource adminRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(adminObjectId)) {
  name: guid(keyVault.id, adminObjectId, 'Key Vault Administrator')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '00482a5a-887f-4fb3-b363-3b7fe8e74483')
    principalId: adminObjectId
    principalType: keyVaultRolePrincipalType
  }
}

output keyVaultName string = keyVault.name
output keyVaultUri string = keyVault.properties.vaultUri
output keyVaultId string = keyVault.id
