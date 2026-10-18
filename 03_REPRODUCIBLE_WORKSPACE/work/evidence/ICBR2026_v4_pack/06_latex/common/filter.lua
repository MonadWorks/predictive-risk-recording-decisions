-- Template-independent pandoc Lua filter (see README.md).
-- Turns the manuscript conventions into template-neutral LaTeX:
--   * "**Fig. N | Title.** ..." paragraph after an image  -> figure / figure*
--   * "**Table N | Title.** note..." paragraph before a pipe table -> table / table*
--   * display math -> numbered equation
--   * leading "2.1 " numbers removed from headings (LaTeX numbers sections)
-- Layout constants (characters that fit in one / both columns at \small).
local COL_CHARS  = 58
local FULL_CHARS = 120
local PAD_CHARS  = 2.4   -- 2*\tabcolsep expressed in characters

local counters = { fig = 0, tab = 0, sfig = 0, eq = 0 }
local mode = 'body'

function Meta(m)
  if m.mode then mode = pandoc.utils.stringify(m.mode) end
end

local function warn(msg) io.stderr:write('md2tex(filter): WARNING: ' .. msg .. '\n') end

local function trim(s) return (s:gsub('^%s+', ''):gsub('%s+$', '')) end

local function to_tex(inlines)
  local s = pandoc.write(pandoc.Pandoc({ pandoc.Plain(inlines) }), 'latex')
  return trim(s)
end

local function cell_tex(blocks)
  local s = pandoc.write(pandoc.Pandoc(blocks), 'latex')
  s = trim(s):gsub('\n\n+', ' '):gsub('\n', ' ')
  return s
end

-- Parse a leading bold label "Fig. 3 |" / "Supplementary Fig. 2 |" / "Table 1 |".
-- Returns kind, number, title_inlines (rest of the strong), rest_inlines (after strong)
local function parse_caption(para)
  if para.t ~= 'Para' and para.t ~= 'Plain' then return nil end
  local first = para.content[1]
  if not first or first.t ~= 'Strong' then return nil end
  local label, idx = '', nil
  for i, el in ipairs(first.content) do
    if el.t == 'Str' and el.text == '|' then idx = i; break end
    label = label .. (el.t == 'Space' and ' ' or pandoc.utils.stringify(el))
  end
  if not idx then return nil end
  local kind, num
  local n = label:match('^Supplementary Fig%.%s*(%d+)%s*$')
  if n then kind, num = 'sfig', tonumber(n) end
  if not kind then
    n = label:match('^Fig%.%s*(%d+)%s*$')
    if n then kind, num = 'fig', tonumber(n) end
  end
  if not kind then
    n = label:match('^Table%s*(%d+)%s*$')
    if n then kind, num = 'tab', tonumber(n) end
  end
  if not kind then return nil end
  local title = pandoc.List()
  for i = idx + 1, #first.content do title:insert(first.content[i]) end
  while #title > 0 and (title[1].t == 'Space' or title[1].t == 'SoftBreak') do title:remove(1) end
  local rest = pandoc.List()
  for i = 2, #para.content do rest:insert(para.content[i]) end
  return kind, num, title, rest
end

local function check_number(kind, num)
  counters[kind] = counters[kind] + 1
  counters[kind .. '_num'] = num
  if counters[kind] ~= num then
    warn(string.format('%s label says %d but it is #%d in document order (LaTeX numbers automatically)',
      kind, num, counters[kind]))
  end
end

local function single_image(block)
  if (block.t == 'Para' or block.t == 'Plain') and #block.content == 1 and block.content[1].t == 'Image' then
    return block.content[1]
  end
end

local function figure_tex(img, cap_tex, kind)
  local wide = false
  for _, c in ipairs(img.classes) do if c == 'wide' then wide = true end end
  local env = wide and 'figure*' or 'figure'
  local w = wide and '\\textwidth' or '\\columnwidth'
  local out = { '\\begin{' .. env .. '}[!t]', '\\centering',
    '\\includegraphics[width=' .. w .. ']{' .. img.src .. '}' }
  if cap_tex then
    table.insert(out, '\\setcounter{figure}{' .. (counters[kind .. '_num'] - 1) .. '}')
    table.insert(out, '\\caption{' .. cap_tex .. '}')
    table.insert(out, '\\label{' .. (kind == 'sfig' and 'sfig:' or 'fig:') .. counters[kind .. '_num'] .. '}')
  end
  table.insert(out, '\\end{' .. env .. '}')
  return pandoc.RawBlock('latex', table.concat(out, '\n'))
end

