# Classe principale de l'agent
class MistralAgent:
    def __init__(self, language="fr", debug=False):
        # Création du répertoire pour les scripts s'il n'existe pas
        os.makedirs(SCRIPTS_DIR, exist_ok=True)
        
        self.debug = debug
        self.language = language
        self.console = Console() if HAS_RICH else None
        self.conversation_history = []
        self.load_history()
        self.setup_signal_handlers()
        
        # Conserver le répertoire de travail actuel
        self.current_dir = os.getcwd()
        
        # Informations système
        self.system_info = {}
        self.collect_system_info()
        
        # Outils DevOps
        self.devops_tools = DevOpsTools()
        
        # Message système initial qui explique le rôle de l'agent
        self.system_message = f"""
Tu es un agent IA d'administration système et DevOps basé sur le modèle Mistral, conçu pour assister dans les tâches Linux et DevOps avancées.
Tu es un expert en gestion de systèmes Linux, réseau, Docker, Kubernetes, CI/CD, automatisation, et déploiement.

Tu travailles actuellement sur un système avec les caractéristiques suivantes:
- OS: {self.system_info.get('os-version', 'Linux')}
- Kernel: {self.system_info.get('kernel-version', 'Unknown')}
- Hostname: {self.system_info.get('hostname', 'Unknown')}
- CPU: {self.system_info.get('cpu-model', 'Unknown')}
- Mémoire: {self.system_info.get('total-memory', 'Unknown')}

Tu peux exécuter des commandes shell, créer des scripts et naviguer dans le système de fichiers.
Voici comment tu dois répondre:

1. Pour une commande à exécuter directement: [EXEC] commande [/EXEC]
2. Pour créer un script: [SCRIPT type nom_fichier] contenu [/SCRIPT]
3. Pour du texte normal: Réponds simplement sans aucun tag spécial
4. Pour naviguer entre les répertoires: [EXEC] cd chemin [/EXEC]
5. Pour utiliser un modèle: [TEMPLATE type nom_fichier]
6. Pour lancer une commande rapide: [QUICKCMD nom_commande paramètres]
7. Pour utiliser des outils DevOps intégrés: [DEVOPS outil paramètres]

N'utilise pas de formatage markdown complexe. Sois concis et précis.
Lorsque l'utilisateur demande de l'aide sur un sujet, donne des exemples pratiques et concrets.
Pour les commandes dangereuses, avertis l'utilisateur d'abord et demande confirmation.

Outils DevOps disponibles:
- [DEVOPS monitor_ressources [durée]]
- [DEVOPS analyze_logs fichier [pattern] [tail=N]]
- [DEVOPS docker_info]
- [DEVOPS k8s_info]
- [DEVOPS network_scan target]
- [DEVOPS generate_ssl_cert domaine]
"""
        # Personnalisation selon la langue
        self.prompt_prefix = "🤖 DevOps@" if language == "fr" else "🤖 DevOps@"
        
        # Charger ou créer le fichier de configuration
        self.config_file = os.path.expanduser("~/.mistral_agent_config.json")
        self.config = self.load_config()
        
    def load_config(self):
        """Charge ou crée le fichier de configuration"""
        default_config = {
            "theme": "dark",
            "max_history": MAX_HISTORY_ENTRIES,
            "default_scripts_dir": SCRIPTS_DIR,
            "custom_commands": {},
            "aliases": {},
            "favorites": []
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Erreur lors du chargement de la configuration: {e}")
                return default_config
        else:
            # Créer le fichier de configuration avec les valeurs par défaut
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
            except Exception as e:
                logging.error(f"Erreur lors de la création de la configuration: {e}")
                return default_config
    
    def save_config(self):
        """Sauvegarde le fichier de configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde de la configuration: {e}")
            
    def collect_system_info(self):
        """Collecte des informations sur le système"""
        for key, command in SYSTEM_INFO_COMMANDS.items():
            try:
                result = subprocess.run(command, shell=True, text=True, capture_output=True)
                if result.returncode == 0:
                    self.system_info[key] = result.stdout.strip()
                else:
                    self.system_info[key] = "Non disponible"
            except Exception:
                self.system_info[key] = "Erreur"

    def setup_signal_handlers(self):
        """Configure les gestionnaires de signaux pour une sortie propre"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Gère les signaux d'interruption"""
        print("\nFermeture propre de l'agent Mistral...")
        self.save_history()
        sys.exit(0)

    def load_history(self):
        """Charge l'historique des conversations"""
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.conversation_history = json.load(f)
                    # Limiter la taille de l'historique
                    if len(self.conversation_history) > MAX_HISTORY_ENTRIES:
                        self.conversation_history = self.conversation_history[-MAX_HISTORY_ENTRIES:]
            except Exception as e:
                logging.error(f"Erreur lors du chargement de l'historique: {e}")
                self.conversation_history = []
    
    def save_history(self):
        """Sauvegarde l'historique des conversations"""
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde de l'historique: {e}")

    def get_prompt(self):
        """Affiche le prompt personnalisé avec le répertoire courant"""
        # Mettre à jour le prompt avec le répertoire actuel
        dir_name = os.path.basename(self.current_dir)
        if dir_name == "":  # Si on est à la racine
            dir_name = "/"
            
        # Collecter des infos système pour l'affichage dans le prompt
        try:
            current_load = self.system_info.get('load-average', '').split()[0]
            memory_used = self.system_info.get('used-memory', 'N/A')
            disk_usage = self.system_info.get('disk-usage-root', 'N/A')
        except (IndexError, KeyError):
            current_load = "N/A"
            memory_used = "N/A"
            disk_usage = "N/A"
            
        # Prompt complet avec infos système
        if self.language == "fr":
            status_info = f"[L:{current_load}|M:{memory_used}|D:{disk_usage}]"
        else:
            status_info = f"[L:{current_load}|M:{memory_used}|D:{disk_usage}]"
            
        prompt = f"{self.prompt_prefix}{dir_name} {status_info} $ "
        
        if HAS_RICH:
            # Colorisation du prompt en fonction de la charge système
            try:
                load = float(current_load)
                if load < 1.0:
                    load_color = "green"
                elif load < 2.0:
                    load_color = "yellow"
                else:
                    load_color = "red"
            except (ValueError, TypeError):
                load_color = "cyan"
                
            # Formater le prompt avec Rich
            prompt_styled = f"[bold cyan]{self.prompt_prefix}[/bold cyan][bold blue]{dir_name}[/bold blue] [bold {load_color}]{status_info}[/bold {load_color}] $ "
            return self.console.input(prompt_styled)
        else:
            return input(prompt)

    def is_dangerous_command(self, command):
        """Vérifie si une commande est potentiellement dangereuse"""
        command_parts = shlex.split(command)
        if not command_parts:
            return False
            
        base_cmd = command_parts[0]
        
        # Vérifier les commandes dangereuses directes
        if base_cmd in DANGEROUS_COMMANDS:
            return True
            
        # Vérifier les redirections et pipes dangereux
        if ">" in command or "|" in command and ("rm" in command or "mv" in command):
            return True
            
        # Vérifier les options dangereuses spécifiques
        if base_cmd == "rm" and "-rf" in command_parts:
            return True
            
        return False