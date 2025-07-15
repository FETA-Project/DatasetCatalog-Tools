"""
Module contains utility functions for general purpose.
"""
import toml
import re
import constants as c


def substitute_patterns(subst_file_name: str, text: str):
    """
    Substitutes regex patterns in text according to subst. rules config file

    :param subst_file_name:
        Substitution rules config file name
    :type subst_file_name:
        str
    :param text:
        Text on which the substitution will be performed
    :type text:
        str
    :return:
        Text with applied substitutions
    :rtype:
        str
    """
    rule_dict = toml.load(subst_file_name)
    text_copy = (str(text) + '.')[:-1]
    for rule in rule_dict[c.SUBSTITUTION_RULES_OPTION_COLLECTION_NAME]:
        text_copy = re.sub(rule[c.REGEX_OPTION_NAME], rule[c.REPLACE_WITH_OPTION_NAME], text_copy)
    return text_copy

def extract_doi_from_url(url: str):
    """
    Extracts numerical DOI identifier portion from DOI url

    :param url:
        String URL containing DOI
    :type url:
        str
    :return:
        String DOI identifier
    :rtype:
        str
    """
    if "http" not in url:
        return url

    url_split = url.split(c.DOI_DOMAIN)
    return url_split[1]


def merge_analyses(original_analysis: any, generated_analysis: dict, suffix: str):
    """
    Merges two dict-like analyses into one.
    If any key is already present in original analysis, then specified suffix will be added to this key in combined output analysis.

    :param original_analysis:
        Primary, dict-like analysis.
        Field names will stay the same in the merged output analysis.
        Can be a dict or a TOMLDocument.
    :type original_analysis:
        dict or TOMLDocument
    :param generated_analysis:
        Secondary, dict-like analysis.
        Field names can be modified using suffix in case of key collision with original analysis in the merged output analysis.
        Must be a dict.
    :type generated_analysis:
        dict
    :param suffix:
        String suffix, which will be added in case of same key names in inputted analyses.
        Suffix is used to distinguish between fields from primary and secondary analysis.
        In case of key collision, suffix will be added to the field name from secondary analysis.
        Key names from the primary analysis will be preserved.
    :type suffix:
        str
    :return: merged analysis
    :rtype:
        Same as original_analysis
    """
    merged_analysis = original_analysis.copy()
    for key, value in generated_analysis.items():
        if key in original_analysis and value is not None:
            merged_analysis[key + suffix] = value
        else:
            merged_analysis[key] = value
    return merged_analysis