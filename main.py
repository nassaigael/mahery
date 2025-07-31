from fastapi import FastAPI, Response, HTTPException, status, Request, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Union

# Initialisation de l'application FastAPI
app = FastAPI()

# --- Stockage en mémoire vive pour les posts (Q4, Q5, Q6) ---
class Post(BaseModel):
    author: str
    title: str
    content: str
    creation_datetime: datetime

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
    posts_db.extend(posts)
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
            posts_db[i] = post
            found = True
            break
    
    if not found:
        posts_db.append(post)
    
    return posts_db

# --- NOUVEAU : Q7 : Route GET /ping/auth avec Basic Authentication ---

# 1. Instancier le mécanisme d'authentification Basic
security = HTTPBasic()

# 2. Définir la fonction de dépendance pour la Basic Authentication
# Cette fonction sera appelée par FastAPI avant d'exécuter la route /ping/auth
async def verify_basic_auth(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Vérifie les identifiants Basic Authentication.
    Si les identifiants sont valides, elle renvoie le nom d'utilisateur.
    Sinon, elle lève une HTTPException 401 Unauthorized.
    """
    correct_username = "admin"
    correct_password = "123456"

    # Vérifier le nom d'utilisateur
    if credentials.username != correct_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant incorrect",
            headers={"WWW-Authenticate": "Basic"}, # Indique au client le type d'authentification attendu
        )
    
    # Vérifier le mot de passe
    if credentials.password != correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mot de passe incorrect",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Si les deux sont corrects, l'authentification est réussie
    return credentials.username # Ou n'importe quelle valeur pour signifier le succès

# 3. Créer la nouvelle route /ping/auth et injecter la dépendance d'authentification
@app.get("/ping/auth", response_class=Response, status_code=status.HTTP_200_OK)
async def ping_auth(username: str = Depends(verify_basic_auth)):
    """
    Route GET /ping/auth
    Retourne 'pong' en texte brut seulement si l'authentification Basic est réussie.
    """
    # Si nous arrivons ici, cela signifie que la dépendance verify_basic_auth a renvoyé avec succès
    # et que l'utilisateur est authentifié.
    return Response(content="pong", media_type="text/plain")

# --- NOUVEAU : Gestionnaire d'exception pour les erreurs 401 spécifiques (personnalisation du message d'erreur) ---
# Ceci est optionnel mais permet de personnaliser davantage la réponse en cas d'erreur d'authentification.
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        # Si la requête n'a pas pu être authentifiée
        # Vous pouvez choisir entre JSON ou texte brut ici
        
        # Réponse en texte brut
        # return Response(content=f"Erreur d'authentification : {exc.detail}", media_type="text/plain", status_code=status.HTTP_401_UNAUTHORIZED, headers=exc.headers)
        
        # Réponse en JSON (par défaut pour HTTPException, mais explicité ici)
        return Response(
            content='{"message": "La ressource demandée ne peut vous être accordée. ' + exc.detail + '"}',
            media_type="application/json",
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers=exc.headers
        )
    # Pour toutes les autres exceptions HTTP, utilisez le gestionnaire par défaut de FastAPI
    return await request.app.default_exception_handler(request, exc)