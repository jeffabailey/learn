# Read from a CSV file, then create files based on the CSV file content
locals {
    csv_data = file("example.csv")
    instances = csvdecode(local.csv_data)
}

resource "local_file" "foo" {
    for_each = { for inst in local.instances : inst.filename=> inst }
    content     = each.value.filecontent
    filename = each.value.filename
}