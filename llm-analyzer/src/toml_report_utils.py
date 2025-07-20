"""Module handles reading and writing toml files."""
import toml
import tomlkit

from logging_utils import setup_logger
import re
import constants as c
from tomlkit import parse, TOMLDocument

logger = setup_logger(__name__, f"{c.LOG_DIRECTORY}{__name__}{c.LOG_FILE_SUFFIX}", level=c.LOG_LEVEL)

def read_report_tomlkit(filename: str):
    """
    Reads TOML file using tomlkit library.

    :param filename:
        File name of the TOML file
    :type filename:
        str
    :return:
        Content of the file as TOMLDocument
    :rtype:
        TOMLDocument
    """
    # read file
    file = open(filename, "r", encoding=c.REPORT_ENCODING)
    content = file.read()
    doc = parse(content)
    return doc

def write_report_tomlkit(doc: TOMLDocument, filename: str):
    """
    Writes TOML file using tomlkit library.

    :param doc:
        TOML content which will be saved
    :type doc:
        TOMLDocument
    :param filename:
        File name of the TOML file
    :type filename:
        str
    :return:
        None
    :rtype:
        None
    """
    with open(filename, "w", encoding=c.REPORT_ENCODING) as file:
        tomlkit.dump(doc, file)

def read_report(filename: str):
    """
    Reads TOML file using toml library.

    :param filename:
        File name of the TOML file
    :type filename:
        str
    :return:
        Content of the file as dictionary
    :rtype:
        tuple(dict, dict)
    """
    logger.info("loading example report file (%s)", filename)
    fields = toml.load(filename)

    info_fields = dict()
    data_fields = dict()

    for key, value in fields.items():
        if str(key).endswith(c.INFO_SUFFIX):
            info_fields.update({key: value})
        else:
            data_fields.update({key: value})
    logger.info("example report file (%s) loaded successfully", filename)
    return info_fields, data_fields


def postprocess_report(file_name: str):
    """
    Substitutes starting and ending quotation marks for three quotation marks, making strings multiline.

    :param file_name:
        Name of TOML file
    :type file_name:
        int
    :return:
        None
    :rtype:
        None
    """
    try:
        # Read the file content
        with open(file_name, "r", encoding=c.REPORT_ENCODING) as f:
            content = f.read()

        # Replace \n with \n and " with """
        modified_content = content.replace("\\n", "\n")
        # convert start quote into triple quotes
        modified_content = re.sub(r'=\s*(?<!")"(?!")', '= """', modified_content)
        # convert end quote into triple quotes
        modified_content = re.sub(r'(?<!")"\s*[\n$]', '"""\n', modified_content)

        # Save the modified content back to the file
        with open(file_name, "w", encoding=c.REPORT_ENCODING) as f:
            f.write(modified_content)

        print(f"File '{file_name}' has been successfully modified.")
    except Exception as e:
        print(f"Error processing file: {e}")
