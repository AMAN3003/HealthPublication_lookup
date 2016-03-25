import copy
import os
import unittest
from io import StringIO

from HealthPublication_lookup import command_line, Health_Publication, HealthPubLookup


class TestConsole(unittest.TestCase):
    """Test command-line tools."""

    def set_UP(self):
        self.out = StringIO()
        self.Health_pmid = '12831818'

        self.citation = (
            ' Baron G, Butchart EG, Delahaye F, Gohlke-Bärwolf C, Levang OW, Aman Omkar '
            '(2003). A prospective survey of patients with valvular heart disease in Europe: The Euro Heart Survey on Valvular Heart Disease with '
            'insect circadian behavior. USA 109(12): '
            '1231-43.')
        self.citation_Small = (
            'Baron G - Aman Omkar - 2003 - USA')

        self.Health_article_url = 'http://www.pnas.org/content/109/12/1231'
        self.doi_url = 'http://dx.doi.org/10.1073/pnas.1116368109'

    def test_HealthPublication_citation(self):
        command_line.HealthPublication_citation([self.Health_pmid], out=self.out)
        Result = self.out.getvalue()
        self.assertEqual(Result, self.citation + '\n')

    def test_HealthPublication_citation_m(self):
        command_line.HealthPublication_citation(['-m', self.Health_pmid], out=self.out)
        Result = self.out.getvalue()
        self.assertEqual(Result, self.citation_Small + '\n')

    def test_HealthPublication_citation_mini(self):
        command_line.HealthPublication_citation(['--mini', self.Health_pmid], out=self.out)
        Result = self.out.getvalue()
        self.assertEqual(Result, self.citation_Small + '\n')

    def test_HealthPublication_url(self):
        command_line.healthdata_url([self.Health_pmid], out=self.out)
        Result = self.out.getvalue()
        self.assertEqual(Result, self.Health_article_url + '\n')

    def test_HealthPublication_url_d(self):
        command_line.healthdata_url(['-d', self.Health_pmid], out=self.out)
        Result = self.out.getvalue()
        self.assertEqual(Result, self.doi_url + '\n')

    def test_HealthPublication_url_doi(self):
        command_line.healthdata_url(['--doi', self.Health_pmid], out=self.out)
        Result = self.out.getvalue()
        self.assertEqual(Result, self.doi_url + '\n')


