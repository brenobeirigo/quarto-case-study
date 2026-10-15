import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from zipfile import ZipFile


REPOSITORY = Path(__file__).resolve().parents[1]


class CaseStudyParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.section_depth = 0
        self.case_depth = None
        self.case_count = 0
        self.label_text = []
        self.in_label = False
        self.sections_inside = []
        self.sections_outside = []
        self.case_style = ""
        self.case_styles = {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)

        if tag == "section":
            self.section_depth += 1
            classes = attributes.get("class", "").split()

            if "case-study" in classes:
                self.case_count += 1
                self.case_depth = self.section_depth
                self.case_style = attributes.get("style", "")
                self.case_styles[attributes.get("id", "")] = self.case_style

            identifier = attributes.get("id", "")
            if self.case_depth is None:
                self.sections_outside.append(identifier)
            else:
                self.sections_inside.append(identifier)

        if tag == "div":
            classes = attributes.get("class", "").split()
            if "case-study-label" in classes and self.case_depth is not None:
                self.in_label = True

    def handle_endtag(self, tag):
        if tag == "div" and self.in_label:
            self.in_label = False

        if tag != "section":
            return

        if self.case_depth == self.section_depth:
            self.case_depth = None

        self.section_depth -= 1

    def handle_data(self, data):
        if self.in_label:
            self.label_text.append(data)


class RenderContractTests(unittest.TestCase):
    def setUp(self):
        if shutil.which("quarto") is None:
            self.fail("Quarto is required for the render-contract tests.")

        self.temporary_directory = tempfile.TemporaryDirectory()
        self.project = Path(self.temporary_directory.name)
        shutil.copy2(REPOSITORY / "example.qmd", self.project / "example.qmd")
        shutil.copytree(
            REPOSITORY / "_extensions",
            self.project / "_extensions",
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def run_quarto(self, output_format):
        return subprocess.run(
            ["quarto", "render", "example.qmd", "--to", output_format],
            cwd=self.project,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def render_source(self, source):
        (self.project / "example.qmd").write_text(source, encoding="utf-8")
        result = self.run_quarto("html")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        html = (self.project / "example.html").read_text(encoding="utf-8")
        parser = CaseStudyParser()
        parser.feed(html)
        return html, parser

    def fixture(self, metadata="", cases=None):
        return (
            "---\ntitle: Theme inheritance\nformat:\n  html:\n"
            "    theme: cosmo\n    toc: true\n    css: host.css\n"
            "filters:\n  - case-study\n" + metadata + "---\n\n"
            + (cases or "## A complete case {#sec-case .case-study}\n\n"
               "Case content.\n\n### Detail\n\nNested content.\n\n"
               "## After {#sec-after}\n\nOutside content.\n"))

    def write_host_css(self):
        (self.project / "host.css").write_text(
            "body { --case-study-accent: #17624a;\n"
            "--case-study-background: #f0f8f4;\n"
            "--case-study-border-color: #a0bcac;\n"
            "--case-study-heading-color: #183e2b;\n"
            "--case-study-label-color: #315c45; }\n",
            encoding="utf-8",
        )

    def bundled_css(self):
        paths = list((self.project / "example_files").rglob("case-study.css"))
        self.assertEqual(len(paths), 1)
        return paths[0].read_text(encoding="utf-8")

    def test_html_wraps_the_complete_section(self):
        result = self.run_quarto("html")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        html = (self.project / "example.html").read_text(encoding="utf-8")
        parser = CaseStudyParser()
        parser.feed(html)

        self.assertEqual(parser.case_count, 1)
        self.assertEqual("".join(parser.label_text).strip(), "CASE STUDY")
        self.assertIn("sec-factory-schedule", parser.sections_inside)
        self.assertIn("a-question-for-later", parser.sections_inside)
        self.assertIn("sec-after-case", parser.sections_outside)
        self.assertIn("--case-study-accent: #6F2DA8", parser.case_style)
        self.assertIn('href="#sec-factory-schedule"', html)
        self.assertIn('id="toc-sec-factory-schedule"', html)
        self.assertIn("case-study.css", html)

    def test_no_accent_defers_to_inherited_host_css(self):
        self.write_host_css()
        html, parser = self.render_source(self.fixture())
        self.assertEqual(parser.case_count, 1)
        self.assertNotIn("--case-study-accent", parser.case_styles["sec-case"])
        self.assertIn("host.css", html)
        self.assertIn("sec-case", parser.sections_inside)
        self.assertIn("sec-after", parser.sections_outside)
        css = self.bundled_css()
        # An own declaration would shadow body/container theme variables.
        self.assertNotRegex(css, r"--case-study-accent\s*:")
        self.assertIn("var(--case-study-accent, var(--bs-primary, #6f2da8))", css)
        for hook in ("background", "border-color", "heading-color", "label-color"):
            self.assertIn("var(--case-study-" + hook + ",", css)

    def test_metadata_and_heading_accents_are_explicit_overrides(self):
        self.write_host_css()
        html, parser = self.render_source(self.fixture(
            'case-study:\n  label: "WORKED CASE"\n  accent: "#123abc"\n',
            "## Metadata case {#sec-meta .case-study}\n\nFirst.\n\n"
            '## Heading case {#sec-override .case-study data-accent="00796b" '
            'data-label="APPLICATION"}\n\nSecond.\n\n'
            '## Invalid case {#sec-invalid .case-study data-accent="red"}\n\nThird.\n',
        ))
        self.assertIn("--case-study-accent: #123ABC", parser.case_styles["sec-meta"])
        self.assertIn("--case-study-accent: #00796B", parser.case_styles["sec-override"])
        self.assertNotIn("--case-study-accent", parser.case_styles["sec-invalid"])
        self.assertIn("APPLICATION", "".join(parser.label_text))
        self.assertIn('id="toc-sec-override"', html)

    def test_invalid_and_empty_accents_do_not_inject_css(self):
        self.write_host_css()
        _, parser = self.render_source(self.fixture(
            'case-study:\n  accent: "not-a-color"\n',
            "## Invalid metadata {#sec-invalid-meta .case-study}\n\nContent.\n\n"
            '## Invalid heading {#sec-invalid-header .case-study '
            'data-accent="#123456;background:red"}\n\nContent.\n\n'
            '## Empty heading {#sec-empty .case-study data-accent=""}\n\nContent.\n',
        ))
        self.assertEqual(parser.case_count, 3)
        self.assertTrue(all("--case-study-accent" not in style
                            for style in parser.case_styles.values()))
        self.assertTrue(all("background:red" not in style
                            for style in parser.case_styles.values()))

    def test_author_styles_survive_an_explicit_accent(self):
        self.write_host_css()
        _, parser = self.render_source(self.fixture(
            cases='## Styled case {#sec-styled .case-study '
            'style="outline: 1px solid black" data-accent="#336699"}\n\nContent.\n',
        ))
        style = parser.case_styles["sec-styled"]
        self.assertIn("outline: 1px solid black;", style)
        self.assertIn("--case-study-accent: #336699", style)

    def test_docx_keeps_content_and_original_heading_anchor(self):
        result = self.run_quarto("docx")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with ZipFile(self.project / "example.docx") as document:
            xml = document.read("word/document.xml").decode("utf-8")
        self.assertIn("Formulating a factory schedule", xml)
        self.assertIn("sec-factory-schedule", xml)
        self.assertIn("A question for later", xml)
        self.assertNotIn("CASE STUDY", xml)
        self.assertNotIn("case-study-label", xml)

if __name__ == "__main__":
    unittest.main()
