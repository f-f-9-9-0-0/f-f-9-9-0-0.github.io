import importlib.util
from pathlib import Path
import unittest

SCRIPTS = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('site_checks', SCRIPTS / 'check-site.py')
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)

# As in the site's palette, the light accent is also the dark inverse accent, and the other way round.
PALETTE = {'light': {'brand': '#0d6b68', 'brand-inverse': '#5fd1c6'}, 'dark': {'brand': '#5fd1c6', 'brand-inverse': '#0d6b68'}}
NEW_LIGHT_BRAND = {'light': {'brand': '#0e6b68', 'brand-inverse': '#5fd1c6'}, 'dark': {'brand': '#5fd1c6', 'brand-inverse': '#0d6b68'}}
WITHOUT_BRAND = {'light': {'brand-inverse': '#5fd1c6'}, 'dark': {'brand-inverse': '#0d6b68'}}
NEW_DARK_BRAND = {'light': {'brand': '#0d6b68', 'brand-inverse': '#5fd1c6'}, 'dark': {'brand': '#6fd1c6', 'brand-inverse': '#0d6b68'}}
THEMED = ('<svg xmlns="http://www.w3.org/2000/svg"><style>:root{--brand:#0d6b68;}'
          '@media (prefers-color-scheme:dark){:root{--brand:#5fd1c6;}}[stroke="#c0ff01"]{stroke:var(--brand)}</style>'
          '<path stroke="#c0ff01"/></svg>')
FILES = {'/assets/css/site.css', '/assets/fonts/plex.woff2', '/assets/images/card.png', '/assets/images/chart-narrow.svg', '/blog/index.html'}


def swap(text, old, new):
    """The text with old replaced by new, failing unless old occurs exactly once."""
    assert text.count(old) == 1, old
    return text.replace(old, new)


