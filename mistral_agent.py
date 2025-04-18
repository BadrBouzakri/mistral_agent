#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mistral Agent DevOps - Un assistant IA pour terminal Linux
Utilise le modèle Mistral pour assister dans les tâches DevOps et SysAdmin
"""

import os
import sys
import re
import json
import logging
import readline
import subprocess
import requests
from datetime import datetime
import argparse
from typing import List, Dict, Any, Optional, Tuple
import shlex
import signal

# Bibliothèques pour l'interface
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.syntax import Syntax
    from rich import box
    import typer
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    print("Pour une meilleure expérience visuelle, installez rich et typer: pip install rich typer")

# Paramètres constants
API_KEY = "n46jy69eatOFdxAI7Rb0PXsj6jrVv16K"
API_URL = "https://api.mistral.ai/v1/chat/completions"
MODEL = "mistral-large-latest"
SCRIPTS_DIR = os.path.expanduser("~/tech/scripts")
LOG_FILE = os.path.expanduser("~/.ia_agent_logs.log")
HISTORY_FILE = os.path.expanduser("~/.ia_agent_history.json")
MAX_HISTORY_ENTRIES = 20
DANGEROUS_COMMANDS = ["rm", "mv", "dd", "mkfs", "fdisk", ">", "2>", "truncate", "rmdir", "pkill", "kill", 
                     "shutdown", "reboot", "halt", "systemctl stop", "systemctl restart", "chown", "chmod", 
                     "userdel", "groupdel", "deluser", "passwd", "parted", "lvremove", "vgremove", "pvremove",
                     "iptables -F", "ufw disable"]

# Extensions de fichiers pour les différents types de scripts
SCRIPT_EXTENSIONS = {
    "python": ".py",
    "bash": ".sh",
    "shell": ".sh",
    "yaml": ".yaml",
    "yml": ".yml",
    "docker": ".dockerfile",
    "dockerfile": ".dockerfile",
    "terraform": ".tf",
    "json": ".json",
    "js": ".js",
    "ansible": ".yml",
    "php": ".php",
    "ruby": ".rb",
    "go": ".go",
    "java": ".java",
    "c": ".c",
    "cpp": ".cpp",
    "csharp": ".cs",
    "sql": ".sql",
    "kubernetes": ".yaml",
    "k8s": ".yaml",
    "helm": ".yaml",
    "nginx": ".conf",
    "apache": ".conf",
    "systemd": ".service",
    "prometheus": ".yml",
    "grafana": ".json",
    "jenkins": "Jenkinsfile",
    "gitlab-ci": ".gitlab-ci.yml",
    "github-workflow": ".yml",
}

# Modèles pour différentes tâches DevOps
TEMPLATES = {
    "docker": """FROM alpine:latest

LABEL maintainer="Your Name <your.email@example.com>"

RUN apk --no-cache add ca-certificates

WORKDIR /app

COPY . .

CMD ["sh"]
""",
    "terraform": """provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  tags = {
    Name = "example-instance"
  }
}
""",
    "kubernetes": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
""",
    "ansible": """---
- name: Example Playbook
  hosts: all
  become: yes
  tasks:
    - name: Ensure a package is installed
      apt:
        name: nginx
        state: present
      when: ansible_os_family == "Debian"
    
    - name: Ensure a service is running
      service:
        name: nginx
        state: started
        enabled: yes
"""
}

# Commandes rapides pour les tâches courantes
QUICK_COMMANDS = {
    # Gestion des services
    "service-status": "systemctl status {service}",
    "service-start": "systemctl start {service}",
    "service-stop": "systemctl stop {service}",
    "service-restart": "systemctl restart {service}",
    "service-enable": "systemctl enable {service}",
    "service-disable": "systemctl disable {service}",
    "service-list": "systemctl list-units --type=service",
    
    # Supervision système
    "cpu-info": "lscpu",
    "mem-info": "free -h",
    "disk-usage": "df -h",
    "top-processes": "ps aux | sort -nrk 3,3 | head -n 10",
    "check-port": "ss -tuln | grep {port}",
    "cpu-load": "mpstat 1 5",
    "io-stats": "iostat -xz 1 5",
    
    # Réseau
    "ping-host": "ping -c 4 {host}",
    "check-ip": "ip addr show",
    "route-table": "ip route",
    "dns-lookup": "dig {domain}",
    "open-ports": "netstat -tuln",
    "traceroute": "traceroute {host}",
    
    # Docker
    "docker-ps": "docker ps",
    "docker-images": "docker images",
    "docker-stats": "docker stats --no-stream",
    "docker-prune": "docker system prune -f",
    
    # Kubernetes
    "k8s-pods": "kubectl get pods",
    "k8s-nodes": "kubectl get nodes",
    "k8s-deployments": "kubectl get deployments",
    "k8s-services": "kubectl get services",
    
    # Journaux
    "logs-system": "journalctl -xe",
    "logs-service": "journalctl -u {service} -f",
    "logs-auth": "tail -n 50 /var/log/auth.log",
    "logs-kernel": "dmesg | tail -n 50",
    
    # Gestion des paquets
    "apt-update": "sudo apt update && sudo apt list --upgradable",
    "apt-upgrade": "sudo apt upgrade -y",
    "pkg-installed": "dpkg -l | grep {package}",
    
    # Surveillance fichiers
    "find-large-files": "find {path} -type f -size +{size}M -exec ls -lh {} \\;",
    "tail-file": "tail -f {file}",
    "find-modified": "find {path} -type f -mtime -{days} -ls",
    
    # Git
    "git-status": "git status",
    "git-log": "git log --oneline --graph --decorate -n 10",
}

# Commandes pour récupérer des informations système
SYSTEM_INFO_COMMANDS = {
    "os-version": "cat /etc/os-release",
    "kernel-version": "uname -a",
    "hostname": "hostname -f",
    "uptime": "uptime",
    "cpu-model": "cat /proc/cpuinfo | grep 'model name' | head -n 1 | cut -d ':' -f 2 | xargs",
    "total-memory": "free -h | grep Mem | awk '{print $2}'",
    "used-memory": "free -h | grep Mem | awk '{print $3}'",
    "disk-usage-root": "df -h / | tail -n 1 | awk '{print $5}'",
    "load-average": "cat /proc/loadavg | awk '{print $1, $2, $3}'",
    "users-logged-in": "who | wc -l",
    "process-count": "ps aux | wc -l",
    "network-interfaces": "ip -br addr show",
}

# Initialisation du logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)