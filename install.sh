#!/bin/bash

# Récupérer le nom de l'utilisateur
USERNAME=$(whoami)

# Saluer l'utilisateur
echo "Wesh, $USERNAME ! Bien? j'ai simplifié l'installation du projet, j'espere que cela te convient."

# Mettre à jour les paquets
echo "Mise à jour des paquets..."
sudo apt-get update

# Installer les dépendances nécessaires pour Python et l'environnement
echo "Installation de Python, pip et des bibliothèques nécessaires..."
sudo apt-get install -y python3 python3-pip unzip

# Installer les dépendances Python
echo "Installation des dépendances Python..."
pip3 install openai python-dotenv requests pillow flask

# Vérifier et extraire uploads.zip
if [ -f "uploads.zip" ]; then
    echo "Décompression de l'archive 'uploads.zip'..."
    
    # Créer le dossier uploads s'il n'existe pas
    if [ ! -d "uploads" ]; then
        mkdir uploads
    fi
    
    # Décompresser l'archive
    unzip -o uploads/uploads.zip -d uploads/
    
    # Vérifier si l'extraction a réussi
    if [ $? -eq 0 ]; then
        echo "Les polices ont été extraites avec succès dans 'uploads/'."
    else
        echo "Erreur lors de la décompression de 'uploads.zip'."
        exit 1
    fi
else
    echo "L'archive 'uploads.zip' est introuvable."
    exit 1
fi

echo "Installation terminée avec succès !"
