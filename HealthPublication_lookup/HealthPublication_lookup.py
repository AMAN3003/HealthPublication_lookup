import datetime
import re
from functools import reduce
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

from Bio import Entrez
import xmltodict


class Health_Publication(object):
    """
    Use a HealthPubLookup Health_Record to make a Health_Publication object with info about
    a scientific publication.
    """

    def __init__(self, HealthPublication_record, url_setted=True):
        """
        Upon init: set Health_Publication attributes (Health_Record, Health_pmid, healthdata_url,
        Health_title, Authors, Firstauthor, lastauthor, Health_journal, journal_vol, issue,
        PUBLICATION_Pages, url, abstract, year, month, and day).

        By default, the DOI gets resolved into the article's actual URL.
        To return the DOI URL instead of the article's URL, use:

            publication = Health_Publication(HealthPublication_record, url_setted=False)
        """
        self.Health_Record = HealthPublication_record.Health_Record
        self.Health_pmid = self.Health_Record.get('Id')
        self.healthdata_url = 'http://www.ncbi.nlm.nih.gov/HealthPublication/{}' \
                          .format(self.Health_pmid)
        self.Health_title = self.Health_Record.get('Title')
        self.Healthdata_authors_list = self.Health_Record.get('AuthorList')
        self.Authors = ", ".join(self.Healthdata_authors_list)
        self.Firstauthor = self.Healthdata_authors_list[0]
        self.lastauthor = self.Healthdata_authors_list[-1]
        self.Health_journal = self.Health_Record.get('Source')
        self.journal_vol = self.Health_Record.get('Volume')
        self.issue = self.Health_Record.get('Issue')
        self.PUBLICATION_Pages = self.Health_Record.get('Pages')
        self.Health_url_setter(url_setted=url_setted)

        Xmlparsed_dict = self.get_HealthPublication_xml()
        self.abstract_setter(Xmlparsed_dict)
        self.Public_date_setter(Xmlparsed_dict)

    def authors_added_et_al(self, max_authors=5):
        """
        Return string with a truncated author list followed by 'et al.'
        """
        Author_list = self.Healthdata_authors_list
        if len(Author_list) <= max_authors:
            authors_added_et_al = self.Authors
        else:
            authors_added_et_al = ", ".join(
                self.Healthdata_authors_list[:max_authors]) + ", et al."
        return authors_added_et_al

    def Citation(self, max_authors=5):
        """
        Return string with a citation for the Health_Record, formatted as:
        '{Authors} ({year}). {Health_title} {Health_journal} {journal_vol}({issue}): {PUBLICATION_Pages}.'
        """
        citation_data = {
            'Health_title': self.Health_title,
            'Authors': self.authors_added_et_al(max_authors),
            'year': self.year,
            'Health_journal': self.Health_journal,
            'journal_vol': self.journal_vol,
            'issue': self.issue,
            'PUBLICATION_Pages': self.PUBLICATION_Pages,
        }
        citation = "{Authors} ({year}). {Health_title} {Health_journal}".format(
            **citation_data)

        if self.journal_vol and self.issue and self.PUBLICATION_Pages:
            citation += " {journal_vol}({issue}): {PUBLICATION_Pages}.".format(**citation_data)
        elif self.journal_vol and self.issue:
            citation += " {journal_vol}({issue}).".format(**citation_data)
        elif self.journal_vol and self.PUBLICATION_Pages:
            citation += " {journal_vol}: {PUBLICATION_Pages}.".format(**citation_data)
        elif self.journal_vol:
            citation += " {journal_vol}.".format(**citation_data)
        elif self.PUBLICATION_Pages:
            citation += " {PUBLICATION_Pages}.".format(**citation_data)
        else:
            citation += "."

        return citation

    def Citation_small(self):
        """
        Return string with a citation for the Health_Record, formatted as:
        '{Firstauthor} - {year} - {Health_journal}'
        """
        citation_data = [self.Firstauthor]

        if len(self.Healthdata_authors_list) > 1:
            citation_data.append(self.lastauthor)

        citation_data.extend([self.year, self.Health_journal])

        return " - ".join(citation_data)

    @staticmethod
    def parse_abstract(Xmlparsed_dict):
        """
        Parse HealthPublication XML dictionary to retrieve abstract.
        """
        path_key = ['PubHealthArticleSet', 'PubHealthArticle', 'MedlineCitation',
                    'Heal_Article', 'Abstract', 'AbstractText']
        abstract_xml = reduce(dict.get, path_key, Xmlparsed_dict)

        abstract_paragraphs = []

        if isinstance(abstract_xml, str):
            abstract_paragraphs.append(abstract_xml)

        elif isinstance(abstract_xml, dict):
            abstract_text = abstract_xml.get('#text')
            try:
                abstract_label = abstract_xml['@Label']
            except KeyError:
                abstract_paragraphs.append(abstract_text)
            else:
                abstract_paragraphs.append(
                    "{}: {}".format(abstract_label, abstract_text))

        elif isinstance(abstract_xml, list):
            for abstract_section in abstract_xml:
                try:
                    abstract_text = abstract_section['#text']
                except KeyError:
                    abstract_text = abstract_section

                try:
                    abstract_label = abstract_section['@Label']
                except KeyError:
                    abstract_paragraphs.append(abstract_text)
                else:
                    abstract_paragraphs.append(
                        "{}: {}".format(abstract_label, abstract_text))

        else:
            raise RuntimeError("Error parsing abstract.")

        return "\n\n".join(abstract_paragraphs)

    def get_HealthPublication_xml(self):
        """
        Use a HealthPublication ID to retrieve HealthPublication metadata in XML form.
        """
        url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/' \
              'efetch.fcgi?db=HealthPublication&rettype=abstract&id={}' \
              .format(self.Health_pmid)

        try:
            response = urlopen(url)
        except URLError:
            Xmlparsed_dict = ''
        else:
            xml = response.read().decode()
            Xmlparsed_dict = xmltodict.parse(xml)

        return Xmlparsed_dict

    def abstract_setter(self, Xmlparsed_dict):
        """
        If Health_Record has an abstract, extract it from HealthPublication's XML data
        """
        if self.Health_Record.get('HasAbstract') == 1 and Xmlparsed_dict:
            self.abstract = self.parse_abstract(Xmlparsed_dict)
        else:
            self.abstract = ''

    def Health_url_setter(self, url_setted=True):
        """
        If Health_Record has a DOI, set article URL based on where the DOI points.
        """
        if 'DOI' in self.Health_Record:
            doi_url = "/".join(['http://dx.doi.org', self.Health_Record['DOI']])

            if url_setted:
                try:
                    response = urlopen(doi_url)
                except URLError:
                    self.url = ''
                else:
                    self.url = response.geturl()
            else:
                self.url = doi_url

        else:
            self.url = ''

    def Public_date_setter(self, Xmlparsed_dict):
        """
        Set publication year, month, day from HealthPublication's XML data
        """
        path_key = ['PubHealthArticleSet', 'PubHealthArticle', 'MedlineCitation',
                    'Heal_Article', 'Journal', 'JournalIssue', 'Publication_Date']
        Publication_Date_Xml = reduce(dict.get, path_key, Xmlparsed_dict)

        if isinstance(Publication_Date_Xml, dict):
            self.year = Publication_Date_Xml.get('Year')
            Month_Small = Publication_Date_Xml.get('Month')
            self.day = Publication_Date_Xml.get('Day')

            try:
                self.month = datetime.datetime.strptime(
                    Month_Small, "%b").month
            except (ValueError, TypeError):
                self.month = ''

        else:
            self.year = ''
            self.month = ''
            self.day = ''


