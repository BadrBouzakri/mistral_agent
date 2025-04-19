    def run(self):
        """Démarre la boucle principale de l'agent"""
        # Affichage du panneau d'accueil
        if HAS_RICH:
            # Créer un panneau d'accueil avec des informations système
            welcome_msg = [
                "[bold cyan]Agent IA DevOps[/bold cyan] - Assistant d'administration système et DevOps",
                "",
                f"[bold]Système:[/bold] {self.system_info.get('os-version', 'Linux').split('=')[1].strip('\"') if '=' in self.system_info.get('os-version', 'Linux') else 'Linux'}",
                f"[bold]Kernel:[/bold] {self.system_info.get('kernel-version', 'Unknown').split(' ')[2] if len(self.system_info.get('kernel-version', '').split(' ')) > 2 else 'Unknown'}",
                f"[bold]Uptime:[/bold] {self.system_info.get('uptime', 'Unknown').split('up')[1].split(',')[0].strip() if 'up' in self.system_info.get('uptime', '') else 'Unknown'}",
                f"[bold]CPU:[/bold] {self.system_info.get('cpu-model', 'Unknown')}",
                f"[bold]Mémoire:[/bold] {self.system_info.get('used-memory', 'Unknown')}/{self.system_info.get('total-memory', 'Unknown')}",
                f"[bold]Disque (/):[/bold] {self.system_info.get('disk-usage-root', 'Unknown')}",
                "",
                f"[bold]Langue:[/bold] {self.language} | [bold]Répertoire des scripts:[/bold] {SCRIPTS_DIR}",
                f"[bold]Répertoire courant:[/bold] {self.current_dir}",
            ]
            
            self.console.print(Panel("\n".join(welcome_msg), border_style="cyan", box=box.DOUBLE_EDGE))
            
            # Afficher les commandes disponibles
            self.console.print("[bold]Commandes spéciales:[/bold]")
            self.console.print("  • [cyan]exit[/cyan], [cyan]quit[/cyan] : quitter l'agent")
            self.console.print("  • [cyan]clear[/cyan] : effacer l'écran")
            self.console.print("  • [cyan]pwd[/cyan] : afficher le répertoire courant")
            self.console.print("  • [cyan]cd[/cyan] [path] : changer de répertoire")
            self.console.print("  • [cyan]sysinfo[/cyan] : afficher les informations système")
            self.console.print("  • [cyan]history[/cyan] : afficher l'historique des commandes")
            self.console.print("  • [cyan]quickcmds[/cyan] : afficher les commandes rapides disponibles")
            self.console.print("  • [cyan]alias[/cyan] : gérer les alias")
            self.console.print("  • [cyan]template[/cyan] [type] : afficher les modèles disponibles")
            self.console.print("  • [cyan]devops[/cyan] : afficher les outils DevOps disponibles\n")
        else:
            print("====== Agent IA DevOps - Assistant d'administration système et DevOps ======")
            print(f"Langue: {self.language} | Répertoire des scripts: {SCRIPTS_DIR}")
            print(f"Répertoire courant: {self.current_dir}")
            print("Commandes spéciales:")
            print("  • exit, quit : quitter l'agent")
            print("  • clear : effacer l'écran")
            print("  • pwd : afficher le répertoire courant")
            print("  • cd [path] : changer de répertoire")
            print("  • sysinfo : afficher les informations système")
            print("  • history : afficher l'historique des commandes")
            print("  • quickcmds : afficher les commandes rapides disponibles")
            print("  • alias : gérer les alias")
            print("  • template [type] : afficher les modèles disponibles")
            print("  • devops : afficher les outils DevOps disponibles\n")

        # Boucle principale
        while True:
            try:
                user_input = self.get_prompt()
                
                # Commandes spéciales
                if user_input.lower() in ['exit', 'quit']:
                    self.save_history()
                    self.save_config()
                    break
                elif user_input.lower() == 'clear':
                    os.system('clear')
                    continue
                elif user_input.lower() == 'pwd':
                    if HAS_RICH:
                        self.console.print(f"[bold green]Répertoire courant:[/bold green] {self.current_dir}")
                    else:
                        print(f"Répertoire courant: {self.current_dir}")
                    continue
                elif user_input.startswith('cd '):
                    # Gérer directement les commandes cd sans passer par l'API
                    result = self.execute_command(user_input)
                    if HAS_RICH:
                        self.console.print(f"[bold green]{result}[/bold green]")
                    else:
                        print(result)
                    continue
                elif user_input.lower() == 'ls' or user_input.lower().startswith('ls '):
                    # Exécuter ls directement pour plus de réactivité
                    result = self.execute_command(user_input)
                    if HAS_RICH:
                        # Affichage amélioré des résultats de ls
                        files = result.strip().split("\n")
                        if len(files) > 0 and files[0]:
                            from rich.table import Table
                            table = Table(show_header=False, box=None)
                            col_count = min(4, max(1, self.console.width // 20))
                            
                            # Grouper les fichiers par type (dossiers, exécutables, etc.)
                            dirs = []
                            execs = []
                            others = []
                            
                            for file in files:
                                file = file.strip()
                                if not file:
                                    continue
                                if file.endswith('/') or (file.startswith('d') and ' ' in file):
                                    dirs.append(file)
                                elif file.endswith('*') or (file.startswith('-') and 'x' in file[:10]):
                                    execs.append(file)
                                else:
                                    others.append(file)
                                    
                            # Réorganiser la liste pour l'affichage en colonnes
                            all_files = []
                            for f in dirs:
                                all_files.append(f"[bold blue]{f}[/bold blue]")
                            for f in execs:
                                all_files.append(f"[bold green]{f}[/bold green]")
                            for f in others:
                                all_files.append(f)
                                
                            # Créer le tableau
                            for i in range(0, len(all_files), col_count):
                                row = all_files[i:i+col_count]
                                while len(row) < col_count:
                                    row.append("")
                                table.add_row(*row)
                                
                            self.console.print(table)
                        else:
                            self.console.print("Aucun fichier trouvé")
                    else:
                        print(result)
                    continue
                elif user_input.lower() == 'sysinfo':
                    # Rafraîchir les informations système
                    self.collect_system_info()
                    
                    if HAS_RICH:
                        # Affichage des informations système
                        from rich.table import Table
                        table = Table(title="Informations système", box=box.ROUNDED)
                        table.add_column("Attribut", style="cyan")
                        table.add_column("Valeur")
                        
                        # Ajouter les informations système au tableau
                        for key, value in sorted(self.system_info.items()):
                            # Formatage du nom de l'attribut
                            attr_name = key.replace('-', ' ').title()
                            table.add_row(attr_name, value)
                            
                        self.console.print(table)
                    else:
                        print("=== Informations système ===")
                        for key, value in sorted(self.system_info.items()):
                            attr_name = key.replace('-', ' ').title()
                            print(f"{attr_name}: {value}")
                    continue