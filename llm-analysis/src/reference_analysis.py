"""
Module handles analysis of referencing papers.
"""
import re
import itertools
import interval_blacklist
from general_utils import extract_doi_from_url
from pdf_utils import read_pdf
import toml
from llm_utils import llm_query, extract_answer
import time
import os
from direct_analysis import analyze_paper_llm
from general_utils import merge_analyses
from logging_utils import setup_logger
import constants as c


logger = setup_logger(__name__, f"{c.LOG_DIRECTORY}{__name__}{c.LOG_FILE_SUFFIX}", level=c.LOG_LEVEL)


def identifier_to_number_set(identifier: str):
    """
    Converts citation identifier to set of all included numbers.
    For example: [8 - 10] -> set{8, 9, 10}
                 [3, 7] -> set{3, 7}
                 [5] -> set{5}.

    :param identifier:
        String representation of identifier (e.g. "[8 - 10]")
    :type identifier:
        str
    :return:
        Set of included citation numbers
    :rtype:
        set
    """
    is_single_number = re.search(r"\[\s*\d+\s*]", identifier) is not None
    is_range = re.search(r"\[\s*\d+\s*[-–—]\s*\d+\s*]", identifier) is not None
    is_list = re.search(r"\[\d+(?:\s*,\s*\d+)*]", identifier) is not None

    if is_single_number:
        number = extract_number_from_reference_identifier(identifier)
        return {number}

    if is_range:
        tmp = re.sub(r"[\[\]]", "", identifier)
        tmp_split = re.split("[-–—]", tmp)
        start_number = int(tmp_split[0])
        end_number = int(tmp_split[1])
        out = set()
        for i in range(start_number, end_number):
            out.add(i)
        return out

    if is_list:
        tmp = re.sub(r"[\[\]]", "", identifier)
        tmp_split = re.split(",", tmp)
        out = set()
        for num in tmp_split:
            out.add(int(num))
        return out
    return None


def get_sections_by_reference_number_or_title(text: str, reference_number: int, chars_before: int, chars_after: int, dataset_title: str):
    """
    Finds all occurrences of reference to main paper or dataset title, extracts contexts around them and concatenates them.

    :param text:
        Text of the referencing paper without references section
    :type text:
        str
    :param reference_number:
        Reference number of main paper
    :type reference_number:
        int
    :param chars_before:
        Number of characters to include in context before individual references
    :type chars_before:
        int
    :param chars_after:
        Number of characters to include in context after individual references
    :type chars_after:
        int
    :param dataset_title:
        Title of the dataset which is being analyzed
    :type dataset_title:
        int
    :return:
        tuple(aggregation, num_occurrences)
        aggregation - Extracted context in which the analyzed dataset is referenced
        num_occurrences - Number of citations in the paper
    :rtype:
        tuple(str, int)
    """
    number_matches = re.finditer(r"\[\d+(?:[-,]\s*\d+)*]", text)
    number_identifier_set = set()
    for nm in number_matches:
        number_identifier_set.add(nm.group())
    title_matches = re.finditer(dataset_title, text)
    matches = itertools.chain(number_matches, title_matches)
    if matches is None:
        matches = []
    aggregation = ""
    num_occurrences = 0
    blacklist = interval_blacklist.IntervalBlacklist()
    for match in matches:
        identifier = match.group()
        # if identifier is a paper number, check if contains our paper
        if match in number_identifier_set:
            ref_number_set = identifier_to_number_set(identifier)
            if reference_number not in ref_number_set:
                continue
        num_occurrences += 1
        index = match.start()
        # checking if index is already in the aggregation to avoid redundancy
        if blacklist.is_blacklisted(index):
            continue
        low_index = max(index - chars_before, 0)
        high_index = min(index + chars_after, len(text))
        blacklist.add_interval(low_index, high_index)
        section = text[low_index:high_index]
        aggregation += section + "\n\n\n"
    return aggregation, num_occurrences


def extract_number_from_reference_identifier(identifier: str):
    """
    Extracts reference number from reference identifier.

    :param identifier:
        String identifier of reference (containing only single reference number e.g. [5])
    :type identifier:
        str
    :return:
        Extracted reference number as int
    :rtype:
        int
    """
    return int(re.search(r"[0-9]+", identifier).group())


def normalize_text(text: str):
    """
    Converts string to lower case and substitutes all white character and new line sequences with single space.

    :param text:
        String to be normalized
    :type text:
        str
    :return:
        Normalized string
    :rtype:
        str
    """
    normalized_text = text.lower()
    normalized_text = re.sub(r'[\s\n]]*', r' ', normalized_text)
    return normalized_text

