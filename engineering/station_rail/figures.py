"""Deterministic SI geometry and target-motion diagrams for the research reader."""
from pathlib import Path
from math import sqrt
import io
from .common import identity

def write(record,output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle,Circle
    from .operations import _coast_time
    matplotlib.rcParams.update({'svg.hashsalt':record['candidate_id'],'font.family':'DejaVu Sans','font.size':9})
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    def save(fig,name):
        path=output/name
        fig.savefig(path,format='svg',metadata={'Date':None,'Description':'Research candidate '+record['candidate_id']});plt.close(fig)
        # Matplotlib writes SVG path commands with trailing spaces. Keep the
        # published source artifacts clean and make git whitespace checks useful.
        path.write_text('\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
    car=record['vehicle'];fig,axes=plt.subplots(2,1,figsize=(11,5.3),gridspec_kw={'height_ratios':[2,1]})
    for p in car['geometry_parts']:
        system=p.get('system','body');pid=p['id'];color='#287c91' if system=='bogies' else '#cb8b36' if system=='passive-secondary' else '#8da9b1'
        if p['kind']=='box':
            x,y,z=p['at_m'];l,w,h=p['size_m'];alpha=.4;order=2
            if system=='body-fitout':
                alpha=.07
                if 'replacement-frame' in pid:alpha=.35;order=3
                if '/fixed-window/' in pid or '/door-window/' in pid:color='#3b9fb9';alpha=.65;order=5
                elif '/door/' in pid:color='#d8ad72';alpha=.25;order=4
            axes[0].add_patch(Rectangle((x,z),l,h,facecolor=color,edgecolor='none',alpha=alpha,zorder=order))
            if system!='body-fitout' or '/seat-unit/' in pid:
                axes[1].add_patch(Rectangle((x,y),l,w,facecolor=color,edgecolor='none',alpha=.4))
        else:
            x,y,z=p['at_m'];r=p['radius_m'];axis=p['axis'];length=p['length_m']
            if abs(axis[1])>.5:axes[0].add_patch(Circle((x,z),r,facecolor=color,edgecolor='none',alpha=.6));axes[1].add_patch(Rectangle((x-r,y),2*r,length,facecolor=color,alpha=.6,edgecolor='none'))
    axes[0].axhline(0,color='#34495e',linewidth=1);axes[0].axhline(1.,color='#c56f23',linewidth=.8,linestyle='--')
    for ax in axes:ax.set_xlim(-9,9);ax.set_aspect('equal');ax.grid(alpha=.15)
    axes[0].set_ylim(-.15,4.3);axes[0].set_ylabel('Height above rail (m)');axes[0].set_title('v0.6 counted material - service equipment and residual accounts are not complete geometry',loc='left')
    axes[1].add_patch(Rectangle((-8.5,-1.325),17,2.65,fill=False,edgecolor='#5d7e88',linewidth=1));axes[1].set_ylim(-1.6,1.6);axes[1].set_ylabel('Across car (m)');axes[1].set_xlabel('Along car (m); roof, skin and floor omitted in top projection')
    fig.tight_layout();save(fig,'vehicle-overview.svg')
    p=record['service']['selected_scenario']['profile'];i=p['inputs'];m=i.get('effective_inertial_mass_kg_per_car',i['mass_kg_per_car']);c=p['constant_wheel_drag_N_per_car']+p['grade_force_N_per_car'];q=i['quadratic_drag_N_per_car_per_m_s_squared_hypothesis']
    peak=p['peak_speed_m_s'];arrival=p['arrival_speed_before_braking_m_s'];xs=[];ts=[];vs=[]
    from .operations import _coast_distance
    for j in range(81):
        v=peak*j/80;ts.append(v/i['acceleration_m_s2']);xs.append(v*v/(2*i['acceleration_m_s2']));vs.append(v)
    for j in range(1,81):
        v=peak-(peak-arrival)*j/80;ts.append(p['launch_time_s']+_coast_time(m,c,q,peak,v));xs.append(p['launch_distance_m']+_coast_distance(m,c,q,peak,v));vs.append(v)
    for j in range(1,81):
        v=arrival*(1-j/80);t=(arrival-v)/i['service_deceleration_m_s2'];ts.append(p['launch_time_s']+p['coast_time_s']+t);xs.append(p['launch_distance_m']+p['coast_distance_m']+arrival*t-i['service_deceleration_m_s2']*t*t/2);vs.append(v)
    fig,axes=plt.subplots(1,2,figsize=(10,3.3));axes[0].plot(xs,[v*3.6 for v in vs],color='#227884',lw=2);axes[0].set_xlabel('Distance (m)');axes[0].set_ylabel('Speed (km/h)');axes[1].plot(ts,[v*3.6 for v in vs],color='#227884',lw=2);axes[1].set_xlabel('Time (s)');axes[1].set_ylabel('Speed (km/h)')
    for ax in axes:ax.grid(alpha=.2);ax.set_ylim(bottom=0)
    fig.suptitle('2 km normal-load kinematic requirement - actual station thrust and braking remain unqualified');fig.tight_layout();save(fig,'service-profile.svg')
    fig,ax=plt.subplots(figsize=(8,4.1));ax.add_patch(Rectangle((-1.,-1.6),2.,1.4,facecolor='#bcc9ce'));ax.add_patch(Rectangle((-.82,-1.42),1.64,1.04,facecolor='white'))
    for side in (-1,1):
        y=side*.7535;ax.add_patch(Rectangle((y-.075,-.2),.15,.2,facecolor='#4c6470'));ax.add_patch(Circle((side*.7475,.38),.38,facecolor='#287c91',alpha=.5));ax.add_patch(Rectangle((side*.09-.045,.02),.09,.16,facecolor='#d9a356',alpha=.65))
    ax.add_patch(Rectangle((-.0075,.02),.015,.16,facecolor='#bc7023'));ax.axhline(0,lw=.7,color='#333');ax.axhline(1.,color='#c56f23',linestyle='--',lw=1)
    ax.set_xlim(-1.55,1.55);ax.set_ylim(-1.75,1.25);ax.set_aspect('equal');ax.set_xlabel('Across track (m)');ax.set_ylabel('Height above rail (m)');ax.set_title('Reference box beam and station interface envelopes\nWheels, fin and primary shown in one projected view; swept clearance unqualified')
    ax.grid(alpha=.15);fig.tight_layout();save(fig,'interface-section.svg')
