variable "service_name"{

}

resource "signalfx_single_value_chart" "chart" {
    name = "Single Value Chart for ${var.service_name}"
    program_text = "hello"
}

output "chart" {
    value = chart
}