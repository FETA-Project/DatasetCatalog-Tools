import requests
from bs4 import BeautifulSoup
from html import escape
import re


def get_html(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        return response.text
    except Exception as e:
        print(e)
        return None


def get_author_scholar_url(name: str):
    query = name.replace(" ", "+")
    url = "https://www.google.com/scholar?q=" + query + "&hl=en"
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    author_a = soup.select(".gs_rt2:first-child a")
    author_href = author_a[0].attrs["href"]
    author_href = "https://scholar.google.com" + author_href
    #print(author_href)
    return author_href


class Author:
    def __init__(self):
        self.name = ""
        self.scholar_link = ""
        self.institution = ""
        self.email_info = ""
        self.fields = []
        self.stat_separation_year = 0
        self.citations = (0, 0)
        self.h_index = (0, 0)
        self.i10_index = (0, 0)


def get_author_data(url: str):
    author = Author()
    author.scholar_link = url
    author_page = get_html(url)
    soup = BeautifulSoup(author_page, "html.parser")
    stat_table = soup.select("#gsc_rsb_st")
    headers = []
    rows = []
    for i, row in enumerate(stat_table[0].find_all('tr')):
        if i == 0:
            headers = [el.text.strip() for el in row.find_all('th')]
        else:
            rows.append([el.text.strip() for el in row.find_all('td')])
    #print(headers)
    #print(rows)
    author.stat_separation_year = int(headers[-1].split()[1])
    author.citations = (int(rows[0][1]), int(rows[0][2]))
    author.h_index = (int(rows[1][1]), int(rows[1][2]))
    author.i10_index = (int(rows[2][1]), int(rows[2][2]))
    author.name = soup.select("#gsc_prf_in")[0].text
    author.institution = soup.select(".gsc_prf_il")[0].text
    author.email_info = soup.select("#gsc_prf_ivh")[0].text
    fields_div = soup.select("#gsc_prf_int")[0]
    fields_links = fields_div.find_all("a")
    for a in fields_links:
        author.fields.append(a.text)
    return author


class Article:
    def __init__(self):
        self.doi = ""
        self.title = ""
        self.authors = dict()
        self.n_citations = 0
        self.n_versions = 0
        self.year = 0
        self.publication_info = ""
        self.citations_link = ""


def get_citation_links(citation_link: str, n_citations: int):
    citation_pages_links = []
    n_pages = n_citations // 10 + 1
    for i in range(n_pages):
        start_str = "scholar?start=" + str(i * 10) + "&"
        page_link = citation_link.replace("scholar?", start_str)
        citation_pages_links.append(page_link)

    citation_link_list = []
    citation_download_links = []
    for page_link in citation_pages_links:
        url = "https://scholar.google.com" + page_link
        print(url)
        html = get_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        citation_div = soup.select("#gs_res_ccl_mid")[0]
        title_headlines = citation_div.select(".gs_rt")
        download_divs = citation_div.select(".gs_or_ggsm")
        for h in title_headlines:
            article_link = h.find_all("a")[0]
            citation_link_list.append(article_link["href"])
        for d in download_divs:
            download_link = d.find_all("a")[0]
            citation_download_links.append(download_link["href"])

    return citation_link_list, citation_download_links


def get_article_scholar_data(doi: str):
    article = Article()
    doi = doi.replace("https://doi.org/", "")
    article.doi = doi
    url = "https://www.google.com/scholar?q=" + escape(doi) + "&hl=en"
    print(url)
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    title_div = soup.select(".gs_rt")[0]
    title_link = title_div.find_all("a")
    article.title = title_link[0].text
    author_div = soup.select(".gs_fmaa")
    author_links = author_div[0].find_all("a")
    for a in author_links:
        name = a.get_text()
        link = "https://scholar.google.com" + a["href"]
        article.authors[name] = link
    article_stat_div = soup.select(".gs_flb")
    article_stat_links = article_stat_div[0].find_all("a")
    for a in article_stat_links:
        if a.text.startswith("Cited by"):
            article.n_citations = int(re.findall(r'\d+', a.text)[0])
            article.citations_link = a["href"]
        if a.text.endswith("versions"):
            article.n_versions = re.findall(r'\d+', a.text)[0]

    publication_info = soup.select(".gs_fma_p")[0].text
    article.year = re.findall(r'\d{4}', publication_info)[0]
    article.publication_info = publication_info.replace(author_div[0].text, "")
    return article