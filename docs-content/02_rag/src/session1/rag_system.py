from typing import List, Dict, Any, Optional
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from config import RAGConfig
from vector_store import VectorStore

class BasicRAGSystem:
    """Core RAG system combining retrieval and generation."""
    
    def __init__(self, config: RAGConfig):
        self.config = config
        self.vector_store = VectorStore(config)
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            openai_api_key=config.OPENAI_API_KEY,
            model_name=config.LLM_MODEL,
            temperature=0.7
        )
        
        # Initialize prompt template
        self.prompt_template = self._create_prompt_template()

    def _create_prompt_template(self) -> PromptTemplate:
        """Create the RAG prompt template."""
        template = """You are a helpful AI assistant. Use the following context to answer the user's question. 
If you cannot find the answer in the context, say "I don't have enough information to answer that question."

Context:
{context}

Question: {question}

Answer: Let me help you with that based on the provided information."""
        return PromptTemplate(
            input_variables=["context", "question"],
            template=template
        )

    def _prepare_context(self, documents: List[Document]) -> str:
        """Prepare context from retrieved documents."""
        if not documents:
            return "No relevant information found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Unknown")
            chunk_info = f"[Source {i}: {source}]"
            context_parts.append(f"{chunk_info}\n{doc.page_content}")
        
        return "\n\n".join(context_parts)

    def query(self, question: str, k: Optional[int] = None) -> Dict[str, Any]:
        """Process a RAG query and return detailed results."""
        # Step 1: Retrieve relevant documents
        retrieved_docs = self.vector_store.similarity_search_with_scores(
            query=question, 
            k=k or self.config.TOP_K
        )
        
        if not retrieved_docs:
            return {
                "answer": "I don't have any relevant information to answer your question.",
                "sources": [],
                "confidence": 0.0
            }

        # Step 2: Prepare context
        documents = [doc for doc, score in retrieved_docs]
        context = self._prepare_context(documents)
        
        # Step 3: Generate response
        prompt = self.prompt_template.format(
            context=context,
            question=question
        )
        
        response = self.llm.predict(prompt)

        # Step 4: Calculate confidence based on retrieval scores
        scores = [score for doc, score in retrieved_docs]
        avg_score = sum(scores) / len(scores)
        confidence = max(0.0, min(1.0, 1.0 - avg_score))  # Convert distance to similarity
        
        return {
            "answer": response,
            "sources": [
                {
                    "content": doc.page_content[:200] + "...",
                    "metadata": doc.metadata,
                    "relevance_score": round(1.0 - score, 3)
                }
                for doc, score in retrieved_docs
            ],
            "confidence": round(confidence, 3),
            "num_sources": len(documents)
        }