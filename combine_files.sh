#!/bin/bash

# Script pour combiner tous les fichiers partiels en un seul fichier mistral_agent.py

echo "Combinaison des fichiers partiels en un seul fichier mistral_agent.py..."

# Vérifie que tous les fichiers nécessaires existent
files=(
    "mistral_agent.py"  
    "mistral_agent_part2.py"
    "mistral_agent_part3.py"
    "mistral_agent_part4.py"
    "mistral_agent_part5.py"
    "mistral_agent_part6.py"
    "mistral_agent_part7.py"
    "mistral_agent_part8.py"
    "mistral_agent_part9.py"
)

missing=false
for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Fichier manquant: $file"
        missing=true
    fi
done

if [ "$missing" = true ]; then
    echo "Certains fichiers sont manquants. Veuillez télécharger tous les fichiers nécessaires."
    exit 1
fi

# Créer un fichier temporaire
temp_file="mistral_agent_combined.py"

# Combiner les fichiers
cat mistral_agent.py > $temp_file
cat mistral_agent_part2.py >> $temp_file
cat mistral_agent_part3.py >> $temp_file
cat mistral_agent_part4.py >> $temp_file
cat mistral_agent_part5.py >> $temp_file
cat mistral_agent_part6.py >> $temp_file
cat mistral_agent_part7.py >> $temp_file
cat mistral_agent_part8.py >> $temp_file
cat mistral_agent_part9.py >> $temp_file

# Remplacer le fichier original
cp $temp_file mistral_agent.py
rm $temp_file

# Rendre le fichier exécutable
chmod +x mistral_agent.py

echo "✅ Fichier mistral_agent.py créé avec succès!"
echo "Vous pouvez maintenant l'installer avec ./install.sh"
