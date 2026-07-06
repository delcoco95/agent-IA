"""
Fichier d'entrée WSGI pour Phusion Passenger sur o2switch.
Ce fichier est requis par l'outil "Setup Python App" de cPanel.

L'outil s'attend à trouver une variable `application` pointant vers l'application WSGI.
"""
import sys
import os

# Ajouter le répertoire courant au path Python
# Cela permet d'importer les modules du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importer l'application Flask depuis app.py
from app import app

# La variable `application` est requise par Phusion Passenger
# Elle doit pointer vers l'instance de l'application WSGI (Flask dans ce cas)
application = app
