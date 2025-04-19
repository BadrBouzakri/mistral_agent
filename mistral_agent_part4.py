    def execute_command(self, command):
        """Exécute une commande shell et retourne le résultat"""
        logging.info(f"Exécution de la commande: {command}")
        
        # Vérifier les alias personnalisés
        for alias, cmd in self.config.get("aliases", {}).items():
            if command.strip() == alias or command.strip().startswith(f"{alias} "):
                # Remplacer l'alias par la commande complète
                command = command.replace(alias, cmd, 1)
                break
        
        # Gestion spéciale pour la commande cd
        if command.strip().startswith("cd "):
            try:
                # Extraire le chemin cible
                target_dir = command.strip()[3:].strip()
                
                # Gestion des chemins relatifs ou absolus
                if target_dir.startswith('/'):
                    new_dir = target_dir  # Chemin absolu
                else:
                    new_dir = os.path.join(self.current_dir, target_dir)
                
                # Résoudre les chemins comme ../ ou ./
                new_dir = os.path.abspath(new_dir)
                
                # Vérifier si le répertoire existe
                if os.path.isdir(new_dir):
                    os.chdir(new_dir)
                    self.current_dir = new_dir
                    # Mettre à jour les informations système
                    self.collect_system_info()
                    return f"Répertoire courant : {new_dir}"
                else:
                    return f"Erreur: Le répertoire {new_dir} n'existe pas."
            except Exception as e:
                logging.error(f"Erreur lors du changement de répertoire: {e}")
                return f"Erreur lors du changement de répertoire: {str(e)}"
        
        # Ajout à l'historique des commandes
        if command not in ['pwd', 'clear'] and not command.startswith('ls'):
            if 'command_history' not in self.config:
                self.config['command_history'] = []
            
            # Ajouter la commande à l'historique avec horodatage
            self.config['command_history'].append({
                'command': command,
                'timestamp': datetime.now().isoformat(),
                'directory': self.current_dir
            })
            
            # Limiter la taille de l'historique
            if len(self.config['command_history']) > 100:
                self.config['command_history'] = self.config['command_history'][-100:]
                
            # Sauvegarder la configuration
            self.save_config()
        
        # Pour les autres commandes, vérifier si elles sont dangereuses
        if self.is_dangerous_command(command):
            if HAS_RICH:
                self.console.print(f"[bold yellow]⚠️ Commande potentiellement dangereuse:[/bold yellow] {command}")
                self.console.print("[bold yellow]Cette commande pourrait avoir des effets destructifs sur votre système.[/bold yellow]")
                confirm = Confirm.ask("Confirmer l'exécution?")
            else:
                print(f"⚠️ Commande potentiellement dangereuse: {command}")
                print("Cette commande pourrait avoir des effets destructifs sur votre système.")
                confirm = input("Confirmer l'exécution? [o/N] ").lower() == 'o'
            
            if not confirm:
                return "Commande annulée par l'utilisateur."
        
        try:
            # Exécuter la commande dans le répertoire courant
            process = subprocess.Popen(
                command, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                cwd=self.current_dir  # Utiliser le répertoire courant
            )
            stdout, stderr = process.communicate()
            
            result = stdout.decode('utf-8')
            error = stderr.decode('utf-8')
            
            if process.returncode != 0:
                return f"Erreur (code {process.returncode}):\n{error}"
            else:
                # Mettre à jour les informations système après certaines commandes
                if any(cmd in command for cmd in ['apt', 'yum', 'dnf', 'systemctl', 'docker', 'kubectl']):
                    self.collect_system_info()
                return result
        except Exception as e:
            logging.error(f"Erreur lors de l'exécution de la commande: {e}")
            return f"Erreur: {str(e)}"

    def save_script(self, script_type, filename, content):
        """Sauvegarde un script généré dans le répertoire approprié"""
        # Détermination de l'extension appropriée
        has_extension = "." in filename
        
        # Si pas d'extension et qu'on a un type connu, ajouter l'extension
        if not has_extension and script_type.lower() in SCRIPT_EXTENSIONS:
            filename = filename + SCRIPT_EXTENSIONS[script_type.lower()]
            
        # Chemin complet du fichier
        filepath = os.path.join(SCRIPTS_DIR, filename)
        
        # Sauvegarde du fichier
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Rendre exécutable les scripts appropriés
            if script_type.lower() in ["bash", "shell", "python", "sh", "py"]:
                os.chmod(filepath, 0o755)
                
            logging.info(f"Script {script_type} sauvegardé: {filepath}")
            return filepath
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde du script: {e}")
            return f"Erreur lors de la sauvegarde: {str(e)}"
            
    def create_from_template(self, template_type, filename):
        """Crée un fichier à partir d'un modèle prédéfini"""
        template_type = template_type.lower()
        
        if template_type not in TEMPLATES:
            return f"Erreur: Modèle '{template_type}' non disponible. Templates disponibles: {', '.join(TEMPLATES.keys())}"
        
        # Détermination de l'extension appropriée
        has_extension = "." in filename
        
        # Si pas d'extension et qu'on a un type connu, ajouter l'extension
        if not has_extension and template_type in SCRIPT_EXTENSIONS:
            filename = filename + SCRIPT_EXTENSIONS[template_type]
            
        # Chemin complet du fichier
        filepath = os.path.join(self.current_dir, filename)
        
        # Sauvegarde du fichier
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(TEMPLATES[template_type])
                
            logging.info(f"Fichier créé à partir du modèle {template_type}: {filepath}")
            return f"Fichier créé à partir du modèle {template_type}: {filepath}"
        except Exception as e:
            logging.error(f"Erreur lors de la création du fichier: {e}")
            return f"Erreur lors de la création: {str(e)}"
            
    def execute_quick_command(self, cmd_name, *args):
        """Exécute une commande rapide prédéfinie"""
        if cmd_name not in QUICK_COMMANDS and cmd_name not in self.config.get("custom_commands", {}):
            available_commands = list(QUICK_COMMANDS.keys()) + list(self.config.get("custom_commands", {}).keys())
            return f"Erreur: Commande '{cmd_name}' non disponible. Commandes disponibles: {', '.join(sorted(available_commands))}"
            
        # Utiliser une commande personnalisée si disponible, sinon utiliser une commande prédéfinie
        if cmd_name in self.config.get("custom_commands", {}):
            cmd_template = self.config["custom_commands"][cmd_name]
        else:
            cmd_template = QUICK_COMMANDS[cmd_name]
            
        # Remplacement des paramètres dans le modèle de commande
        if "{" in cmd_template and "}" in cmd_template:
            # Extraire les noms des paramètres du modèle
            param_names = re.findall(r'\{([^}]+)\}', cmd_template)
            
            # Vérifier si nous avons suffisamment d'arguments
            if len(args) < len(param_names):
                return f"Erreur: La commande '{cmd_name}' nécessite les paramètres suivants: {', '.join(param_names)}"
                
            # Créer un dictionnaire des paramètres
            params = {}
            for i, name in enumerate(param_names):
                if i < len(args):
                    params[name] = args[i]
                    
            # Remplacer les paramètres dans le modèle
            try:
                cmd = cmd_template.format(**params)
            except KeyError as e:
                return f"Erreur: Paramètre manquant: {e}"
        else:
            # Pas de paramètres à remplacer
            cmd = cmd_template
            
        # Exécuter la commande
        return self.execute_command(cmd)
        
    def execute_devops_tool(self, tool_name, *args):
        """Exécute un outil DevOps intégré"""
        try:
            if tool_name == "monitor_ressources":
                # Surveiller les ressources système
                duration = int(args[0]) if args else 5  # Durée par défaut: 5 secondes
                return self.devops_tools.monitor_ressources(duration=duration)
                
            elif tool_name == "analyze_logs":
                # Analyser un fichier de logs
                if not args:
                    return "Erreur: Veuillez spécifier un fichier de logs"
                    
                log_file = args[0]
                pattern = args[1] if len(args) > 1 else None
                tail_param = None
                
                # Vérifier si on a un paramètre tail
                if len(args) > 2 and args[2].startswith("tail="):
                    try:
                        tail_param = int(args[2].split("=")[1])
                    except (ValueError, IndexError):
                        return "Erreur: Format incorrect pour le paramètre tail (exemple: tail=100)"
                
                return self.devops_tools.analyze_logs(log_file, pattern, tail_param)
                
            elif tool_name == "docker_info":
                # Informations Docker
                return self.devops_tools.docker_info()
                
            elif tool_name == "k8s_info":
                # Informations Kubernetes
                return self.devops_tools.k8s_info()
                
            elif tool_name == "network_scan":
                # Scan réseau
                if not args:
                    return "Erreur: Veuillez spécifier une cible (ex: 192.168.1.1)"
                    
                target = args[0]
                return self.devops_tools.network_scan(target)
                
            elif tool_name == "generate_ssl_cert":
                # Générer un certificat SSL
                if not args:
                    return "Erreur: Veuillez spécifier un nom de domaine"
                    
                domain = args[0]
                output_dir = args[1] if len(args) > 1 else None
                return self.devops_tools.generate_ssl_cert(domain, output_dir)
                
            else:
                available_tools = ["monitor_ressources", "analyze_logs", "docker_info", "k8s_info", "network_scan", "generate_ssl_cert"]
                return f"Erreur: Outil '{tool_name}' non reconnu. Outils disponibles: {', '.join(available_tools)}"
                
        except Exception as e:
            logging.error(f"Erreur lors de l'exécution de l'outil DevOps {tool_name}: {str(e)}")
            return f"Erreur lors de l'exécution de l'outil DevOps {tool_name}: {str(e)}"