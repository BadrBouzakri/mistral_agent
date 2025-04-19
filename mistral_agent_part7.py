                elif user_input.lower() == 'history':
                    # Afficher l'historique des commandes
                    if 'command_history' in self.config and self.config['command_history']:
                        if HAS_RICH:
                            from rich.table import Table
                            table = Table(title="Historique des commandes", box=box.ROUNDED)
                            table.add_column("N°", style="cyan")
                            table.add_column("Commande")
                            table.add_column("Date/Heure")
                            table.add_column("Répertoire")
                            
                            for i, cmd in enumerate(self.config['command_history'], 1):
                                try:
                                    # Formater la date
                                    timestamp = datetime.fromisoformat(cmd['timestamp'])
                                    formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                                    
                                    table.add_row(
                                        str(i),
                                        cmd['command'],
                                        formatted_time,
                                        cmd.get('directory', '')
                                    )
                                except (KeyError, ValueError) as e:
                                    logging.error(f"Erreur dans l'historique: {e}")
                                    
                            self.console.print(table)
                        else:
                            print("=== Historique des commandes ===")
                            for i, cmd in enumerate(self.config['command_history'], 1):
                                try:
                                    timestamp = datetime.fromisoformat(cmd['timestamp'])
                                    formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                                    print(f"{i}. {cmd['command']} ({formatted_time} @ {cmd.get('directory', '')})")
                                except (KeyError, ValueError) as e:
                                    print(f"{i}. {cmd.get('command', '?')}")
                    else:
                        if HAS_RICH:
                            self.console.print("[italic]Aucun historique de commandes disponible[/italic]")
                        else:
                            print("Aucun historique de commandes disponible")
                    continue
                elif user_input.lower() == 'quickcmds':
                    # Afficher les commandes rapides disponibles
                    if HAS_RICH:
                        from rich.table import Table
                        table = Table(title="Commandes rapides disponibles", box=box.ROUNDED)
                        table.add_column("Nom", style="cyan")
                        table.add_column("Commande")
                        table.add_column("Paramètres")
                        
                        # Ajouter les commandes prédéfinies
                        for name, cmd in sorted(QUICK_COMMANDS.items()):
                            params = ", ".join(re.findall(r'\{([^}]+)\}', cmd))
                            table.add_row(name, cmd, params)
                            
                        # Ajouter les commandes personnalisées
                        for name, cmd in sorted(self.config.get("custom_commands", {}).items()):
                            params = ", ".join(re.findall(r'\{([^}]+)\}', cmd))
                            table.add_row(f"{name} (custom)", cmd, params)
                            
                        self.console.print(table)
                    else:
                        print("=== Commandes rapides disponibles ===")
                        print("--- Commandes prédéfinies ---")
                        for name, cmd in sorted(QUICK_COMMANDS.items()):
                            params = ", ".join(re.findall(r'\{([^}]+)\}', cmd))
                            print(f"{name}: {cmd} (Params: {params})")
                        print("--- Commandes personnalisées ---")
                        for name, cmd in sorted(self.config.get("custom_commands", {}).items()):
                            params = ", ".join(re.findall(r'\{([^}]+)\}', cmd))
                            print(f"{name}: {cmd} (Params: {params})")
                    continue
                elif user_input.lower() == 'devops':
                    # Afficher les outils DevOps disponibles
                    if HAS_RICH:
                        from rich.table import Table
                        table = Table(title="Outils DevOps disponibles", box=box.ROUNDED)
                        table.add_column("Outil", style="cyan")
                        table.add_column("Description")
                        table.add_column("Paramètres")
                        
                        table.add_row("monitor_ressources", "Surveille l'utilisation des ressources système", "[durée en secondes]")
                        table.add_row("analyze_logs", "Analyse un fichier de logs", "fichier [pattern] [tail=N]")
                        table.add_row("docker_info", "Affiche des informations sur Docker", "")
                        table.add_row("k8s_info", "Affiche des informations sur Kubernetes", "")
                        table.add_row("network_scan", "Effectue un scan réseau basique", "cible (IP ou nom d'hôte)")
                        table.add_row("generate_ssl_cert", "Génère un certificat SSL auto-signé", "domaine [répertoire de sortie]")
                        
                        self.console.print(table)
                    else:
                        print("=== Outils DevOps disponibles ===")
                        print("monitor_ressources [durée] : Surveille l'utilisation des ressources système")
                        print("analyze_logs fichier [pattern] [tail=N] : Analyse un fichier de logs")
                        print("docker_info : Affiche des informations sur Docker")
                        print("k8s_info : Affiche des informations sur Kubernetes")
                        print("network_scan cible : Effectue un scan réseau basique")
                        print("generate_ssl_cert domaine [répertoire] : Génère un certificat SSL auto-signé")
                    continue
                elif user_input.lower().startswith('alias'):
                    # Gestion des alias
                    parts = user_input.split(maxsplit=2)
                    
                    if len(parts) == 1:
                        # Afficher tous les alias
                        if 'aliases' in self.config and self.config['aliases']:
                            if HAS_RICH:
                                from rich.table import Table
                                table = Table(title="Alias", box=box.ROUNDED)
                                table.add_column("Alias", style="cyan")
                                table.add_column("Commande")
                                
                                for alias, cmd in sorted(self.config['aliases'].items()):
                                    table.add_row(alias, cmd)
                                    
                                self.console.print(table)
                            else:
                                print("=== Alias ===")
                                for alias, cmd in sorted(self.config['aliases'].items()):
                                    print(f"{alias} = {cmd}")
                        else:
                            if HAS_RICH:
                                self.console.print("[italic]Aucun alias défini[/italic]")
                            else:
                                print("Aucun alias défini")
                                
                    elif len(parts) == 2 and parts[1] == '--help':
                        # Afficher l'aide pour la gestion des alias
                        help_text = """
Gestion des alias:
  alias                   - Afficher tous les alias
  alias nom               - Afficher la commande associée à cet alias
  alias nom commande      - Définir un nouvel alias
  alias --delete nom      - Supprimer un alias
  alias --help            - Afficher cette aide
"""
                        if HAS_RICH:
                            self.console.print(Panel(help_text, title="Aide sur les alias", border_style="cyan"))
                        else:
                            print(help_text)
                            
                    elif len(parts) == 3 and parts[1] == '--delete':
                        # Supprimer un alias
                        alias_name = parts[2]
                        if 'aliases' in self.config and alias_name in self.config['aliases']:
                            del self.config['aliases'][alias_name]
                            self.save_config()
                            if HAS_RICH:
                                self.console.print(f"[green]Alias '{alias_name}' supprimé[/green]")
                            else:
                                print(f"Alias '{alias_name}' supprimé")
                        else:
                            if HAS_RICH:
                                self.console.print(f"[yellow]Alias '{alias_name}' non trouvé[/yellow]")
                            else:
                                print(f"Alias '{alias_name}' non trouvé")
                                
                    elif len(parts) == 2:
                        # Afficher un alias spécifique
                        alias_name = parts[1]
                        if 'aliases' in self.config and alias_name in self.config['aliases']:
                            if HAS_RICH:
                                self.console.print(f"[bold]{alias_name}[/bold] = {self.config['aliases'][alias_name]}")
                            else:
                                print(f"{alias_name} = {self.config['aliases'][alias_name]}")
                        else:
                            if HAS_RICH:
                                self.console.print(f"[yellow]Alias '{alias_name}' non trouvé[/yellow]")
                            else:
                                print(f"Alias '{alias_name}' non trouvé")
                                
                    elif len(parts) == 3:
                        # Définir un nouvel alias
                        alias_name = parts[1]
                        cmd = parts[2]
                        
                        if 'aliases' not in self.config:
                            self.config['aliases'] = {}
                            
                        self.config['aliases'][alias_name] = cmd
                        self.save_config()
                        
                        if HAS_RICH:
                            self.console.print(f"[green]Alias '{alias_name}' défini: {cmd}[/green]")
                        else:
                            print(f"Alias '{alias_name}' défini: {cmd}")
                    continue