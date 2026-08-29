local DEFAULT_LABEL = "CASE STUDY"
local DEFAULT_ACCENT = "6F2DA8"

local function has_class(element, class_name)
  for _, class in ipairs(element.classes) do
    if class == class_name then
      return true
    end
  end
  return false
end

local function metadata_string(value, fallback)
  if value == nil then
    return fallback
  end

  local text = pandoc.utils.stringify(value)
  if text == "" then
    return fallback
  end

  return text
end

local function normalize_accent(value, fallback)
  local candidate = metadata_string(value, fallback)
  local hexadecimal = candidate:match("^#?([0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F])$")

  if hexadecimal == nil then
    return fallback
  end

  return hexadecimal:upper()
end

local function latex_text(text)
  local document = pandoc.Pandoc({
    pandoc.Plain({pandoc.Str(text)})
  })
  return pandoc.write(document, "latex"):gsub("%s+$", "")
end

local function case_options(meta, header)
  local config = meta["case-study"] or {}
  local label = metadata_string(config.label, DEFAULT_LABEL)
  local accent = normalize_accent(config.accent, DEFAULT_ACCENT)

  if header.attributes["data-label"] ~= nil then
    label = metadata_string(header.attributes["data-label"], label)
  end

  if header.attributes["data-accent"] ~= nil then
    accent = normalize_accent(header.attributes["data-accent"], accent)
  end

  return label, accent
end

local function latex_case(blocks, label, accent)
  local output = pandoc.List({
    pandoc.RawBlock(
      "latex",
      "\\begin{caseStudyBox}{" .. accent .. "}\n" ..
      "\\caseStudyLabel{" .. latex_text(label) .. "}"
    )
  })

  output:extend(blocks)
  output:insert(pandoc.RawBlock("latex", "\\end{caseStudyBox}"))
  return output
end

local function add_style(header, declaration)
  local existing = header.attributes.style or ""
  if existing ~= "" and not existing:match(";%s*$") then
    existing = existing .. ";"
  end
  header.attributes.style = existing .. declaration
end

local function decorate_html_cases(blocks, meta)
  local output = pandoc.List()

  for _, block in ipairs(blocks) do
    output:insert(block)

    if block.t == "Header" and has_class(block, "case-study") then
      local label, accent = case_options(meta, block)
      block.attributes["data-case-study-label"] = label
      add_style(block, "--case-study-accent: #" .. accent .. ";")
      output:insert(
        pandoc.Div(
          {pandoc.Plain({pandoc.Str(label)})},
          pandoc.Attr("", {"case-study-label"})
        )
      )
    end
  end

  return output
end

local function wrap_latex_cases(blocks, meta)
  local output = pandoc.List()
  local index = 1

  while index <= #blocks do
    local block = blocks[index]

    if block.t == "Header" and has_class(block, "case-study") then
      local case_level = block.level
      local case_blocks = pandoc.List({block})
      local label, accent = case_options(meta, block)
      index = index + 1

      while index <= #blocks do
        local next_block = blocks[index]
        if next_block.t == "Header" and next_block.level <= case_level then
          break
        end

        case_blocks:insert(next_block)
        index = index + 1
      end

      output:extend(latex_case(case_blocks, label, accent))
    else
      output:insert(block)
      index = index + 1
    end
  end

  return output
end

function Pandoc(document)
  if quarto.doc.is_format("html") or FORMAT:match("html") then
    quarto.doc.add_html_dependency({
      name = "quarto-case-study",
      version = "0.1.0",
      stylesheets = {"case-study.css"}
    })
    document.blocks = decorate_html_cases(document.blocks, document.meta)
  elseif quarto.doc.is_format("latex") or FORMAT:match("latex") then
    quarto.doc.include_file("in-header", "case-study.tex")
    document.blocks = wrap_latex_cases(document.blocks, document.meta)
  end

  return document
end
