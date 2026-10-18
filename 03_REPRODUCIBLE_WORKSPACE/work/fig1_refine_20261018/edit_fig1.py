from pathlib import Path
p=Path('outputs/pastel_figure_suite/render_schematic_extension.py');s=p.read_text()
start=s.index("        if node.name=='audit_schematic':")
end=s.index('        exec(code,ns)',start)
block='''        if node.name=='audit_schematic':
            code=refine_audit(code)
'''
s=s[:start]+block+s[end:]
helper=r'''
def refine_audit(code):
    code=code.replace("fc='#E3E8EC', ec='#B4BDC5'", "fc='#FBEAF1', ec='#EAB8CC'")
    code=code.replace("'fig_audit_schematic_v5'", "'fig1_audit'")
    a=code.index('    # layer 2 box');b=code.index('    # "cannot differ" arrow',a)
    code=code[:a]+"""    # Compact, aligned result block; frozen values are unchanged.
    box(base, 148, 42, 177, 77, fc=PANEL)
    arrow(base, (143, ym), (148, ym))
    T(155, 72.5, 'Response error', va='baseline')
    T(150.5, 68.2, 'Predicted vs true response', va='center')
    T(150.5, 63.0, 'Single response', va='center')
    T(174.5, 63.0, f'{eff['scalar'][0]:+.1f}%'.replace('-', '−'), ha='right', va='center')
    T(174.5, 59.5, f'[{eff['scalar'][1]:+.1f}, {eff['scalar'][2]:+.1f}]'.replace('-', '−'), ha='right', va='center')
    T(150.5, 54.5, 'Shared response', va='center')
    T(174.5, 54.5, f'{eff['vector'][0]:+.1f}%'.replace('-', '−'), ha='right', va='center')
    T(174.5, 51.0, f'[{eff['vector'][1]:+.1f}, {eff['vector'][2]:+.1f}]'.replace('-', '−'), ha='right', va='center')
    T(150.5, 45.5, '97.5% CIs include zero', va='center')
    badge(base, 148, 77, 2)

"""+code[b:]
    a=code.index('    # "cannot differ" arrow');b=code.index('    # lower row',a);code=code[:a]+code[b:]
    a=code.index('    # lower row');b=code.index('    # key insight (left lower)',a)
    code=code[:a]+"""    # The lower forecast box shares x=87 with the recording-agreement box.
    box(base, 87, 8, 143, 38)
    arrow(base, (133.5, 49), (133.5, 38.5))
    T(90, 33.4, 'Risk forecasts and squared error', va='baseline')
    T(90, 29.4, 'Fixed point prediction; different risk estimates', va='center')
    for nm, yy, width, col in [('Forecast risk, v', 23.3, 19, VECTOR), ('Squared error, e²', 17.4, 25, '#B5708C')]:
        T(90, yy, nm, va='center')
        base.add_patch(Rectangle((115, yy-1.2), width, 2.4, fc=col, ec='none', zorder=4))
    T(90, 11.0, 'Illustrative quantities; compared by the score', va='center')

    box(base, 148, 8, 177, 38, fc=PANEL)
    arrow(base, (143, 23), (148, 23))
    T(155, 33.2, 'Forecast score', va='baseline')
    T(162.5, 28.1, 'log v + e²/v', ha='center', va='center')
    T(162.5, 24.9, 'Lower is better', ha='center', va='center')
    T(150.5, 20.8, f'{SCORE[0]:+.2f}'.replace('-', '−'), va='center')
    T(150.5, 17.2, f'[{SCORE[1]:+.2f}, {SCORE[2]:+.2f}]'.replace('-', '−'), va='center')
    T(150.5, 13.5, '95% CI includes zero', va='center')
    T(150.5, 10.2, 'Lower score in 19/40 networks', va='center')
    badge(base, 148, 38, 3)

"""+code[b:]
    a=code.index('    # key insight (left lower)');b=code.index('    export(fig,',a)
    code=code[:a]+"""    T(7, 31.5, '1  Recording agreement', va='baseline')
    T(10, 25.5, 'The same observations and a common deterministic fit\\nproduce identical point predictions.', va='center', linespacing=1.25)
    T(7, 18.5, '2  Risk assessment', va='baseline')
    T(10, 12.5, 'With the point prediction fixed, score each risk estimate\\nagainst the realised squared error.', va='center', linespacing=1.25)
"""+code[b:]
    return code

'''
s=s.replace('# Rebind original functions',helper+'# Rebind original functions')
s=s.replace("'Risk forecast v vs realised error e','Single-response objective'","'Risk forecast v vs realised error e','Risk forecasts and squared error','1  Recording agreement','2  Risk assessment','Single-response objective'")
# Keep the original two-family palette elsewhere; only the illustrative pair is pink.
s=s.replace("elif value in categories or value.startswith(('All sites,','No endpoints,')):","elif value in categories or value.startswith(('All sites,','No endpoints,','Endpoints excluded,')):")
# Extra result formatting and bounds check happen after the general font assignments.
anchor="    for ext in ('pdf','svg','png'):"
inject=r'''    if stem=='fig1_audit':
        import re,json
        base=fig.axes[0]
        for text in fig.findobj(Text):
            v=text.get_text()
            if v in ('Single response','Shared response'):
                text.set_fontsize(6);text.set_color('#49424B')
            if re.match(r'^[+−-]\d',v) or v.startswith('['):
                text.set_fontfamily('JuliaMono');text.set_fontsize(6);text.set_color('#2E2531')
            if v in ('Forecast risk, v','Squared error, e²'):
                text.set_fontsize(6.4);text.set_color('#49424B')
            if v=='log v + e²/v':
                text.set_fontfamily('Times New Roman');text.set_fontsize(6.8);text.set_color('#49424B')
        fig.canvas.draw();renderer=fig.canvas.get_renderer();issues=[];bounds=[]
        for text in base.texts:
            x,y=text.get_position();container=None
            if 148<=x<=177 and 42<=y<=77:container=(148,42,177,77)
            elif 148<=x<=177 and 8<=y<=38:container=(148,8,177,38)
            elif 87<=x<=143 and 8<=y<=38:container=(87,8,143,38)
            if container:
                b=text.get_window_extent(renderer).transformed(base.transData.inverted())
                got=[b.x0,b.y0,b.x1,b.y1];bounds.append({'text':text.get_text(),'bounds_mm':got,'container_mm':container})
                if b.x0<container[0]+.4 or b.x1>container[2]-.4 or b.y0<container[1]+.3 or b.y1>container[3]-.3:issues.append(text.get_text())
        assert not issues,('text exceeds panel',issues)
        (OUT/'fig1_layout_audit.json').write_text(json.dumps({'panel_text_bounds':bounds,'panel_overflow':issues,'aligned_box_left_edges_mm':[87,87],'estimated_intervals_unchanged':True},indent=2))
'''
s=s.replace(anchor,inject+anchor)
p.write_text(s)
