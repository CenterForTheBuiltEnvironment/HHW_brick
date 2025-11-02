"""
Brick Application Deployment Module

This module provides functionality to deploy and manage Brick applications for HHWS.


Author: Mingchen Li
"""

import logging
import yaml
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import subprocess
import shutil


class BrickDeployment:
    """
    Handles deployment and management of Brick applications for HHWS.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Brick deployment manager.

        Args:
            config_path: Path to deployment configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config = {}
        self.deployment_dir = Path("./deployments")

        if config_path:
            self.load_config(config_path)

    def load_config(self, config_path: str) -> None:
        """Load deployment configuration from file."""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                if config_path.endswith(".yaml") or config_path.endswith(".yml"):
                    self.config = yaml.safe_load(f)
                elif config_path.endswith(".json"):
                    self.config = json.load(f)
                else:
                    raise ValueError("Config file must be .yaml, .yml, or .json")
            self.logger.info(f"Loaded deployment config from {config_path}")
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            raise

    def deploy_application(self, app_config: Dict[str, Any]) -> bool:
        """
        Deploy a Brick application.

        Args:
            app_config: Application configuration dictionary

        Returns:
            bool: True if deployment successful, False otherwise
        """
        try:
            app_name = app_config.get("name", "hhws_app")
            self.logger.info(f"Starting deployment of {app_name}")

            # Create deployment directory
            app_dir = self.deployment_dir / app_name
            app_dir.mkdir(parents=True, exist_ok=True)

            # Deploy based on deployment type
            deployment_type = app_config.get("type", "local")

            if deployment_type == "local":
                return self._deploy_local(app_config, app_dir)
            elif deployment_type == "docker":
                return self._deploy_docker(app_config, app_dir)
            elif deployment_type == "kubernetes":
                return self._deploy_kubernetes(app_config, app_dir)
            else:
                raise ValueError(f"Unsupported deployment type: {deployment_type}")

        except Exception as e:
            self.logger.error(f"Deployment failed: {e}")
            return False

    def _deploy_local(self, config: Dict[str, Any], app_dir: Path) -> bool:
        """Deploy application locally."""
        try:
            # Copy application files
            source_dir = Path(config.get("source_dir", "./"))
            if source_dir.exists():
                shutil.copytree(source_dir, app_dir / "app", dirs_exist_ok=True)

            # Create startup script
            startup_script = app_dir / "start.sh"
            with open(startup_script, "w") as f:
                f.write(f"#!/bin/bash\n")
                f.write(f"cd {app_dir / 'app'}\n")
                f.write(f"python {config.get('main_file', 'main.py')}\n")

            startup_script.chmod(0o755)

            # Start application if requested
            if config.get("auto_start", False):
                return self.start_application(config["name"])

            return True

        except Exception as e:
            self.logger.error(f"Local deployment failed: {e}")
            return False

    def _deploy_docker(self, config: Dict[str, Any], app_dir: Path) -> bool:
        """Deploy application using Docker."""
        try:
            # Create Dockerfile if not exists
            dockerfile_path = app_dir / "Dockerfile"
            if not dockerfile_path.exists():
                self._create_dockerfile(config, dockerfile_path)

            # Create docker-compose.yml
            compose_path = app_dir / "docker-compose.yml"
            self._create_docker_compose(config, compose_path)

            # Build and start containers
            if config.get("auto_start", False):
                cmd = f"cd {app_dir} && docker-compose up -d"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.error(f"Docker deployment failed: {result.stderr}")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Docker deployment failed: {e}")
            return False

    def _deploy_kubernetes(self, config: Dict[str, Any], app_dir: Path) -> bool:
        """Deploy application to Kubernetes."""
        try:
            # Create Kubernetes manifests
            self._create_k8s_manifests(config, app_dir)

            # Apply manifests if requested
            if config.get("auto_start", False):
                cmd = f"kubectl apply -f {app_dir / 'k8s'}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.error(f"Kubernetes deployment failed: {result.stderr}")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Kubernetes deployment failed: {e}")
            return False

    def _create_dockerfile(self, config: Dict[str, Any], dockerfile_path: Path) -> None:
        """Create a Dockerfile for the application."""
        python_version = config.get("python_version", "3.9")

        dockerfile_content = f"""FROM python:{python_version}-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {config.get('port', 8000)}

