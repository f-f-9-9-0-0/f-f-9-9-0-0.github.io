#!/usr/bin/env python3
"""Build public privacy pages. Python 3.10+, no third-party dependencies."""
import argparse
import datetime as dt
import html
import json
import os
from pathlib import Path
import re
from string import Template
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
FIELDS = ('purpose', 'data', 'basis', 'recipients', 'retention', 'transfers')
PAGES = ('privacy', 'choices')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def obj(value, required, optional=()):
    require(isinstance(value, dict), 'Expected an object')
    require(set(required) <= value.keys(), 'Missing fields: ' + ', '.join(sorted(set(required) - value.keys())))
    require(value.keys() <= set(required) | set(optional), 'Unknown configuration field')


def text(value):
    require(isinstance(value, str) and bool(value.strip()), 'Expected nonempty text')
    require(not any(ord(c) < 32 and c not in '\n\t' for c in value), 'Invalid control character')
    return value


def url(value, local=False):
    text(value)
    require(not re.search(r'[\s\\<>"\x00-\x1f]', value), 'Invalid URL characters')
    parsed = urlsplit(value)
    if local:
        require(value.startswith('/') and not value.startswith('//') and not parsed.scheme and not parsed.netloc,
                'Expected a same-origin absolute path')
    else:
        require(parsed.scheme == 'https' and bool(parsed.hostname) and not parsed.username and not parsed.password,
                'Expected an HTTPS URL without credentials')
    return value


def translated(value, languages):
    obj(value, languages)
    for language in languages:
        text(value[language])


def validate(config, publish, environ):
    obj(config, ('site_name', 'site_url', 'languages', 'reviewed_on', 'publication_reviewed',
                 'authority', 'processing', 'analytics', 'additional_information'), ('design', 'page_urls'))
    text(config['site_name'])
    url(config['site_url'])
    languages = config['languages']
    require(isinstance(languages, list) and languages and all(x in ('en', 'hu') for x in languages)
            and len(set(languages)) == len(languages), 'Languages must be unique en/hu entries')
    date = dt.date.fromisoformat(config['reviewed_on'])
    require(date <= dt.date.today(), 'Review date cannot be in the future')
    require(type(config['publication_reviewed']) is bool, 'publication_reviewed must be boolean')
    obj(config['authority'], ('name', 'url'))
    text(config['authority']['name'])
    url(config['authority']['url'])
    translated(config['additional_information'], languages)
    require(isinstance(config['processing'], list) and config['processing'], 'A processing inventory is required')
    for activity in config['processing']:
        obj(activity, ('name',) + FIELDS)
        for field in ('name',) + FIELDS:
            translated(activity[field], languages)
    analytics = config['analytics']
    obj(analytics, ('mode',), ('controls_url', 'description', 'review_reference'))
    require(analytics['mode'] in ('off', 'consent', 'reviewed_exemption'), 'Unknown analytics mode')
    if analytics['mode'] == 'off':
        require(set(analytics) == {'mode'}, 'Disabled analytics must not declare controls or an exemption')
    else:
        translated(analytics.get('description'), languages)
        text(analytics.get('review_reference'))
        if analytics['mode'] == 'consent':
            url(analytics.get('controls_url'), local=True)
        elif 'controls_url' in analytics:
            url(analytics['controls_url'], local=True)
    design = config.get('design', {})
    obj(design, (), ('stylesheet', 'pages'))
    if 'stylesheet' in design:
        url(design['stylesheet'], local=True)
    if 'pages' in design:
        obj(design['pages'], (), PAGES)
        for page_design in design['pages'].values():
            obj(page_design, ('stylesheet',))
            url(page_design['stylesheet'], local=True)
    if 'page_urls' in config:
        obj(config['page_urls'], languages)
        for routes in config['page_urls'].values():
            obj(routes, PAGES)
            for route in routes.values():
                url(route, local=True)
    if publish:
        require(config['publication_reviewed'], 'Publication requires publication_reviewed: true')
        operator = text(environ.get('SITE_OPERATOR_NAME'))
        email = text(environ.get('PRIVACY_CONTACT_EMAIL'))
        require(re.fullmatch(r'[^\s@<>"&]+@[^\s@<>"&]+\.[^\s@<>"&]+', email) is not None,
                'Invalid privacy contact email')
        require(not email.lower().endswith(('.invalid', '@example.com', '@example.org', '@example.net')),
                'Publication requires a real privacy contact')
        require(not urlsplit(config['site_url']).hostname.endswith(('.invalid', 'example.com', 'example.org', 'example.net')),
                'Publication requires a real website URL')
    else:
        # Never expose caller secrets in draft/PR artifacts.
        operator, email = 'Example Operator (preview)', 'privacy@example.invalid'
    return operator, email


