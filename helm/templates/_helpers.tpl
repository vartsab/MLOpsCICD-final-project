{{- define "aiops-quality-service.name" -}}
{{- .Chart.Name -}}
{{- end -}}

{{- define "aiops-quality-service.fullname" -}}
{{- .Release.Name -}}
{{- end -}}