local function longest_word(s)
  local m = 0
  for w in s:gmatch('%S+') do if utf8.len(w) and utf8.len(w) > m then m = utf8.len(w) end end
  return m
end

local function table_tex(tbl, kind, title, note)
  local ncol = #tbl.colspecs
  local header, rows = {}, {}
  local function collect(rowlist, dest)
    for _, r in ipairs(rowlist) do
      local cells = {}
      for j, c in ipairs(r.cells) do
        cells[j] = { tex = cell_tex(c.contents), txt = trim(pandoc.utils.stringify(c.contents)) }
      end
      table.insert(dest, cells)
    end
  end
  collect(tbl.head.rows, header)
  for _, b in ipairs(tbl.bodies) do collect(b.body, rows) end

  local aligns, maxlen, minw, demand = {}, {}, {}, {}
  local bodymax, nobreak, hdrlen, hdrword = {}, {}, {}, {}
  for j = 1, ncol do
    local a = tbl.colspecs[j][1]
    aligns[j] = (a == 'AlignRight') and 'r' or (a == 'AlignCenter') and 'c' or 'l'
    maxlen[j], minw[j] = 0, 0
    bodymax[j], nobreak[j], hdrlen[j], hdrword[j] = 0, 0, 0, 0
  end
  local function measure(list)
    for _, cells in ipairs(list) do
      for j = 1, ncol do
        local c = cells[j]
        if c then
          local L = utf8.len(c.txt) or #c.txt
          if L > maxlen[j] then maxlen[j] = L end
          local lw = longest_word(c.txt)
          if lw > minw[j] then minw[j] = lw end
        end
      end
    end
  end
  measure(header); measure(rows)
  for _, cells in ipairs(header) do
    for j = 1, ncol do
      if cells[j] then
        hdrlen[j] = math.max(hdrlen[j], utf8.len(cells[j].txt) or #cells[j].txt)
        hdrword[j] = math.max(hdrword[j], longest_word(cells[j].txt))
      end
    end
  end
  for _, cells in ipairs(rows) do
    for j = 1, ncol do
      if cells[j] then
        local L = utf8.len(cells[j].txt) or #cells[j].txt
        bodymax[j] = math.max(bodymax[j], L)
        if L <= 30 then nobreak[j] = math.max(nobreak[j], L) end
      end
    end
  end
  local natural = 0
  for j = 1, ncol do natural = natural + maxlen[j] + PAD_CHARS end

  local wide, mode_p = false, false
  if natural <= COL_CHARS then
    wide, mode_p = false, false
  elseif natural <= FULL_CHARS then
    wide, mode_p = true, false
  else
    wide, mode_p = true, true
  end

  local colspec, fracs = {}, {}
  if mode_p then
    local avail = FULL_CHARS - ncol * PAD_CHARS
    for j = 1, ncol do
      minw[j] = math.max(hdrword[j], nobreak[j])
      maxlen[j] = math.max(bodymax[j], math.min(hdrlen[j], math.max(hdrword[j], 16)), minw[j])
    end
    local sumdem, summin = 0, 0
    for j = 1, ncol do sumdem = sumdem + maxlen[j]; summin = summin + minw[j] end
    local w = {}
    if sumdem <= avail then
      for j = 1, ncol do w[j] = maxlen[j] end
      local extra = (avail - sumdem) / ncol
      for j = 1, ncol do w[j] = w[j] + extra end
    else
      local spare = math.max(avail - summin, 0)
      local want = 0
      for j = 1, ncol do want = want + (maxlen[j] - minw[j]) end
      for j = 1, ncol do
        w[j] = minw[j] + (want > 0 and spare * (maxlen[j] - minw[j]) / want or 0)
      end
    end
    local tot = 0
    for j = 1, ncol do tot = tot + w[j] end
    for j = 1, ncol do
      local f = w[j] / tot
      local ra = (aligns[j] == 'r') and '\\raggedleft\\arraybackslash'
          or (aligns[j] == 'c') and '\\centering\\arraybackslash' or '\\raggedright\\arraybackslash'
      colspec[j] = string.format('>{%s}p{%.4f\\tblw}', ra, f)
    end
  else
    for j = 1, ncol do colspec[j] = aligns[j] end
  end

  local lines = {}
  local function emit(list)
    for _, cells in ipairs(list) do
      local t = {}
      for j = 1, ncol do t[j] = cells[j] and cells[j].tex or '' end
      table.insert(lines, table.concat(t, ' & ') .. ' \\\\')
    end
  end
  table.insert(lines, '\\toprule')
  if #header > 0 then emit(header); table.insert(lines, '\\midrule') end
  emit(rows)
  table.insert(lines, '\\bottomrule')

  local out = {}
  local env = wide and 'table*' or 'table'
  local captioned = title ~= nil
  local float = captioned or wide
  if float then table.insert(out, '\\begin{' .. env .. '}[!t]') else table.insert(out, '\\begin{center}') end
  if captioned then
    table.insert(out, '\\setcounter{table}{' .. (counters.tab_num - 1) .. '}')
    table.insert(out, '\\caption{' .. title .. '}')
    table.insert(out, '\\label{tab:' .. counters.tab_num .. '}')
  end
  table.insert(out, '\\centering\\small')
  if mode_p then
    table.insert(out, string.format('\\setlength{\\tblw}{\\dimexpr\\textwidth-%d\\tabcolsep\\relax}', 2 * ncol))
    table.insert(out, '\\begin{tabular}{' .. table.concat(colspec) .. '}')
  elseif wide then
    table.insert(out, '\\begin{tabular*}{\\textwidth}{@{\\extracolsep{\\fill}}' .. table.concat(colspec) .. '}')
  else
    table.insert(out, '\\begin{tabular}{' .. table.concat(colspec) .. '}')
  end
  for _, l in ipairs(lines) do table.insert(out, l) end
  table.insert(out, (wide and not mode_p) and '\\end{tabular*}' or '\\end{tabular}')
  if note and note ~= '' then
    table.insert(out, '\\par\\vspace{3pt}{\\footnotesize\\raggedright\\setlength{\\parindent}{0pt}' .. note .. '\\par}')
  end
  if float then table.insert(out, '\\end{' .. env .. '}') else table.insert(out, '\\end{center}') end
  return pandoc.RawBlock('latex', table.concat(out, '\n'))
end

local function strip_trailing_period(inls)
  local n = #inls
  if n > 0 and inls[n].t == 'Str' then
    inls[n].text = inls[n].text:gsub('%.$', '')
  end
  return inls
end

function Blocks(blocks)
  local out = pandoc.List()
  local i = 1
  while i <= #blocks do
    local b = blocks[i]
    local img = single_image(b)
    if img then
      local nxt = blocks[i + 1]
      local kind, num, title, rest
      if nxt then kind, num, title, rest = parse_caption(nxt) end
      if kind == 'fig' or kind == 'sfig' then
        check_number(kind, num)
        local cap = pandoc.List()
        if #title > 0 then cap:insert(pandoc.Strong(title)) end
        if #rest > 0 then
          cap:insert(pandoc.Space())
          cap:extend(rest)
        end
        out:insert(figure_tex(img, to_tex(cap), kind))
        i = i + 2
      else
        out:insert(figure_tex(img, nil, 'fig'))
        i = i + 1
      end
    elseif b.t == 'Para' and parse_caption(b) and select(1, parse_caption(b)) == 'tab'
        and blocks[i + 1] and blocks[i + 1].t == 'Table' then
      local _, num, title, rest = parse_caption(b)
      check_number('tab', num)
      title = strip_trailing_period(title)
      local note = ''
      if #rest > 0 then
        while #rest > 0 and (rest[1].t == 'Space' or rest[1].t == 'SoftBreak') do rest:remove(1) end
        note = to_tex(rest)
      end
      out:insert(table_tex(blocks[i + 1], 'tab', to_tex(title), note))
      i = i + 2
    elseif b.t == 'Table' then
      out:insert(table_tex(b, nil, nil, nil))
      i = i + 1
    else
      out:insert(b)
      i = i + 1
    end
  end
  return out
end

function Para(p)
  if #p.content == 1 and p.content[1].t == 'Math' and p.content[1].mathtype == 'DisplayMath' then
    counters.eq = counters.eq + 1
    local m = p.content[1].text
    local body = m
    if m:find('\\\\', 1, true) and not m:find('\\begin') then
      body = '\\begin{aligned}\n' .. m .. '\n\\end{aligned}'
    end
    return pandoc.RawBlock('latex', '\\begin{equation}\n' .. body .. '\n\\end{equation}')
  end
end

function Header(h)
  local c = h.content
  if #c > 0 and c[1].t == 'Str' and c[1].text:match('^%d+[%.%d]*%.?$') then
    c:remove(1)
    while #c > 0 and c[1].t == 'Space' do c:remove(1) end
    h.content = c
    return h
  end
end

-- Meta must run first, then Blocks (so figures/tables are built before Para sees math)
return {
  { Meta = Meta },
  { Blocks = Blocks },
  { Para = Para, Header = Header },
}
