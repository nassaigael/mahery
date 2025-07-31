from fastapi import FastAPI, HTTPException

app = FastAPI()


from fastapi import FastAPI, Response, HTTPException, status, Request
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Union

# Initialisation de l'application FastAPI
app = FastAPI()

# --- Stockage en mémoire vive pour les posts (Q4, Q5, Q6) ---
# Utilisation d'une liste simple pour simuler le stockage en mémoire.
# En production, cela serait remplacé par une base de données.
class Post(BaseModel):
    author: str
    title: str
    content: str
    creation_datetime: datetime

# Variable globale pour stocker les posts en mémoire
posts_db: List[Post] = []

# --- Q1 : Route GET /ping ---
@app.get("/ping", response_class=Response, status_code=status.HTTP_200_OK)
async def ping():
    """
    Route GET /ping
    Retourne 'pong' en texte brut avec un code de statut 200.
    """
    return Response(content="pong", media_type="text/plain")

# --- Q2 : Route GET /home ---
@app.get("/home", response_class=Response, status_code=status.HTTP_200_OK)
async def home():
    """
    Route GET /home
    Retourne une page HTML simple avec 'Welcome home!' en titre H1.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Home</title>
    </head>
    <body>
        <h1>Welcome home!</h1>
    </body>
    </html>
    """
    return Response(content=html_content, media_type="text/html")

# --- Q3 : Configuration pour les routes inconnues (404 Not Found) ---
# FastAPI gère cela via un gestionnaire d'exception ou un catch-all.
# Nous allons utiliser la gestion des exceptions pour les 404.
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    """
    Gestionnaire personnalisé pour les erreurs 404.
    Retourne une page HTML '404 NOT FOUND' avec un code de statut 404.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Page Not Found</title>
    </head>
    <body>
        <h1>404 NOT FOUND</h1>
    </body>
    </html>
    """
    return Response(content=html_content, media_type="text/html", status_code=status.HTTP_404_NOT_FOUND)

# --- Q4 : Route POST /posts ---
@app.post("/posts", response_model=List[Post], status_code=status.HTTP_201_CREATED)
async def create_posts(posts: List[Post]):
    """
    Route POST /posts
    Prend une liste d'objets JSON 'post', les mémorise en mémoire vive
    et retourne la liste complète des posts.
    """
    posts_db.extend(posts)  # Ajoute les nouveaux posts à la liste existante
    return posts_db

# --- Q5 : Route GET /posts ---
@app.get("/posts", response_model=List[Post], status_code=status.HTTP_200_OK)
async def get_all_posts():
    """
    Route GET /posts
    Retourne le contenu de la liste d'objets 'posts' actuellement stockés en mémoire.
    """
    return posts_db

# --- Q6 : Route PUT /posts (Idempotente) ---
@app.put("/posts", response_model=List[Post], status_code=status.HTTP_200_OK)
async def upsert_post(post: Post):
    """
    Route PUT /posts (Idempotente)
    Utilise 'title' comme identifiant unique.
    Met à jour un post si le titre existe, sinon l'ajoute.
    Retourne la liste complète des posts.
    """
    found = False
    for i, existing_post in enumerate(posts_db):
        if existing_post.title == post.title:
            # Si le titre existe, mettre à jour le post
            # On pourrait ajouter une logique pour vérifier si les valeurs ont réellement changé
            # et retourner 204 No Content si aucune modification n'est nécessaire.
            posts_db[i] = post
            found = True
            break
    
    if not found:
        # Si le titre n'existe pas, ajouter le nouveau post
        posts_db.append(post)
        # Bien que l'énoncé demande 200 OK pour PUT, un 201 Created serait sémantiquement plus précis ici
        # si une création a lieu. Pour se conformer à la consigne de retourner 200 OK, nous le gardons.
        # Toutefois, en API REST strict, PUT devrait retourner 201 si la ressource est créée.
        # Vous pouvez changer 'status.HTTP_200_OK' à 'status.HTTP_201_CREATED' pour ce cas spécifique si désiré.
        pass # Le status_code par défaut de la route est 200 OK, ou 201 si on le set dans le code.

    return posts_db

# Exemple de démarrage de l'application (pour le développement)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)