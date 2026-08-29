# Quarto Case Study

Quarto Case Study gives a complete example or case study a visible beginning
and end. Add `.case-study` to a heading, and the extension places that heading
and its contents inside one box. The box ends at the next heading of the same
or a higher level.

The heading keeps its identifier, table-of-contents entry, and cross-reference
target. HTML output uses a semantic section with a subtle background, a thin
border, and a 4 px accent rule. PDF output uses a breakable `tcolorbox`.

## Install

```bash
quarto add brenobeirigo/quarto-case-study
```

Confirm the prompt to install the extension into the current Quarto project.

## Use

Add the filter to the document or project configuration:

```yaml
filters:
  - case-study
```

Mark the heading that starts the case:

```markdown
## Formulating a factory schedule {#sec-factory-schedule .case-study}

The complete case starts here.

### A question for later

This subsection remains inside the case.

## The next concept

The next section is outside the case.
```

Use an explicit identifier such as `#sec-factory-schedule` when the heading is
referenced elsewhere. The extension preserves the identifier and heading
classes.

## Configure

Set the default label and accent in document or project metadata:

```yaml
case-study:
  label: "CASE STUDY"
  accent: "#6f2da8"
```

The accent must be a six-digit hexadecimal color. An invalid value falls back
to `#6f2da8`. A case can override either value on its heading:

```markdown
## Worked application {#sec-worked-application .case-study data-label="APPLICATION" data-accent="#00796b"}
```

## Example

[Open the complete source example](example.qmd). It includes content before
and after the case, a nested subsection, a table, and a cross-reference to the
case heading.

Render both supported formats with:

```bash
quarto render example.qmd --to html
quarto render example.qmd --to pdf
```

The styled treatment supports Quarto HTML and PDF output. Other output formats
keep their ordinary headings and content. PDF rendering requires a LaTeX
installation with `tcolorbox`; Quarto TinyTeX installs the package when needed.

## Test

The render-contract tests create a disposable Quarto project. They confirm
that the complete section is boxed, the following section remains outside,
the stable heading identifier resolves, the stylesheet loads, and the PDF is
produced.

```bash
python -m unittest discover -s tests -v
```

## License

[MIT](LICENSE)
