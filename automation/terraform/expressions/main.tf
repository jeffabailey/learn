variable "sfx_auth_token" {
}

locals {
    services = {
        servicea = "Service A"
        serviceb = "Service B"
    }
}

# Configure the SignalFx provider
provider "signalfx" {
  auth_token = var.sfx_auth_token
  # If your organization uses a different realm
  # api_url = "https://api.us2.signalfx.com"
  # If your organization uses a custom URL
  # custom_app_url = "https://myorg.signalfx.com"
}

module "single_value_chart" {
    source = "./module"
    for_each = local.services
    service_name = local.services[count.index]
}

# Create a new dashboard
resource "signalfx_dashboard" "dashboard" {

}