                elif user_input.lower().startswith('template'):
                    parts = user_input.split(maxsplit=2)
                    
                    if len(parts) == 1:
                        # Afficher tous les modèles disponibles
                        if HAS_RICH:
                            from rich.table import Table
                            table = Table(title="Modèles disponibles", box=box.ROUNDED)
                            table.add_column("Type", style="cyan")
                            table.add_column("Extension")
                            table.add_column("Description")
                            
                            for template_type in sorted(TEMPLATES.keys()):
                                ext = SCRIPT_EXTENSIONS.get(template_type, ".txt")
                                description = ""
                                if template_type == "docker":
                                    description = "Fichier Dockerfile de base (Alpine)"
                                elif template_type == "terraform":
                                    description = "Configuration Terraform pour AWS"
                                elif template_type == "kubernetes":
                                    description = "Déploiement Kubernetes basique"
                                elif template_type == "ansible":
                                    description = "Playbook Ansible d'exemple"
                                    
                                table.add_row(template_type, ext, description)
                                
                            self.console.print(table)
                        else:
                            print("=== Modèles disponibles ===")
                            for template_type in sorted(TEMPLATES.keys()):
                                ext = SCRIPT_EXTENSIONS.get(template_type, ".txt")
                                print(f"{template_type} ({ext})")
                    elif len(parts) >= 2:
                        template_type = parts[1]
                        
                        if template_type in TEMPLATES:
                            # Afficher le contenu du modèle
                            if HAS_RICH:
                                self.console.print(f"[bold]Modèle {template_type}:[/bold]")
                                self.console.print(Syntax(TEMPLATES[template_type], template_type))
                                
                                # Si un nom de fichier est fourni, proposer de créer le fichier
                                if len(parts) == 3:
                                    filename = parts[2]
                                    if Confirm.ask(f"Créer {filename} avec ce modèle?"):
                                        result = self.create_from_template(template_type, filename)
                                        self.console.print(result)
                            else:
                                print(f"=== Modèle {template_type} ===")
                                print(TEMPLATES[template_type])
                                
                                # Si un nom de fichier est fourni, proposer de créer le fichier
                                if len(parts) == 3:
                                    filename = parts[2]
                                    if input(f"Créer {filename} avec ce modèle? [o/N] ").lower() == 'o':
                                        result = self.create_from_template(template_type, filename)
                                        print(result)
                        else:
                            if HAS_RICH:
                                self.console.print(f"[yellow]Modèle '{template_type}' non trouvé[/yellow]")
                                self.console.print(f"Modèles disponibles: {', '.join(sorted(TEMPLATES.keys()))}")
                            else:
                                print(f"Modèle '{template_type}' non trouvé")
                                print(f"Modèles disponibles: {', '.join(sorted(TEMPLATES.keys()))}")
                    continue
                elif user_input.lower().startswith('run-'):
                    # Raccourci pour les commandes rapides
                    cmd_parts = user_input[4:].split(maxsplit=1)
                    cmd_name = cmd_parts[0]
                    args = cmd_parts[1].split() if len(cmd_parts) > 1 else []
                    
                    result = self.execute_quick_command(cmd_name, *args)
                    
                    if HAS_RICH:
                        self.console.print(f"\n[bold green]Commande rapide '{cmd_name}':[/bold green]")
                        self.console.print(result)
                    else:
                        print(f"\nCommande rapide '{cmd_name}':")
                        print(result)
                    continue
                elif user_input.lower().startswith('devops-'):
                    # Raccourci pour les outils DevOps
                    tool_parts = user_input[7:].split(maxsplit=1)
                    tool_name = tool_parts[0]
                    args = tool_parts[1].split() if len(tool_parts) > 1 else []
                    
                    result = self.execute_devops_tool(tool_name, *args)
                    
                    if HAS_RICH:
                        self.console.print(f"\n[bold blue]Outil DevOps '{tool_name}':[/bold blue]")
                        self.console.print(result)
                    else:
                        print(f"\nOutil DevOps '{tool_name}':")
                        print(result)
                    continue
                    
                # Appel à l'API Mistral
                try:
                    assistant_response = self.call_mistral_api(user_input)
                    
                    # Traitement de la réponse
                    self.process_response(assistant_response)
                    
                    # Sauvegarde périodique de l'historique
                    self.save_history()
                except Exception as e:
                    logging.error(f"Erreur lors de l'appel à l'API Mistral: {str(e)}")
                    if HAS_RICH:
                        self.console.print(f"[bold red]Erreur lors de l'appel à l'API Mistral:[/bold red] {str(e)}")
                    else:
                        print(f"Erreur lors de l'appel à l'API Mistral: {str(e)}")
                
            except KeyboardInterrupt:
                print("\nInterruption détectée. Pour quitter, tapez 'exit'.")
            except Exception as e:
                logging.error(f"Erreur dans la boucle principale: {str(e)}")
                if self.debug:
                    import traceback
                    traceback.print_exc()
                if HAS_RICH:
                    self.console.print(f"[bold red]Erreur:[/bold red] {str(e)}")
                else:
                    print(f"Erreur: {str(e)}")