output "secured_url" {
  value       = "https://${local.secured_domain}"
  description = "The url to access GenMedia Studio UI (with Google Managed certificate)."
}
