#libraries
import openai

import pymongo
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from pinecone import Pinecone

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
#os.environ.get("SECRET_KEY")

# Inicialización de la aplicación FastAPI
app = FastAPI()

# Clave de API de OpenAI
openai.api_key = 'TU_CLAVE_API_DE_OPENAI'

# Configuración de MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['base_de_datos_documentos']
collection = db['documentos']

# Configuración de Pinecone
pc = Pinecone(api_key='TU_API_KEY_PINECONE', environment='us-west1-gcp')
index = pc.Index('nombre_de_tu_indice')

# Modelo para recibir nuevos documentos
class Documento(BaseModel):
    contenido: str

# 1. Endpoint para agregar documentos
@app.post("/documentos/")
async def agregar_documento(documento: Documento):
    try:
        # # Generar embeddings avanzados con OpenAI
        # embedding = openai.Embedding.create(
        #     input=documento.contenido,
        #     model="text-embedding-ada-002"
        # )['data'][0]['embedding']

        # Guardar el documento en MongoDB
        document_id = collection.insert_one({
            "contenido": documento.contenido,
            #"embedding": embedding
        }).inserted_id

        # Añadir el embedding a Pinecone para búsqueda vectorial
        #index.upsert([(str(document_id), embedding)])
        # Agregar el documento directamente en el índice de Pinecone (Pinecone genera el embedding)
        index.upsert([
            {"id": str(document_id), "values": documento.contenido}  # Se envía el contenido, Pinecone generará el embedding automáticamente
        ])

        return {"mensaje": "Documento agregado con éxito", "document_id": str(document_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Recuperar documentos usando Pinecone
def recuperar_documentos(pregunta, top_k=2):
    try:
        # Generar embeddings de la pregunta
        # pregunta_embedding = openai.Embedding.create(
        #     input=pregunta,
        #     model="text-embedding-ada-002"
        # )['data'][0]['embedding']
        # Realizar la búsqueda en Pinecone (Pinecone generará el embedding de la pregunta y hará la búsqueda)
        #result = index.query(queries=[pregunta_embedding], top_k=top_k)      

        # Realizar la búsqueda en Pinecone
        result = index.query(queries=[pregunta], top_k=top_k)

        # Recuperar documentos desde MongoDB usando los IDs obtenidos
        document_ids = [match['id'] for match in result['matches']]
        documentos_recuperados = collection.find({"_id": {"$in": [pymongo.ObjectId(doc_id) for doc_id in document_ids]}})

        return [doc['contenido'] for doc in documentos_recuperados]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#Generar respuestas usando GPT-4
def generar_respuesta(pregunta, documentos_recuperados):
    contexto = "\n".join(documentos_recuperados)

    # Llamar a la API de GPT-4 para generar la respuesta
    respuesta = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un asistente experto en diferentes temas."},
            {"role": "user", "content": f"Pregunta: {pregunta} \nDocumentos: {contexto}"}
        ]
    )

    return respuesta['choices'][0]['message']['content']


#recuperación + generación
def pipeline_rag(pregunta):
    # Recuperar documentos relevantes
    documentos_recuperados = recuperar_documentos(pregunta)

    # Generar respuesta con GPT-4 basada en los documentos recuperados
    respuesta = generar_respuesta(pregunta, documentos_recuperados)

    return respuesta

# 5. Endpoint para realizar la consulta
@app.post("/rag/")
async def rag_endpoint(pregunta: str):
    try:
        # Ejecutar el pipeline RAG con la pregunta del usuario
        respuesta = pipeline_rag(pregunta)
        return {"pregunta": pregunta, "respuesta": respuesta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("Starting webserver...")
    uvicorn.run(
        app,
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 80)),
        debug=os.getenv("DEBUG", False),
        log_level=os.getenv('LOG_LEVEL', "info"),
        proxy_headers=True
    )