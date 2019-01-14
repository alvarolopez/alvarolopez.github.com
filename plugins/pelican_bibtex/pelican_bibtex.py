"""
Pelican BibTeX
==============

A Pelican plugin that populates the context with a list of formatted
citations, loaded from a BibTeX file at a configurable path.

The use case for now is to generate a ``Publications'' page for academic
websites.
"""
# Author: Vlad Niculae <vlad@vene.ro>
# Unlicense (see UNLICENSE for details)

import re

import logging
logger = logging.getLogger(__name__)

from pelican import signals

__version__ = '0.2.1'

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
try:
    from pybtex.database.input.bibtex import Parser
    from pybtex.database.output.bibtex import Writer
    from pybtex.database import BibliographyData, PybtexError
    from pybtex.backends import html
    from pybtex.style.formatting import toplevel
    from pybtex.style.formatting import plain, unsrt
    from pybtex.style.template import (
        field, first_of, href, join, names, optional, optional_field, sentence,
        tag, together, words
    )
except ImportError:
    logger.warn('`pelican_bibtex` failed to load dependency `pybtex`')


class Backend(html.Backend):
    symbols = {
          'ndash': u'&ndash;',
          'newblock': u'<br />\n',
          'nbsp': u'&nbsp;'
    }

date = words [optional_field('month'), field('year')]
pages = field('pages', apply_func=unsrt.dashify)

class Style(plain.Style):
    def get_article_template(self, e):
        volume_and_pages = first_of [
            # volume and pages, with optional issue number
            optional [
                join [
                    field('volume'),
                    optional['(', field('number'),')'],
                    ':', pages
                ],
            ],
            # pages only
            words ['pages', pages],
        ]
        template = toplevel [
            self.format_names('author'),
            self.format_title(e, 'title'),
            sentence [
                tag('em') [field('journal')],
                optional[ volume_and_pages ],
                date,
                self.format_web_refs(e),
            ],
#            sentence [ optional_field('note') ],
        ]
        return template

    def format_web_refs(self, e):
        # based on urlbst output.web.refs
        return sentence [
#            optional [ self.format_url(e) ],
            optional [ self.format_eprint(e) ],
            optional [ self.format_pubmed(e) ],
            optional [ self.format_doi(e) ],
            ]

    def format_url(self, e):
        # based on urlbst format.url
        return words [
            'URL:',
            href [
                field('url', raw=True),
                field('url', raw=True)
                ]
        ]


def add_publications(generator):
    """
    Populates context with a list of BibTeX publications.

    Configuration
    -------------
    generator.settings['PUBLICATIONS_SRC']:
        local path to the BibTeX file to read.

    Output
    ------
    generator.context['publications']:
        List of tuples (key, year, text, bibtex, pdf, slides, poster).
        See Readme.md for more details.
    """
    if 'PUBLICATIONS_SRC' not in generator.settings:
        return

    refs_file = generator.settings['PUBLICATIONS_SRC']
    try:
        bibdata_all = Parser().parse_file(refs_file)
    except PybtexError as e:
        logger.warn('`pelican_bibtex` failed to parse file %s: %s' % (
            refs_file,
            str(e)))
        return

    publications = []

    # format entries
#    plain_style = plain.Style()
#    html_backend = html.Backend()
    plain_style = Style()
    html_backend = Backend()

    def sort_by_year(y, x):
        x = bibdata_all.entries[x.key]
        y = bibdata_all.entries[y.key]
        return int(x.fields['year']) - int(y.fields['year'])

    formatted_entries = plain_style.format_entries(bibdata_all.entries.values())

    bib_sorted = sorted(formatted_entries, cmp=sort_by_year)

    for formatted_entry in bib_sorted:
        key = formatted_entry.key
        entry = bibdata_all.entries[key]
        year = entry.fields.get('year')
        authors = entry.persons.get('author')
        title = entry.fields.get('title')
        journal = entry.fields.get('journal')
        # This shouldn't really stay in the field dict
        # but new versions of pybtex don't support pop
        pdf = entry.fields.get('pdf', None)
        slides = entry.fields.get('slides', None)
        poster = entry.fields.get('poster', None)

        #render the bibtex string for the entry
        bib_buf = StringIO()
        bibdata_this = BibliographyData(entries={key: entry})
        Writer().write_stream(bibdata_this, bib_buf)
        text = formatted_entry.text.render(html_backend)

        publications.append((key,
                             year,
                             authors,
                             title,
                             journal,
                             text,
                             bib_buf.getvalue(),
                             pdf,
                             slides,
                             poster))

    generator.context['publications'] = publications


def register():
    signals.generator_init.connect(add_publications)
