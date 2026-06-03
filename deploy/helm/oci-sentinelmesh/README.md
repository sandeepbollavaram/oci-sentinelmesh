# OCI-SentinelMesh Helm Chart

Helm chart for local/mock-first OCI-SentinelMesh deployments.

Build local images from the repository root:

```powershell
docker build -f apps/api/Dockerfile -t oci-sentinelmesh-api:local .
docker build -f apps/dashboard/Dockerfile -t oci-sentinelmesh-dashboard:local apps/dashboard
```

Install:

```powershell
helm install oci-sentinelmesh deploy/helm/oci-sentinelmesh
```

Port forward:

```powershell
kubectl -n oci-sentinelmesh port-forward svc/oci-sentinelmesh-api 8000:8000
kubectl -n oci-sentinelmesh port-forward svc/oci-sentinelmesh-dashboard 5173:5173
```

Uninstall:

```powershell
helm uninstall oci-sentinelmesh -n oci-sentinelmesh
kubectl delete namespace oci-sentinelmesh
```

This chart uses local images by default and does not include secrets, OCI credentials, cloud resource creation, or auto-remediation.