class DrawingColourTests(unittest.TestCase):
    def test_illustration_in_palette_colours_passes(self):
        site.check_drawing('assets/images/articles/topic.svg', THEMED, PALETTE)

    def test_light_colour_changed_in_the_palette_only_fails(self):
        with self.assertRaisesRegex(AssertionError, r"articles/topic\.svg: light colours differ from _data/palette\.json: \{'brand': '#0d6b68'\}"):
            site.check_drawing('assets/images/articles/topic.svg', THEMED, NEW_LIGHT_BRAND)

    def test_dark_colour_changed_in_the_palette_only_fails(self):
        with self.assertRaisesRegex(AssertionError, r"hero\.svg: dark colours differ from _data/palette\.json: \{'brand': '#5fd1c6'\}"):
            site.check_drawing('assets/images/hero.svg', THEMED, NEW_DARK_BRAND)

    def test_theme_without_a_dark_block_fails(self):
        svg = swap(THEMED, '@media (prefers-color-scheme:dark){:root{--brand:#5fd1c6;}}', '')
        with self.assertRaisesRegex(AssertionError, r'topic\.svg: theme must declare the same colours for light and dark mode'):
            site.check_drawing('assets/images/articles/topic.svg', svg, PALETTE)

    def test_theme_painting_a_literal_colour_fails(self):
        svg = swap(THEMED, 'stroke:var(--brand)', 'stroke:#0d6b68')
        with self.assertRaisesRegex(AssertionError, r"topic\.svg: theme paints a colour that is not a palette colour: \['#0d6b68'\]"):
            site.check_drawing('assets/images/articles/topic.svg', svg, PALETTE)

    def test_colour_the_theme_does_not_repaint_fails(self):
        svg = swap(THEMED, '</svg>', '<rect fill="#10212d"/></svg>')
        with self.assertRaisesRegex(AssertionError, r"topic\.svg: colours the theme does not repaint: \['fill=#10212d'\]"):
            site.check_drawing('assets/images/articles/topic.svg', svg, PALETTE)

    def test_drawing_in_a_new_folder_without_a_theme_fails(self):
        with self.assertRaisesRegex(AssertionError, r'diagrams/flow\.svg: drawing has no light and dark theme'):
            site.check_drawing('assets/images/diagrams/flow.svg', '<svg xmlns="http://www.w3.org/2000/svg"><path stroke="#55dcf5"/></svg>', PALETTE)

    def test_drawing_in_a_new_folder_with_a_fixed_colour_fails(self):
        svg = swap(THEMED, '</svg>', '<path fill="#e69f00"/></svg>')
        with self.assertRaisesRegex(AssertionError, r"diagrams/flow\.svg: colours the theme does not repaint: \['fill=#e69f00'\]"):
            site.check_drawing('assets/images/diagrams/flow.svg', svg, PALETTE)

    def test_empty_theme_fails(self):
        with self.assertRaisesRegex(AssertionError, r'topic\.svg: theme must declare the same colours for light and dark mode'):
            site.check_drawing('assets/images/articles/topic.svg', '<svg xmlns="http://www.w3.org/2000/svg"><style/></svg>', PALETTE)

    def test_spaced_declaration_is_compared(self):
        svg = swap(THEMED, ':root{--brand:#0d6b68;}', ':root{--brand: #0e6b68;}')
        with self.assertRaisesRegex(AssertionError, r"topic\.svg: light colours differ from _data/palette\.json: \{'brand': '#0e6b68'\}"):
            site.check_drawing('assets/images/articles/topic.svg', svg, PALETTE)

    def test_colour_missing_from_the_palette_fails(self):
        with self.assertRaisesRegex(AssertionError, r"topic\.svg: light colours differ from _data/palette\.json: \{'brand': '#0d6b68'\}"):
            site.check_drawing('assets/images/articles/topic.svg', THEMED, WITHOUT_BRAND)

    def test_undeclared_theme_colour_fails(self):
        svg = swap(THEMED, 'stroke:var(--brand)', 'stroke:var(--brand-inverse)')
        with self.assertRaisesRegex(AssertionError, r"topic\.svg: theme uses colours it does not declare: \['brand-inverse'\]"):
            site.check_drawing('assets/images/articles/topic.svg', svg, PALETTE)

    def test_fill_in_a_colour_only_repainted_as_a_stroke_fails(self):
        svg = swap(THEMED, '</svg>', '<rect fill="#c0ff01"/></svg>')
        with self.assertRaisesRegex(AssertionError, r"topic\.svg: colours the theme does not repaint: \['fill=#c0ff01'\]"):
            site.check_drawing('assets/images/articles/topic.svg', svg, PALETTE)

    def test_nested_colour_the_theme_does_not_repaint_fails(self):
        svg = swap(THEMED, '</svg>', '<g><rect fill="#10212d"/></g></svg>')
        with self.assertRaisesRegex(AssertionError, r"topic\.svg: colours the theme does not repaint: \['fill=#10212d'\]"):
            site.check_drawing('assets/images/articles/topic.svg', svg, PALETTE)

    def test_theme_filling_a_named_colour_fails(self):
        svg = swap(THEMED, '</style>', 'rect{fill:teal}</style>')
        with self.assertRaisesRegex(AssertionError, r"topic\.svg: theme paints a colour that is not a palette colour: \['teal'\]"):
            site.check_drawing('assets/images/articles/topic.svg', svg, PALETTE)

    def test_literal_colour_in_a_second_style_fails(self):
        svg = swap(THEMED, '</svg>', '<style>rect{stroke:#0d6b68}</style></svg>')
        with self.assertRaisesRegex(AssertionError, r"topic\.svg: theme paints a colour that is not a palette colour: \['#0d6b68'\]"):
            site.check_drawing('assets/images/articles/topic.svg', svg, PALETTE)

    def test_unpainted_shapes_and_stroke_settings_pass(self):
        svg = swap(THEMED, '</style>', 'rect{fill:none}text{-webkit-text-stroke:1px;stroke-width:3px;paint-order:stroke}</style>')
        site.check_drawing('assets/images/articles/topic.svg', svg, PALETTE)

    def test_spaced_dark_media_query_is_read(self):
        svg = swap(THEMED, '@media (prefers-color-scheme:dark)', '@media (prefers-color-scheme: dark)')
        site.check_drawing('assets/images/articles/topic.svg', svg, PALETTE)

    def test_named_colour_fails(self):
        svg = swap(THEMED, '</svg>', '<rect fill="white"/></svg>')
        with self.assertRaisesRegex(AssertionError, r"topic\.svg: colours the theme does not repaint: \['fill=white'\]"):
            site.check_drawing('assets/images/articles/topic.svg', svg, PALETTE)

    def test_chart_example_keeps_its_series_colours(self):
        svg = swap(THEMED, '</svg>', '<path fill="#e69f00"/></svg>')
        site.check_drawing('assets/images/projects/library/chart.svg', svg, PALETTE)


