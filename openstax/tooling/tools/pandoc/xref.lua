-- xref.lua -- numbering + cross-references for the pandoc HTML build.
--
-- pandoc does not run our LaTeX counters (the envs come from thmtools, which it
-- can't see) and buries equation \labels inside the math. This filter:
--   * numbers theorem/definition/example/checkpoint/... per chapter (one shared
--     counter, matching the PDF's `numberwithin=chapter` siblings) and prepends
--     "Theorem 3.2." etc.;
--   * numbers figures (calcfig) and labelled display equations per chapter;
--   * pulls each \label{} out of the div/figure/equation and onto its HTML id,
--     so cross-references land on a real target;
--   * titles the objectives/key-concepts/key-equations/project boxes;
--   * rewrites \cref links to read "Theorem 3.2" / "Figure 3.1" / "Equation (3.2)".

local NAMED = {            -- numbered, sharing the per-chapter item counter
  theorem = "Theorem", corollary = "Corollary", lemma = "Lemma",
  proposition = "Proposition", definition = "Definition",
  example = "Example", checkpoint = "Checkpoint",
}
local TITLED = {           -- titled, not numbered
  objectives = "Learning Objectives", keyconcepts = "Key Concepts",
  keyequations = "Key Equations", project = "Student Project",
}

local chapter, item, fig, eq = 0, 0, 0, 0
local labels = {}          -- label-id -> "Theorem 3.2" / "Figure 3.1" / ...

-- pandoc renders \label{x} as an (empty) Span with a `label` attribute and
-- identifier x -- already a valid anchor. Read that id (leave the span as the
-- link target) so we can record this element's number for cross-references.
local function find_label_id(el)
  local id = nil
  el:walk{
    Span = function(s)
      if id == nil and s.attributes and s.attributes.label then
        id = s.attributes.label
      end
    end,
  }
  return id
end

-- prepend a bold run-in label to a Div's first paragraph
local function prepend_head(div, text)
  local head = pandoc.Span({ pandoc.Strong(pandoc.Str(text)) }, { class = "envhead" })
  if div.content[1] and div.content[1].t == "Para" then
    table.insert(div.content[1].content, 1, pandoc.Space())
    table.insert(div.content[1].content, 1, head)
  else
    table.insert(div.content, 1, pandoc.Plain({ head, pandoc.Space() }))
  end
end

local function Header(h)
  if h.level == 1 then
    chapter = chapter + 1
    item, fig, eq = 0, 0, 0
  end
  return h
end

local function Div(d)
  local cls
  for _, c in ipairs(d.classes) do
    if NAMED[c] or TITLED[c] or c == "calcfig" then cls = c break end
  end
  if not cls then return d end

  local id = find_label_id(d)

  if NAMED[cls] then
    item = item + 1
    local num = chapter .. "." .. item
    prepend_head(d, NAMED[cls] .. " " .. num .. ".")
    if id then labels[id] = NAMED[cls] .. " " .. num end
  elseif cls == "calcfig" then
    fig = fig + 1
    local num = chapter .. "." .. fig
    -- the caption (recovered via the \captionof shim in html.sh) is the last
    -- block; prefix it with "Figure N.M.".
    local last = d.content[#d.content]
    local head = pandoc.Span({ pandoc.Strong(pandoc.Str("Figure " .. num .. ".")) },
                             { class = "envhead" })
    if last and (last.t == "Para" or last.t == "Plain") then
      table.insert(last.content, 1, pandoc.Space())
      table.insert(last.content, 1, head)
    else
      table.insert(d.content, pandoc.Plain({ head }))
    end
    if id then labels[id] = "Figure " .. num end
  elseif TITLED[cls] then
    table.insert(d.content, 1,
      pandoc.Plain({ pandoc.Span({ pandoc.Strong(pandoc.Str(TITLED[cls])) },
                                 { class = "envhead" }) }))
  end
  return d
end

-- a labelled display equation: strip \label from the math, wrap in an id'd Div,
-- and append the equation number.
local function Para(p)
  if #p.content ~= 1 or p.content[1].t ~= "Math" then return nil end
  local m = p.content[1]
  if m.mathtype ~= pandoc.DisplayMath then return nil end
  local id = m.text:match("\\label%s*{(.-)}")
  if not id then return nil end
  eq = eq + 1
  local num = chapter .. "." .. eq
  m.text = m.text:gsub("\\label%s*{.-}", "")
  labels[id] = "Equation (" .. num .. ")"
  return pandoc.Div({ pandoc.Para({ m }) }, pandoc.Attr(id, { "equation" }))
end

-- second pass: rewrite \cref links to the target's number
local function Link(l)
  local tgt = l.target:gsub("^#", "")
  if labels[tgt] then
    return pandoc.Link(pandoc.Str(labels[tgt]), l.target, l.title, l.attr)
  end
  return l
end

-- point bare image filenames at the media/ directory beside the HTML
local function Image(img)
  -- this book's SVG figures are rasterized to PNG for the web (the converter
  -- emits .pdf names for them, which pandoc can't embed); point at the .png.
  img.src = img.src:gsub("%.pdf$", ".png")
  if not img.src:match("/") then img.src = "media/" .. img.src end
  return img
end

function Pandoc(doc)
  doc = doc:walk{ traverse = "topdown", Header = Header, Div = Div, Para = Para }
  doc = doc:walk{ Link = Link, Image = Image }
  return doc
end
