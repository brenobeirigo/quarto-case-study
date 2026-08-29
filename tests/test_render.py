import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


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

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)

        if tag == "section":
            self.section_depth += 1
            classes = attributes.get("class", "").split()

            if "case-study" in classes:
                self.case_count += 1
                self.case_depth = self.section_depth
                self.case_style = attributes.get("style", "")

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
        )

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

    def test_pdf_uses_a_breakable_case_box(self):
        result = self.run_quarto("pdf")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        pdf = self.project / "example.pdf"
        self.assertTrue(pdf.exists())
        self.assertGreater(pdf.stat().st_size, 10_000)
        self.assertEqual(pdf.read_bytes()[:4], b"%PDF")


if __name__ == "__main__":
    unittest.main()
