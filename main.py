''' 
How the AI Works from a high level
- First the words in your file are broken down into tokens - which are words or parts of words
- Each token has a corresponding index, because the AI works with numbers, its just a pointer to the word or part of the word
- Each token points to one row in the embedding table, and in this case each row has 1024 numbers and now each word is a vector in 1024 dimensional space
- The more dimensions, the more the AI has space for encoding information and differenating information 
- The table is learned during training, at first each token ID just points to a random 1024 dimensional vector, and then the idea is the AI needs to predict a word in the sentence 
- If the AI is wrong with what it predicts it computes the loss and changes the vector slighly to get a better predicition using gradient descent 
- The idea with gradient descent is we try to find the minimum of the loss function, so each time the model is wrong we compute the loss, compute the gradient, and move a little bit in the opposite direction from the gradient 
- This is because the gradient gives you the maximum possible increase
- We update every number slighly opposite the gradient -> We have losses for how close each word is and we have losses for how good the prediction was
'''
'''
What we use is RAG 
- Embed notes into vectors
- User asks a question and you embed the question 
- Measure similartiy between the question vector and the docuement vectors 
- The closest vector, feed into command R and get the answer
'''

from cohere.client_v2 import ClientV2 
import numpy
import os 

# Front end 
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

API_KEY = "uIjbkHber3Y56hZsko4B8oNw4FkqzOcnp6uSHnQ6"
# Create a client object with the API KEY to access cohere models
cohere_client = ClientV2(API_KEY)

# Creates the server, the router for all API endpoints, the place where you register routes, runs when you start the app
# Route includes the url path, method, and handler, and the router runs the correct function when someone goes to the a url 
app = FastAPI()
emb = [] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Using the formula cos(theta) = a*b / |a||b| to get cosine similarity of vectors 
def cosine_dot_product(a, b): 
    return numpy.dot(a, b) / (numpy.linalg.norm(a) * numpy.linalg.norm(b))

# Any class that inherits from BaseModel, what happens is any incoming JSON from the front end, this checks if the field question exsists and is a string 
# Otherwise FastAPI automatically returns an error
class Query(BaseModel): 
    question: str


docs = [] 
# Add all the files names that we want for names into a list
file_names = []

for file_name in os.listdir("Notes"):
    with open(f"Notes/{file_name}", "r", encoding="utf-8") as f:
        text = f.read()
        docs.append(text)
        file_names.append(file_name)

        emb_resp = cohere_client.embed(
            texts=[text],
            model="embed-english-v3.0",
            input_type="search_document"
        )
        emb.append(numpy.array(emb_resp.embeddings.float[0]))

# When we get a post request from the frontend do the below 
# The function is async meaning while waiting on something, like response from Cohere API, it other requests can be accepted and worked on
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    text = contents.decode("utf-8")  # assuming text file
    docs.append(text)
    file_names.append(file.filename)

    # # Creates an embedding and extracts only the list of numbers 
    emb_resp = cohere_client.embed(
        texts=[text],
        model="embed-english-v3.0",
        input_type="search_document"
    )
    emb.append(numpy.array(emb_resp.embeddings.float[0]))
    # file.filename comes from the UploadFileName class 
    return {"filename": file.filename, "status": "uploaded"}

@app.post("/ask")
async def ask_question(query: Query):
    if not docs:
        return {"answer": "No documents uploaded yet.", "source": ""}
    # # Creates an embedding and extracts only the list of numbers 
    # emb_resp = cohere_client.embed(texts=docs, model="embed-english-v3.0", input_type="search_document")
    # emb = [numpy.array(e) for e in emb_resp.embeddings.float]

    query_resp = cohere_client.embed(texts=[query.question], model="embed-english-v3.0",  input_type="search_document")
    query_emb = [numpy.array(e) for e in query_resp.embeddings.float]

    scores = [] 
    for e in emb: 
        sim = cosine_dot_product(query_emb[0], e)
        scores.append(sim)

    # We want the score closest to 1, and cosine similarity gives us the angle between two vectors, so its always gonna be between 0 and pi 
    best_index = int(numpy.argmax(scores))
    best_doc = docs[best_index]

    response = cohere_client.chat(model="command-a-03-2025", 
                                messages=[
                                    {"role": "system", "content": "You are hired to the answer a user's question based the context provided by them. Please note that the context provided comes from the user's notes, so if every time you want to say context please instead say notes. You have been instructed to only use this info to answer the question. If you know the answer from the context is wrong, please still provide the wrong answer and then tell the user is wrong and what the correct answer is. If the user's prompt and the context provided have no relation, tell the user that and then tell them the answer to their question. Also the user cannot respond after this, so do not ask them anymore questions or offer to do anything more after you have provided the previous responses. Do not use markdown format."},
                                    {"role": "user", "content": f"Context:\n{best_doc}\n\nQuestion: {query.question}"}
                                  ]
                                 )
    
    answer = response.message.content[0].text
    # Python dictionary automatically becomes JSON 
    return {
        "answer": answer,
        "source": file_names[best_index]
    } 






