    def call_mistral_api(self, user_message):
        """Appelle l'API Mistral pour obtenir une réponse"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        # Préparer les messages pour l'API
        messages = [
            {"role": "system", "content": self.system_message}
        ]
        
        # Ajouter l'historique de conversation
        for entry in self.conversation_history:
            messages.append(entry)
            
        # Ajouter le message de l'utilisateur
        messages.append({"role": "user", "content": user_message})
        
        payload = {
            "model": MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                if self.debug:
                    print(json.dumps(response_data, indent=2))
                    
                assistant_message = response_data['choices'][0]['message']['content']
                
                # Mettre à jour l'historique de conversation
                self.conversation_history.append({"role": "user", "content": user_message})
                self.conversation_history.append({"role": "assistant", "content": assistant_message})
                
                # Limiter la taille de l'historique
                if len(self.conversation_history) > MAX_HISTORY_ENTRIES * 2:
                    self.conversation_history = self.conversation_history[-MAX_HISTORY_ENTRIES * 2:]
                    
                return assistant_message
            else:
                error_message = f"Erreur API ({response.status_code}): {response.text}"
                logging.error(error_message)
                return f"Erreur lors de l'appel à l'API Mistral: {error_message}"
        except Exception as e:
            logging.error(f"Exception lors de l'appel à l'API: {str(e)}")
            return f"Erreur de connexion à l'API Mistral: {str(e)}"

    def process_response(self, response):
        """Traite la réponse de l'API pour exécuter des commandes ou créer des scripts"""
        # Rechercher les commandes à exécuter
        exec_pattern = r"\[EXEC\](.*?)\[\/EXEC\]"
        script_pattern = r"\[SCRIPT\s+(\w+)\s+([^\]]+)\](.*?)\[\/SCRIPT\]"
        template_pattern = r"\[TEMPLATE\s+(\w+)\s+([^\]]+)\]"
        quickcmd_pattern = r"\[QUICKCMD\s+(\w+)(?:\s+([^\]]+))?\]"
        devops_pattern = r"\[DEVOPS\s+(\w+)(?:\s+([^\]]+))?\]"
        
        # Exécution des commandes
        for match in re.finditer(exec_pattern, response, re.DOTALL):
            command = match.group(1).strip()
            result = self.execute_command(command)
            
            if HAS_RICH:
                self.console.print("\n[bold green]Commande:[/bold green]")
                self.console.print(Syntax(command, "bash"))
                self.console.print("\n[bold green]Résultat:[/bold green]")
                
                # Détection du type de contenu pour un affichage adapté
                if re.search(r'^\s*<\?xml|^\s*<html|^\s*<!DOCTYPE', result, re.IGNORECASE):
                    # Contenu XML/HTML
                    self.console.print(Syntax(result, "xml"))
                elif re.search(r'^\s*\{|\}\s*$', result) and '":' in result:
                    # Contenu JSON potentiel
                    try:
                        formatted_json = json.dumps(json.loads(result), indent=2)
                        self.console.print(Syntax(formatted_json, "json"))
                    except:
                        self.console.print(result)
                elif command.startswith("ls") and not command.endswith("| grep"):
                    # Résultat de ls - affichage en colonnes
                    files = result.strip().split("\n")
                    # Créer un tableau avec Rich
                    from rich.table import Table
                    table = Table(show_header=False, box=None)
                    # Diviser en colonnes (ajuster selon la largeur du terminal)
                    col_count = 3
                    for i in range(0, len(files), col_count):
                        row = files[i:i+col_count]
                        while len(row) < col_count:  # Padding
                            row.append("")
                        table.add_row(*row)
                    self.console.print(table)
                else:
                    self.console.print(result)
            else:
                print(f"\nCommande: {command}")
                print(f"Résultat: {result}")
        
        # Création de scripts
        for match in re.finditer(script_pattern, response, re.DOTALL):
            script_type = match.group(1).strip()
            script_name = match.group(2).strip()
            script_content = match.group(3).strip()
            
            filepath = self.save_script(script_type, script_name, script_content)
            
            if HAS_RICH:
                self.console.print(f"\n[bold green]Script {script_type} créé:[/bold green] {filepath}")
                self.console.print(Syntax(script_content, script_type.lower()))
                
                # Demander si l'utilisateur veut exécuter le script
                if script_type.lower() in ["bash", "shell", "python", "sh", "py"]:
                    if Confirm.ask("Voulez-vous exécuter ce script maintenant?"):
                        if script_type.lower() in ["python", "py"]:
                            cmd = f"python3 {filepath}"
                        else:
                            cmd = filepath
                            
                        result = self.execute_command(cmd)
                        self.console.print("\n[bold green]Résultat de l'exécution:[/bold green]")
                        self.console.print(result)
            else:
                print(f"\nScript {script_type} créé: {filepath}")
                print(f"\n--- Début du script ---\n{script_content}\n--- Fin du script ---")
                
                # Demander si l'utilisateur veut exécuter le script
                if script_type.lower() in ["bash", "shell", "python", "sh", "py"]:
                    if input("Voulez-vous exécuter ce script maintenant? [o/N] ").lower() == 'o':
                        if script_type.lower() in ["python", "py"]:
                            cmd = f"python3 {filepath}"
                        else:
                            cmd = filepath
                            
                        result = self.execute_command(cmd)
                        print(f"\nRésultat de l'exécution:\n{result}")
                        
        # Création à partir de modèles
        for match in re.finditer(template_pattern, response, re.DOTALL):
            template_type = match.group(1).strip()
            filename = match.group(2).strip()
            
            result = self.create_from_template(template_type, filename)
            
            if HAS_RICH:
                self.console.print(f"\n[bold green]Utilisation du modèle {template_type}:[/bold green]")
                self.console.print(result)
            else:
                print(f"\nUtilisation du modèle {template_type}: {result}")
                
        # Exécution de commandes rapides
        for match in re.finditer(quickcmd_pattern, response, re.DOTALL):
            cmd_name = match.group(1).strip()
            args = match.group(2).strip().split() if match.group(2) else []
            
            result = self.execute_quick_command(cmd_name, *args)
            
            if HAS_RICH:
                self.console.print(f"\n[bold green]Commande rapide '{cmd_name}':[/bold green]")
                self.console.print(result)
            else:
                print(f"\nCommande rapide '{cmd_name}':")
                print(result)
                
        # Exécution des outils DevOps
        for match in re.finditer(devops_pattern, response, re.DOTALL):
            tool_name = match.group(1).strip()
            args = match.group(2).strip().split() if match.group(2) else []
            
            result = self.execute_devops_tool(tool_name, *args)
            
            if HAS_RICH:
                self.console.print(f"\n[bold blue]Outil DevOps '{tool_name}':[/bold blue]")
                self.console.print(result)
            else:
                print(f"\nOutil DevOps '{tool_name}':")
                print(result)
        
        # Afficher le texte normal (sans les tags spéciaux)
        clean_response = re.sub(exec_pattern, "", response)
        clean_response = re.sub(script_pattern, "", clean_response)
        clean_response = re.sub(template_pattern, "", clean_response)
        clean_response = re.sub(quickcmd_pattern, "", clean_response)
        clean_response = re.sub(devops_pattern, "", clean_response)
        clean_response = clean_response.strip()
        
        if clean_response:
            if HAS_RICH:
                self.console.print(Panel(clean_response, border_style="cyan", box=box.ROUNDED))
            else:
                print(f"\n{clean_response}\n")