CMD ["python", "{config.get('main_file', 'main.py')}"]
"""

        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)

    def _create_docker_compose(self, config: Dict[str, Any], compose_path: Path) -> None:
        """Create docker-compose.yml for the application."""
        compose_content = {
            "version": "3.8",
            "services": {
                config.get("name", "hhws_app"): {
                    "build": ".",
                    "ports": [f"{config.get('port', 8000)}:{config.get('port', 8000)}"],
                    "environment": config.get("environment", {}),
                    "volumes": config.get("volumes", []),
                    "restart": "unless-stopped",
                }
            },
        }

        with open(compose_path, "w") as f:
            yaml.dump(compose_content, f)

    def _create_k8s_manifests(self, config: Dict[str, Any], app_dir: Path) -> None:
        """Create Kubernetes manifests."""
        k8s_dir = app_dir / "k8s"
        k8s_dir.mkdir(exist_ok=True)

        app_name = config.get("name", "hhws-app")

        # Deployment manifest
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": app_name},
            "spec": {
                "replicas": config.get("replicas", 1),
                "selector": {"matchLabels": {"app": app_name}},
                "template": {
                    "metadata": {"labels": {"app": app_name}},
                    "spec": {
                        "containers": [
                            {
                                "name": app_name,
                                "image": config.get("image", f"{app_name}:latest"),
                                "ports": [{"containerPort": config.get("port", 8000)}],
                                "env": [
                                    {"name": k, "value": str(v)}
                                    for k, v in config.get("environment", {}).items()
                                ],
                            }
                        ]
                    },
                },
            },
        }

        with open(k8s_dir / "deployment.yaml", "w") as f:
            yaml.dump(deployment, f)

        # Service manifest
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": f"{app_name}-service"},
            "spec": {
                "selector": {"app": app_name},
                "ports": [
                    {"port": config.get("port", 8000), "targetPort": config.get("port", 8000)}
                ],
                "type": config.get("service_type", "ClusterIP"),
            },
        }

        with open(k8s_dir / "service.yaml", "w") as f:
            yaml.dump(service, f)

    def start_application(self, app_name: str) -> bool:
        """Start a deployed application."""
        try:
            app_dir = self.deployment_dir / app_name
            if not app_dir.exists():
                self.logger.error(f"Application {app_name} not found")
                return False

            # Check deployment type and start accordingly
            if (app_dir / "docker-compose.yml").exists():
                cmd = f"cd {app_dir} && docker-compose up -d"
            elif (app_dir / "start.sh").exists():
                cmd = f"cd {app_dir} && ./start.sh"
            else:
                self.logger.error(f"No start method found for {app_name}")
                return False

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info(f"Application {app_name} started successfully")
                return True
            else:
                self.logger.error(f"Failed to start {app_name}: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to start application: {e}")
            return False

    def stop_application(self, app_name: str) -> bool:
        """Stop a running application."""
        try:
            app_dir = self.deployment_dir / app_name
            if not app_dir.exists():
                self.logger.error(f"Application {app_name} not found")
                return False

            # Check deployment type and stop accordingly
            if (app_dir / "docker-compose.yml").exists():
                cmd = f"cd {app_dir} && docker-compose down"
            else:
                # For local deployments, we'd need to track PIDs
                self.logger.warning("Local application stop not implemented")
                return False

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info(f"Application {app_name} stopped successfully")
                return True
            else:
                self.logger.error(f"Failed to stop {app_name}: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to stop application: {e}")
            return False

    def list_applications(self) -> List[str]:
        """List all deployed applications."""
        if not self.deployment_dir.exists():
            return []

        return [d.name for d in self.deployment_dir.iterdir() if d.is_dir()]

    def get_application_status(self, app_name: str) -> Dict[str, Any]:
        """Get status of a deployed application."""
        app_dir = self.deployment_dir / app_name
        if not app_dir.exists():
            return {"status": "not_found"}

        status = {"status": "deployed", "type": "unknown"}

        if (app_dir / "docker-compose.yml").exists():
            status["type"] = "docker"
            # Check if containers are running
            cmd = f"cd {app_dir} && docker-compose ps -q"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                status["status"] = "running"
            else:
                status["status"] = "stopped"
        elif (app_dir / "start.sh").exists():
            status["type"] = "local"
            # For local apps, status checking would require process tracking
            status["status"] = "unknown"

        return status
