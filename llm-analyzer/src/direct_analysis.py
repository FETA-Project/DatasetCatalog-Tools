"""
Module contains functions for handling main paper analysis.
"""
import toml
from llm_utils import llm_query, extract_answer
from logging_utils import setup_logger
from vector_database import VectorDatabase
import constants as c
import re
logger = setup_logger(__name__, f"{c.LOG_DIRECTORY}{__name__}{c.LOG_FILE_SUFFIX}", level=c.LOG_LEVEL)


def get_section(text: str, keywords: list, chars_before: int, chars_after: int):
    """
    Cuts out a portion of text around first occurrence of keyword.

    :param text:
        Text from which the portion will be extracted
    :type text:
        str
    :param keywords:
        List of regex keywords which will be searched in text
    :type keywords:
        list
    :param chars_before:
        Number of characters which will be extracted before first keyword match
    :type chars_before:
        int
    :param chars_after:
        Number of characters which will be extracted after first keyword match
    :type chars_after:
        int
    :return:
        Extracted substring.
    :rtype:
        str
    """
    index = 0
    for k in keywords:
        res = re.search(k, text)
        if res is not None:
            index = res.start()
            break
    # if keywords were not found, then return beginning
    low_index = max(index - chars_before, 0)
    high_index = min(index + chars_after, len(text))
    return text[low_index:high_index]


def analyze_paper_llm(full_text: str, prompt_file_name: str):
    """
    Performs main article llm analysis based on provided main analysis prompt config file.

    :param full_text:
        Full text of main article
    :type full_text:
        int
    :param prompt_file_name:
        Main analysis prompt config file name
    :type prompt_file_name:
        str
    :return:
        tuple: (analysis_dict, debug_dict)
        analysis_dict: dictionary with LLM responses corresponding to fields
        analysis_dict: dictionary with debug info corresponding to fields
    :type:
        tuple(dict, dict)
    """
    prompt_dict = toml.load(prompt_file_name)
    global_system_prompt = prompt_dict[c.GLOBAL_SYSTEM_PROMPT_OPTION_NAME]
    global_chunk_size = prompt_dict[c.GLOBAL_CHUNK_SIZE_OPTION_NAME]
    global_chunk_overlap = prompt_dict[c.GLOBAL_CHUNK_OVERLAP_OPTION_NAME]
    vector_db = None
    if prompt_dict[c.USE_VECTOR_DATABASE_OPTION_NAME]:
        vector_db = VectorDatabase(full_text, global_chunk_size, global_chunk_overlap)
    analysis_dict = dict()
    debug_dict = dict()
    debug_dict_list = []
    for prompt in prompt_dict[c.PROMPTS_OPTION_COLLECTION_NAME]:
        field_debug_dict = dict()
        # searching relevant context
        if prompt[c.SEARCH_METHOD_OPTION_NAME] == c.SEARCH_METHOD_VECTOR_VALUE:
            chunks_before = prompt[c.CHUNKS_BEFORE_OPTION_NAME]
            chunks_after = prompt[c.CHUNKS_AFTER_OPTION_NAME]
            vector_db_query = prompt[c.VECTOR_DATABASE_SEARCH_QUERY_OPTION_NAME]
            top_k = prompt[c.VECTOR_DATABASE_TOP_K_OPTION_NAME]
            context = vector_db.get_prepared_context(vector_db_query, top_k, chunks_before, chunks_after)
        else:
            chars_before = prompt[c.CHARS_BEFORE_OPTION_NAME]
            chars_after = prompt[c.CHARS_AFTER_OPTION_NAME]
            keywords = [k[c.KEYWORD_OPTION_NAME] for k in prompt[c.KEYWORDS_OPTION_COLLECTION_NAME]]
            context = get_section(full_text, keywords, chars_before, chars_after)

        print("\nfield " + prompt[c.FIELD_NAME_OPTION_NAME] + ":")
        #print("context:\n" + context + "\n\n")
        system_prompt = global_system_prompt
        custom_system_prompt = prompt[c.PER_PROMPT_SYSTEM_PROMPT_OPTION_NAME]
        if custom_system_prompt != "":
            system_prompt = custom_system_prompt
        # query llm
        response = llm_query(context, system_prompt, prompt[c.PROMPT_OPTION_NAME], prompt[c.FIELD_NAME_OPTION_NAME], prompt[c.RESPONSE_TYPE_OPTION_NAME])
        answer = extract_answer(response, prompt[c.FIELD_NAME_OPTION_NAME])
        analysis_dict[prompt[c.FIELD_NAME_OPTION_NAME]] = answer
        # logging
        logger.info("analyzing field " + prompt[c.FIELD_NAME_OPTION_NAME])
        field_debug_dict[c.FIELD_NAME_OPTION_NAME] = prompt[c.FIELD_NAME_OPTION_NAME]
        field_debug_dict[c.PER_PROMPT_SYSTEM_PROMPT_OPTION_NAME] = system_prompt
        field_debug_dict[c.PROMPT_OPTION_NAME] = prompt[c.PROMPT_OPTION_NAME]
        field_debug_dict[c.CONTEXT_FIELD_NAME] = context
        field_debug_dict[c.RESPONSE_TYPE_OPTION_NAME] = prompt[c.RESPONSE_TYPE_OPTION_NAME]
        field_debug_dict[c.RESPONSE_FIELD_NAME] = response
        field_debug_dict[c.ANSWER_FIELD_NAME] = answer
        debug_dict_list.append(field_debug_dict)
    # logging
    debug_dict[c.PER_PAPER_DEBUG_COLLECTION_NAME] = debug_dict_list
    return analysis_dict, debug_dict
