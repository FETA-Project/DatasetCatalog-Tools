"""
Main module.
"""
import builtins
import toml
from direct_analysis import analyze_paper_llm
from reference_analysis import analyze_references
from toml_report_utils import write_report_tomlkit
from toml_report_utils import postprocess_report, read_report_tomlkit
from reference_analysis_aggregation import aggregate_reference_analysis
from pdf_utils import read_pdf
from general_utils import merge_analyses
import logging
import constants as c

logging.basicConfig(filename=c.ROOT_LOG_FILE_NAME, level=c.LOG_LEVEL, format=c.LOG_FORMAT, encoding=c.LOG_ENCODING)


def main():
    """main function"""
    basic_config = toml.load(c.BASIC_CONFIG_FILE_NAME)
    input_analysis = read_report_tomlkit(basic_config[c.INPUT_ANALYSIS_FILE_OPTION_NAME])
    if c.DOI_FIELD_NAME not in input_analysis or c.PAPER_TITLE_FIELD_NAME not in input_analysis or c.DATASET_TITLE_FIELD_NAME not in input_analysis:
        raise RuntimeError(c.ERROR_MESSAGE_REQUIRED_FIELDS_MISSING)
    analysis = input_analysis
    full_text, _ = read_pdf(basic_config[c.INPUT_DIRECT_ANALYSIS_PAPER_FILE_OPTION_NAME])
    llm_direct_analysis, direct_debug_dict = analyze_paper_llm(full_text, c.DIRECT_ANALYSIS_PROMPTS_FILE_NAME)
    llm_reference_analysis, references_debug_dict = analyze_references(basic_config[c.INPUT_REFERENCE_PAPERS_DIRECTORY_OPTION_NAME], input_analysis)
    aggregated_reference_analysis = aggregate_reference_analysis(llm_reference_analysis,
                                                                 c.REFERENCE_ANALYSIS_PROMPTS_FILE_NAME)
    analysis = merge_analyses(analysis, llm_direct_analysis, c.DIRECT_ANALYSIS_FIELD_SUFFIX)
    analysis = merge_analyses(analysis, aggregated_reference_analysis, c.AGGREGATED_REFERENCE_ANALYSIS_SUFFIX)
    #  save analysis to toml
    write_report_tomlkit(analysis, basic_config[c.OUTPUT_MAIN_ANALYSIS_FILE_OPTION_NAME])
    # save per paper reference analysis
    with builtins.open(basic_config[c.OUTPUT_PER_PAPER_ANALYSIS_FILE_OPTION_NAME], 'w', encoding=c.REPORT_ENCODING) as f:
       toml.dump(llm_reference_analysis, f)
    with builtins.open(basic_config[c.OUTPUT_DIRECT_ANALYSIS_DEBUG_FILE_OPTION_NAME], 'w', encoding=c.REPORT_ENCODING) as f:
       toml.dump(direct_debug_dict, f)
    with builtins.open(basic_config[c.OUTPUT_REFERENCE_ANALYSIS_DEBUG_FILE_OPTION_NAME], 'w', encoding=c.REPORT_ENCODING) as f:
       toml.dump(references_debug_dict, f)
    # make strings int toml multiline
    postprocess_report(basic_config[c.OUTPUT_MAIN_ANALYSIS_FILE_OPTION_NAME])
    postprocess_report(basic_config[c.OUTPUT_PER_PAPER_ANALYSIS_FILE_OPTION_NAME])
    postprocess_report(basic_config[c.OUTPUT_DIRECT_ANALYSIS_DEBUG_FILE_OPTION_NAME])
    postprocess_report(basic_config[c.OUTPUT_REFERENCE_ANALYSIS_DEBUG_FILE_OPTION_NAME])


main()

