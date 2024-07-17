from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings, VectorStoreIndex

from llama_index.core.node_parser import (
    SentenceSplitter,
    SemanticSplitterNodeParser,
)
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

import os
import torch
import os

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.weaviate import WeaviateVectorStore
import weaviate
from weaviate.embedded import EmbeddedOptions

from llama_index.core.postprocessor import SentenceTransformerRerank

from llama_index.core.indices.query.query_transform import HyDEQueryTransform
import os
import streamlit as st

def semantic_splitter(pdf_folder, embed_model, device_type):
  documents = SimpleDirectoryReader(pdf_folder).load_data()
  splitter = SemanticSplitterNodeParser(
      buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
  )
  nodes = splitter.get_nodes_from_documents(documents)
  return nodes

def vector_storage(pdf_folder):
  device_type = torch.device("cuda" if torch.cuda.is_available else "cpu")
  embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5", device=device_type) # must be the same as the previous stage
  client = weaviate.Client(embedded_options=EmbeddedOptions())
  index_name = "RAG_Doc"

  # Construct vector store
  vector_store = WeaviateVectorStore(
      weaviate_client = client,
      index_name = index_name,
  )
  # Set up the storage for the embeddings
  storage_context = StorageContext.from_defaults(vector_store=vector_store)

  # If an index with the same index name already exists within Weaviate, delete it
  if client.schema.exists(index_name):
      client.schema.delete_class(index_name)

  # Setup the index
  # build VectorStoreIndex that takes care of chunking documents
  # and encoding chunks to embeddings for future retrieval
  nodes = semantic_splitter(pdf_folder, embed_model, device_type)
  index = VectorStoreIndex(
      nodes,
      storage_context = storage_context,
      embed_model=embed_model
  )
  return index

def retrival_reraking(pdf_folder, query):
  #https://console.groq.com/keys
  from llama_index.llms.groq import Groq

  llm = Groq(model="llama3-8b-8192", api_key="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")
  Settings.llm = llm

  hyde = HyDEQueryTransform(include_original=True)

  query_bundle = hyde.run(query)
  rerank_postprocessor = SentenceTransformerRerank(
      model='mixedbread-ai/mxbai-rerank-xsmall-v1',
      top_n=2, # number of nodes after re-ranking,
      keep_retrieval_score=True,
  )
  index = vector_storage(pdf_folder)
  query_engine = index.as_query_engine(
      similarity_top_k=2,  # Number of nodes before re-ranking
      node_postprocessors=[rerank_postprocessor],
  )
  return query_engine.query(query).response

def list_of_symptoms(history_chat, summarize ):
  #llm = Groq(model="llama3-8b-8192", api_key="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")
  from groq import Groq
  client = Groq(api_key= "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",)
  if summarize == None:
    summarize = "Không có hồ sơ trước đó"
  prompt = f"""
  Hồ sơ bệnh nhân trước đó: {summarize}
  Bạn đang đóng vai là một nhà tư vấn sức khỏe tâm thần, người dùng tìm đến bạn là người cần tham vấn sức khỏe tâm thần, bạn hãy tóm tắt thành các thông tin cần thiết bằng tiếng việt dựa vào hồ sơ bệnh nhân trước đó và cuộc hội thoại sau:
  {history_chat}
  """
    # Gọi API của Groq để sinh ra câu trả lời
  chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-70b-8192",  # Chọn model phù hợp
    )

  return chat_completion.choices[0].message.content

def new_response(prompt, response1, summarize):
              answer = prompt
              history_chat = f"""
              Người tư vấn: {response1}
              Người dùng: {answer}
              """
              # Process updated conversation history to get summary
              summarize = list_of_symptoms(history_chat, summarize)
              # Prepare next query based on updated conversation
              query2 = f"""
              Bạn đang trong vai một người tư vấn sức khỏe tâm thần.
              Hồ sơ bệnh nhân chẩn đoán trước đó:
              {summarize}
              Đoạn hội thoại tiếp theo:
              {history_chat}
              Hãy đưa ra lời khuyên bằng tiếng việt dài 150 từ, không được hơn
              """
              # Get next response based on updated query
              response2 = retrival_reraking("./data", query2)
              return summarize, response2

def simulate_conversation():

    st.title("Simulate Counseling Conversation")

    st.write("Trước khi bắt đầu cuộc trò chuyện, bạn hãy giúp mình trả lời ba câu hỏi bên dưới để mình hiểu nhau hơn tí nhé")

    questions = [
        "Gần đây có chuyện gì khiến bạn cảm thấy cần tìm ai đó để chia sẻ không?",
        "Điều gì đang làm bạn cảm thấy buồn hay lo lắng?",
        "Điều gì khiến bạn chọn gặp mình ở đây hôm nay?"
    ]

    history_chat1 = ""
    answers = [""] * len(questions)  # List to store user answers, initialized with empty strings


    # Loop through each question and get user input
    for idx, question in enumerate(questions):
        answers[idx] = st.text_input(f"Người tư vấn: {question}")
        history_chat1 += f"Người tư vấn: {question}\nNgười dùng: {answers[idx]}\n"

    # Wait until all questions have been answered
    while any(answer == "" for answer in answers):
        st.warning("Vui lòng trả lời đầy đủ các câu hỏi trước khi tiếp tục.")
        st.stop()  # Stop execution until all questions are answered
    if "summarize1" not in st.session_state:
      st.session_state.summarize1 = []
      # Process the conversation history to get initial summary
      summarize = list_of_symptoms(history_chat1, None)
      st.session_state.summarize1.append(summarize)
      # Display initial query based on conversation history
      query2 = f"""
      Bạn đang trong vai một người tư vấn sức khỏe tâm thần.
      Hồ sơ bệnh nhân chẩn đoán trước đó:
      {summarize}
      Đoạn hội thoại tiếp theo:
      Người tư vấn: {history_chat1.split("Người tư vấn:")[-1].split("Người dùng")[0]}
      Người dùng:  {history_chat1.split("Người tư vấn:")[-1]}
      Hãy trả lời, đưa ra lời khuyên bằng tiếng việt.
      """
      if "messages" not in st.session_state:
          st.session_state.messages = []

      response = retrival_reraking("./data", query2)
      with st.chat_message("assistant"):
              st.markdown(response)
              st.session_state.messages.append({"role": "assistant", "content": response})

    if prompt := st.chat_input("write something..."):
        for message in st.session_state.messages:
              with st.chat_message(message["role"]):
                  st.markdown(message["content"])
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        latest_summarize = st.session_state.summarize1[-1]
        lastest_response = st.session_state.messages[-1]["content"]
        summarize_result, response = new_response(prompt, lastest_response, latest_summarize)
        st.session_state.summarize1.append(summarize_result)
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
if __name__ == "__main__":
  simulate_conversation()