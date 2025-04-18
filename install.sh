#!/bin/bash

# Script d'installation pour l'agent Mistral DevOps
# Ce script installe les dépendances nécessaires et configure l'agent Mistral optimisé pour DevOps

set -e

echo "🤖 Installation de l'agent Mistral DevOps..."

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Installation en cours..."
    sudo apt update
    sudo apt install -y python3 python3-pip
else
    echo "✅ Python 3 est déjà installé"
fi

# Créer un environnement virtuel pour l'agent
AGENT_DIR="$HOME/.mistral_agent"
mkdir -p "$AGENT_DIR"

echo "📁 Création de l'environnement virtuel..."
python3 -m venv "$AGENT_DIR/venv"
source "$AGENT_DIR/venv/bin/activate"

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install rich typer requests psutil

# Créer le répertoire pour les scripts
SCRIPTS_DIR="$HOME/tech/scripts"
mkdir -p "$SCRIPTS_DIR"
echo "📁 Répertoire de scripts créé: $SCRIPTS_DIR"

# Copier le script principal
echo "📝 Configuration de l'agent..."
cp mistral_agent.py "$AGENT_DIR/"
chmod +x "$AGENT_DIR/mistral_agent.py"

# Créer un alias pour l'agent
SHELL_CONFIG="$HOME/.bashrc"
if [ -f "$HOME/.zshrc" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
fi

# Vérifier si l'alias existe déjà
if ! grep -q "alias mistral=" "$SHELL_CONFIG"; then
    echo "🔧 Ajout de l'alias 'mistral' à $SHELL_CONFIG..."
    echo "" >> "$SHELL_CONFIG"
    echo "# Agent Mistral IA DevOps" >> "$SHELL_CONFIG"
    echo "alias mistral='$AGENT_DIR/venv/bin/python3 $AGENT_DIR/mistral_agent.py'" >> "$SHELL_CONFIG"
    echo 'export PATH="$PATH:$HOME/tech/scripts"' >> "$SHELL_CONFIG"
else
    echo "✅ L'alias 'mistral' existe déjà dans $SHELL_CONFIG"
fi

# Création du fichier d'exécution
cat > "$AGENT_DIR/run.sh" << 'EOF'
#!/bin/bash
source "$HOME/.mistral_agent/venv/bin/activate"
python3 "$HOME/.mistral_agent/mistral_agent.py" "$@"
EOF

chmod +x "$AGENT_DIR/run.sh"

# Créer un lien symbolique dans /usr/local/bin
echo "🔗 Création d'un lien symbolique pour l'agent..."
if [ -w "/usr/local/bin" ]; then
    sudo ln -sf "$AGENT_DIR/run.sh" /usr/local/bin/mistral
else
    echo "⚠️ Impossible de créer le lien symbolique dans /usr/local/bin (besoin de droits sudo)"
    echo "   Vous pouvez utiliser l'alias 'mistral' après avoir rechargé votre shell"
fi

# Installation des outils complémentaires (Docker, K8s, etc.)
echo "🧰 Vérification des outils DevOps..."

# Docker
if ! command -v docker &> /dev/null; then
    echo "ℹ️ Docker n'est pas installé. Pour l'installer, exécutez:"
    echo "   curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh"
else
    echo "✅ Docker est déjà installé"
fi

# kubectl
if ! command -v kubectl &> /dev/null; then
    echo "ℹ️ kubectl n'est pas installé. Pour l'installer, exécutez:"
    echo "   curl -LO 'https://dl.k8s.io/release/stable.txt'"
    echo "   curl -LO 'https://dl.k8s.io/release/$(cat stable.txt)/bin/linux/amd64/kubectl'"
    echo "   chmod +x kubectl && sudo mv kubectl /usr/local/bin/"
else
    echo "✅ kubectl est déjà installé"
fi

# Terraform
if ! command -v terraform &> /dev/null; then
    echo "ℹ️ Terraform n'est pas installé. Pour l'installer, exécutez:"
    echo "   wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg"
    echo "   echo 'deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main' | sudo tee /etc/apt/sources.list.d/hashicorp.list"
    echo "   sudo apt update && sudo apt install terraform"
else
    echo "✅ Terraform est déjà installé"
fi

# Ansible
if ! command -v ansible &> /dev/null; then
    echo "ℹ️ Ansible n'est pas installé. Pour l'installer, exécutez:"
    echo "   sudo apt update && sudo apt install -y ansible"
else
    echo "✅ Ansible est déjà installé"
fi

echo ""
echo "✅ Installation terminée!"
echo "🚀 Pour démarrer l'agent, vous pouvez:"
echo "   1. Recharger votre shell avec 'source $SHELL_CONFIG' puis utiliser la commande 'mistral'"
echo "   2. Ou exécuter directement '$AGENT_DIR/run.sh'"
echo ""
echo "Options disponibles:"
echo "   --lang fr|en        : Définir la langue (français par défaut)"
echo "   --debug             : Activer le mode debug"
echo "   --scripts-dir       : Spécifier un dossier pour les scripts"
echo "   --start-dir         : Définir le répertoire de démarrage"
echo "   --shell-completion  : Installer la complétion shell"
echo "   --command, -c       : Exécuter une commande puis quitter"
echo "   --file, -f          : Exécuter les commandes d'un fichier puis quitter"
echo "   --update-sysinfo    : Mettre à jour les informations système"
echo "   --theme             : Définir le thème (dark/light)"
echo ""
echo "Exemples:"
echo "   mistral --lang en"
echo "   mistral --start-dir ~/projets"
echo "   mistral -c 'créer un script pour surveiller le cpu'"
echo "   mistral -f commandes.txt"
echo ""
echo "📂 Navigation et fonctionnalités:"
echo "   • Commandes intégrées: cd, ls, pwd, sysinfo, history, quickcmds, alias, template"
echo "   • Templates DevOps: docker, kubernetes, terraform, ansible"
echo "   • Commandes rapides spécialisées pour les tâches SysAdmin et DevOps"
echo "   • Mise en forme améliorée pour les résultats de commandes"
echo "   • Outils DevOps intégrés pour une expérience complète"

# Recharger le shell si possible
if [[ "$0" = "$BASH_SOURCE" ]]; then
    echo "Rechargement du shell..."
    exec "$SHELL"
fi