# Azure Container Apps

Deploy with Azure Developer CLI from this template directory:

```bash
cd deploy/azure
azd auth login
azd init --environment semantica-ke
azd env set AZURE_LOCATION eastus
azd up
```

The Bicep template provisions a Container Apps managed environment, HTTP ingress, scale-to-zero, max 10 replicas, and a `/api/health` liveness probe.
