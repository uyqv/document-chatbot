import os
import logging
import json
from common.cfgcommon import CfgCommon
from elasticsearch import Elasticsearch
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders.pdf import PDFMinerLoader
from langchain_community.vectorstores.elasticsearch import ElasticsearchStore
from langchain_openai import OpenAIEmbeddings

"""
Elasticsearch PDF Indexer:
- Indexes PDFs in a folder into Elasticsearch using PDFMiner and OpenAI embeddings.
- Avoids duplicates, offers re-indexing of missed files.
- Configured with constants for cloud ID, API key.
- Logs progress and errors.
"""

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_index_tracking_file(tracking_file_path):
    try:
        with open(tracking_file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_index_tracking_file(tracking_file_path, tracking_data):
    with open(tracking_file_path, 'w') as file:
        json.dump(tracking_data, file, indent=4)


def index_pdf_folder(path, index):
    total_files = 0
    text_splitter = CharacterTextSplitter()
    tracking_file_path = 'common/indexed_files.json'
    embeddings = OpenAIEmbeddings(api_key=CfgCommon().OPENAI_API_KEY)
    es = Elasticsearch(
        ["http://localhost:9200"],
        basic_auth=("elastic", CfgCommon().ELASTIC_CLOUD_PASSWORD)
    )

    tracking_data = load_index_tracking_file(tracking_file_path)
    all_pdf_files = [f for f in os.listdir(path) if f.endswith('.pdf')]
    indexed_files = tracking_data.get(index, [])

    if not es.indices.exists(index=index):
        logging.info(f"Index {index} does not exist. Creating...")
        es.indices.create(index=index)
    else:
        logging.info(f"Index {index} already exists.")

    for filename in os.listdir(path):
        if filename.endswith(".pdf"):
            if filename in indexed_files:
                logging.info(f"Skipping {filename}, already indexed.")
                continue

            file_path = os.path.join(path, filename)
            logging.info(f"Processing {file_path}...")

            try:
                loader = PDFMinerLoader(file_path)
                docs = loader.load()
                docs = text_splitter.split_documents(docs)

                ElasticsearchStore.from_documents(
                    docs,
                    es_connection=es,
                    index_name=index,
                    embedding=embeddings,
                )
                logging.info(f"Successfully indexed {filename}")
                indexed_files.append(filename)
                total_files += 1
            except Exception as e:
                logging.error(f"Failed to index {filename} due to {e}")

    not_indexed_files = list(set(all_pdf_files) - set(indexed_files))
    if not_indexed_files:
        logging.info("\nThe following files have not been indexed:")
        for file in not_indexed_files:
            logging.info(file)
    else:
        logging.info(f"\nAll {total_files} files have been successfully indexed.")

    tracking_data[index] = indexed_files
    save_index_tracking_file(tracking_file_path, tracking_data)


if __name__ == "__main__":
    folder_path = input("Enter the path to the folder containing PDF documents: ")
    index_name = input("Enter the Elasticsearch index name: ")
    index_pdf_folder(folder_path, index_name)
