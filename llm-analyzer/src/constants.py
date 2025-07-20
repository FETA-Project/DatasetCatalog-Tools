"""Module where constants are initialized."""
######################
# logging parameters #
######################
ROOT_LOG_FILE_NAME = "../logs/root_info.log"
LOG_LEVEL = "INFO"
LOG_FORMAT = "[%(asctime)s:%(levelname)9s:%(filename)20s:%(lineno)s - %(funcName)20s()] %(message)s"
LOG_ENCODING = "utf-8"
LOG_DIRECTORY = "../logs/"
LOG_FILE_SUFFIX = ".log"
##############
# file names #
##############
TEMPLATE_REPORT_FILE_NAME = "../resources/analysis_example_ref.toml"
INPUT_REPORT_FILE_NAME = "../in/quic_input.toml"
DIRECT_ANALYSIS_PAPER_FILE_NAME = "../resources/quic_paper.pdf"
DIRECT_ANALYSIS_PROMPTS_FILE_NAME = "../config/direct_analysis_prompts.toml"
REFERENCE_ANALYSIS_DIRECTORY = "../resources/all_references"
REFERENCE_ANALYSIS_PROMPTS_FILE_NAME = "../config/reference_analysis_prompts.toml"
MAIN_ANALYSIS_OUTPUT_FILE_NAME = "../out/main_analysis6_quic.toml"
PER_PAPER_REFERENCE_ANALYSIS_OUTPUT_FILE_NAME = "../out/per_paper_reference_analysis6_quic.toml"
LLM_CONFIG_FILE_NAME = "../config/llm_config.toml"
SUBSTITUTION_RULES_FILE_NAME = "../config/substitution_rules.toml"
BASIC_INFO_PROMPTS_FILE_NAME = "../config/reference_basic_info_prompts.toml"
BASIC_CONFIG_FILE_NAME = "../config/basic_config.toml"
###############################
# direct analysis field names #
###############################
DOI_FIELD_NAME = "doi"
PAPER_TITLE_FIELD_NAME = "paper_title"
DATASET_TITLE_FIELD_NAME = "dataset_title"
# direct analysis prompts config field names
GLOBAL_SYSTEM_PROMPT_OPTION_NAME = "global_system_prompt"
GLOBAL_CHUNK_SIZE_OPTION_NAME = "global_vector_db_chunk_size"
GLOBAL_CHUNK_OVERLAP_OPTION_NAME = "global_vector_db_chunk_overlap"
USE_VECTOR_DATABASE_OPTION_NAME = "use_vector_database"
PROMPTS_OPTION_COLLECTION_NAME = "prompts"
RESPONSE_TYPE_OPTION_NAME = "response_type"
# per prompt options in direct analysis
FIELD_NAME_OPTION_NAME = "field_name"
PER_PROMPT_SYSTEM_PROMPT_OPTION_NAME = "system_prompt"
PROMPT_OPTION_NAME = "prompt"
# vector database options
SEARCH_METHOD_OPTION_NAME = "search_method"
SEARCH_METHOD_VECTOR_VALUE = "vector"
CHUNKS_BEFORE_OPTION_NAME = "chunks_before"
CHUNKS_AFTER_OPTION_NAME = "chunks_after"
VECTOR_DATABASE_SEARCH_QUERY_OPTION_NAME = "vector_db_search_query"
VECTOR_DATABASE_TOP_K_OPTION_NAME = "vector_db_top_k"
# regex search options
CHARS_BEFORE_OPTION_NAME = "chars_before"
CHARS_AFTER_OPTION_NAME = "chars_after"
KEYWORD_OPTION_NAME = "keyword"
KEYWORDS_OPTION_COLLECTION_NAME = "keywords"
############################################
# per paper reference analysis field names #
############################################
PER_PAPER_REFERENCE_ANALYSIS_COLLECTION_NAME = "per_paper_reference_analysis"
# config options
GLOBAL_CHARS_BEFORE_OPTION_NAME = "global_chars_before"
GLOBAL_CHARS_AFTER_OPTION_NAME = "global_chars_after"
GLOBAL_SUMMARIZATION_PROMPT_OPTION_NAME = "global_summarization_prompt"
# field names
NUMBER_OF_CITATIONS_FIELD_NAME = "number_of_citations"
FILE_NAME_FIELD_NAME = "file_name"
AGGREGATION_METHOD_OPTION_NAME = "aggregation_method"
SKIP_DEFAULT_OPTION_NAME = "aggregation_skip_default"
CONCATENATION_FORMAT_OPTION_NAME = "concatenation_format"
# per prompt options
DEFAULT_VALUE_OPTION_NAME = "default_value"
# substitution keys
CITATION_NUMBER_SUBSTITUTION_KEY = "__citation_number__"
DATASET_TITLE_SUBSTITUTION_KEY = "__dataset_title__"
DYNAMIC_N_POINTS_SUBSTITUTION_KEY = "__dynamic_n_points__"
#############################################
# aggregated reference analysis field names #
#############################################
AGGREGATION_METHOD_NONE = "none"
AGGREGATION_METHOD_CONCATENATE = "concatenate"
AGGREGATION_METHOD_SUMMARIZE = "summarize"
AGGREGATION_METHOD_VALUE_COUNTS = "value_counts"
# substitution keys
INDEX_SUBSTITUTION_KEY = "__index__"
PAPER_TITLE_SUBSTITUTION_KEY = "__paper_title__"
RESPONSE_SUBSTITUTION_KEY = "__response__"
#####################################
# substitution rules config options #
#####################################
SUBSTITUTION_RULES_OPTION_COLLECTION_NAME ="substitution_rules"
REGEX_OPTION_NAME = "regex"
REPLACE_WITH_OPTION_NAME = "replace_with"
########################
# basic config options #
########################
INPUT_ANALYSIS_FILE_OPTION_NAME = "input_analysis_file"
INPUT_DIRECT_ANALYSIS_PAPER_FILE_OPTION_NAME = "input_direct_analysis_paper_file"
INPUT_REFERENCE_PAPERS_DIRECTORY_OPTION_NAME = "input_reference_papers_directory"
OUTPUT_MAIN_ANALYSIS_FILE_OPTION_NAME = "output_main_analysis_file"
OUTPUT_PER_PAPER_ANALYSIS_FILE_OPTION_NAME = "output_per_paper_reference_analysis_file"
######################
# llm config options #
######################
URL_OPTION_NAME = "url"
MODEL_NAME_OPTION_NAME = "model_name"
MODEL_OPTIONS_OPTION_NAME = "model_options"
LLM_REQUEST_TIMEOUT_OPTION_NAME = "timeout"
LLM_REQUEST_MAX_RETRIES = "max_retries"
THINK_SECTION_DELIMITER_OPTION_NAME = "think_section_delimiter"
EMBEDDING_MODEL_OPTION_NAME = "embedding_model_name"
EMBEDDING_BASE_URL_OPTION_NAME = "embedding_base_url"
EMBEDDING_DOCUMENT_PREFIX_OPTION_NAME = "embedding_document_prefix"
EMBEDDING_QUERY_PREFIX_OPTION_NAME = "embedding_query_prefix"
##################
# error messages #
##################
ERROR_MESSAGE_REQUIRED_FIELDS_MISSING = "input analysis must contain at least doi, paper_title and dataset_title"
############
# suffixes #
############
# suffix is added if there already is filled field with the same name
DIRECT_ANALYSIS_FIELD_SUFFIX = "_llm"
AGGREGATED_REFERENCE_ANALYSIS_SUFFIX = "_aggregated_reference_analysis"
###################
# other constants #
###################
DOI_DOMAIN = "doi.org/"
INFO_SUFFIX = "_info"
REPORT_ENCODING = "utf-8"
################
# debug fields #
################
CONTEXT_FIELD_NAME = "context"
RESPONSE_FIELD_NAME = "response"
ANSWER_FIELD_NAME = "answer"
DEBUG_FIELDS_COLLECTION_NAME = "fields"
PER_PAPER_DEBUG_COLLECTION_NAME = "per_paper_debug_collection"
BASIC_INFO_DEBUG_FIELD_NAME = "basic_info_debug_data"
####################
# debug file names #
####################
OUTPUT_DIRECT_ANALYSIS_DEBUG_FILE_OPTION_NAME = "output_direct_analysis_debug_file"
OUTPUT_REFERENCE_ANALYSIS_DEBUG_FILE_OPTION_NAME = "output_reference_analysis_debug_file"