def find_citation_number(input_analysis: dict, text: str):
    """
    Finds citation number of the main paper in references section of a reference paper.

    :param input_analysis:
        Dictionary containing at least paper title and doi of the main paper
    :type input_analysis:
        dict
    :param text:
        Text of the paper including reference section
    :type text:
        str
    :return:
        Extracted reference number as int
    :rtype:
        int
    """
    reference_index = -1
    text_norm = normalize_text(text)
    doi = extract_doi_from_url(input_analysis[c.DOI_FIELD_NAME])
    keywords = [doi, normalize_text(input_analysis[c.PAPER_TITLE_FIELD_NAME])]
    for k in keywords:
        reference_index = str.lower(text_norm).rfind(k)
        if reference_index != -1:
            break
    if reference_index == -1:
        return -1
    # find indices of all [n] identifiers
    identifiers = re.finditer(r"\[\s*[0-9]*\s*]", text_norm)
    # index of our paper in identifier_indices list
    paper_identifier_index = -1
    paper_identifier = ""
    # find last identifier before doi/title of our paper
    for identifier in identifiers:
        if identifier.start() > reference_index:
            break
        paper_identifier_index = identifier.start()
        paper_identifier = identifier.group()
    # extract paper number from identifier
    if paper_identifier == "":
        return -1
    paper_number = extract_number_from_reference_identifier(paper_identifier)
    return paper_number


def analyze_reference(file_name: str, main_text: str, full_text: str, input_analysis: dict, prompt_file_name: str):
    """
    Extracts information from single referencing paper using LLM.

    :param file_name:
        File name of referencing paper
    :type file_name:
        str
    :param main_text:
        Main text excluding reference section
    :type main_text:
        str
    :param full_text:
        Text including the reference section
    :type full_text:
        str
    :param input_analysis:
        Dictionary containing at least paper title and doi of the main paper
    :type input_analysis:
        dict
    :param prompt_file_name:
        File name of reference prompts config file
    :type prompt_file_name:
        str
    :return:
        tuple: (analysis_dict, debug_dict)
        analysis_dict: dictionary with LLM responses corresponding to fields
        analysis_dict: dictionary with debug info corresponding to fields
    :rtype:
        tuple(dict, dict)
    """
    citation_number = find_citation_number(input_analysis, full_text)
    if citation_number == -1:
        print("Main paper citation number not found")
        print("Only searching dataset name")
        pass
    # get aggregated context for llm
    prompt_dict = toml.load(prompt_file_name)
    global_system_prompt = prompt_dict[c.GLOBAL_SYSTEM_PROMPT_OPTION_NAME]
    global_chars_before = prompt_dict[c.GLOBAL_CHARS_BEFORE_OPTION_NAME]
    global_chars_after = prompt_dict[c.GLOBAL_CHARS_AFTER_OPTION_NAME]
    context, num_references = get_sections_by_reference_number_or_title(main_text, citation_number, global_chars_before, global_chars_after, input_analysis[c.DATASET_TITLE_FIELD_NAME])
    # perform llm analysis
    analysis_dict = dict()
    # logging debug info
    debug_dict = dict()
    debug_dict[c.FILE_NAME_FIELD_NAME] = file_name
    debug_dict[c.NUMBER_OF_CITATIONS_FIELD_NAME] = num_references
    debug_dict_list = []
    # filling out analysis fields
    analysis_dict[c.NUMBER_OF_CITATIONS_FIELD_NAME] = num_references
    analysis_dict[c.FILE_NAME_FIELD_NAME] = file_name
    # paper wasn't referenced in text => using default values
    if num_references <= 0:
        print("\nnot referenced, using default values")
        for prompt in prompt_dict[c.PROMPTS_OPTION_COLLECTION_NAME]:
            analysis_dict[prompt[c.FIELD_NAME_OPTION_NAME]] = prompt[c.DEFAULT_VALUE_OPTION_NAME]
        return analysis_dict, debug_dict
    # paper was referenced in text => llm reference analysis
    for prompt in prompt_dict[c.PROMPTS_OPTION_COLLECTION_NAME]:
        field_debug_dict = dict()
        print("\nfield " + prompt[c.FIELD_NAME_OPTION_NAME] + ":")
        # print("context:\n" + context + "\n\n")
        system_prompt = global_system_prompt
        custom_system_prompt = prompt[c.PER_PROMPT_SYSTEM_PROMPT_OPTION_NAME]
        if custom_system_prompt != "":
            system_prompt = custom_system_prompt
        # number of points suggested in prompt
        num_points = min(max(num_references, 5), 10)
        # substitute special keywords in prompt
        main_prompt = prompt[c.PROMPT_OPTION_NAME]
        main_prompt = main_prompt.replace(c.CITATION_NUMBER_SUBSTITUTION_KEY, str(citation_number))
        main_prompt = main_prompt.replace(c.DATASET_TITLE_SUBSTITUTION_KEY, input_analysis[c.DATASET_TITLE_FIELD_NAME])
        main_prompt = main_prompt.replace(c.DYNAMIC_N_POINTS_SUBSTITUTION_KEY, str(num_points))
        # generate response by sending query to llm
        response = llm_query(context, system_prompt, main_prompt, prompt[c.FIELD_NAME_OPTION_NAME], prompt[c.RESPONSE_TYPE_OPTION_NAME])
        answer = extract_answer(response, prompt[c.FIELD_NAME_OPTION_NAME])
        analysis_dict[prompt[c.FIELD_NAME_OPTION_NAME]] = answer
        # logging
        logger.info(f"analyzing field {prompt[c.FIELD_NAME_OPTION_NAME]}")
        field_debug_dict[c.FIELD_NAME_OPTION_NAME] = prompt[c.FIELD_NAME_OPTION_NAME]
        field_debug_dict[c.DYNAMIC_N_POINTS_SUBSTITUTION_KEY] = num_points
        field_debug_dict[c.PER_PROMPT_SYSTEM_PROMPT_OPTION_NAME] = system_prompt
        field_debug_dict[c.PROMPT_OPTION_NAME] = prompt[c.PROMPT_OPTION_NAME]
        field_debug_dict[c.RESPONSE_TYPE_OPTION_NAME] = prompt[c.RESPONSE_TYPE_OPTION_NAME]
        field_debug_dict[c.RESPONSE_FIELD_NAME] = response
        field_debug_dict[c.ANSWER_FIELD_NAME] = answer
        debug_dict_list.append(field_debug_dict)
    # logging
    debug_dict[c.CONTEXT_FIELD_NAME] = context
    debug_dict[c.DEBUG_FIELDS_COLLECTION_NAME] = debug_dict_list
    return analysis_dict, debug_dict


