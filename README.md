# FTP-Sync-IUT2
Permet de transferer ses fichiers vers un serveur FTP à chaque modification

Ce script s'execute en arrière plan et permet de synchroniser un dossier local avec un serveur FTP distant. Il est possible de synchroniser plusieurs dossiers en même temps.
L'objectif est de lancé le script une fois et de ne plus s'en occuper.

Ce script est destiné au étudiants flemmards de l'IUT2 de Grenoble pour leur cours de PHP.

## Installation
1. Télécharger le script
```bash
git clone https://github.com/MothixExe/FTP-Sync-IUT2.git
```
2. Lancer le script
```bash
python "FTP-Sync-IUT2/Synchronisation FTP.py"
```
3. Lors de la première exécution, le script installera les dépendances nécessaires et aura besoins de redémarrer puis vous demandera les identifiants de connexion au serveur FTP.

## Configuration
### Variables à configurer

- `SERVER`: Adresse du serveur FTP.
- `REMOTE_FOLDER`: Chemin du dossier sur le serveur FTP où les fichiers seront synchronisés.
- `FICHIER_IMPORTER`: Extensions des fichiers à synchroniser.

Assurez-vous de modifier ces variables dans le script selon vos besoins avant de l'exécuter.

Les identifiants de connexion au serveur FTP sont demandés lors de l'exécution du script pour la première fois. Ensuite ils sont stockés dans un fichier credentials.txt encrypté.

## Auteur

- [MothixExe](Auteur) - Étudiant en BUT Science des données à l'IUT2 de Grenoble