class PaletteTests(unittest.TestCase):
    def test_palette_naming_the_same_colours_in_both_modes_passes(self):
        site.check_palette(PALETTE)

    def test_colour_missing_in_dark_mode_fails(self):
        with self.assertRaisesRegex(AssertionError, r'_data/palette\.json: light and dark must name the same colours'):
            site.check_palette({'light': {'ink': '#13232a', 'muted': '#4f5f5e'}, 'dark': {'ink': '#e3ece8'}})


class PageLoadTests(unittest.TestCase):
    def test_site_files_listed_origins_and_plain_links_pass(self):
        page = ('<link rel="stylesheet" href="/assets/css/site.css?v=1"><link rel="preload" href="/assets/fonts/plex.woff2" as="font">'
                '<script src="https://static.cloudflareinsights.com/beacon.min.js"></script><source srcset="/assets/images/chart-narrow.svg">'
                '<a href="https://example.com/">A link loads nothing</a>')
        site.check_page_loads('index.html', page, FILES)

    def test_relative_url_resolves_against_the_page(self):
        site.check_page_loads('blog/index.html', '<img src="../assets/images/chart-narrow.svg" alt="">', FILES)

    def test_missing_relative_image_fails(self):
        with self.assertRaisesRegex(AssertionError, r'blog/index\.html: missing local target cover\.png'):
            site.check_page_loads('blog/index.html', '<img src="cover.png" alt="">', FILES)

    def test_reference_links_and_upper_case_listed_hosts_pass(self):
        page = ('<link rel="canonical" href="https://example.com/"><link rel="alternate" type="application/rss+xml" href="https://example.com/feed.xml">'
                '<script src="https://STATIC.cloudflareinsights.com/beacon.min.js"></script>')
        site.check_page_loads('index.html', page, FILES)

    def test_backslash_before_a_listed_host_fails(self):
        with self.assertRaisesRegex(AssertionError, r'index\.html: loads https://evil\.example'):
            site.check_page_loads('index.html', '<script src="https://evil.example\\@static.cloudflareinsights.com/x.js"></script>', FILES)

    def test_line_break_inside_a_source_fails(self):
        with self.assertRaisesRegex(AssertionError, r'loads https://static\.cloudflareinsights\.com\.evil\.example/y\.js'):
            site.check_page_loads('index.html', '<script src="https://static.cloudflareinsights.com\n.evil.example/y.js"></script>', FILES)

    def test_gist_embed_fails(self):
        with self.assertRaisesRegex(AssertionError, r'index\.html: loads https://gist\.github\.com/a/b\.js'):
            site.check_page_loads('index.html', '<script src="https://gist.github.com/a/b.js"></script>', FILES)

    def test_trailing_comma_in_srcset_passes(self):
        site.check_page_loads('index.html', '<img src="/assets/images/chart-narrow.svg" srcset="/assets/images/chart-narrow.svg 1x, " alt="">', FILES)

    def test_third_party_track_fails(self):
        with self.assertRaisesRegex(AssertionError, r'loads https://cdn\.example\.com/captions\.vtt'):
            site.check_page_loads('index.html', '<track src="https://cdn.example.com/captions.vtt">', FILES)

    def test_third_party_script_fails(self):
        with self.assertRaisesRegex(AssertionError, r'index\.html: loads https://cdn\.example\.com/x\.js'):
            site.check_page_loads('index.html', '<script src="https://cdn.example.com/x.js"></script>', FILES)

    def test_image_candidate_from_another_origin_fails(self):
        with self.assertRaisesRegex(AssertionError, r'loads https://cdn\.example\.com/b\.svg'):
            site.check_page_loads('index.html', '<img src="/assets/images/chart-narrow.svg" srcset="https://cdn.example.com/b.svg 2x" alt="">', FILES)

    def test_touch_icon_from_another_origin_fails(self):
        with self.assertRaisesRegex(AssertionError, r'loads https://cdn\.example\.com/icon\.png'):
            site.check_page_loads('index.html', '<link rel="apple-touch-icon" href="https://cdn.example.com/icon.png">', FILES)

    def test_empty_image_source_fails(self):
        with self.assertRaisesRegex(AssertionError, r'index\.html: loads an empty URL'):
            site.check_page_loads('index.html', '<img src="" alt="Chart">', FILES)

    def test_font_service_stylesheet_fails(self):
        with self.assertRaisesRegex(AssertionError, r'blog/index\.html: loads https://fonts\.googleapis\.com/'):
            site.check_page_loads('blog/index.html', '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter">', FILES)

    def test_protocol_relative_image_fails(self):
        with self.assertRaisesRegex(AssertionError, r'loads //cdn\.example\.com/a\.png'):
            site.check_page_loads('index.html', '<img src="//cdn.example.com/a.png" alt="">', FILES)

    def test_second_image_candidate_from_another_origin_fails(self):
        with self.assertRaisesRegex(AssertionError, r'loads https://cdn\.example\.com/b\.svg'):
            site.check_page_loads('index.html', '<source srcset="/assets/images/chart-narrow.svg 1x, https://cdn.example.com/b.svg 2x">', FILES)

    def test_preconnect_hint_fails(self):
        with self.assertRaisesRegex(AssertionError, r'loads https://fonts\.gstatic\.com'):
            site.check_page_loads('index.html', '<link rel="preconnect" href="https://fonts.gstatic.com">', FILES)

    def test_missing_font_preload_fails(self):
        with self.assertRaisesRegex(AssertionError, r'index\.html: missing local target /assets/fonts/mono\.woff2'):
            site.check_page_loads('index.html', '<link rel="preload" href="/assets/fonts/mono.woff2" as="font">', FILES)

    def test_missing_phone_render_fails(self):
        with self.assertRaisesRegex(AssertionError, r'projects/index\.html: missing local target /assets/images/chart-narow\.svg'):
            site.check_page_loads('projects/index.html', '<picture><source srcset="/assets/images/chart-narow.svg"></picture>', FILES)


