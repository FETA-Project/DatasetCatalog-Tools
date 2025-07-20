"""Module contains utility functions for PDF processing."""
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
from pypdf import PdfReader
from general_utils import substitute_patterns
from unstructured.partition.pdf import partition_pdf
import constants as c


def read_pdf(filename: str):
    """
    Reads PDF using unstructured OCR.

    :param filename:
        File name of the PDF.
    :type filename:
        str
    :return:
        tuple(main_text, full_text)
        main_text: Main text excluding reference section
        full_text: Text of the reference section
    :rtype:
        tuple(str, str)
    """
    elements = partition_pdf(filename=filename)
    main_text = ""
    full_text = ""
    pre_reference = True
    # separate main text and references
    for el in elements:
        if (el.text == "References" or el.text == "REFERENCES") and el.category == "Title":
            pre_reference = False
        if pre_reference:
            main_text += el.text + "\n"
        full_text += el.text + "\n"

    main_text = substitute_patterns(c.SUBSTITUTION_RULES_FILE_NAME, main_text)
    full_text = substitute_patterns(c.SUBSTITUTION_RULES_FILE_NAME, full_text)
    return main_text, full_text


def read_pdf_pdfminer(filename: str):
    """
    Reads PDF using pdfminer.

    :param filename:
        File name of the PDF.
    :type filename:
        str
    :return:
        Text of the pdf file.
    :rtype:
        str
    """
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    fp = open(filename, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()
    text = substitute_patterns(c.SUBSTITUTION_RULES_FILE_NAME, text)

    fp.close()
    device.close()
    retstr.close()
    return text


def read_pdf_pypdf(file_name):
    """
    Reads PDF using pypdf.

    :param filename:
        File name of the PDF.
    :type file_name:
        str
    :return:
        Text of the pdf file.
    :rtype:
        str
    """
    article_file = open(file_name, "rb", encoding="utf-8")
    pdf = PdfReader(article_file)
    page_texts = []
    full_text = ""
    for page in pdf.pages:
        page_text = page.extract_text()
        page_text = substitute_patterns(c.SUBSTITUTION_RULES_FILE_NAME, page_text)
        full_text += page_text
        page_texts.append(page_text)
    return full_text, page_texts


