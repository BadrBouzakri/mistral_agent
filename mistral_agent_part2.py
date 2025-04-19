# Ajouter les fonctions utilitaires pour les tâches DevOps courantes
class DevOpsTools:
    """Classe contenant des outils/utilitaires pour les tâches DevOps courantes"""
    
    @staticmethod
    def monitor_ressources(duration=5, interval=1):
        """Surveille les ressources système pendant une durée donnée"""
        import time
        import psutil
        
        try:
            # Vérifier si psutil est installé
            if not 'psutil' in sys.modules:
                return "Module psutil requis. Installez-le avec: pip install psutil"
                
            results = []
            print(f"Surveillance des ressources pendant {duration} secondes...")
            
            for i in range(duration):
                cpu = psutil.cpu_percent(interval=1)
                mem = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                results.append({
                    'time': i,
                    'cpu': cpu,
                    'mem_percent': mem.percent,
                    'disk_percent': disk.percent
                })
                
                print(f"CPU: {cpu}% | MEM: {mem.percent}% | DISK: {disk.percent}%")
                
                if i < duration - 1:
                    time.sleep(interval)
                    
            # Calculer les moyennes
            avg_cpu = sum(r['cpu'] for r in results) / len(results)
            avg_mem = sum(r['mem_percent'] for r in results) / len(results)
            avg_disk = sum(r['disk_percent'] for r in results) / len(results)
            
            summary = f"""
Résumé de la surveillance ({duration} secondes):
- CPU moyenne: {avg_cpu:.1f}%
- Mémoire moyenne: {avg_mem:.1f}%
- Utilisation disque: {avg_disk:.1f}%
"""
            return summary
        except Exception as e:
            return f"Erreur lors de la surveillance des ressources: {str(e)}"
    
    @staticmethod
    def analyze_logs(log_file, pattern=None, tail=None, head=None):
        """Analyse un fichier de logs et extrait des informations pertinentes"""
        try:
            # Vérifier si le fichier existe
            if not os.path.exists(log_file):
                return f"Fichier de logs introuvable: {log_file}"
                
            # Lire le fichier
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                if tail:
                    # Lire les dernières lignes
                    lines = f.readlines()[-tail:]
                elif head:
                    # Lire les premières lignes
                    lines = []
                    for i, line in enumerate(f):
                        if i >= head:
                            break
                        lines.append(line)
                else:
                    # Lire tout le fichier
                    lines = f.readlines()
            
            # Filtrer par motif si demandé
            if pattern:
                filtered_lines = [line for line in lines if pattern in line]
                
                # Statistiques sur les motifs trouvés
                stats = f"Motif '{pattern}' trouvé dans {len(filtered_lines)} lignes sur {len(lines)} ({len(filtered_lines)/len(lines)*100:.1f}%)"
                
                # Limiter le nombre de lignes retournées
                if len(filtered_lines) > 100:
                    filtered_lines = filtered_lines[:100]
                    stats += " (affichage limité aux 100 premières lignes)"
                    
                return stats + "\n\n" + "".join(filtered_lines)
            else:
                # Limiter le nombre de lignes retournées
                if len(lines) > 100:
                    stats = f"Fichier contient {len(lines)} lignes (affichage limité aux 100 premières lignes)"
                    lines = lines[:100]
                    return stats + "\n\n" + "".join(lines)
                else:
                    return "".join(lines)
        except Exception as e:
            return f"Erreur lors de l'analyse des logs: {str(e)}"
    
    @staticmethod
    def docker_info():
        """Récupère des informations sur Docker"""
        try:
            # Vérifier si Docker est installé
            docker_version = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if docker_version.returncode != 0:
                return "Docker n'est pas installé ou accessible"
                
            # Récupérer les informations Docker
            docker_info = subprocess.run(['docker', 'info'], capture_output=True, text=True)
            containers = subprocess.run(['docker', 'ps', '-a'], capture_output=True, text=True)
            images = subprocess.run(['docker', 'images'], capture_output=True, text=True)
            
            return f"""
=== Docker ===
{docker_version.stdout}

=== Informations système Docker ===
{docker_info.stdout}

=== Conteneurs ===
{containers.stdout}

=== Images ===
{images.stdout}
"""
        except Exception as e:
            return f"Erreur lors de la récupération des informations Docker: {str(e)}"
    
    @staticmethod
    def k8s_info():
        """Récupère des informations sur Kubernetes"""
        try:
            # Vérifier si kubectl est installé
            kubectl_version = subprocess.run(['kubectl', 'version', '--client'], capture_output=True, text=True)
            if kubectl_version.returncode != 0:
                return "kubectl n'est pas installé ou accessible"
                
            # Récupérer les informations K8s
            try:
                nodes = subprocess.run(['kubectl', 'get', 'nodes'], capture_output=True, text=True, timeout=5)
                pods = subprocess.run(['kubectl', 'get', 'pods', '--all-namespaces'], capture_output=True, text=True, timeout=5)
                deployments = subprocess.run(['kubectl', 'get', 'deployments', '--all-namespaces'], capture_output=True, text=True, timeout=5)
                services = subprocess.run(['kubectl', 'get', 'services', '--all-namespaces'], capture_output=True, text=True, timeout=5)
                
                return f"""
=== Kubernetes ===
{kubectl_version.stdout}

=== Nœuds ===
{nodes.stdout}

=== Pods ===
{pods.stdout}

=== Déploiements ===
{deployments.stdout}

=== Services ===
{services.stdout}
"""
            except subprocess.TimeoutExpired:
                return "Erreur de délai d'attente lors de la communication avec Kubernetes. Le cluster est-il accessible?"
        except Exception as e:
            return f"Erreur lors de la récupération des informations Kubernetes: {str(e)}"
    
    @staticmethod
    def network_scan(target):
        """Effectue un scan réseau basique"""
        try:
            # Vérifier si ping est disponible
            ping_cmd = 'ping' if os.name != 'nt' else 'ping -n'
            
            if '/' in target:  # C'est un réseau CIDR
                return "Scan CIDR non implémenté pour l'instant"
            else:  # C'est un hôte unique
                ping = subprocess.run(f'{ping_cmd} 4 {target}', shell=True, capture_output=True, text=True)
                
                # Vérifier les ports ouverts avec nc si disponible
                try:
                    common_ports = [22, 80, 443, 3306, 5432, 8080]
                    open_ports = []
                    
                    for port in common_ports:
                        nc = subprocess.run(f'nc -z -w 1 {target} {port}', shell=True, capture_output=True, text=True)
                        if nc.returncode == 0:
                            open_ports.append(port)
                    
                    ports_info = f"\n\nPorts ouverts: {', '.join(map(str, open_ports)) if open_ports else 'Aucun trouvé'}"
                except:
                    ports_info = "\n\nVérification des ports impossible (nc non disponible)"
                    
                return f"""
=== Scan réseau pour {target} ===
{ping.stdout}
{ports_info}
"""
        except Exception as e:
            return f"Erreur lors du scan réseau: {str(e)}"
    
    @staticmethod
    def generate_ssl_cert(domain, output_dir=None):
        """Génère un certificat SSL auto-signé"""
        try:
            if output_dir is None:
                output_dir = os.getcwd()
                
            # Construire le chemin des fichiers
            key_file = os.path.join(output_dir, f"{domain}.key")
            cert_file = os.path.join(output_dir, f"{domain}.crt")
            
            # Générer la clé privée
            openssl_cmd = f"openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout {key_file} -out {cert_file} -subj '/CN={domain}'"
            result = subprocess.run(openssl_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                return f"Erreur lors de la génération du certificat: {result.stderr}"
                
            return f"""
Certificat SSL auto-signé généré avec succès:
- Clé privée: {key_file}
- Certificat: {cert_file}
- Validité: 365 jours
- Domaine: {domain}
"""
        except Exception as e:
            return f"Erreur lors de la génération du certificat SSL: {str(e)}"