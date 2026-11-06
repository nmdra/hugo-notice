"""Offline integration tests. Run: python3 -m unittest discover -s tests -v."""

import base64
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
TYPES = (
    "note", "abstract", "info", "todo", "tip", "success", "question",
    "warning", "failure", "danger", "bug", "example", "quote",
)
ALIASES = {
    "summary": "abstract", "tldr": "abstract", "hint": "tip",
    "important": "tip", "check": "success", "done": "success",
    "help": "question", "faq": "question", "caution": "warning",
    "attention": "warning", "fail": "failure", "missing": "failure",
    "error": "danger", "cite": "quote",
}


class Element:
    def __init__(self, tag, attrs=(), parent=None):
        self.tag = tag
        self.attrs = dict(attrs)
        self.parent = parent
        self.children = []

    @property
    def classes(self):
        return self.attrs.get("class", "").split()

    @property
    def text(self):
        return "".join(child.text if isinstance(child, Element) else child
                       for child in self.children)

    def find(self, tag=None, css_class=None):
        found = []
        for child in self.children:
            if isinstance(child, Element):
                if ((tag is None or child.tag == tag)
                        and (css_class is None or css_class in child.classes)):
                    found.append(child)
                found.extend(child.find(tag, css_class))
        return found


class Document(HTMLParser):
    """Keep source nesting, including invalid p/details nesting browsers repair."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Element("document")
        self.current = self.root
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attrs):
        element = Element(tag, attrs, self.current)
        self.current.children.append(element)
        if tag not in self.VOID:
            self.current = element

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        node = self.current
        while node.parent is not None:
            if node.tag == tag:
                self.current = node.parent
                return
            node = node.parent

    def handle_data(self, data):
        self.current.children.append(data)


class Site:
    def __init__(self, directory, pages, unsafe=False, language="en", extra_config="",
                 alternate_output=False):
        self.root = Path(directory)
        theme = self.root / "themes" / "hugo-notice"
        theme.mkdir(parents=True)
        # Copy only Hugo inputs. No go.mod, network module resolution, or repo writes.
        for name in ("layouts", "assets", "i18n"):
            if (ROOT / name).exists():
                shutil.copytree(ROOT / name, theme / name)
        if alternate_output:
            extra_config += '''
[outputs]
page = ["HTML", "ALT"]
[outputFormats.ALT]
mediaType = "text/html"
isHTML = true
baseName = "alternate"
'''
        self.write("hugo.toml", f'''baseURL = "https://example.org/"
theme = "hugo-notice"
defaultContentLanguage = "{language}"
disableKinds = ["taxonomy", "term", "RSS", "sitemap"]
{extra_config}
[markup.goldmark.renderer]
unsafe = {str(unsafe).lower()}
''')
        self.write("layouts/_default/single.html",
                   "<!doctype html><html><head><title>{{ .Title }}</title></head>"
                   "<body><main>{{ .Content }}</main></body></html>")
        self.write("layouts/index.html", "<!doctype html><html><body>Home</body></html>")
        self.write("layouts/_default/_markup/render-link.html",
                   '<a href="{{ .Destination | safeURL }}" '
                   'data-page-title="{{ .Page.Title }}">{{ .Text | safeHTML }}</a>')
        if alternate_output:
            self.write("layouts/_default/single.alt.html",
                       "<!doctype html><html><head><title>{{ .Title }}</title></head>"
                       "<body><main>{{ .Content }}</main></body></html>")
            self.write("layouts/_default/_markup/render-link.html",
                       '<a href="{{ .Destination | safeURL }}" data-output="HTML" '
                       'data-page-title="{{ .Page.Title }}">{{ .Text | safeHTML }}</a>')
            self.write("layouts/_default/_markup/render-link.alt.html",
                       '<a href="{{ .Destination | safeURL }}" data-output="ALT" '
                       'data-page-title="{{ .Page.Title }}">{{ .Text | safeHTML }}</a>')
        for slug, content in pages.items():
            self.write(f"content/{slug}.md", f'+++\ntitle = "Page {slug}"\n+++\n\n{content}\n')
        result = subprocess.run(
            ["hugo", "--source", str(self.root), "--destination", str(self.root / "public")],
            text=True, capture_output=True, timeout=30,
        )
        if result.returncode:
            raise AssertionError(f"Hugo build failed:\n{result.stdout}\n{result.stderr}")

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def source(self, slug, filename="index.html"):
        return (self.root / "public" / slug / filename).read_text(encoding="utf-8")

    def document(self, slug, filename="index.html"):
        return Document(self.source(slug, filename)).root

    def stylesheet(self, href):
        path = unquote(urlsplit(href).path).lstrip("/")
        return self.root / "public" / path


def notice(kind="", title=None, body="Body."):
    args = f' "{kind}"' if kind else ""
    if title is not None:
        args += f" `{title}`"
    return "{{< notice" + args + " >}}\n" + body + "\n{{< /notice >}}"


@unittest.skipUnless(shutil.which("hugo"), "Hugo is required for integration tests")
class NoticeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="hugo-notice-tests-")
        cls.addClassCleanup(cls.temporary.cleanup)
        root = Path(cls.temporary.name)
        pages = {
            "types": "\n\n".join(notice(kind) for kind in TYPES),
            "aliases": "\n\n".join(notice(alias) for alias in ALIASES),
            "folds": "\n\n".join(notice(kind) for kind in
                                    ("tip+", "warning-", "hint+", "error-", "bogus+")),
            "defaults": "\n\n".join((notice(), notice("unknown"), notice("TIP"))),
            "custom": notice("tip", '<img src=x onerror=alert(1)> & "quoted"'),
            "nested": notice("note-", "Outer", "Before **bold**.\n\n"
                             + notice("tip+", "Inner", "A *nested* paragraph.")
                             + '\n\nAfter.\n\n<script>alert("unsafe")</script>'),
            "deep": notice("note-", "Outer", "Outer before.\n\n"
                           + notice("tip+", "Middle", "Middle before.\n\n"
                                    + notice("warning-", "Deep", "Deep **body**.")
                                    + "\n\n" + notice("question+", "Inner sibling", "Inner sibling body.")
                                    + "\n\nMiddle after.")
                           + "\n\n" + notice("success-", "Outer sibling", "Outer sibling body.")
                           + "\n\nOuter after.")
                    + "\n\n" + notice("quote+", "Top sibling", "Top sibling body."),
            "hook": notice("note", body="[Link](https://example.org/target)"),
            "empty": "A page without callouts.",
        }
        cls.safe = Site(root / "safe", pages)
        cls.unsafe = Site(root / "unsafe", {
            "raw": notice("note", body='<details><summary>Raw summary</summary>\n\n'
                          'Raw **body**.\n\n</details>'),
            "commented": notice("note", body='<!-- Leading block comment -->\n'
                                '<details><summary>Commented summary</summary>\n\n'
                                'Commented body.\n\n</details>'),
        }, unsafe=True)
        cls.german = Site(root / "german", {
            "translated": notice("warning") + "\n\n" + notice("abstract"),
        }, language="de")
        cls.german_placeholders = Site(root / "german-placeholders", {
            "translated": "\n\n".join(notice(kind) for kind in TYPES),
        }, language="de", extra_config="enableMissingTranslationPlaceholders = true")

    def callouts(self, slug, site=None):
        return (site or self.safe).document(slug).find(css_class="notice")

    def title(self, callout):
        return callout.find(css_class="notice-title")[0].text.strip()

    def test_all_canonical_types_and_default_titles(self):
        callouts = self.callouts("types")
        self.assertEqual(len(callouts), len(TYPES))
        for callout, kind in zip(callouts, TYPES):
            with self.subTest(kind=kind):
                self.assertIn(kind, callout.classes)
                self.assertEqual(self.title(callout), kind.capitalize())
                self.assertEqual(callout.tag, "div")
                self.assertTrue(callout.find("svg"))

    def test_all_aliases_use_canonical_type_and_title(self):
        callouts = self.callouts("aliases")
        self.assertEqual(len(callouts), len(ALIASES))
        for callout, (alias, kind) in zip(callouts, ALIASES.items()):
            with self.subTest(alias=alias):
                self.assertIn(kind, callout.classes)
                self.assertEqual(self.title(callout), kind.capitalize())

    def test_quoted_fold_markers_control_native_details(self):
        callouts = self.callouts("folds")
        self.assertEqual(len(callouts), 5)
        for callout, kind, opened in zip(callouts,
                                         ("tip", "warning", "tip", "danger", "note"),
                                         (True, False, True, False, True)):
            with self.subTest(kind=kind, opened=opened):
                self.assertEqual(callout.tag, "details")
                self.assertIn(kind, callout.classes)
                self.assertEqual("open" in callout.attrs, opened)
                self.assertEqual(len([node for node in callout.children
                                      if isinstance(node, Element) and node.tag == "summary"]), 1)

    def test_default_unknown_and_case_normalization(self):
        callouts = self.callouts("defaults")
        self.assertEqual(len(callouts), 3)
        for callout, kind in zip(callouts, ("note", "note", "tip")):
            self.assertIn(kind, callout.classes)
            self.assertEqual(self.title(callout), kind.capitalize())

    def test_custom_title_is_text_not_injected_html(self):
        callout, = self.callouts("custom")
        self.assertEqual(self.title(callout), '<img src=x onerror=alert(1)> & "quoted"')
        self.assertEqual(callout.find("img"), [])
        self.assertEqual(callout.find("script"), [])

    def test_nested_callouts_preserve_html_with_goldmark_safe_defaults(self):
        callouts = self.callouts("nested")
        self.assertEqual(len(callouts), 2, "Both nested callouts must survive safe Markdown rendering")
        outer, inner = callouts
        self.assertIn(inner, outer.find(css_class="notice"))
        self.assertEqual(self.title(outer), "Outer")
        self.assertEqual(self.title(inner), "Inner")
        self.assertEqual([node.text for node in outer.find("strong")], ["bold"])
        self.assertEqual([node.text for node in inner.find("em")], ["nested"])
        self.assertIn("After.", outer.text)
        self.assertNotIn("<details", outer.text)
        self.assertEqual(outer.find("script"), [])

    def test_three_level_nesting_with_siblings_preserves_structure_and_states(self):
        document = self.safe.document("deep")
        callouts = document.find(css_class="notice")
        expected = (
            ("Outer", None, False),
            ("Middle", "Outer", True),
            ("Deep", "Middle", False),
            ("Inner sibling", "Middle", True),
            ("Outer sibling", "Outer", False),
            ("Top sibling", None, True),
        )
        self.assertEqual(len(callouts), len(expected))
        for callout, (title, parent_title, opened) in zip(callouts, expected):
            with self.subTest(title=title):
                self.assertEqual(self.title(callout), title)
                self.assertEqual(callout.tag, "details")
                self.assertEqual("open" in callout.attrs, opened)
                parent_callout = None
                ancestor = callout.parent
                while ancestor is not None:
                    self.assertNotEqual(ancestor.tag, "p", "A paragraph must not contain a callout block")
                    if parent_callout is None and "notice" in ancestor.classes:
                        parent_callout = ancestor
                    ancestor = ancestor.parent
                actual_parent = self.title(parent_callout) if parent_callout is not None else None
                self.assertEqual(actual_parent, parent_title)
        self.assertEqual([node.text for node in document.find("strong")], ["body"])
        for text in ("Outer before.", "Middle before.", "Middle after.", "Outer after."):
            self.assertEqual(document.text.count(text), 1)
        for slug in ("nested", "deep"):
            self.assertNotIn("HUGONOTICE", self.safe.source(slug))

    def test_all_icons_and_chevrons_are_decorative(self):
        for slug, expected_count in (("types", len(TYPES)), ("folds", 10), ("deep", 12)):
            with self.subTest(page=slug):
                icons = self.safe.document(slug).find("svg")
                self.assertEqual(len(icons), expected_count)
                for icon in icons:
                    self.assertEqual(icon.attrs.get("aria-hidden"), "true")
                    self.assertEqual(icon.attrs.get("focusable"), "false")

    def test_render_link_hook_receives_owning_page(self):
        link, = self.safe.document("hook").find("a")
        self.assertEqual(link.attrs.get("data-page-title"), "Page hook")
        self.assertEqual(link.text, "Link")

    def test_raw_details_with_unsafe_enabled_are_not_wrapped_in_paragraph(self):
        callout, = self.callouts("raw", self.unsafe)
        details, = callout.find("details")
        ancestor = details.parent
        while ancestor is not None:
            self.assertNotEqual(ancestor.tag, "p", "Block details cannot be inside a paragraph")
            ancestor = ancestor.parent
        self.assertEqual(details.find("summary")[0].text, "Raw summary")
        self.assertIn("Raw", details.text)

    def test_leading_comment_and_raw_details_are_not_wrapped_in_paragraph(self):
        callout, = self.callouts("commented", self.unsafe)
        details, = callout.find("details")
        ancestor = details.parent
        while ancestor is not None:
            self.assertNotEqual(ancestor.tag, "p", "A comment before details must not cause paragraph wrapping")
            ancestor = ancestor.parent
        self.assertEqual(details.find("summary")[0].text, "Commented summary")
        self.assertIn("Commented body.", details.text)
        self.assertNotIn("HUGONOTICE", self.unsafe.source("commented"))

    def test_missing_translation_placeholders_do_not_replace_english_fallback(self):
        callouts = self.callouts("translated", self.german_placeholders)
        self.assertEqual(len(callouts), len(TYPES))
        translations = {"note": "Anmerkung", "info": "Info", "tip": "Hinweis", "warning": "Warnung"}
        for callout, kind in zip(callouts, TYPES):
            with self.subTest(kind=kind):
                self.assertEqual(self.title(callout), translations.get(kind, kind.capitalize()))
        self.assertNotIn("[i18n]", self.german_placeholders.source("translated"))

    def test_german_default_language_has_translation_and_english_fallback(self):
        warning, abstract = self.callouts("translated", self.german)
        self.assertEqual(self.title(warning), "Warnung")
        self.assertEqual(self.title(abstract), "Abstract")

    def test_stylesheet_is_external_fingerprinted_and_once_per_page(self):
        hrefs = set()
        for slug in ("types", "aliases", "nested", "folds"):
            with self.subTest(page=slug):
                document = self.safe.document(slug)
                self.assertEqual(document.find("style"), [])
                links = [link for link in document.find("link")
                         if "stylesheet" in link.attrs.get("rel", "").split()]
                self.assertEqual(len(links), 1)
                link = links[0]
                href = link.attrs["href"]
                hrefs.add(href)
                self.assertRegex(urlsplit(href).path, r"hugo-notice\.[0-9a-f]{32,}\.css$")
                asset = self.safe.stylesheet(href)
                self.assertTrue(asset.is_file(), f"Missing generated CSS: {href}")
                # Check integrity when supplied, without requiring a specific hash algorithm.
                if "integrity" in link.attrs:
                    algorithm, digest = link.attrs["integrity"].split("-", 1)
                    actual = hashlib.new(algorithm, asset.read_bytes()).digest()
                    self.assertEqual(base64.b64encode(actual).decode("ascii"), digest)
        self.assertEqual(len(hrefs), 1, "All pages should share the fingerprinted asset")
        self.assertEqual(self.safe.document("empty").find("link"), [])

    def test_each_html_output_gets_one_stylesheet_when_hooks_force_rerender(self):
        with tempfile.TemporaryDirectory(prefix="hugo-notice-outputs-") as directory:
            body = notice("note", "First outer", "[First link](/first/)\n\n"
                          + notice("tip+", "Nested", "[Nested link](/nested/)"))
            body += "\n\n" + notice("warning-", "Second outer", "[Second link](/second/)")
            site = Site(directory, {"outputs": body}, alternate_output=True)
            stylesheet_hrefs = set()
            for filename, marker in (("index.html", "HTML"), ("alternate.html", "ALT")):
                with self.subTest(output=marker):
                    document = site.document("outputs", filename)
                    self.assertEqual(document.find("style"), [])
                    stylesheets = [link for link in document.find("link")
                                   if "stylesheet" in link.attrs.get("rel", "").split()]
                    self.assertEqual(len(stylesheets), 1)
                    href = stylesheets[0].attrs["href"]
                    self.assertRegex(urlsplit(href).path, r"hugo-notice\.[0-9a-f]{32,}\.css$")
                    self.assertTrue(site.stylesheet(href).is_file())
                    stylesheet_hrefs.add(href)
                    links = document.find("a")
                    self.assertEqual([link.text for link in links],
                                     ["First link", "Nested link", "Second link"])
                    # Distinct hooks prove each output rendered its own content rather than
                    # reusing cached HTML from the other output.
                    self.assertEqual([link.attrs.get("data-output") for link in links],
                                     [marker] * 3)
                    self.assertEqual([link.attrs.get("data-page-title") for link in links],
                                     ["Page outputs"] * 3)
                    callouts = document.find(css_class="notice")
                    self.assertEqual(len(callouts), 3)
                    self.assertIn(callouts[1], callouts[0].find(css_class="notice"))
                    self.assertNotIn(callouts[2], callouts[0].find(css_class="notice"))
            self.assertEqual(len(stylesheet_hrefs), 1)

    def test_css_uses_readable_title_colors_and_native_scoped_folding(self):
        links = self.safe.document("types").find("link")
        self.assertEqual(len(links), 1, "Expected one external callout stylesheet")
        link = links[0]
        css = self.safe.stylesheet(link.attrs["href"]).read_text(encoding="utf-8")
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        self.assertRegex(css, r"--notice-title-color\s*:\s*#343a40\b")
        dark_rules = re.findall(r"([^{}]*\[data-theme=[^{}]*dark[^{}]*\][^{}]*)\{([^{}]*)\}", css)
        self.assertTrue(any(re.search(r"--notice-title-color\s*:\s*#cdd6f4\b", body)
                            for _, body in dark_rules), "Dark mode needs a readable title default")
        title_rules = [body for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css)
                       if re.search(r"\.notice-title\s*(?:,|$)", selector.strip())]
        self.assertTrue(any(re.search(r"(?:^|;)\s*color\s*:\s*var\(--notice-title-color", body)
                            for body in title_rules))
        self.assertFalse(any(re.search(r"(?:^|;)\s*color\s*:\s*var\(--notice-accent", body)
                             for body in title_rules), "Accent must not control title text")
        self.assertNotIn("::details-content", css, "Keep native instant details folding")
        self.assertNotRegex(css, r"grid-template-rows\s*:")
        for selector, _ in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
            for branch in selector.split(","):
                branch = branch.strip()
                if "details.notice" not in branch:
                    continue
                # A parent open/collapsed state must not change a nested callout's title/chevron.
                for target in ("summary", ".notice-title", ".notice-chevron"):
                    if target in branch:
                        suffix = branch.split("details.notice", 1)[1]
                        self.assertIn(">", suffix, f"Unscoped nested-callout selector: {branch}")


class ModuleDeclarationTests(unittest.TestCase):
    def test_module_path_matches_public_repository(self):
        declaration = (ROOT / "go.mod").read_text(encoding="utf-8")
        self.assertRegex(declaration, r"(?m)^module\s+github\.com/nmdra/hugo-notice\s*$")


if __name__ == "__main__":
    unittest.main()