class PreviewImageTests(unittest.TestCase):
    def test_preview_image_among_the_site_files_passes(self):
        site.check_preview('index.html', 'https://example.com/assets/images/card.png', FILES, 'https://example.com')

    def test_missing_preview_image_fails(self):
        with self.assertRaisesRegex(AssertionError, r'index\.html: missing link-preview image https://example\.com/assets/images/none\.png'):
            site.check_preview('index.html', 'https://example.com/assets/images/none.png', FILES, 'https://example.com')

    def test_page_without_preview_image_fails(self):
        with self.assertRaisesRegex(AssertionError, r'index\.html: no link-preview image'):
            site.check_preview('index.html', None, FILES, 'https://example.com')

    def test_preview_image_on_another_site_fails(self):
        with self.assertRaisesRegex(AssertionError, r'index\.html: link-preview image https://cdn\.example\.net/card\.png is not an absolute URL on this site'):
            site.check_preview('index.html', 'https://cdn.example.net/card.png', FILES, 'https://example.com')

    def test_preview_image_naming_this_site_only_in_its_query_fails(self):
        with self.assertRaisesRegex(AssertionError, r'index\.html: link-preview image https://cdn\.example\.net/assets/images/card\.png\?u=https://example\.com/ is not an absolute URL on this site'):
            site.check_preview('index.html', 'https://cdn.example.net/assets/images/card.png?u=https://example.com/', FILES, 'https://example.com')


if __name__ == '__main__':
    unittest.main()
