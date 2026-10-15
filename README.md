# Quarto Case Study

Quarto Case Study gives a complete example or case study a visible beginning
and end. Add `.case-study` to a heading, and the extension places that heading
and its contents inside one box. The box ends at the next heading of the same
or a higher level.

The heading keeps its identifier, table-of-contents entry, and cross-reference
target. HTML output uses a semantic section with a subtle background, a thin
border, and a 4 px accent rule. Non-HTML formats pass through unchanged.

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

By default, cases inherit their accent from the host page's CSS.
The extension uses `--case-study-accent` when available, then the Bootstrap
`--bs-primary` color, and finally `#6f2da8` for a page without either variable.
It adds no inline accent when the metadata does not specify one.

Set the default label and an optional explicit accent in document or project metadata:

```yaml
case-study:
  label: "CASE STUDY"
  accent: "#6f2da8"
```

An explicit accent must be a six-digit hexadecimal color, with an optional
leading `#`.
An invalid or empty accent uses the host CSS fallback instead of adding an
inline value.
A case can override either value on its heading:

```markdown
## Worked application {#sec-worked-application .case-study data-label="APPLICATION" data-accent="#00796b"}
```

An explicit valid heading accent takes precedence over a metadata accent.
An invalid heading accent falls back to the host CSS, even if the metadata has
a valid accent.
Existing author-supplied inline styles are preserved.

### CSS hooks

Set these variables on the page, a surrounding container, or an individual
case.
They are consumed by the separate `case-study.css` stylesheet; the Lua filter
only adds the label and an optional validated accent.

```css
:root {
  --case-study-accent: var(--bs-primary);
  --case-study-background: var(--bs-body-bg);
  --case-study-border-color: var(--bs-border-color);
  --case-study-heading-color: var(--bs-heading-color);
  --case-study-label-color: var(--bs-primary);
}
```

| Variable | Treatment when the variable is absent |
|---|---|
| `--case-study-accent` | Bootstrap primary, then `#6f2da8`; controls the left rule and default tint |
| `--case-study-background` | Subtle accent tint over the host `--paper` or Bootstrap body background |
| `--case-study-border-color` | Accent-tinted host `--line` or Bootstrap border color |
| `--case-study-heading-color` | Host `--accent-strong`, otherwise a darker accent |
| `--case-study-label-color` | Host `--accent-strong`, otherwise a darker accent |

The extension does not redeclare the accent on each case, so inherited theme
variables remain effective.
Explicit metadata or heading accents are inline overrides for that case.
Print output retains the monochrome treatment.

## Example

[Open the complete source example](example.qmd). It includes content before
and after the case, a nested subsection, a table, and a cross-reference to the
case heading.

Render the example with:

```bash
quarto render example.qmd --to html
```

The styled treatment supports Quarto HTML output. Other output formats keep
their ordinary headings and content.

## Test

The render-contract tests create a disposable Quarto project. They confirm
that the complete section is boxed, the following section remains outside,
the stable heading identifier resolves, and the stylesheet loads.
They also render host-theme, metadata, per-heading, and invalid-accent cases,
and check that non-HTML output keeps the original content and identifiers.

```bash
python -m unittest discover -s tests -v
```

## License

[MIT](LICENSE)
