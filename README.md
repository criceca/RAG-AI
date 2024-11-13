# FastAPI RAG  

## Descripción del Proyecto
Este proyecto implementa una API basada en **FastAPI** que utiliza la técnica de **Recuperación Asistida por Generación (RAG)** para responder preguntas de los usuarios. Combina tres tecnologías principales:

1. **MongoDB**: para almacenar documentos.
2. **Pinecone**: para indexar y realizar búsquedas vectoriales de embeddings de documentos.
3. **OpenAI**: para generar embeddings con "text-embedding-ada-002" y generar respuestas utilizando "gpt-4".

La API proporciona endpoints para almacenar documentos y generar respuestas basadas en la búsqueda vectorial de documentos almacenados.

## Requisitos Previos
- **Python 3.7+**
- Claves de API para OpenAI y Pinecone
- Instancias de MongoDB y Pinecone configuradas

### Instalación de Dependencias

```sh
pip install openai pinecone-client pymongo fastapi pydantic uvicorn
```

## Estructura del Código

### 1. Configuración e Inicialización
- **FastAPI** se utiliza como el framework para definir los endpoints.
- La **API de OpenAI** se inicializa con la clave del usuario.
- Se conecta con una base de datos **MongoDB** y una instancia de **Pinecone**.

### 2. Endpoints y Funcionalidades

#### 2.1 Endpoint para Agregar Documentos (`POST /documentos/`)
- **Entrada**: Un objeto `Documento` con un campo `contenido`.
- **Proceso**:
  - Genera un embedding del documento usando OpenAI.
  - Guarda el documento y su embedding en MongoDB.
  - Inserta el embedding en Pinecone para habilitar la búsqueda.
- **Salida**: Confirmación del documento agregado con éxito, junto con su ID en la base de datos.

#### 2.2 Función para Recuperar Documentos
- **Entrada**: Una pregunta del usuario.
- **Proceso**:
  - Genera un embedding para la pregunta usando OpenAI.
  - Utiliza Pinecone para buscar documentos relevantes.
  - Recupera los contenidos de los documentos desde MongoDB.
- **Salida**: Lista de documentos relevantes.

#### 2.3 Función para Generar Respuesta con GPT-4
- **Entrada**: Pregunta del usuario y documentos recuperados.
- **Proceso**:
  - Genera un contexto a partir de los documentos recuperados.
  - Utiliza GPT-4 para generar una respuesta basada en la pregunta y el contexto.
- **Salida**: Respuesta generada por GPT-4.

#### 2.4 Pipeline de Recuperación y Generación (`pipeline_rag()`)
- Combina la recuperación de documentos y la generación de respuestas.
- **Entrada**: Una pregunta del usuario.
- **Salida**: Respuesta generada por GPT-4 basada en los documentos recuperados.

#### 2.5 Endpoint para Consultar (`POST /rag/`)
- **Entrada**: Una pregunta del usuario.
- **Proceso**: Llama al pipeline RAG para generar una respuesta.
- **Salida**: Respuesta generada.

## Uso
Para ejecutar la API, utilice el siguiente comando:

```sh
uvicorn main:app --reload
```

Una vez que el servidor esté en ejecución, puede probar los endpoints:

1. **Agregar Documento**:
   - URL: `http://127.0.0.1:8000/documentos/`
   - Método: `POST`
   - Body: `{ "contenido": "Este es el contenido del documento." }`

2. **Realizar una Consulta**:
   - URL: `http://127.0.0.1:8000/rag/`
   - Método: `POST`
   - Body: `{ "pregunta": "¿Cuál es la información relevante?" }`

## Detalles Técnicos
- **Embeddings**: Utiliza el modelo "text-embedding-ada-002" de OpenAI para generar embeddings de documentos y preguntas.
- **Búsqueda Vectorial**: Pinecone se usa para indexar y realizar búsquedas vectoriales eficientes.
- **Generación de Respuestas**: GPT-4 es empleado para generar respuestas basadas en los documentos relevantes recuperados.

## Manejo de Errores
- Todos los endpoints y funciones están envueltos en bloques `try-except` para manejar excepciones y devolver errores HTTP apropiados.

## Consideraciones
- **Seguridad**: Las claves de API de OpenAI y Pinecone no deben ser compartidas. Considere el uso de variables de entorno para gestionarlas.
- **Escalabilidad**: Para un entorno de producción, sería recomendable usar un servidor como **Gunicorn** junto con un **proxy reverso**.

## Futuras Mejoras
- **Autenticación**: Agregar autenticación a los endpoints.
- **Optimización**: Mejora de los tiempos de respuesta para consultas con documentos de gran tamaño.
- **Almacenamiento**: Posibilidad de almacenar y manejar documentos más grandes usando almacenamiento distribuido.

## Autor
Este proyecto fue desarrollado como una implementación de un pipeline RAG utilizando FastAPI, OpenAI, Pinecone y MongoDB.

## Licencia
Este proyecto se distribuye bajo la licencia MIT.
