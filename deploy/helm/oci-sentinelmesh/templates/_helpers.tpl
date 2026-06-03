{{- define "oci-sentinelmesh.namespace" -}}
{{- .Values.global.namespace -}}
{{- end -}}

{{- define "oci-sentinelmesh.name" -}}
{{- .Chart.Name -}}
{{- end -}}

{{- define "oci-sentinelmesh.apiName" -}}
{{- printf "%s-api" (include "oci-sentinelmesh.name" .) -}}
{{- end -}}

{{- define "oci-sentinelmesh.dashboardName" -}}
{{- printf "%s-dashboard" (include "oci-sentinelmesh.name" .) -}}
{{- end -}}