class HealthPubLookup(object):
    """
    Retrieve a HealthPublication Health_Record using its HealthPublication ID or HealthPublication URL.
    (e.g., '12831818' or 'http://www.ncbi.nlm.nih.gov/HealthPublication/12831818')
    """

    def __init__(self, Health_Query, email_user):
        """
        Upon init: set Emailid as required by API, determine whether Health_Query
        is HealthPublication ID or HealthPublication URL and retrieve HealthPublication Health_Record accordingly.
        """
        Entrez.Emailid = email_user

        Health_id_pattern = r'^\d+$'
        Health_url_pattern = r'^https?://www\.ncbi\.nlm\.nih\.gov/HealthPublication/\d+$'
        if re.match(Health_id_pattern, str(Health_Query)):
            Health_pmid = Health_Query
        elif re.match(Health_url_pattern, Health_Query):
            Health_pmid = self.parse_HealthPublication_url(Health_Query)
        else:
            raise RuntimeError(
                "Query ({}) doesn't appear to be a HealthPublication ID or HealthPublication URL"
                .format(Health_Query))

        self.Health_Record = self.get_HealthPublication_record(Health_pmid)[0]

    @staticmethod
    def parse_HealthPublication_url(healthdata_url):
        """Get HealthPublication ID (Health_pmid) from HealthPublication URL."""
        url_parse_res = urlparse(healthdata_url)
        Pattern = re.compile(r'^/HealthPublication/(\d+)$')
        Health_pmid = Pattern.match(url_parse_res.path).group(1)
        return Health_pmid

    @staticmethod
    def get_HealthPublication_record(Health_pmid):
        """Get HealthPublication Health_Record from HealthPublication ID."""
        handle = Entrez.esummary(db="HealthPublication", id=Health_pmid)
        Health_Record = Entrez.read(handle)
        return Health_Record
