def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Agent IA Mistral pour administration système et DevOps")
    parser.add_argument("--lang", "-l", choices=["fr", "en"], default="fr", help="Langue de l'agent (fr/en)")
    parser.add_argument("--debug", "-d", action="store_true", help="Mode debug")
    parser.add_argument("--scripts-dir", "-s", help="Répertoire pour les scripts générés")
    parser.add_argument("--start-dir", "-cd", help="Répertoire de démarrage")
    parser.add_argument("--shell-completion", action="store_true", help="Installer la complétion shell")
    parser.add_argument("--command", "-c", help="Exécuter une commande puis quitter")
    parser.add_argument("--file", "-f", help="Fichier contenant des commandes à exécuter (une par ligne)")
    parser.add_argument("--update-sysinfo", action="store_true", help="Mettre à jour les informations système")
    parser.add_argument("--theme", "-t", choices=["dark", "light"], help="Thème d'affichage")
    args = parser.parse_args()
    
    # Configuration du répertoire des scripts si spécifié
    if args.scripts_dir:
        global SCRIPTS_DIR
        SCRIPTS_DIR = os.path.expanduser(args.scripts_dir)
    
    # Création du répertoire des scripts s'il n'existe pas
    os.makedirs(SCRIPTS_DIR, exist_ok=True)
    
    # Configuration du répertoire de démarrage
    if args.start_dir:
        start_dir = os.path.expanduser(args.start_dir)
        if os.path.isdir(start_dir):
            os.chdir(start_dir)
        else:
            print(f"Le répertoire de démarrage {start_dir} n'existe pas. Utilisation du répertoire courant.")
    
    # Mise à jour des informations système
    if args.update_sysinfo:
        agent = MistralAgent(language=args.lang, debug=args.debug)
        agent.collect_system_info()
        agent.save_config()
        print("Informations système mises à jour avec succès")
        sys.exit(0)
            
    # Installation de la complétion shell
    if args.shell_completion:
        try:
            shell_config = os.path.expanduser("~/.bashrc")
            if os.path.exists(os.path.expanduser("~/.zshrc")):
                shell_config = os.path.expanduser("~/.zshrc")
                
            completion_script = f"""
# Complétion pour l'agent Mistral IA DevOps
_mistral_completions()
{{
    local cur prev opts cmd_opts
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    prev="${{COMP_WORDS[COMP_CWORD-1]}}"
    opts="--lang --debug --scripts-dir --start-dir --shell-completion --command --file --update-sysinfo --theme"
    cmd_opts="ls pwd cd sysinfo history quickcmds alias template clear exit quit"
    
    if [[ ${{prev}} == "--lang" || ${{prev}} == "-l" ]]; then
        COMPREPLY=( $(compgen -W "fr en" -- ${{cur}}) )
        return 0
    elif [[ ${{prev}} == "--scripts-dir" || ${{prev}} == "--start-dir" || ${{prev}} == "-s" || ${{prev}} == "-cd" ]]; then
        COMPREPLY=( $(compgen -d -- ${{cur}}) )
        return 0
    elif [[ ${{prev}} == "--file" || ${{prev}} == "-f" ]]; then
        COMPREPLY=( $(compgen -f -- ${{cur}}) )
        return 0
    elif [[ ${{prev}} == "--theme" || ${{prev}} == "-t" ]]; then
        COMPREPLY=( $(compgen -W "dark light" -- ${{cur}}) )
        return 0
    elif [[ ${{prev}} == "cd" ]]; then
        COMPREPLY=( $(compgen -d -- ${{cur}}) )
        return 0
    elif [[ ${{prev}} == "template" ]]; then
        COMPREPLY=( $(compgen -W "docker terraform kubernetes ansible" -- ${{cur}}) )
        return 0
    fi
    
    if [[ ${{cur}} == -* ]]; then
        COMPREPLY=( $(compgen -W "${{opts}}" -- ${{cur}}) )
        return 0
    elif [[ "${{COMP_CWORD}}" -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "${{cmd_opts}}" -- ${{cur}}) )
        return 0
    fi
}}
complete -F _mistral_completions mistral
"""
            with open(shell_config, "a") as f:
                f.write(completion_script)
            print(f"Complétion shell installée dans {shell_config}. Rechargez votre shell ou exécutez 'source {shell_config}'.")
            sys.exit(0)
        except Exception as e:
            print(f"Erreur lors de l'installation de la complétion shell: {e}")
            sys.exit(1)
    
    # Création et démarrage de l'agent
    agent = MistralAgent(language=args.lang, debug=args.debug)
    
    # Application du thème si spécifié
    if args.theme:
        agent.config["theme"] = args.theme
        agent.save_config()
    
    # Exécution d'une commande unique
    if args.command:
        if args.command.startswith('cd '):
            # Pour les commandes cd, on doit changer le répertoire
            result = agent.execute_command(args.command)
            print(result)
        else:
            # Utiliser l'agent pour obtenir une réponse
            try:
                response = agent.call_mistral_api(args.command)
                agent.process_response(response)
            except Exception as e:
                print(f"Erreur lors de l'exécution de la commande: {e}")
        sys.exit(0)
    
    # Exécution des commandes à partir d'un fichier
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                commands = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            print(f"Exécution de {len(commands)} commandes depuis {args.file}...")
            for cmd in commands:
                print(f"\n> {cmd}")
                if cmd.startswith('cd '):
                    # Pour les commandes cd, on doit changer le répertoire
                    result = agent.execute_command(cmd)
                    print(result)
                else:
                    # Utiliser l'agent pour obtenir une réponse
                    try:
                        response = agent.call_mistral_api(cmd)
                        agent.process_response(response)
                    except Exception as e:
                        print(f"Erreur lors de l'exécution de la commande: {e}")
            sys.exit(0)
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier de commandes: {e}")
            sys.exit(1)
    
    # Démarrage de l'agent en mode interactif
    agent.run()

if __name__ == "__main__":
    main()