import os
import psycopg2

def get_connection():
    """Crée et retourne une connexion à la base de données en utilisant les variables d'environnement"""
    return psycopg2.connect(
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        sslmode=os.environ.get("DB_SSLMODE")  # obligatoire pour Neon
    )
