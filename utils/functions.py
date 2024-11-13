import openai
import pinecone
#Recuperar documentos usando Pinecone
def recuperar_documentos(pregunta, top_k=2):
    try:
        # Generar embeddings de la pregunta
        pregunta_embedding = openai.Embedding.create(
            input=pregunta,
            model="text-embedding-ada-002"
        )['data'][0]['embedding']

        # Realizar la búsqueda en Pinecone
        result = index.query(queries=[pregunta_embedding], top_k=top_k)

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
