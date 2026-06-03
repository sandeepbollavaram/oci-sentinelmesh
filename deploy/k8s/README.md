# Kubernetes Manifests

Local-development Kubernetes manifests for OCI-SentinelMesh.

Build local images from the repository root:

```powershell
docker build -f apps/api/Dockerfile -t oci-sentinelmesh-api:local .
docker build -f apps/dashboard/Dockerfile -t oci-sentinelmesh-dashboard:local apps/dashboard
```

Apply manifests:

```powershell
kubectl apply -k deploy/k8s
```

Port forward services:

```powershell
kubectl -n oci-sentinelmesh port-forward svc/oci-sentinelmesh-api 8000:8000
kubectl -n oci-sentinelmesh port-forward svc/oci-sentinelmesh-dashboard 5173:5173
```

Remove local resources:

```powershell
kubectl delete namespace oci-sentinelmesh
```

These manifests are mock/local-first and do not include secrets, OCI credentials, cloud resource creation, or auto-remediation.
