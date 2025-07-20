import toml
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
import constants as c

def add_prefixes_to_chunks(chunks: list, prefix: str):
    prefixed_chunks = []
    for chunk in chunks:
        prefixed_chunk = prefix + " " + chunk
        prefixed_chunks.append(prefixed_chunk)
    return prefixed_chunks


class VectorDatabase:
    def __init__(self, full_text: str, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initializes vector database with given text.

        :param full_text:
            Full text to be stored in database
        :type full_text:
            str
        :param chunk_size:
            Size of a chunk in characters
        :type chunk_size:
            int
        :param chunk_overlap:
            Overlap between chunks in characters
        :type chunk_overlap:
            int
        :return:
            None
        :rtype:
            None
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.full_text = full_text
        print("initializing vector database...\n")
        # Rozdelenie textu na chunky
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        raw_chunks = text_splitter.split_text(full_text)
        config = toml.load(c.LLM_CONFIG_FILE_NAME)
        # adding prefixes to chunks
        self.document_prefix = config[c.EMBEDDING_DOCUMENT_PREFIX_OPTION_NAME]
        self.query_prefix = config[c.EMBEDDING_QUERY_PREFIX_OPTION_NAME]
        self.chunks = add_prefixes_to_chunks(raw_chunks, self.document_prefix)
        # Vytvorenie vektorovej databázy
        self.embeddings = OllamaEmbeddings(
            model = config[c.EMBEDDING_MODEL_OPTION_NAME]
        )
        self.embeddings.base_url = config[c.EMBEDDING_BASE_URL_OPTION_NAME]
        self.vector_db = FAISS.from_texts(self.chunks, self.embeddings)

    def get_relevant_chunks(self, query: str, top_k: int = 5):
        """
        Finds the most relevant chunks according to search query.

        :param query:
            Query for target text
        :type query:
            str
        :param top_k:
            Number of the best results to return
        :type top_k:
            int
        :return:
            List of *k* most relevant chunks
        :rtype:
            list
        """
        query = self.query_prefix + " " + query
        results = self.vector_db.similarity_search(query, k=top_k)
        return [res.page_content for res in results]

    def get_expanded_chunks(self, query: str, top_k: int = 5, chunks_before: int = 1, chunks_after: int = 1):
        """
        Finds the most relevant chunks according to search query and expands them with more chunks before and after.

        :param query:
            Query for target text
        :type query:
            str
        :param top_k:
            Number of the best results to return
        :type top_k:
            int
        :param chunks_before:
            Number of chunks to add before to the found chunks
        :type chunks_before:
            int
        :param chunks_after:
            Number of chunks to add after to the found chunks
        :type chunks_after:
            int
        :return:
            List of *k* most relevant chunks (expanded)
        :rtype:
            list
        """
        query = self.query_prefix + " " + query
        results = self.vector_db.similarity_search(query, k=top_k)
        indices = [self.chunks.index(res.page_content) for res in results]
        expanded_chunks = []

        for index in indices:
            start = max(0, index - chunks_before)
            end = min(len(self.chunks), index + chunks_after + 1)
            expanded_chunks.extend(self.chunks[start:end])

        return list(set(expanded_chunks))

    def get_prepared_context(self, query: str, top_k: int, chunks_before: int, chunks_after: int):
        """
        Finds the most relevant chunks according to search query and expands them with more chunks before and after and concatenates them into single context.

        :param query:
            Query for target text
        :type query:
            str
        :param top_k:
            Number of the best results to return
        :type top_k:
            int
        :param chunks_before:
            Number of chunks to add before to the found chunks
        :type chunks_before:
            int
        :param chunks_after:
            Number of chunks to add after to the found chunks
        :type chunks_after:
            int
        :return:
            String of most relevant chunks (expanded and concatenated)
        :rtype:
            str
        """
        chunks = self.get_expanded_chunks(query, top_k, chunks_before, chunks_after)
        context = ""
        for chunk in chunks:
            context += chunk + "\n\n"
        return context


#vector_db = VectorDatabase("../resources/quic_paper.pdf", 2000, 0)
#relevant_chunks = vector_db.get_relevant_chunks("TLS capture from CESNET2 backbone network over one year. The capture was done using high-speed monitoring probes at the perimeter of CESNET2 network. This dataset provides realistic characteristics of traffic originating from various web browsers, operating systems, mobile devices, desktop machines, and both HTTP/1.1 and HTTP/2 protocols."
#                                                , 5)
#for ch in relevant_chunks:
#    print(ch)
#    print()