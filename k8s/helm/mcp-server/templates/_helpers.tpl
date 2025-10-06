{{/*
Expand the name of the chart.
*/}}
{{- define "mcp-server.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "mcp-server.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "mcp-server.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "mcp-server.labels" -}}
helm.sh/chart: {{ include "mcp-server.chart" . }}
{{ include "mcp-server.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: mcp-platform
app.kubernetes.io/component: server
{{- end }}

{{/*
Selector labels
*/}}
{{- define "mcp-server.selectorLabels" -}}
app.kubernetes.io/name: {{ include "mcp-server.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "mcp-server.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "mcp-server.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the configmap
*/}}
{{- define "mcp-server.configmapName" -}}
{{- printf "%s-config" (include "mcp-server.fullname" .) }}
{{- end }}

{{/*
Create the name of the secret
*/}}
{{- define "mcp-server.secretName" -}}
{{- printf "%s-secrets" (include "mcp-server.fullname" .) }}
{{- end }}

{{/*
Create Redis connection URL
*/}}
{{- define "mcp-server.redisUrl" -}}
{{- if .Values.redis.enabled }}
{{- if .Values.redis.auth.enabled }}
{{- printf "redis://:%s@%s-redis-master:6379" .Values.redis.auth.password (include "mcp-server.fullname" .) }}
{{- else }}
{{- printf "redis://%s-redis-master:6379" (include "mcp-server.fullname" .) }}
{{- end }}
{{- else }}
{{- .Values.externalRedis.url | default "redis://localhost:6379" }}
{{- end }}
{{- end }}

{{/*
Generate certificates for webhook
*/}}
{{- define "mcp-server.webhookCerts" -}}
{{- $altNames := list ( printf "%s.%s" (include "mcp-server.fullname" .) .Release.Namespace ) ( printf "%s.%s.svc" (include "mcp-server.fullname" .) .Release.Namespace ) -}}
{{- $ca := genCA "mcp-server-ca" 365 -}}
{{- $cert := genSignedCert ( include "mcp-server.fullname" . ) nil $altNames 365 $ca -}}
tls.crt: {{ $cert.Cert | b64enc }}
tls.key: {{ $cert.Key | b64enc }}
ca.crt: {{ $ca.Cert | b64enc }}
{{- end }}

{{/*
Return the appropriate apiVersion for ingress.
*/}}
{{- define "mcp-server.ingress.apiVersion" -}}
{{- if and (.Capabilities.APIVersions.Has "networking.k8s.io/v1") (semverCompare ">= 1.19-0" .Capabilities.KubeVersion.Version) -}}
{{- print "networking.k8s.io/v1" -}}
{{- else if .Capabilities.APIVersions.Has "networking.k8s.io/v1beta1" -}}
{{- print "networking.k8s.io/v1beta1" -}}
{{- else -}}
{{- print "extensions/v1beta1" -}}
{{- end -}}
{{- end -}}

{{/*
Return if ingress is stable.
*/}}
{{- define "mcp-server.ingress.isStable" -}}
{{- eq (include "mcp-server.ingress.apiVersion" .) "networking.k8s.io/v1" -}}
{{- end -}}

{{/*
Return if ingress supports ingressClassName.
*/}}
{{- define "mcp-server.ingress.supportsIngressClassName" -}}
{{- or (eq (include "mcp-server.ingress.isStable" .) "true") (and (eq (include "mcp-server.ingress.apiVersion" .) "networking.k8s.io/v1beta1") (semverCompare ">= 1.18-0" .Capabilities.KubeVersion.Version)) -}}
{{- end -}}

{{/*
Return if ingress supports pathType.
*/}}
{{- define "mcp-server.ingress.supportsPathType" -}}
{{- or (eq (include "mcp-server.ingress.isStable" .) "true") (and (eq (include "mcp-server.ingress.apiVersion" .) "networking.k8s.io/v1beta1") (semverCompare ">= 1.18-0" .Capabilities.KubeVersion.Version)) -}}
{{- end -}}