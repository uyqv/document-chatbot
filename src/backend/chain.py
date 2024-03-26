from typing import Sequence
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores.elasticsearch import ElasticsearchStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.retrievers import BaseRetriever
from langchain.memory import ElasticsearchChatMessageHistory
from langchain_core.documents import Document
from langchain_core.runnables import (
    Runnable,
    RunnablePassthrough,
)
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from elasticsearch import Elasticsearch, NotFoundError
from common.cfgcommon import CfgCommon
from uuid import uuid4
import logging
import uuid

"""
LangChain Chatbot with Elasticsearch:
- Conversational AI using LangChain and OpenAI for response generation.
- Elasticsearch for chat history and document indexing.
- Dynamic question rephrasing and context-aware responses.
- Session management with unique IDs and history cleanup.
- Uses Elasticsearch vector storage and OpenAI embeddings for similarity.
- Configurable response templates for custom formatting.
"""

RESPONSE_TEMPLATE = """\
    You are an expert programmer and problem-solver, tasked with answering any question \
    about InfoReach.
    
    Generate a comprehensive and informative answer for the \
    given question based solely on the context provided and the chat history. You must \
    only use information from the provided context and the chat history. Use an unbiased and \
    journalistic tone.
    
    You should use bullet points in your answer for readability. If the question is simple \
    do not give a long answer.
    
    If there is nothing in the context relevant to the question at hand, just say "Hmm, \
    I'm not sure." Don't try to make up an answer.
    
    add to include chathistory
    
    <context>
        {context} 
    <context/>
    
    Question: {input}
    
    REMEMBER: If there is no relevant information within the context, just say "Hmm, I'm \
    not sure." Don't try to make up an answer. Anything between the preceding 'context' \
    html blocks is retrieved from a knowledge bank, not part of the conversation with the \
    user.\
    """

REPHRASE_TEMPLATE = """\
    Given the following conversation and a follow up question, rephrase the follow up \
    question to be a standalone question. If there is no relevant information within \
    the context, just say "Hmm, I'm not sure." Don't try to make up an answer.
    
    Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone Question:
    """

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='chatbot.log',
                    filemode='a')
logger = logging.getLogger(__name__)


class ChatbotWithHistory:
    def __init__(self):
        self.session_id = str(uuid4())
        self.index_name = CfgCommon().INDEX_NAME
        self.es_connection = Elasticsearch(
            ["http://localhost:9200"],
            basic_auth=("elastic", CfgCommon().ELASTIC_CLOUD_PASSWORD)
        )

        self.llm = ChatOpenAI(
            openai_api_key=CfgCommon().OPENAI_API_KEY,
            model=CfgCommon().LMM_MODEL
        )

        self.retriever = self.get_retriever()
        self.conversation_chain = self.create_retriever_chain()

        self.chat_history_index = f"chat-history-{self.session_id}"
        self.chat_history = ElasticsearchChatMessageHistory(
            es_connection=self.es_connection,
            session_id=self.session_id,
            index=self.chat_history_index
        )

        logger.info("Initializing chatbot with session ID: %s", self.session_id)

    def get_retriever(self) -> BaseRetriever:
        embedding = OpenAIEmbeddings(api_key=CfgCommon().OPENAI_API_KEY)
        vector_store = ElasticsearchStore(
            es_connection=self.es_connection,
            index_name=self.index_name,
            embedding=embedding,
        )
        return vector_store.as_retriever()

    def create_retriever_chain(self) -> Runnable:
        condense_question_prompt = PromptTemplate.from_template(REPHRASE_TEMPLATE)

        condense_question_chain = condense_question_prompt | self.llm | StrOutputParser()

        retriever_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            return_source_documents=True,
        )

        return retriever_chain

    def format_docs(self, docs: Sequence[Document]) -> str:
        return "\n".join(f"<doc id='{i}'>{doc.page_content}</doc>" for i, doc in enumerate(docs))

    def process_query(self, query):
        query_id = str(uuid.uuid4())
        sources = set()
        logger.info("Received query: %s with ID: %s", query, query_id)

        try:
            context = (
                RunnablePassthrough.assign(docs=self.conversation_chain)
                .assign(context=lambda x: self.format_docs(x["docs"]))
                .with_config(run_name="RetrieveDocs")
            )
            prompt = RESPONSE_TEMPLATE.format(input=query, context=context)

            logger.info("Generating response for query ID: %s", query_id)
            result = self.conversation_chain({"question": prompt, "chat_history": self.chat_history.messages})

            for doc in result['source_documents']:
                sources.add(doc.metadata['source'])
            sources = sorted(sources)
            sources_str = "; ".join(sources)

            final_answer = f"{result['answer']} \n\n\nSources: {sources_str}"
            logger.info("Generated response: %s for query ID: %s", result['answer'], query_id)
            logger.info("Sources: %s", sources_str)

            self.chat_history.add_user_message(query)
            self.chat_history.add_ai_message(result["answer"])

            return final_answer
        except Exception as e:
            logger.error("An error occurred while processing query ID: %s, Error: %s", query_id, e, exc_info=True)
            return "Hmm, I'm not sure."

    def terminate_conversation(self):
        try:
            self.es_connection.indices.delete(index=self.chat_history_index)
            logger.info("Chat history for session ID %s has been deleted.", self.session_id)
        except NotFoundError:
            logger.warning("Chat history not found or already deleted for session ID %s.", self.session_id)


# chatbot = ChatbotWithHistory()
# chatbot.process_query("Give a one sentence answer, what is the FIX engine")
# chatbot.terminate_conversation()