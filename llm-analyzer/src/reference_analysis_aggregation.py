"""
Module handles aggregation of analyses from referencing papers.
"""
import toml
from llm_utils import llm_query, extract_answer
from logging_utils import setup_logger
import constants as c


logger = setup_logger(__name__, f"{c.LOG_DIRECTORY}{__name__}{c.LOG_FILE_SUFFIX}", level=c.LOG_LEVEL)


def concatenate_field(analyses_list: list, field_name: str, default_value: str, skip_default: bool, concatenation_format: str):
    """
    Concatenates responses from given field from all referencing papers while adding paper headers to each record.

    :param analyses_list:
        List of referencing paper analyses
    :type analyses_list:
        dict
    :param field_name:
        Name of the field which will be concatenated
    :type field_name:
        str
    :param default_value:
        Default value of the field which is present if analyzed dataset was not referenced
    :type default_value:
        str
    :param skip_default:
        Whether to skip papers with default values
    :type skip_default:
        int
    :param concatenation_format:
        Format of each paper record including header and response placement
    :type concatenation_format:
        str
    :return:
        Aggregated responses as string
    :rtype:
        str
    """
    aggregation = "\n"
    for i, paper_analysis in enumerate(analyses_list):
        if skip_default and paper_analysis[field_name] == default_value:
            continue
        # fill values in format
        record = concatenation_format.replace(c.INDEX_SUBSTITUTION_KEY, str(i))
        record = record.replace(c.PAPER_TITLE_SUBSTITUTION_KEY, paper_analysis[c.PAPER_TITLE_FIELD_NAME])
        record = record.replace(c.RESPONSE_SUBSTITUTION_KEY, paper_analysis[field_name])

        aggregation += record + "\n"
    return aggregation


def value_count_aggregation(analyses_list: list, field_name: str):
    """
    Counts responses from given field from all referencing papers and lists all unique values and their counts.

    :param analyses_list:
        List of referencing paper analyses
    :type analyses_list:
        list
    :param field_name:
        Name of the field which will be aggregated
    :type field_name:
        str
    :return:
        Aggregated response as string
    :rtype:
        str
    """
    value_list = []
    for paper_analysis in analyses_list:
        value = paper_analysis[field_name]
        value_list.append(value)
    # counting values
    count_dict = dict.fromkeys(value_list, 0)
    for value in value_list:
        count_dict[value] += 1
    return str(count_dict)


def aggregate_reference_analysis(per_paper_analysis: dict, reference_prompts_file_name: str):
    """
    Aggregates responses from corresponding fields from all referencing papers.

    :param per_paper_analysis:
        Dictionary with structured analyses of referencing papers
    :type per_paper_analysis:
        dict
    :param reference_prompts_file_name:
        File name of reference analysis prompts config file
    :type reference_prompts_file_name:
        str
    :return:
        Aggregated structured analysis of referencing papers as dictionary
    :rtype:
        dict
    """
    prompt_dict = toml.load(reference_prompts_file_name)
    analyses_list = per_paper_analysis[c.PER_PAPER_REFERENCE_ANALYSIS_COLLECTION_NAME]
    aggregated_analysis = dict()
    # iterating through field config dictionaries
    for prompt in prompt_dict[c.PROMPTS_OPTION_COLLECTION_NAME]:
        field_name = prompt[c.FIELD_NAME_OPTION_NAME]
        aggregation_method = prompt[c.AGGREGATION_METHOD_OPTION_NAME]
        default_value = prompt[c.DEFAULT_VALUE_OPTION_NAME]
        skip_default = bool(prompt[c.SKIP_DEFAULT_OPTION_NAME])
        print(f"\naggregating field {field_name}, aggregation method: {aggregation_method}\n")
        if aggregation_method == c.AGGREGATION_METHOD_NONE:
            continue
        if aggregation_method == c.AGGREGATION_METHOD_CONCATENATE:
            concatenation_format = prompt[c.CONCATENATION_FORMAT_OPTION_NAME]
            concatenation = concatenate_field(analyses_list, field_name, default_value, skip_default, concatenation_format)
            aggregated_analysis[field_name] = concatenation
        if aggregation_method == c.AGGREGATION_METHOD_SUMMARIZE:
            concatenation_format = prompt[c.CONCATENATION_FORMAT_OPTION_NAME]
            concatenation = concatenate_field(analyses_list, field_name, default_value, skip_default, concatenation_format)
            logger.info("summarizing reference analysis")
            summary = llm_query(concatenation, prompt_dict[c.GLOBAL_SYSTEM_PROMPT_OPTION_NAME], prompt_dict[c.GLOBAL_SUMMARIZATION_PROMPT_OPTION_NAME], prompt[c.FIELD_NAME_OPTION_NAME])
            summary = extract_answer(summary, field_name)
            aggregated_analysis[field_name] = summary
        if aggregation_method == c.AGGREGATION_METHOD_VALUE_COUNTS:
            summary = value_count_aggregation(analyses_list, field_name)
            aggregated_analysis[field_name] = summary
    return aggregated_analysis