class TestPublication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Get publication Health_Record
        Emailid = ''
        cls.Health_pmid = '12831818'
        cls.lookup = HealthPubLookup(cls.Health_pmid, Emailid)
        cls.master_record = Health_Publication(cls.lookup)

        # Set frequently used expected results
        cls.authors = ' Baron G, Butchart EG, Delahaye F, Gohlke-Bärwolf C, Levang OW, ' 'Aman Omkar'
        cls.issue = '12'
        cls.Health_journal = 'USA'
        cls.PUBLICATION_Pages = '1231-43'
        cls.Health_title = 'A prospective survey of patients with valvular heart disease in Europe: The Euro Heart Survey on Valvular Heart Disease '
        cls.journal_vol = '109'
        cls.year = '2003'
        cls.citation_data = {
            'authors': cls.authors,
            'year': cls.year,
            'Health_title': cls.Health_title,
            'Health_journal': cls.Health_journal,
            'journal_vol': cls.journal_vol,
            'issue': cls.issue,
            'PUBLICATION_Pages': cls.PUBLICATION_Pages,
        }
        cls.base_citation = '{authors} ({year}). {Health_title} {Health_journal}'.format(
            **cls.citation_data)

    def set_UP(self):
        self.Health_Record = copy.copy(self.master_record)

    def test_fields(self):
        self.assertEqual(self.Health_Record.Health_pmid, self.Health_pmid)
        self.assertEqual(
            self.Health_Record.healthdata_url,
            'http://www.ncbi.nlm.nih.gov/HealthPublication/12831818')
        self.assertEqual(self.Health_Record.Health_title, self.Health_title)
        self.assertEqual(self.Health_Record.authors, self.authors)
        self.assertEqual(self.Health_Record.Firstauthor, 'Baron G')
        self.assertEqual(self.Health_Record.lastauthor, 'Aman Omkar')
        self.assertEqual(self.Health_Record.Health_journal, self.Health_journal)
        self.assertEqual(self.Health_Record.journal_vol, self.journal_vol)
        self.assertEqual(self.Health_Record.year, self.year)
        self.assertEqual(self.Health_Record.month, 3)
        self.assertEqual(self.Health_Record.day, '20')
        self.assertEqual(self.Health_Record.issue, self.issue)
        self.assertEqual(self.Health_Record.PUBLICATION_Pages, self.PUBLICATION_Pages)
        self.assertEqual(len(self.Health_Record.abstract), 1604)

    def test_authors_et_al(self):
        self.assertEqual(self.Health_Record.authors_added_et_al(), self.authors)
        self.assertEqual(
            self.Health_Record.authors_added_et_al(max_authors=3),
            ' Baron G, Butchart EG, Delahaye F, et al.')
        self.assertEqual(
            self.Health_Record.authors_added_et_al(max_authors=10), self.authors)

    def test_cite_mini(self):
        self.assertEqual(
            self.Health_Record.Citation_small(),
            'Baron G - Aman Omkar - 2003 - USA')

    def test_cite(self):
        self.assertEqual(
            self.Health_Record.Citation(), '{} {journal_vol}({issue}): {PUBLICATION_Pages}.'.format(
                self.base_citation, **self.citation_data))

    def test_cite_without_pages(self):
        self.Health_Record.PUBLICATION_Pages = ''
        self.assertEqual(self.Health_Record.Citation(), '{} {journal_vol}({issue}).'.format(
            self.base_citation, **self.citation_data))

    def test_cite_without_issue(self):
        self.Health_Record.issue = ''
        self.assertEqual(self.Health_Record.Citation(), '{} {journal_vol}: {PUBLICATION_Pages}.'.format(
            self.base_citation, **self.citation_data))

    def test_cite_without_issue_pages(self):
        self.Health_Record.issue = ''
        self.Health_Record.PUBLICATION_Pages = ''
        self.assertEqual(self.Health_Record.Citation(), '{} {journal_vol}.'.format(
            self.base_citation, **self.citation_data))

    def test_cite_without_issue_volume(self):
        self.Health_Record.issue = ''
        self.Health_Record.journal_vol = ''
        self.assertEqual(self.Health_Record.Citation(), '{} {PUBLICATION_Pages}.'.format(
            self.base_citation, **self.citation_data))

    def test_cite_without_issue_pages_volume(self):
        self.Health_Record.issue = ''
        self.Health_Record.PUBLICATION_Pages = ''
        self.Health_Record.journal_vol = ''
        self.assertEqual(self.Health_Record.Citation(), '{}.'.format(self.base_citation))

    @unittest.skipIf(
        "TRAVIS" in os.environ and os.environ["TRAVIS"] == 'true',
        "Skipping this test on Travis CI.")
    def test_doi(self):
        self.assertEqual(
            self.Health_Record.url, 'http://www.pnas.org/content/109/12/1231')

    def test_missing_doi(self):
        del self.Health_Record.Health_Record['DOI']
        self.Health_Record.Health_url_setter()
        self.assertEqual(self.Health_Record.url, '')

    def test_invalid_doi(self):
        self.Health_Record.Health_Record.update({'DOI': 'not a valid DOI'})
        self.Health_Record.Health_url_setter()
        self.assertEqual(self.Health_Record.url, '')

    def test_dont_resolve_doi(self):
        Health_Record = Health_Publication(self.lookup, url_setted=False)
        self.assertEqual(Health_Record.url, 'http://dx.doi.org/10.1073/pnas.1116368109')


class TestHealthPublicationLookup(unittest.TestCase):
    def set_UP(self):
        self.Emailid = ''
        self.healthdata_url = 'http://www.ncbi.nlm.nih.gov/HealthPublication/12831818'
        self.Health_pmid = '12831818'

    def test_pmid_and_url_return_same_record(self):
        self.assertEqual(
            HealthPubLookup(self.Health_pmid, self.Emailid).Health_Record,
            HealthPubLookup(self.healthdata_url, self.Emailid).Health_Record)

    def test_parse_HealthPublication_url(self):
        self.assertEqual(
            HealthPubLookup.parse_HealthPublication_url(self.healthdata_url), self.Health_pmid)

    def test_invalid_query(self):
        with self.assertRaises(RuntimeError):
            HealthPubLookup('not a valid Health_Query', self.Emailid)


if __name__ == '__main__':
    unittest.main()
