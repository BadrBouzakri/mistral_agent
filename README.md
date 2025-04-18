# Mistral Agent DevOps

Un assistant IA en ligne de commande basé sur le modèle Mistral pour les tâches DevOps et d'administration système.

## Caractéristiques

- **Interface en ligne de commande** avec prompt personnalisé et coloré
- **Exécution de commandes shell** directement depuis l'agent
- **Création de scripts** (Bash, Python, YAML, Dockerfile, Terraform, etc.)
- **Outils DevOps intégrés** pour Docker, Kubernetes, analyse de logs, monitoring, scan réseau, etc.
- **Templates prêts à l'emploi** pour Docker, Kubernetes, Terraform, Ansible
- **Commandes rapides** prédéfinies pour les tâches courantes
- **Navigation complète** dans le système de fichiers
- **Interface moderne** avec affichage coloré grâce à la bibliothèque `rich`
- **Support du français et de l'anglais**
- **Sécurité intégrée** avec confirmation pour les commandes destructives
- **Journalisation** des actions dans `~/.ia_agent_logs.log`

## Installation

1. Clonez ce dépôt :
```bash
git clone https://github.com/BadrBouzakri/mistral_agent.git
cd mistral_agent
```

2. Exécutez le script d'installation :
```bash
chmod +x install.sh
./install.sh
```

3. Redémarrez votre terminal ou exécutez :
```bash
source ~/.bashrc  # ou ~/.zshrc si vous utilisez zsh
```

## Utilisation

Lancez l'agent en mode interactif :
```bash
mistral
```

Options disponibles :
- `--lang fr|en` : Définir la langue (français par défaut)
- `--debug` : Activer le mode debug
- `--scripts-dir` : Spécifier un dossier pour les scripts
- `--start-dir` : Définir le répertoire de démarrage
- `--shell-completion` : Installer la complétion shell
- `--command, -c` : Exécuter une commande puis quitter
- `--file, -f` : Exécuter les commandes d'un fichier puis quitter
- `--update-sysinfo` : Mettre à jour les informations système
- `--theme` : Définir le thème (dark/light)

### Exemples d'utilisation

Exécuter une commande unique :
```bash
mistral -c "Crée un script python pour monitorer l'utilisation CPU"
```

Exécuter des commandes à partir d'un fichier :
```bash
mistral -f commandes.txt
```

Utiliser les outils DevOps intégrés :
```bash
mistral
🤖 DevOps@home $ devops
# Affiche la liste des outils DevOps disponibles

🤖 DevOps@home $ devops-docker_info
# Affiche les informations Docker
```

### Commandes intégrées

- `exit`, `quit` : Quitter l'agent
- `clear` : Effacer l'écran
- `pwd` : Afficher le répertoire courant
- `cd [path]` : Changer de répertoire
- `ls` : Afficher les fichiers avec coloration
- `sysinfo` : Afficher les informations système
- `history` : Afficher l'historique des commandes
- `quickcmds` : Afficher les commandes rapides disponibles
- `alias` : Gérer les alias
- `template [type]` : Afficher/utiliser les modèles
- `devops` : Afficher les outils DevOps disponibles

## Configuration

L'agent stocke sa configuration dans `~/.mistral_agent_config.json` et enregistre les scripts générés dans `~/tech/scripts/` par défaut.

## Prérequis

- Python 3.6+
- Bibliothèques : `rich`, `typer`, `requests`, `psutil`
- Une clé API Mistral (configurée dans le fichier principal)

## Licence

MIT

## Contributeurs

- [Badr Bouzakri](https://github.com/BadrBouzakri)
