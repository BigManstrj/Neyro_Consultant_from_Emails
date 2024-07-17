from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from dotenv import load_dotenv
import openai
import os
import importlib
import mdTOdocx
import requests
import re

# получим переменные окружения из .env
load_dotenv()

# API-key
openai.api_key = os.environ.get("OPENAI_API_KEY")

class Chunk():

    def __init__(self, path_to_base, faiss_db_name):
        self.path_to_base = path_to_base  # полное имя базы в md или txt
        self.path_to_base_w2q = f'{path_to_base}_2.md'  # имя md файла для базы знаний с дублирующимися вопросами

        self.db = self.create_index_base()
        self.docx_file = f'{self.path_to_base}.docx' # полное имя базы в docx.
        self.faiss_db_name = faiss_db_name

    def read_document(self):
        with open(self.path_to_base_w2q, 'r', encoding='utf-8') as file:
            return file.read()

    def create_index_base(self):
        document = self.read_document()
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        source_chunks = splitter.split_text(document)
        print(f'\n\nТекст разбит на {len(source_chunks)} чанков.')
        embeddings = OpenAIEmbeddings()
        return FAISS.from_documents(source_chunks, embeddings)


    def save_faiss_db(self):
        self.db.save_local(self.faiss_db_name)
        return

    def load_faiss_db(self):
        embeddings = OpenAIEmbeddings()
        faiss_db = FAISS.load_local(self.faiss_db_name, embeddings)
        return faiss_db


    def load_document_text(self, docx_url: str) -> str:
        ''' функция для загрузки документа docx по ссылке из гугл драйв '''

        # Extract the document ID from the URL
        match_ = re.search('/document/d/([a-zA-Z0-9-_]+)', docx_url)
        if match_ is None:
            raise ValueError('Invalid Google Docs URL')
        doc_id = match_.group(1)

        # Download the document as plain text
        response = requests.get(f'https://docs.google.com/document/d/{doc_id}/export?format=docx')
        response.raise_for_status()
        text = response.content

        with open(self.docx_file, 'wb') as f:
            f.write(response.content)

        return text

    def google_docx_to_md(self, docx_url:str):
        ''' функция загрузки базы из google docx, конвертация в md и сохранения на диске '''

        self.load_document_text(docx_url)

        # конвертация в md для базы знаний
        mdTOdocx.convert_docx_to_md(self.docx_file, self.path_to_base)  # обычная ковертация в md для последующего ковертации в docx или excel
        mdTOdocx.convert_docx_to_md_w2q(self.docx_file, self.path_to_base_w2q) # ковертация в md c дублированием вопросов ка простой текст для базы знаний
        
        # пересоздание векторной базы
        self.db = self.create_index_base() 
        return

    async def async_get_answer(self, query:str = None):
        '''Асинхронная функция получения ответа от chatgpt
        '''
        # релевантные отрезки из базы
        docs = self.db.similarity_search(query, k=4)
        message_content = '\n'.join([f'{doc.page_content}' for doc in docs])
        # print("Найден чанки:")
        # print(docs)
       
        system = """Вы консультант службы поддержки клиентов в авиакомпании MEGACOMPANY.
        Ваша задача - отвечать на вопросы клиентов, используя исключительно предоставленные вам части текста. 
        Вы не должны ссылаться на эти части текста напрямую и не должны придумывать ответы от себя. 
        Все ваши ответы должны основываться исключительно на предоставленной информации. 
        Будьте подробным и точным в своих ответах. НИКОГДА НЕ УПОМИНАЙТЕ В ОТВЕТЕ ПЕРСОНАЛЬНЫЕ ДАННЫЕ ЛЮДЕЙ: ФАМИЛИЮ, ИМЯ, НОМЕР ПАСПОРТА! Будьте предельно внимательным к персональным данным!"""

        user = f"""Клиент задал вопрос. Используйте предоставленные ниже части текста, 
        чтобы ответить на вопрос клиента. Не ссылайтесь на текст напрямую и не придумывайте ничего от себя. 
        Ответ должен быть основан только на информации из предоставленных текстов.
        Если в предоставленной вам информации нет ответа на вопрос клиента, скажите: "У меня нет такой информации" и рекомендуйте клиенту обратиться в службу поддержки: E-mail: mail@mail.com Тел: +8-888-8888
        Ваш ответ должен быть лаконичным, но при этом передавать все важные детали из предоставленного вам документа.
        Ответ начинайте с фразы: Здравствуйте, уважаемый пассажир! 
        Документ с информацией для ответа клиенту: {message_content}\n\nВопрос клиента: \n{query}"""


        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]

        # получение ответа от chatgpt
        completion = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo",
                                                  messages=messages,
                                                  temperature=0)
        
        return completion.choices[0].message.content