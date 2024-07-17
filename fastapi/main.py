from fastapi import FastAPI
from chunks import Chunk
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os


print(os.listdir())

# инициализация индексной базы для linux!!!
chunk = Chunk(path_to_base="../base/output/base_final.md", faiss_db_name="faiss_db") # для linux
# chunk = Chunk(path_to_base="./base/output/base_final.md", faiss_db_name="faiss_db")


# класс с типами данных параметров 
class Item(BaseModel): 
    text: str

# создаем объект приложения
app = FastAPI()

# настройки для работы запросов
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# функция обработки get запроса + декоратор 
@app.get("/")
def read_root():
    return {"message": "server is run"}

# перезагрузка базы из гугл docx и создание векторной базы
@app.post("/api/load_base_from_google_docx")
def load_base_from_google_docx(docx_url: Item):
    print(docx_url.text)
    chunk.google_docx_to_md(docx_url.text)
    return {"message": f"base from {docx_url} save in md format and faiss db reloaded"}

# перезагрузка базы faiss из сохраненной на диске 
@app.get("/api/reload_faiss_db_from_disk")
def reload_base_from_disk():
    chunk.load_faiss_db()
    return {"message": f"faiss db reloaded from disk"}

# перезагрузка базы faiss из сохраненной на диске 
@app.get("/api/save_faiss_db_to_disk")
def save_faiss_db_to_disk():
    chunk.save_faiss_db()
    return {"message": f"faiss db saved to disk"}


# асинхронная функция обработки post запроса + декоратор 
@app.post("/api/get_answer_async")
async def get_answer_async(question: Item):
    answer = await chunk.async_get_answer(query=question.text)
    return {"message": answer}

if __name__ == "__main__":
    import uvicorn 
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
    # uvicorn.run('main:app', host='127.0.0.1', port=5000, reload=True)
