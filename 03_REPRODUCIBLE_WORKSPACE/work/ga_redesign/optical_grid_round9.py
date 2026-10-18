def optical_grid(fig,base):
    from matplotlib.text import Text
    from matplotlib.patches import Circle,FancyBboxPatch
    import numpy as np
    ink='#2E2531';muted='#655D69'
    rails={1:58.7,2:100.7,3:142.7}
    # Harmonise the header: one light-weight line, not three competing sizes.
    for t in fig.findobj(Text):
        v=t.get_text()
        if v=='Predictive risk and recording decisions':
            t.set_text('Predictive risk and recording decisions in partially observed neural networks')
            t.set_fontfamily('BentonSans');t.set_fontweight('normal');t.set_fontsize(18);t.set_position((8,127.8))
        elif v=='in partially observed neural networks':t.set_visible(False)
        elif v.startswith('Nominal versus prior-averaged local risk for'):
            t.set_position((8,119.5));t.set_fontsize(9.2)
        elif v in ['1','2','3']:t.set_visible(False)
        elif v in ['Recording agreement','Response error','Risk forecasts']:
            i={'Recording agreement':1,'Response error':2,'Risk forecasts':3}[v]
            t.set_text(f'{i}  {v}');t.set_position((rails[i],103.9));t.set_va('baseline');t.set_ha('left')
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
            t.set_text(lines[0]);t.set_position((rails[i],98.8));t.set_va('baseline');t.set_ha('left');t.set_fontsize(8.1)
            base.text(rails[i],96.0,lines[1],fontsize=8.1,fontfamily='BentonSans',color=muted,va='baseline')
        elif v=='known connectivity' or v=='uncertain physiology':t.set_visible(False)
        elif v=='12 simulated units · M=3':
            t.set_text('12 simulated units · M=3');t.set_fontsize(9.0)
        elif v=='Known connectivity; uncertain physiology':
            t.set_text('Uncertain gains and biases');t.set_fontsize(8.4)
        if v=='q' and x>45:t.set_y(74.1)
    base.text(30,85.2,'Known\nconnectivity',fontsize=8.8,fontfamily='BentonSans',color=muted,ha='center',va='center',linespacing=1.12,bbox=dict(facecolor='#FEFDFC',edgecolor='none',pad=.6,alpha=.92))
    # Baselines, not centre alignment, for the number+description groups.
    key={}
    for t in fig.findobj(Text):
        v=t.get_text()
        if v in ['68%','65%','19']:
            i=3 if v=='19' else 1;y=89.0 if v!='65%' else 60.1
            t.set_position((rails[i],y));t.set_va('baseline');t.set_ha('left');t.set_fontsize(16);t.set_fontfamily('BentonSans');t.set_fontweight('bold');key[v]=t
    fig.canvas.draw();r=fig.canvas.get_renderer()
    gap=1.7/1.3684210526
    end={v:base.transData.inverted().transform((t.get_window_extent(r).x1,0))[0]+gap for v,t in key.items()}
    for t in fig.findobj(Text):
        v=t.get_text()
        if v.startswith('82 of 120'):t.set_position((end['68%'],89.0));t.set_va('baseline');t.set_fontsize(8.0)
        elif v.startswith('26 of 40'):t.set_position((end['65%'],60.1));t.set_va('baseline');t.set_fontsize(8.0)
        elif v=='designs are identical':
            oldy=t.get_position()[1];isfirst=oldy>70
            t.set_position((end['68%' if isfirst else '65%'],85.9 if isfirst else 57.0));t.set_va('baseline');t.set_fontsize(8.0)
        elif v=='of 40 favour prior averaging;':t.set_position((end['19'],89.0));t.set_va('baseline');t.set_fontsize(8.0)
        elif v=='21 favour nominal':t.set_position((end['19'],85.9));t.set_va('baseline');t.set_fontsize(8.0)
        elif v=='same recording set':t.set_position((62.1,40.9));t.set_fontsize(7.2)
    # Clear whitespace around the dot grids, retaining all 120 and 40 markers.
    for p in base.patches:
        if isinstance(p,Circle):
            x,y=p.center
            if abs(p.get_radius()-.85)<.01 and x<97:
                if y>65:p.center=(x,81.8-round((83.4-y)/2.3)*2.1)
                elif 48<y<57:p.center=(x,53.4-round((55.4-y)/2.3)*2.1)
            elif abs(p.get_radius()-.85)<.01 and abs(y-41.4)<.01:p.center=(x,40.9)
    # Plot regions share the card inset and axis baseline.
    for i,a in enumerate(fig.axes[1:],2):
        pos=a.get_position();a.set_position([rails[i]/190,pos.y0,35.6/190,pos.height])
    # Per-group spacing: heading -> value -> CI, same left rail.
    for t in fig.findobj(Text):
        v=t.get_text()
        if v=='Single response':t.set_transform(base.transData);t.set_position((rails[2],89.0));t.set_va('baseline');t.set_fontsize(8.8)
        elif v=='Shared three-response':t.set_transform(base.transData);t.set_position((rails[2],69.5));t.set_va('baseline');t.set_fontsize(8.8)
        elif v.startswith('−3.7%'):t.set_transform(base.transData);t.set_position((rails[2],85.5));t.set_va('baseline')
        elif v.startswith('+2.7%'):t.set_transform(base.transData);t.set_position((rails[2],66.0));t.set_va('baseline')
        elif v=='MSE-forecast score difference':t.set_text('Forecast-score difference');t.set_transform(base.transData);t.set_position((rails[3],66.0));t.set_va('baseline');t.set_fontsize(8.8)
        elif v.startswith('−0.46'):t.set_transform(base.transData);t.set_position((rails[3],62.5));t.set_va('baseline')
        elif v.startswith('$S(v,e)'):t.set_position((rails[3],79.8));t.set_fontsize(11.5)
        elif v.startswith('v: MSE forecast;'):
            t.set_position((rails[3],76.1));t.set_va('baseline');t.set_fontsize(7.4)
        elif v.startswith('One network contributes'):
            t.set_text('One network accounts for 64%\nof the summed score difference')
            t.set_position((rails[3],73.8));t.set_va('top');t.set_fontsize(7.4);t.set_linespacing(1.15)
    # Shift CI marks only, retaining the same numerical x coordinates/scales.
    for i,a in enumerate(fig.axes[1:],2):
        p=a.get_position();lo,hi=a.get_ylim()
        def unit(y):return p.y0*135+(y-lo)/(hi-lo)*p.height*135
        for line in a.lines:
            yy=np.asarray(line.get_ydata(),dtype=float)
            if not len(yy):continue
            mean=unit(float(yy.mean()))
            target=(80.5 if mean>70 else 61.0) if i==2 else 58.0
            delta=(target-mean)/(p.height*135)*(hi-lo)
            line.set_ydata(yy+delta)
    # The score title and values must remain on the page grid after plot movements.
    return {'heading_baseline':103.9,'card_left_inset_mm':2.2*1.3684210526,'major_stat_baseline':89.0,'number_text_gap_mm':1.7}
