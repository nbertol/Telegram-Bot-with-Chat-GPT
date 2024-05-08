from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader, DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")


def load_documents(url):
    loader = WebBaseLoader(url)
    return loader.load()

def create_vectorstore(splits):
    return FAISS.from_documents(documents=splits, embedding=OpenAIEmbeddings())

def create_retriever(vectorstore):
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

def format_document_content(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def create_prompt_template():
    return """You are an assistant for the latoken crypto hackathon and if the information is not in the provided context you should not answer.
    Use the following pieces of retrieved context to answer the question.
    If you don't know the answer, give the necessary informations about the hackathon.
    \nQuestion: {question} \nContext: {context}  \nAnswer:"""

def generate_answer_question_chain(retriever, llm):
    prompt_template = create_prompt_template()
    prompt = ChatPromptTemplate.from_template(prompt_template)
    rag_chain = (
        {"context": retriever | format_document_content, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain

def directory_loader(path):
    loader = DirectoryLoader(path, glob='**/*.txt', loader_cls=TextLoader )
    return loader.load()

def answer_question(question: str="Hello, could you give me information about the hackathon?", url: str="https://deliver.latoken.com/hackathon", directory_path='./texts')-> str:
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", api_key=api_key)

    docs = load_documents(url)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    documents = text_splitter.split_documents(docs)
    documents_txt = directory_loader(directory_path)
    documents = documents + documents_txt
    vectorstore = create_vectorstore(documents)
    retriever = vectorstore.as_retriever()
    rag_chain = generate_answer_question_chain(retriever, llm)
    return rag_chain.invoke(question)


