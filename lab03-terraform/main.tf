terraform {
  required_version = ">= 1.0"
}

# Deploy the Containerlab topology
resource "null_resource" "deploy_topology" {
  triggers = {
    topology_file = filemd5("${path.module}/topology.clab.yml")
  }

  provisioner "local-exec" {
    command = "containerlab deploy -t ${path.module}/topology.clab.yml --reconfigure --skip-post-deploy"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "containerlab destroy -t ${path.module}/topology.clab.yml --cleanup"
  }
}
