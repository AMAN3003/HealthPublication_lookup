import argparse
import sys

from HealthPublication_lookup import HealthPubLookup, Health_Publication


def HealthPublication_citation(args=sys.argv[1:], out=sys.stdout):
    """citation using command line as HealthPublication ID or HealthPublication URL"""

    parser = argparse.ArgumentParser(
        description='Get a citation using a HealthPublication ID or HealthPublication URL')
    parser.add_argument('Health_Query', help='HealthPublication ID or HealthPublication URL')
    parser.add_argument(
        '-m', '--mini', action='store_true', help='get mini citation')
    parser.add_argument(
        '-e', '--Emailid', action='store', help='set user Emailid', default='')

    args = parser.parse_args(args=args)

    lookup = HealthPubLookup(args.Health_Query, args.Emailid)
    publication = Health_Publication(lookup, resolve_doi=False)

    if args.mini:
        out.write(publication.cite_mini() + '\n')
    else:
        out.write(publication.cite() + '\n')


def HealthPublication_url(args=sys.argv[1:], resolve_doi=True, out=sys.stdout):
    """
    Get a publication URL via the command line using a HealthPublication ID or HealthPublication URL
    """

    parser = argparse.ArgumentParser(
        description='Get a publication URL using a HealthPublication ID or HealthPublication URL')
    parser.add_argument('Health_Query', help='HealthPublication ID or HealthPublication URL')
    parser.add_argument(
        '-d', '--doi', action='store_false', help='get DOI URL')
    parser.add_argument(
        '-e', '--Emailid', action='store', help='set user Emailid', default='')

    args = parser.parse_args(args=args)

    lookup = HealthPubLookup(args.Health_Query, args.Emailid)
    publication = Health_Publication(lookup, resolve_doi=args.doi)

    out.write(publication.url + '\n')
