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

function Pandoc(document)
  if quarto.doc.is_format("html") or FORMAT:match("html") then
    quarto.doc.add_html_dependency({
      name = "quarto-case-study",
      version = "0.2.0",
      stylesheets = {"case-study.css"}
    })
    document.blocks = decorate_html_cases(document.blocks, document.meta)
  end

  return document
end