def escape(value):
    return html.escape(str(value), quote=True)


def template(name, **values):
    return Template((ROOT / 'templates' / name).read_text()).substitute(values)


def paragraph(value):
    return '<p>' + escape(value).replace('\n', '<br>') + '</p>'


def link(href, label):
    return '<a href="' + escape(href) + '">' + escape(label) + '</a>'


def build(config, output, *, publish=False, fragment=False, environ=None):
    operator, email = validate(config, publish, os.environ if environ is None else environ)
    labels = json.loads((ROOT / 'templates/labels.json').read_text())
    output = Path(output)
    # Dedicated new output directory prevents stale pages and accidental overwrites.
    require(not output.exists(), 'Output directory must not already exist')
    output.mkdir(parents=True)
    for language in config['languages']:
        out = output / language
        out.mkdir()
        words = labels[language]
        def section(identifier, heading, content):
            return template('section.html', id=identifier, heading=escape(heading), content=content)
        identity = paragraph(words['operator_text'] + ': ' + operator)
        identity += '<p>' + escape(words['contact']) + ': ' + link('mailto:' + email, email) + '</p>'
        identity += '<p>' + escape(words['site']) + ': ' + link(config['site_url'], config['site_name']) + '</p>'
        processing = ''
        for activity in config['processing']:
            processing += '<h3>' + escape(activity['name'][language]) + '</h3><dl>'
            for field in FIELDS:
                processing += '<dt>' + escape(words[field]) + '</dt><dd>' + paragraph(activity[field][language]) + '</dd>'
            processing += '</dl>'
        authority = config['authority']
        privacy = section('wp-operator', words['operator'], identity)
        privacy += section('wp-processing', words['processing'], processing)
        privacy += section('wp-rights', words['rights'], paragraph(words['rights_text']))
        privacy += section('wp-complaints', words['complaints'], paragraph(words['complaints_text']) + link(authority['url'], authority['name']))
        privacy += section('wp-details', words['details'], paragraph(config['additional_information'][language]))
        analytics = config['analytics']
        choices_text = paragraph(words['none'] if analytics['mode'] == 'off' else analytics['description'][language])
        if 'controls_url' in analytics:
            choices_text += link(analytics['controls_url'], words['control_link'])
        choices_text += '<p>' + link(config['site_url'], words['home']) + '</p>'
        choices = section('wp-controls', words['controls'], choices_text)
        for page, sections in (('privacy', privacy), ('choices', choices)):
            other = 'choices' if page == 'privacy' else 'privacy'
            other_href = config.get('page_urls', {}).get(language, {}).get(other, other + '.html')
            content = template('article.html', page=page, language=language,
                draft='' if publish else '<p class="wp-draft" role="note">' + escape(words['draft']) + '</p>',
                title=escape(words[page]), updated_label=escape(words['updated']),
                reviewed_on=escape(config['reviewed_on']), sections=sections,
                other_href=escape(other_href), other_title=escape(words[other]))
            if not fragment:
                design = config.get('design', {})
                stylesheets = [design.get('stylesheet'), design.get('pages', {}).get(page, {}).get('stylesheet')]
                stylesheet = '\n'.join('<link rel="stylesheet" href="' + escape(x) + '">' for x in stylesheets if x)
                content = template('page.html', language=language,
                    robots='' if publish else '<meta name="robots" content="noindex,nofollow">',
                    title=escape(words[page]), site_name=escape(config['site_name']), stylesheet=stylesheet, content=content)
            (out / (page + '.html')).write_text(content, encoding='utf-8')
        (out / 'privacy.css').write_text((ROOT / 'templates/privacy.css').read_text(), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--format', choices=('standalone', 'fragment'), default='standalone')
    args = parser.parse_args()
    try:
        build(json.loads(args.config.read_text()), args.output, publish=args.publish, fragment=args.format == 'fragment')
    except (ValueError, TypeError, KeyError, OSError) as error:
        # Configuration values may be supplied from secrets: don't print the input.
        print('Privacy build failed: ' + type(error).__name__ + '. Check configuration and output path.', file=sys.stderr)
        return 1
    print('Privacy pages generated (' + ('publication' if args.publish else 'draft') + ').')
    return 0


if __name__ == '__main__':
    sys.exit(main())