def analyze_references(directory_name: str, input_analysis: dict):
    """
    Extracts information from all referencing papers using LLM.

    :param directory_name:
        Name of the directory where referencing papers are located
    :type directory_name:
        str
    :param input_analysis:
        Dictionary containing at least paper title and doi of the main paper
    :type input_analysis:
        dict
    :return:
        tuple: (output_analysis, debug_dict)
        output_analysis: dictionary with per paper analysis containing LLM responses corresponding to fields
        analysis_dict: dictionary with debug info corresponding to papers and fields
    :rtype:
        tuple(dict, dict)
    """
    start = time.time()
    files = []
    for file in os.listdir(directory_name):
        filename = os.fsdecode(file)
        if filename.endswith(".pdf"):
            files.append(os.path.join(directory_name, filename))

    analyses_list = []
    n_files = len(files)
    i = 0
    debug_dict_list = []
    debug_dict = dict()
    for file_name in files:
        i += 1
        print("\n\n**********************************")
        print(f"analyzing reference {i}/{n_files}, file name: {file_name}")
        pdf_text_main, pdf_text_full = read_pdf(file_name)
        basic_info, basic_info_debug_dict = analyze_paper_llm(pdf_text_main, c.BASIC_INFO_PROMPTS_FILE_NAME)
        citation_analysis, paper_debug_dict = analyze_reference(file_name, pdf_text_main, pdf_text_full, input_analysis, c.REFERENCE_ANALYSIS_PROMPTS_FILE_NAME)
        paper_analysis = merge_analyses(basic_info, citation_analysis, c.DIRECT_ANALYSIS_FIELD_SUFFIX)
        analyses_list.append(paper_analysis)
        # logging
        paper_debug_dict[c.PAPER_TITLE_FIELD_NAME] = basic_info[c.PAPER_TITLE_FIELD_NAME]
        paper_debug_dict[c.BASIC_INFO_DEBUG_FIELD_NAME] = basic_info_debug_dict
        debug_dict_list.append(paper_debug_dict)
    # aggregation of analyses
    output_analysis = {"per_paper_reference_analysis" : analyses_list}
    debug_dict[c.PER_PAPER_DEBUG_COLLECTION_NAME] = debug_dict_list
    end = time.time()
    elapsed = end - start
    print(f"\nAnalysis of all references performed in {elapsed//60} min, {elapsed%60:.2f} s.\n")
    return output_analysis, debug_dict