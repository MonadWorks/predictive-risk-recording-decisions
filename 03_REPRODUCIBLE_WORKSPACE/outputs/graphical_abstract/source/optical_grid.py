def optical_grid(fig,base):
    from matplotlib.text import Text
    from matplotlib.patches import Circle,FancyBboxPatch,FancyArrowPatch
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    import numpy as np
    ink='#2E2531';muted='#655D69'
    rails={1:59.3,2:101.3,3:143.3}
    # Preserve the bold/light title pair; tighten the two-line lockup.
    for t in fig.findobj(Text):
        v=t.get_text()
        if v=='Predictive risk and recording decisions':
            t.set_text('Predictive risk and recording decisions')
            t.set_fontfamily('BentonSans');t.set_fontweight('bold');t.set_fontsize(26.0);t.set_position((8,126.6))
        elif v=='in partially observed neural networks':t.set_visible(True);t.set_fontfamily('BentonSans');t.set_fontweight('normal');t.set_fontsize(19.5);t.set_position((8,120.1))
        elif v.startswith('Nominal versus prior-averaged local risk for'):
            t.set_visible(False)
        elif v in ['1','2','3']:t.set_visible(False)
        elif v in ['Recording agreement','Response error','Risk forecasts']:
            i={'Recording agreement':1,'Response error':2,'Risk forecasts':3}[v]
            t.set_text(v);t.set_position((rails[i]+2.75,103.9));t.set_va('baseline');t.set_ha('left')
            base.text(rails[i]+1.35,103.9,str(i),fontsize=9.5,fontweight='bold',fontfamily='BentonSans',color=ink,ha='right',va='baseline')
            t.set_fontfamily('BentonSans');t.set_fontsize(9.5);t.set_fontweight('bold')
    for patch in base.patches:
        if isinstance(patch,FancyBboxPatch):
            patch.set_boxstyle('round,pad=0,rounding_size=1.2');patch.set_linewidth(.6)
            if patch.get_y()<30 and patch.get_x()>50:patch.set_facecolor('#F7F5F6')
    for line in base.lines:
        if len(line.get_xdata())==2 and list(line.get_xdata())==[8,182]:line.set_xdata([8,180.5])
    # Common insets and real baseline rails for the meta lines.
    for t in list(base.texts):
        v=t.get_text();x,y=t.get_position()
        if '\n' in v and (v.startswith('Nominal vs ') or v.startswith('Common MAP ') or v.startswith('Fixed data ')):
            i=1 if v.startswith('Nominal vs ') else 2 if v.startswith('Common MAP ') else 3
            lines=v.splitlines();lines[0]=lines[0].replace('local risk','risk')
            if i==1:
                t.set_text('40 independent networks');t.set_position((rails[i],100.6));t.set_va('baseline');t.set_fontsize(8.1)
                continue
            t.set_text(lines[0]);t.set_position((rails[i],100.6));t.set_va('baseline');t.set_ha('left');t.set_fontsize(8.1)
            base.text(rails[i],97.9,lines[1],fontsize=8.1,fontfamily='BentonSans',color=muted,va='baseline')
        elif v=='known connectivity' or v=='uncertain physiology':t.set_visible(False)
        elif v=='12 simulated units · M=3':
            t.set_text('12 simulated units · M=3');t.set_fontsize(8.6)
        elif v=='Known connectivity; uncertain physiology':
            t.set_text('Uncertain gains and biases');t.set_fontsize(8.1)
        if v=='q' and x>45:t.set_position((50.6,74.5))
    base.text(30,86.2,'Known\nconnectivity',fontsize=8.8,fontfamily='BentonSans',color=muted,ha='center',va='center',linespacing=1.12,bbox=dict(facecolor='#FEFDFC',edgecolor='none',pad=.6,alpha=.92))
    # Baselines, not centre alignment, for the number+description groups.
    key={}
    for t in fig.findobj(Text):
        v=t.get_text()
        if v in ['68%','65%','19']:
            i=3 if v=='19' else 1;y=93.6 if v=='19' else 89.8 if v=='68%' else 58.8
            t.set_position((rails[i],y));t.set_va('baseline');t.set_ha('left');t.set_fontsize(16);t.set_fontfamily('BentonSans');t.set_fontweight('bold');key[v]=t
    base.text(rails[1],95.0,'Single-response designs',fontsize=8.3,fontweight='bold',fontfamily='BentonSans',color='#A34E79',va='baseline')
    base.text(rails[1],64.0,'Shared three-response designs',fontsize=8.3,fontweight='bold',fontfamily='BentonSans',color='#65566F',va='baseline')
    fig.canvas.draw();r=fig.canvas.get_renderer()
    gap=1.7/1.3684210526
    end={v:base.transData.inverted().transform((t.get_window_extent(r).x1,0))[0]+gap for v,t in key.items()}
    tops={v:base.transData.inverted().transform((0,t.get_window_extent(r).y1))[1] for v,t in key.items()}
    for t in fig.findobj(Text):
        v=t.get_text()
        if v.startswith('82 of 120'):t.set_text('82 of 120 designs');t.set_position((end['68%'],tops['68%']));t.set_va('top');t.set_fontsize(8.0)
        elif v.startswith('26 of 40'):t.set_text('26 of 40 designs');t.set_position((end['65%'],tops['65%']));t.set_va('top');t.set_fontsize(8.0)
        elif v=='designs are identical':
            oldy=t.get_position()[1];isfirst=oldy>70
            t.set_text('identical recording sets');t.set_position((end['68%' if isfirst else '65%'],tops['68%' if isfirst else '65%']-2.8));t.set_va('top');t.set_fontsize(8.0)
        elif v=='of 40 favour prior averaging;':t.set_position((end['19'],tops['19']));t.set_va('top');t.set_fontsize(8.0)
        elif v=='21 favour nominal':t.set_position((end['19'],tops['19']-2.8));t.set_va('top');t.set_fontsize(8.0)
        elif v=='same recording set':t.set_position((rails[1]+2.8,41.2));t.set_fontsize(7.2)
    # Clear whitespace around the dot grids, retaining all 120 and 40 markers.
    for p in base.patches:
        if isinstance(p,Circle):
            x,y=p.center
            if abs(p.get_radius()-.85)<.01 and x<97:
                if y>65:p.set_radius(.78);p.center=(rails[1]+.78+round((x-59)/2.3)*((34.4-1.56)/14),86.5-round((83.4-y)/2.3)*1.8)
                elif 48<y<57:p.set_radius(.78);p.center=(rails[1]+.78+round((x-59)/2.3)*((34.4-1.56)/14),53.8-round((55.4-y)/2.3)*2.05)
            elif abs(p.get_radius()-.85)<.01 and abs(y-41.4)<.01:p.center=(rails[1]+.78,41.2)
    # Move the original network, not its source weights or its topology.
    for p in base.patches:
        if isinstance(p,Circle) and p.get_radius()>=2.45:
            x,y=p.center;p.center=(x,y+1.0)
        elif isinstance(p,FancyArrowPatch) and p._posA_posB is not None:
            a,b=p._posA_posB;p.set_positions(np.asarray(a)+[0,1.0],np.asarray(b)+[0,1.0])
    # Plot regions share the card inset and axis baseline.
    for i,a in enumerate(fig.axes[1:],2):
        pos=a.get_position();a.set_position([rails[i]/190,pos.y0,34.4/190,36/135 if i==2 else pos.height])
    # Per-group spacing: heading -> value -> CI, same left rail.
    for t in fig.findobj(Text):
        v=t.get_text()
        if v=='Single response':t.set_transform(base.transData);t.set_position((rails[2],95.0));t.set_va('baseline');t.set_fontsize(8.8)
        elif v=='Shared three-response':t.set_transform(base.transData);t.set_position((rails[2],72.0));t.set_va('baseline');t.set_fontsize(8.8)
        elif v.startswith('−3.7%'):t.set_transform(base.transData);t.set_position((rails[2],91.5));t.set_va('baseline')
        elif v.startswith('+2.7%'):t.set_transform(base.transData);t.set_position((rails[2],68.5));t.set_va('baseline')
        elif v=='MSE-forecast score difference':t.set_text('Forecast-score difference');t.set_transform(base.transData);t.set_position((rails[3],66.0));t.set_va('baseline');t.set_fontsize(8.8)
        elif v.startswith('−0.46'):t.set_transform(base.transData);t.set_position((rails[3],62.5));t.set_va('baseline')
        elif v.startswith('$S(v,e)'):t.set_position((rails[3],84.4));t.set_fontsize(11.2);t.set_color(ink)
        elif v.startswith('v: MSE forecast;'):
            t.set_position((rails[3],78.6));t.set_va('baseline');t.set_fontsize(7.4)
        elif v.startswith('One network contributes'):
            t.set_text('One network accounts for 64%\nof the summed score difference')
            t.set_position((rails[3],76.2));t.set_va('top');t.set_fontsize(7.4);t.set_linespacing(1.15)
    # Shift CI marks only, retaining the same numerical x coordinates/scales.
    for i,a in enumerate(fig.axes[1:],2):
        p=a.get_position();lo,hi=a.get_ylim()
        def unit(y):return p.y0*135+(y-lo)/(hi-lo)*p.height*135
        for line in a.lines:
            yy=np.asarray(line.get_ydata(),dtype=float)
            if not len(yy):continue
            mean=unit(float(yy.mean()))
            target=(86.5 if mean>70 else 63.5) if i==2 else 58.0
            delta=(target-mean)/(p.height*135)*(hi-lo)
            line.set_ydata(yy+delta)
    # Compact network key: smaller type, equal row pitch, actual glyph-centred markers.
    legend_y={'Recorded node':50.5,'Stimulated node':46.1,'Response readout (one shown)':41.7}
    for t in fig.findobj(Text):
        v=t.get_text()
        if v in legend_y:
            ink_box=TextPath((0,0),v,size=8.2,prop=FontProperties(family='BentonSans')).get_extents()
            units_per_pt=190/(fig.get_figwidth()*72)
            baseline=legend_y[v]-(ink_box.y0+ink_box.y1)/2*units_per_pt
            if v=='Response readout (one shown)':baseline-=.12
            t.set_position((12.3,baseline));t.set_fontsize(8.2);t.set_va('baseline')
        elif v=='12 simulated units · M=3':t.set_y(58.7)
        elif v=='Uncertain gains and biases':t.set_y(55.5)
        elif v.startswith('Blue: positive;'):t.set_visible(False)
        elif v=='Integrated stimulus response':
            t.set_fontweight('normal');t.set_fontsize(9.0);t.set_y(31.4)
        elif v.endswith('paired network-cluster CI'):
            i=2 if v.startswith('97.5') else 3
            t.set_x(rails[i]);t.set_fontsize(7.0)
    for line in base.lines:
        if len(line.get_xdata())==2 and list(line.get_xdata())==[8,180.5]:line.set_ydata([115.5,115.5])
    for i in (1,2,3):
        divider=43.8
        base.plot([rails[i],rails[i]+34.4],[divider,divider],color='#DED5DC',lw=.45,zorder=2)
    fig.canvas.draw();renderer=fig.canvas.get_renderer()
    # Visually centre key circles on glyph bounds, rather than text anchor boxes.
    textkeys={t.get_text():t for t in base.texts if t.get_visible()}
    for p in base.patches:
        if isinstance(p,Circle) and abs(p.get_radius()-1.45)<.01:
            oldy=p.center[1]
            label='Recorded node' if oldy>47 else 'Stimulated node' if oldy>42 else 'Response readout (one shown)'
            p.center=(9.3,legend_y[label]);p.set_radius(1.25)
        elif isinstance(p,Circle) and abs(p.get_radius()-.85)<.01 and 40<p.center[1]<43:
            b=textkeys['same recording set'].get_window_extent(renderer)
            cy=base.transData.inverted().transform((0,(b.y0+b.y1)/2))[1]
            p.center=(rails[1]+.78,cy)
    # Equal whitespace between whole information groups, independently in each card.
    from matplotlib.lines import Line2D
    fig.canvas.draw();renderer=fig.canvas.get_renderer()
    T={t.get_text():t for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()}
    def named(*names):return [T[n] for n in names]
    def bounds(artists):
        boxes=[base.transData.inverted().transform(a.get_window_extent(renderer).get_points()) for a in artists]
        return min(b[0,1] for b in boxes),max(b[1,1] for b in boxes)
    def shift(artists,dy):
        for a in artists:
            if isinstance(a,Text):a.set_y(a.get_position()[1]+dy)
            elif isinstance(a,Circle):a.center=(a.center[0],a.center[1]+dy)
            elif isinstance(a,Line2D):
                ax=a.axes;lo,hi=ax.get_ylim();a.set_ydata(np.asarray(a.get_ydata(),dtype=float)+dy/(ax.get_position().height*135)*(hi-lo))
    header=[named('1','Recording agreement','40 independent networks'),named('2','Response error','Common MAP fit and budget','Same 40 networks'),named('3','Risk forecasts','Fixed data and point prediction','40 new independent networks')]
    dots=[p for p in base.patches if isinstance(p,Circle) and abs(p.get_radius()-.78)<.01]
    a1=named('Single-response designs','68%','82 of 120 designs')+[t for t in base.texts if t.get_text()=='identical recording sets' and t.get_position()[1]>70]+[p for p in dots if p.center[1]>65]
    a2=named('Shared three-response designs','65%','26 of 40 designs')+[t for t in base.texts if t.get_text()=='identical recording sets' and t.get_position()[1]<70]+[p for p in dots if p.center[1]<65]
    # The value/description block clears its own dot grid by the same distance.
    for group in [a1,a2]:
        labels=[a for a in group if isinstance(a,Text)]
        markers=[a for a in group if isinstance(a,Circle)]
        dy=bounds(labels)[0]-2.0-bounds(markers)[1]
        shift(markers,dy)
    fig.canvas.draw();renderer=fig.canvas.get_renderer()
    ax=fig.axes[1]
    high=[];low=[]
    for line in ax.lines:
        page_y=base.transData.inverted().transform(ax.transData.transform((0,float(np.mean(line.get_ydata())))))[1]
        (high if page_y>75 else low).append(line)
    a3=named('Single response')+[t for t in fig.findobj(Text) if t.get_text().startswith('−3.7%')]+high
    a4=named('Shared three-response')+[t for t in fig.findobj(Text) if t.get_text().startswith('+2.7%')]+low
    a5=named('19','of 40 favour prior averaging;','21 favour nominal')
    a6=[t for t in base.texts if t.get_text().startswith(('$S(v,e)','v: MSE forecast;','One network accounts'))]
    a7=named('Forecast-score difference')+[t for t in fig.findobj(Text) if t.get_text().startswith('−0.46')]+list(fig.axes[2].lines)
    spacing={}
    for i,groups in enumerate([[a1,a2],[a3,a4],[a5,a6,a7]]):
        header_bottom=bounds(header[i])[0];bottom=bounds(groups[-1])[0]
        heights=[bounds(g)[1]-bounds(g)[0] for g in groups]
        gap=(header_bottom-bottom-sum(heights))/len(groups)
        assert gap>0
        cursor=header_bottom
        for g,h in zip(groups,heights):
            target_top=cursor-gap;shift(g,target_top-bounds(g)[1]);cursor=target_top-h
        fig.canvas.draw();renderer=fig.canvas.get_renderer()
        actual=[];prior=header_bottom
        for g in groups:
            lo,hi=bounds(g);actual.append(prior-hi);prior=lo
        assert max(actual)-min(actual)<1e-6
        spacing[i+1]={'gap_source_units':gap,'gap_mm':gap*260/190,'actual_gaps':actual}
    dot_clearances=[];percent_clearances=[]
    for group,num in [(a1,'68%'),(a2,'65%')]:
        labels=[a for a in group if isinstance(a,Text)];markers=[a for a in group if isinstance(a,Circle)]
        dot_clearances.append(bounds(labels)[0]-bounds(markers)[1])
        percent_clearances.append(bounds(named(num))[0]-bounds(markers)[1])
    assert max(dot_clearances)-min(dot_clearances)<1e-6
    assert max(percent_clearances)-min(percent_clearances)<1e-6
    score_formula=[t for t in base.texts if t.get_text().startswith('$S(v,e)')]
    score_definition=[t for t in base.texts if t.get_text().startswith('v: MSE forecast;')]
    score_contribution=[t for t in base.texts if t.get_text().startswith('One network accounts')]
    # Score notation is subordinate to its equation; keep it closer than group separators.
    shift(score_formula,.6);shift(score_definition,1.7);shift(score_contribution,1.7)
    fig.canvas.draw();renderer=fig.canvas.get_renderer()
    prior=bounds(header[2])[0];actual=[]
    for g in [a5,a6,a7]:
        lo,hi=bounds(g);actual.append(prior-hi);prior=lo
    spacing[3]['actual_gaps']=actual
    spacing[3]['mode']='optical: equation/definition grouped; result position retained'
    score_inner_gaps=[bounds(score_formula)[0]-bounds(score_definition)[1],bounds(score_definition)[0]-bounds(score_contribution)[1]]
    assert .8<score_inner_gaps[0]<1.1 and 1.8<score_inner_gaps[1]<2.2
    # Axis-title top edges have the same physical clearance from their baselines.
    axis_title_gaps=[]
    for ax in fig.axes[1:]:
        pos=ax.get_position();axis_baseline=pos.y0*135
        top=bounds([ax.xaxis.label])[1];desired=axis_baseline-7.4
        x,y=ax.xaxis.label.get_position()
        ax.xaxis.set_label_coords(x,y+(desired-top)/(pos.height*135))
    fig.canvas.draw();renderer=fig.canvas.get_renderer()
    for ax in fig.axes[1:]:
        gap=ax.get_position().y0*135-bounds([ax.xaxis.label])[1]
        axis_title_gaps.append(gap)
    assert max(axis_title_gaps)-min(axis_title_gaps)<1e-6
    return {'heading_baseline':103.9,'card_left_inset_mm':2.8*260/190,'card_right_inset_mm':2.8*260/190,'content_width':34.4,'legend_pitch':4.4,'legend_alignment':'actual glyph ink centre; response readout text has user-requested -0.12 optical offset','footer_separator_y':43.8,'title_number_pt':9.5,'forecast_definition_box':None,'equal_group_spacing':spacing,'axis_baseline_to_title_top_source_units':axis_title_gaps,'axis_baseline_to_title_top_mm':axis_title_gaps[0]*260/190,'score_inner_gaps':score_inner_gaps,'number_description_to_dot_gap':dot_clearances,'percent_to_dot_gap':percent_clearances,'definition_underline':False,'header_translation_y':-1.7,'export_bottom_y':12.7,'top_context_removed':True}
