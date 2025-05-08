import logging
from pathlib import Path
import subprocess
import sys

import yaml


def load_config(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def create_deployment_file(config):
    service_root = config["service"]
    service_name = service_root["name"]
    image_used = service_root["image"]
    replicas = service_root["replicas"]

    deployment_content = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": service_name},
        "spec": {
            "replicas": replicas,
            "selector": {"matchLabels": {"app": service_name}},
            "template": {
                "metadata": {"labels": {"app": service_name}},
                "spec": {
                    "containers": [
                        {
                            "name": service_name,
                            "image": image_used,
                            "ports": [{"containerPort": 80}],
                        }
                    ]
                },
            },
        },
    }

    return deployment_content


def save_yaml(content, output_file):
    with open(output_file, "w") as f:
        yaml.dump(content, f)


def apply_kubectl(deployment_file):
    try:
        subprocess.run(["echo", "kubectl", "apply", "-f", deployment_file], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Unable to execute command: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path_to_config_file = sys.argv[1]
        config = load_config(path_to_config_file)
        deployment_file_content = create_deployment_file(config)
        path_to_deployment_file = Path("./infra/k8s/deployment.yaml")
        save_yaml(deployment_file_content, path_to_deployment_file)
        apply_kubectl(path_to_deployment_file)
