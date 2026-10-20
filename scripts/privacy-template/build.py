#!/usr/bin/env python3
"""Build public privacy pages. Python 3.10+, no third-party dependencies."""

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import unicodedata
from collections.abc import Mapping, Sequence
from pathlib import Path
from string import Template
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
FIELDS = ("purpose", "data", "basis", "recipients", "retention", "transfers")
PAGES = ("privacy", "choices")
PLACEHOLDER_DOMAINS = ("invalid", "example.com", "example.org", "example.net")


class ConfigError(ValueError):
    """A failed check. Messages are fixed text and field names, never input values."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise ConfigError(message)


def require_object(
    value: Any, required: Sequence[str], optional: Sequence[str] = ()
) -> None:
    require(isinstance(value, dict), "Expected an object")
    require(
        set(required) <= value.keys(),
        "Missing fields: " + ", ".join(sorted(set(required) - value.keys())),
    )
    require(
        value.keys() <= set(required) | set(optional), "Unknown configuration field"
    )


def require_text(value: Any) -> str:
    require(isinstance(value, str) and bool(value.strip()), "Expected nonempty text")
    require(
        not any(
            unicodedata.category(c) in ("Cc", "Cs") and c not in "\n\t" for c in value
        ),
        "Invalid control or surrogate character",
    )
    return value


def require_url(value: Any, local: bool = False) -> str:
    require_text(value)
    require(not re.search(r'[\s\\<>"\x00-\x1f]', value), "Invalid URL characters")
    parsed = urlsplit(value)
    if local:
        require(
            value.startswith("/")
            and not value.startswith("//")
            and not parsed.scheme
            and not parsed.netloc,
            "Expected a same-origin absolute path",
        )
    else:
        require(
            parsed.scheme == "https"
            and bool(parsed.hostname)
            and not parsed.username
            and not parsed.password,
            "Expected an HTTPS URL without credentials",
        )
    return value


def require_translations(value: Any, languages: Sequence[str]) -> None:
    require_object(value, languages)
    for language in languages:
        require_text(value[language])


def validate(
    config: dict[str, Any], publish: bool, environ: Mapping[str, str]
) -> tuple[str, str]:
    require_object(
        config,
        (
            "site_name",
            "site_url",
            "languages",
            "reviewed_on",
            "publication_reviewed",
            "authority",
            "processing",
            "analytics",
            "additional_information",
        ),
        ("design", "page_urls"),
    )
    require_text(config["site_name"])
    require_url(config["site_url"])
    languages = config["languages"]
    require(
        isinstance(languages, list)
        and languages
        and all(language in ("en", "hu") for language in languages)
        and len(set(languages)) == len(languages),
        "Languages must be unique en/hu entries",
    )
    reviewed_on = require_text(config["reviewed_on"])
    require(
        re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", reviewed_on) is not None,
        "reviewed_on must be a YYYY-MM-DD date",
    )
    date = dt.date.fromisoformat(reviewed_on)
    require(date <= dt.date.today(), "Review date cannot be in the future")
    require(
        isinstance(config["publication_reviewed"], bool),
        "publication_reviewed must be boolean",
    )
    require_object(config["authority"], ("name", "url"))
    require_text(config["authority"]["name"])
    require_url(config["authority"]["url"])
    require_translations(config["additional_information"], languages)
    require(
        isinstance(config["processing"], list) and config["processing"],
        "A processing inventory is required",
    )
    for activity in config["processing"]:
        require_object(activity, ("name",) + FIELDS)
        for field in ("name",) + FIELDS:
            require_translations(activity[field], languages)
    validate_analytics(config["analytics"], languages)
    validate_design(config.get("design", {}))
    if "page_urls" in config:
        validate_page_urls(config["page_urls"], languages)
    if publish:
        return publication_identity(config, environ)
    # Never expose caller secrets in draft/PR artifacts.
    return "Example Operator (preview)", "privacy@example.invalid"


def validate_analytics(analytics: Any, languages: Sequence[str]) -> None:
    require_object(
        analytics, ("mode",), ("controls_url", "description", "review_reference")
    )
    require(
        analytics["mode"] in ("off", "consent", "reviewed_exemption"),
        "Unknown analytics mode",
    )
    if analytics["mode"] == "off":
        require(
            set(analytics) == {"mode"},
            "Disabled analytics must not declare controls or an exemption",
        )
    else:
        require_translations(analytics.get("description"), languages)
        require_text(analytics.get("review_reference"))
        if analytics["mode"] == "consent":
            require_url(analytics.get("controls_url"), local=True)
        elif "controls_url" in analytics:
            require_url(analytics["controls_url"], local=True)


def validate_design(design: Any) -> None:
    require_object(design, (), ("stylesheet", "pages"))
    if "stylesheet" in design:
        require_url(design["stylesheet"], local=True)
    if "pages" in design:
        require_object(design["pages"], (), PAGES)
        for page_design in design["pages"].values():
            require_object(page_design, ("stylesheet",))
            require_url(page_design["stylesheet"], local=True)


def validate_page_urls(page_urls: Any, languages: Sequence[str]) -> None:
    require_object(page_urls, languages)
    for routes in page_urls.values():
        require_object(routes, PAGES)
        for route in routes.values():
            require_url(route, local=True)


def publication_identity(
    config: dict[str, Any], environ: Mapping[str, str]
) -> tuple[str, str]:
    require(
        config["publication_reviewed"],
        "Publication requires publication_reviewed: true",
    )
    operator = require_text(environ.get("SITE_OPERATOR_NAME"))
    email = require_text(environ.get("PRIVACY_CONTACT_EMAIL"))
    require(
        re.fullmatch(r'[^\s@<>"&]+@[^\s@<>"&]+\.[^\s@<>"&]+', email) is not None,
        "Invalid privacy contact email",
    )
    require(
        not is_placeholder_domain(email.rpartition("@")[2]),
        "Publication requires a real privacy contact",
    )
    require(
        not is_placeholder_domain(urlsplit(config["site_url"]).hostname),
        "Publication requires a real website URL",
    )
    return operator, email


def is_placeholder_domain(domain: str) -> bool:
    domain = domain.lower().rstrip(".")
    return any(
        domain == placeholder or domain.endswith("." + placeholder)
        for placeholder in PLACEHOLDER_DOMAINS
    )


def escape(value: object) -> str:
    # Braces too: Jekyll renders included fragments through Liquid.
    return (
        html.escape(str(value), quote=True)
        .replace("{", "&#123;")
        .replace("}", "&#125;")
    )


def template(name: str, **values: str) -> str:
    source = (ROOT / "templates" / name).read_text(encoding="utf-8")
    return Template(source).substitute(values)


def paragraph(value: str) -> str:
    return "<p>" + escape(value).replace("\n", "<br>") + "</p>"


def link(href: str, label: str) -> str:
    return '<a href="' + escape(href) + '">' + escape(label) + "</a>"


def section(identifier: str, heading: str, content: str) -> str:
    return template(
        "section.html", id=identifier, heading=escape(heading), content=content
    )


def render_privacy(
    config: dict[str, Any],
    words: dict[str, str],
    language: str,
    operator: str,
    email: str,
) -> str:
    identity = paragraph(words["operator_text"] + ": " + operator)
    identity += (
        "<p>"
        + escape(words["contact"])
        + ": "
        + link("mailto:" + email, email)
        + "</p>"
    )
    identity += (
        "<p>"
        + escape(words["site"])
        + ": "
        + link(config["site_url"], config["site_name"])
        + "</p>"
    )
    processing = ""
    for activity in config["processing"]:
        processing += "<h3>" + escape(activity["name"][language]) + "</h3><dl>"
        for field in FIELDS:
            processing += (
                "<dt>"
                + escape(words[field])
                + "</dt><dd>"
                + paragraph(activity[field][language])
                + "</dd>"
            )
        processing += "</dl>"
    authority = config["authority"]
    privacy = section("wp-operator", words["operator"], identity)
    privacy += section("wp-processing", words["processing"], processing)
    privacy += section("wp-rights", words["rights"], paragraph(words["rights_text"]))
    privacy += section(
        "wp-complaints",
        words["complaints"],
        paragraph(words["complaints_text"]) + link(authority["url"], authority["name"]),
    )
    privacy += section(
        "wp-details",
        words["details"],
        paragraph(config["additional_information"][language]),
    )
    return privacy


def render_choices(config: dict[str, Any], words: dict[str, str], language: str) -> str:
    analytics = config["analytics"]
    choices_text = paragraph(
        words["none"]
        if analytics["mode"] == "off"
        else analytics["description"][language]
    )
    if "controls_url" in analytics:
        choices_text += link(analytics["controls_url"], words["control_link"])
    choices_text += "<p>" + link(config["site_url"], words["home"]) + "</p>"
    return section("wp-controls", words["controls"], choices_text)


def render_article(
    config: dict[str, Any],
    words: dict[str, str],
    language: str,
    page: str,
    sections: str,
    publish: bool,
) -> str:
    other = "choices" if page == "privacy" else "privacy"
    other_href = (
        config.get("page_urls", {}).get(language, {}).get(other, other + ".html")
    )
    return template(
        "article.html",
        page=page,
        language=language,
        draft=(
            ""
            if publish
            else '<p class="wp-draft" role="note">' + escape(words["draft"]) + "</p>"
        ),
        title=escape(words[page]),
        updated_label=escape(words["updated"]),
        reviewed_on=escape(config["reviewed_on"]),
        sections=sections,
        other_href=escape(other_href),
        other_title=escape(words[other]),
    )


def wrap_page(
    config: dict[str, Any],
    words: dict[str, str],
    language: str,
    page: str,
    content: str,
    publish: bool,
) -> str:
    design = config.get("design", {})
    stylesheets = [
        design.get("stylesheet"),
        design.get("pages", {}).get(page, {}).get("stylesheet"),
    ]
    stylesheet = "\n".join(
        '<link rel="stylesheet" href="' + escape(href) + '">'
        for href in stylesheets
        if href
    )
    return template(
        "page.html",
        language=language,
        robots="" if publish else '<meta name="robots" content="noindex,nofollow">',
        title=escape(words[page]),
        site_name=escape(config["site_name"]),
        stylesheet=stylesheet,
        content=content,
    )


def build(
    config: dict[str, Any],
    output: str | Path,
    *,
    publish: bool = False,
    fragment: bool = False,
    environ: Mapping[str, str] | None = None,
) -> None:
    operator, email = validate(
        config, publish, os.environ if environ is None else environ
    )
    labels = json.loads((ROOT / "templates/labels.json").read_text(encoding="utf-8"))
    output = Path(output)
    # Dedicated new output directory prevents stale pages and accidental overwrites.
    require(not output.exists(), "Output directory must not already exist")
    output.mkdir(parents=True)
    for language in config["languages"]:
        language_dir = output / language
        language_dir.mkdir()
        words = labels[language]
        privacy = render_privacy(config, words, language, operator, email)
        choices = render_choices(config, words, language)
        for page, sections in (("privacy", privacy), ("choices", choices)):
            content = render_article(config, words, language, page, sections, publish)
            if not fragment:
                content = wrap_page(config, words, language, page, content, publish)
            (language_dir / (page + ".html")).write_text(content, encoding="utf-8")
        (language_dir / "privacy.css").write_text(
            (ROOT / "templates/privacy.css").read_text(encoding="utf-8"),
            encoding="utf-8",
        )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument(
        "--format", choices=("standalone", "fragment"), default="standalone"
    )
    args = parser.parse_args(argv)
    try:
        build(
            json.loads(args.config.read_text(encoding="utf-8")),
            args.output,
            publish=args.publish,
            fragment=args.format == "fragment",
        )
    except ConfigError as error:
        print("Privacy build failed: " + str(error) + ".", file=sys.stderr)
        return 1
    except (ValueError, TypeError, KeyError, OSError, RecursionError) as error:
        # Configuration values may be supplied from secrets: don't print the input.
        print(
            "Privacy build failed: "
            + type(error).__name__
            + ". Check configuration and output path.",
            file=sys.stderr,
        )
        return 1
    print(
        "Privacy pages generated ("
        + ("publication" if args.publish else "draft")
        + ")."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
