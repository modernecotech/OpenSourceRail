// scenes.jsx — OpenSourceRail hero animation, suburban version

// ── Palette ──
const C = {
  bg:      'oklch(96% 0.010 85)',   // warm cream sky top
  bg2:     'oklch(93% 0.018 75)',   // warm cream sky mid
  bg3:     'oklch(90% 0.028 70)',   // sky near horizon
  ground:  'oklch(88% 0.020 80)',   // warm ground
  ground2: 'oklch(82% 0.030 70)',   // grass shadow band
  ink:     '#1a1a1a',
  ink2:    '#3a3530',
  muted:   '#8a8278',
  rule:    '#cfc7b8',
  sun:     'oklch(78% 0.14 65)',
  sunCore: 'oklch(88% 0.10 85)',
  signal:  'oklch(62% 0.14 155)',
  leaf:    'oklch(58% 0.11 140)',
  leaf2:   'oklch(50% 0.10 140)',
  leafHi:  'oklch(70% 0.10 130)',
  roofA:   'oklch(55% 0.11 35)',    // terracotta
  roofB:   'oklch(45% 0.09 25)',    // deep terracotta
  roofC:   'oklch(42% 0.03 260)',   // slate
  wallA:   'oklch(94% 0.015 80)',   // cream wall
  wallB:   'oklch(88% 0.025 70)',   // warm wall
  wallC:   'oklch(82% 0.015 80)',   // stone wall
  windowLit: 'oklch(80% 0.13 80)',  // warm lit window
  windowDim: 'oklch(55% 0.02 240)',
  track:   '#2b2724',
};

// ── Sky ──
function Sky() {
  const t = useTime();
  const glow = interpolate([0, 3, 12], [0.35, 0.85, 0.95], Easing.easeOutCubic)(t);
  return (
    <div style={{
      position: 'absolute', inset: 0,
      background: `
        radial-gradient(ellipse 1600px 700px at 68% 78%,
          oklch(92% 0.06 70 / ${glow}) 0%,
          oklch(94% 0.03 70 / ${glow * 0.55}) 35%,
          transparent 70%),
        linear-gradient(180deg,
          ${C.bg} 0%,
          ${C.bg2} 45%,
          ${C.bg3} 82%,
          oklch(88% 0.035 65) 100%)
      `,
    }}/>
  );
}

// ── Sun ──
function Sun() {
  const t = useTime();
  const y = interpolate([0, 3, 12], [760, 600, 580], Easing.easeOutCubic)(t);
  const opacity = interpolate([0, 1, 2], [0, 0.75, 1], Easing.easeOutCubic)(t);
  const size = 260;
  return (
    <div style={{
      position: 'absolute',
      left: 1920 * 0.72 - size/2,
      top: y - size/2,
      width: size, height: size,
      opacity,
    }}>
      <div style={{
        position: 'absolute', inset: 0, borderRadius: '50%',
        background: `radial-gradient(circle, ${C.sunCore} 0%, ${C.sun} 50%, transparent 72%)`,
        filter: 'blur(2px)',
      }}/>
      <div style={{
        position: 'absolute', left: '50%', top: '50%',
        width: 120, height: 120, marginLeft: -60, marginTop: -60,
        borderRadius: '50%', background: C.sunCore,
        boxShadow: `0 0 80px ${C.sun}, 0 0 140px oklch(82% 0.10 70 / 0.6)`,
      }}/>
    </div>
  );
}

// ── Far hills (soft) ──
function FarHills() {
  const t = useTime();
  const drift = -t * 2;
  return (
    <svg width={1920} height={200} style={{position:'absolute', left:0, top: 650}} viewBox="0 0 1920 200">
      <g style={{transform: `translateX(${drift}px)`}}>
        <path d="M -50 130 Q 120 80, 280 110 T 600 100 T 940 115 T 1280 95 T 1620 110 T 1970 100 L 1970 200 L -50 200 Z"
              fill="oklch(86% 0.03 75)" opacity="0.55"/>
        <path d="M -50 160 Q 180 130, 380 150 T 740 145 T 1100 155 T 1460 140 T 1800 155 L 1970 150 L 1970 200 L -50 200 Z"
              fill="oklch(81% 0.035 70)" opacity="0.5"/>
      </g>
    </svg>
  );
}

// ── Suburban houses — back row (far, small, parallax) ──
function BackRowHouses() {
  const t = useTime();
  const drift = -t * 8;
  const houses = [
    { x: 40,   w: 110, h: 60, roof: C.roofC, wall: C.wallC, type: 'gable' },
    { x: 200,  w: 130, h: 70, roof: C.roofA, wall: C.wallA, type: 'gable' },
    { x: 380,  w: 100, h: 55, roof: C.roofB, wall: C.wallB, type: 'flat' },
    { x: 530,  w: 140, h: 72, roof: C.roofA, wall: C.wallA, type: 'gable' },
    { x: 720,  w: 115, h: 60, roof: C.roofC, wall: C.wallC, type: 'gable' },
    { x: 880,  w: 130, h: 68, roof: C.roofB, wall: C.wallA, type: 'flat' },
    { x: 1060, w: 120, h: 64, roof: C.roofA, wall: C.wallB, type: 'gable' },
    { x: 1230, w: 135, h: 70, roof: C.roofC, wall: C.wallA, type: 'gable' },
    { x: 1420, w: 110, h: 58, roof: C.roofB, wall: C.wallC, type: 'flat' },
    { x: 1580, w: 130, h: 68, roof: C.roofA, wall: C.wallA, type: 'gable' },
    { x: 1760, w: 120, h: 62, roof: C.roofC, wall: C.wallB, type: 'gable' },
  ];
  return (
    <svg width={1920} height={200} style={{position:'absolute', left:0, top: 720, opacity: 0.75}} viewBox="0 0 1920 200">
      <g style={{transform: `translateX(${drift}px)`}}>
        {houses.map((h, i) => <TinyHouse key={i} {...h} />)}
      </g>
    </svg>
  );
}

function TinyHouse({ x, w, h, roof, wall, type }) {
  const bodyY = 80;
  const roofH = type === 'gable' ? 22 : 8;
  return (
    <g transform={`translate(${x}, 0)`}>
      {/* Wall */}
      <rect x={0} y={bodyY} width={w} height={h} fill={wall} stroke={C.ink} strokeWidth="0.7" opacity="0.95"/>
      {/* Roof */}
      {type === 'gable' ? (
        <path d={`M -4 ${bodyY} L ${w/2} ${bodyY - roofH} L ${w+4} ${bodyY} Z`} fill={roof} stroke={C.ink} strokeWidth="0.7"/>
      ) : (
        <rect x={-3} y={bodyY - roofH} width={w+6} height={roofH} fill={roof} stroke={C.ink} strokeWidth="0.7"/>
      )}
      {/* Windows */}
      <rect x={w*0.15} y={bodyY + h*0.35} width={w*0.18} height={h*0.25} fill={C.windowLit} opacity="0.8"/>
      <rect x={w*0.62} y={bodyY + h*0.35} width={w*0.18} height={h*0.25} fill={C.windowLit} opacity="0.8"/>
      {/* Chimney (sometimes) */}
      {type === 'gable' && w > 120 && (
        <rect x={w*0.7} y={bodyY - roofH - 6} width={5} height={10} fill={C.ink2}/>
      )}
    </g>
  );
}

// ── Mid row: suburban houses along track, larger, more detail ──
function MidRowHouses() {
  const t = useTime();
  const drift = -t * 18; // parallax faster than back row
  // Tile across 2x width so it loops
  const houses = [
    { x: 0,    w: 180, h: 130, roof: C.roofA, wall: C.wallA, style: 'cottage' },
    { x: 220,  w: 210, h: 150, roof: C.roofC, wall: C.wallB, style: 'twostory' },
    { x: 470,  w: 190, h: 135, roof: C.roofB, wall: C.wallA, style: 'cottage' },
    { x: 700,  w: 240, h: 160, roof: C.roofC, wall: C.wallC, style: 'twostory' },
    { x: 990,  w: 200, h: 140, roof: C.roofA, wall: C.wallA, style: 'cottage' },
    { x: 1230, w: 220, h: 150, roof: C.roofB, wall: C.wallB, style: 'twostory' },
    { x: 1500, w: 190, h: 135, roof: C.roofA, wall: C.wallA, style: 'cottage' },
    { x: 1740, w: 210, h: 145, roof: C.roofC, wall: C.wallC, style: 'twostory' },
  ];
  const loopW = 1980;

  return (
    <svg width={1920} height={260} style={{position:'absolute', left:0, top: 700}} viewBox="0 0 1920 260">
      <g style={{transform: `translateX(${drift % loopW}px)`}}>
        {[0, loopW].map(off => (
          <g key={off} transform={`translate(${off}, 0)`}>
            {houses.map((h, i) => <MidHouse key={i} {...h} />)}
          </g>
        ))}
      </g>
    </svg>
  );
}

function MidHouse({ x, w, h, roof, wall, style }) {
  const bodyTop = 260 - h - 30;
  const roofH = style === 'twostory' ? 42 : 36;
  return (
    <g transform={`translate(${x}, 0)`}>
      {/* Shadow */}
      <ellipse cx={w/2} cy={bodyTop + h + 6} rx={w/2 + 4} ry={4} fill="#000" opacity="0.08"/>
      {/* Body */}
      <rect x={0} y={bodyTop} width={w} height={h} fill={wall} stroke={C.ink} strokeWidth="1.1"/>
      {/* Roof */}
      <path d={`M -6 ${bodyTop} L ${w/2} ${bodyTop - roofH} L ${w+6} ${bodyTop} Z`}
            fill={roof} stroke={C.ink} strokeWidth="1.1"/>
      {/* Roof shade (right half darker) */}
      <path d={`M ${w/2} ${bodyTop - roofH} L ${w+6} ${bodyTop} L ${w/2} ${bodyTop} Z`}
            fill="#000" opacity="0.12"/>

      {/* Door */}
      <rect x={w*0.45} y={bodyTop + h*0.45} width={w*0.12} height={h*0.55}
            fill={C.ink2} stroke={C.ink} strokeWidth="0.8"/>
      <circle cx={w*0.55} cy={bodyTop + h*0.72} r={1.2} fill={C.sun}/>

      {/* Windows - row(s) */}
      {style === 'twostory' ? (
        <>
          {/* Upper floor */}
          <rect x={w*0.12} y={bodyTop + h*0.12} width={w*0.18} height={h*0.22}
                fill={C.windowLit} stroke={C.ink} strokeWidth="0.8"/>
          <rect x={w*0.70} y={bodyTop + h*0.12} width={w*0.18} height={h*0.22}
                fill={C.windowLit} stroke={C.ink} strokeWidth="0.8"/>
          {/* Window cross */}
          <line x1={w*0.21} y1={bodyTop + h*0.12} x2={w*0.21} y2={bodyTop + h*0.34} stroke={C.ink} strokeWidth="0.6"/>
          <line x1={w*0.12} y1={bodyTop + h*0.23} x2={w*0.30} y2={bodyTop + h*0.23} stroke={C.ink} strokeWidth="0.6"/>
          <line x1={w*0.79} y1={bodyTop + h*0.12} x2={w*0.79} y2={bodyTop + h*0.34} stroke={C.ink} strokeWidth="0.6"/>
          <line x1={w*0.70} y1={bodyTop + h*0.23} x2={w*0.88} y2={bodyTop + h*0.23} stroke={C.ink} strokeWidth="0.6"/>
          {/* Lower floor */}
          <rect x={w*0.12} y={bodyTop + h*0.50} width={w*0.22} height={h*0.28}
                fill={C.windowLit} stroke={C.ink} strokeWidth="0.8" opacity="0.85"/>
          <rect x={w*0.66} y={bodyTop + h*0.50} width={w*0.22} height={h*0.28}
                fill={C.windowLit} stroke={C.ink} strokeWidth="0.8" opacity="0.85"/>
        </>
      ) : (
        <>
          <rect x={w*0.12} y={bodyTop + h*0.30} width={w*0.22} height={h*0.32}
                fill={C.windowLit} stroke={C.ink} strokeWidth="0.8"/>
          <rect x={w*0.66} y={bodyTop + h*0.30} width={w*0.22} height={h*0.32}
                fill={C.windowLit} stroke={C.ink} strokeWidth="0.8"/>
          <line x1={w*0.23} y1={bodyTop + h*0.30} x2={w*0.23} y2={bodyTop + h*0.62} stroke={C.ink} strokeWidth="0.6"/>
          <line x1={w*0.12} y1={bodyTop + h*0.46} x2={w*0.34} y2={bodyTop + h*0.46} stroke={C.ink} strokeWidth="0.6"/>
          <line x1={w*0.77} y1={bodyTop + h*0.30} x2={w*0.77} y2={bodyTop + h*0.62} stroke={C.ink} strokeWidth="0.6"/>
          <line x1={w*0.66} y1={bodyTop + h*0.46} x2={w*0.88} y2={bodyTop + h*0.46} stroke={C.ink} strokeWidth="0.6"/>
        </>
      )}

      {/* Chimney */}
      {w > 200 && (
        <rect x={w*0.72} y={bodyTop - roofH - 12} width={8} height={18} fill={C.ink2} stroke={C.ink} strokeWidth="0.7"/>
      )}

      {/* Tiny PV on one rooftop, nods to the project */}
      {style === 'twostory' && (
        <g transform={`translate(${w*0.18} ${bodyTop - roofH*0.45}) rotate(-18)`}>
          <rect x={0} y={0} width={40} height={10} fill="oklch(35% 0.06 240)" stroke={C.ink} strokeWidth="0.6"/>
          <line x1={10} y1={0} x2={10} y2={10} stroke="oklch(55% 0.05 240)" strokeWidth="0.5"/>
          <line x1={20} y1={0} x2={20} y2={10} stroke="oklch(55% 0.05 240)" strokeWidth="0.5"/>
          <line x1={30} y1={0} x2={30} y2={10} stroke="oklch(55% 0.05 240)" strokeWidth="0.5"/>
        </g>
      )}
    </g>
  );
}

// ── Tree clumps between houses ──
function Trees() {
  const t = useTime();
  const drift = -t * 22;
  const trees = [
    { x: 180, s: 1.0, kind: 'round' },
    { x: 420, s: 0.85, kind: 'tall' },
    { x: 660, s: 1.1, kind: 'round' },
    { x: 940, s: 0.9, kind: 'round' },
    { x: 1200, s: 1.0, kind: 'tall' },
    { x: 1450, s: 1.15, kind: 'round' },
    { x: 1700, s: 0.9, kind: 'tall' },
    { x: 1940, s: 1.0, kind: 'round' },
  ];
  const loopW = 2100;
  return (
    <svg width={1920} height={260} style={{position:'absolute', left:0, top: 690}} viewBox="0 0 1920 260">
      <g style={{transform: `translateX(${drift % loopW}px)`}}>
        {[0, loopW].map(off => (
          <g key={off} transform={`translate(${off}, 0)`}>
            {trees.map((tr, i) => <Tree key={i} {...tr} />)}
          </g>
        ))}
      </g>
    </svg>
  );
}
function Tree({ x, s, kind }) {
  const cx = x, cy = 210;
  const trunkW = 6*s, trunkH = 26*s;
  const canopyR = kind === 'round' ? 36*s : 28*s;
  const canopyH = kind === 'tall' ? 62*s : 42*s;
  return (
    <g>
      {/* Trunk */}
      <rect x={cx - trunkW/2} y={cy - trunkH} width={trunkW} height={trunkH} fill="#4a3b2c" stroke={C.ink} strokeWidth="0.6"/>
      {/* Canopy */}
      {kind === 'round' ? (
        <>
          <circle cx={cx} cy={cy - trunkH - canopyR*0.6} r={canopyR} fill={C.leaf2} stroke={C.ink} strokeWidth="0.8"/>
          <circle cx={cx - canopyR*0.35} cy={cy - trunkH - canopyR*0.75} r={canopyR*0.7} fill={C.leaf} stroke={C.ink} strokeWidth="0.6"/>
          <circle cx={cx + canopyR*0.3} cy={cy - trunkH - canopyR*0.55} r={canopyR*0.6} fill={C.leafHi} opacity="0.9"/>
        </>
      ) : (
        <ellipse cx={cx} cy={cy - trunkH - canopyH/2} rx={canopyR} ry={canopyH/2}
                 fill={C.leaf2} stroke={C.ink} strokeWidth="0.8"/>
      )}
    </g>
  );
}

// ── Ground (grass strip + ballast between rails) ──
function Ground() {
  return (
    <>
      {/* Grass strip */}
      <div style={{
        position: 'absolute', left: 0, top: 920, width: 1920, height: 24,
        background: `linear-gradient(180deg, ${C.ground} 0%, ${C.ground2} 100%)`,
      }}/>
      {/* Ballast */}
      <div style={{
        position: 'absolute', left: 0, top: 944, width: 1920, height: 36,
        background: 'oklch(72% 0.015 70)',
        borderTop: `1px solid ${C.muted}`, borderBottom: `1px solid ${C.muted}`,
      }}/>
      {/* Ballast texture dots */}
      <svg width={1920} height={36} style={{position:'absolute', left:0, top:944, opacity:0.5}}>
        {Array.from({length: 220}).map((_, i) => {
          const bx = (i * 97) % 1920;
          const by = 3 + (i * 53) % 30;
          const r = 0.8 + (i % 3) * 0.4;
          return <circle key={i} cx={bx} cy={by} r={r} fill={C.muted}/>;
        })}
      </svg>
      {/* Ground below tracks */}
      <div style={{
        position: 'absolute', left: 0, top: 980, width: 1920, height: 100,
        background: `linear-gradient(180deg, oklch(84% 0.022 75) 0%, oklch(78% 0.030 70) 100%)`,
      }}/>
    </>
  );
}

// ── Rail track ──
function RailTrack() {
  const t = useTime();
  const draw = interpolate([1.2, 2.8, 12], [0, 1, 1], Easing.easeInOutCubic)(t);
  const trackTop = 955;
  return (
    <svg width={1920} height={40} style={{position:'absolute', left:0, top: trackTop}} viewBox="0 0 1920 40">
      {/* Sleepers */}
      {Array.from({length: 48}).map((_, i) => {
        const sp = clamp(draw * 48 - i, 0, 1);
        return (
          <rect key={i} x={i * 42 - 8} y={14} width={30} height={8}
                fill={C.ink2} opacity={sp * 0.55}/>
        );
      })}
      {/* Rails */}
      <rect x={0} y={10} width={1920 * draw} height={3} fill={C.track}/>
      <rect x={0} y={26} width={1920 * draw} height={3} fill={C.track}/>
      <rect x={0} y={9} width={1920 * draw} height={1} fill="oklch(78% 0.02 70)" opacity="0.8"/>
      <rect x={0} y={25} width={1920 * draw} height={1} fill="oklch(78% 0.02 70)" opacity="0.8"/>
    </svg>
  );
}

// ── Wayside consensus nodes ──
function WaysideNodes() {
  const t = useTime();
  const positions = [150, 460, 770, 1080, 1410, 1760];
  const nodeY = 922;
  const beatPeriod = 3;
  const beatStart = 3.4;
  const beatT = (t - beatStart) % beatPeriod;

  return (
    <>
      {positions.map((x, i) => {
        const appear = interpolate([2.4 + i*0.12, 2.9 + i*0.12], [0, 1], Easing.easeOutCubic)(t);
        const nodeBeatTime = (i / positions.length) * 1.4;
        const pulse = t > beatStart ? Math.max(0, 1 - Math.abs(beatT - nodeBeatTime) * 4.5) : 0;
        return (
          <div key={i} style={{
            position: 'absolute',
            left: x - 14, top: nodeY - 36,
            width: 28, height: 50, opacity: appear,
          }}>
            <div style={{position:'absolute', left: 13, top: 22, width: 2, height: 30, background: C.ink2}}/>
            <div style={{
              position:'absolute', left: 0, top: 0,
              width: 28, height: 22,
              background: C.bg, border: `1.2px solid ${C.ink}`, borderRadius: 2,
              boxShadow: pulse > 0.1 ? `0 0 ${pulse*14}px ${C.signal}` : 'none',
            }}>
              <div style={{
                position:'absolute', right: 3, top: 3,
                width: 4, height: 4, borderRadius:'50%',
                background: pulse > 0.1 ? C.signal : C.muted,
                boxShadow: pulse > 0.1 ? `0 0 5px ${C.signal}` : 'none',
              }}/>
              <div style={{
                position:'absolute', left: 3, top: 3,
                fontFamily:'JetBrains Mono, monospace',
                fontSize: 6, fontWeight: 700, color: C.ink, letterSpacing: '0.05em',
              }}>W{String(i+1).padStart(2,'0')}</div>
            </div>
          </div>
        );
      })}

      {/* Link arcs */}
      <svg width={1920} height={80} style={{position:'absolute', left:0, top: 858, pointerEvents:'none'}}>
        {positions.slice(0, -1).map((x, i) => {
          const x2 = positions[i+1];
          const mid = (i + 0.5) / positions.length * 1.4;
          const active = t > beatStart ? Math.max(0, 1 - Math.abs(beatT - mid) * 5) : 0;
          if (active < 0.05) return null;
          const cx = (x + x2) / 2;
          const cy = 50 - active * 30;
          return (
            <path key={i}
              d={`M ${x} 70 Q ${cx} ${cy}, ${x2} 70`}
              stroke={C.signal} strokeWidth="1.5" fill="none"
              opacity={active * 0.7} strokeDasharray="4 3"/>
          );
        })}
      </svg>
    </>
  );
}

// ── A level crossing (road + barrier) mid-scene ──
function LevelCrossing() {
  const t = useTime();
  const appear = interpolate([2.5, 3.4], [0, 1], Easing.easeOutCubic)(t);
  // Barrier lowers as train approaches (t=4.5 -> 5.3), raises after t=10
  const barrierAngle = interpolate([4.5, 5.3, 10, 10.8], [0, -75, -75, 0], Easing.easeInOutCubic)(t);
  // Warning light blinks while barrier down
  const blink = (t > 5 && t < 10.5) ? (Math.floor(t*4) % 2) : 0;

  const cx = 960; // crossing center X
  return (
    <div style={{position:'absolute', left: cx - 90, top: 870, width: 180, height: 120, opacity: appear}}>
      {/* Road stripes crossing the tracks (behind rails) */}
      <div style={{
        position:'absolute', left: -(cx - 90) + cx - 70, top: 80, width: 140, height: 40,
        // will be overdrawn by rails — positioned relative anyway
      }}/>
      <svg width={180} height={120} viewBox="0 0 180 120">
        {/* Left barrier pole */}
        <rect x={10} y={54} width={4} height={40} fill={C.ink}/>
        {/* Signal head */}
        <rect x={4} y={44} width={16} height={14} fill={C.ink} stroke={C.ink2} strokeWidth="0.6"/>
        <circle cx={12} cy={51} r={3.2}
                fill={blink ? 'oklch(65% 0.2 25)' : 'oklch(40% 0.04 25)'}
                style={{filter: blink ? 'drop-shadow(0 0 6px oklch(65% 0.2 25))' : 'none'}}/>
        {/* Barrier arm (left), rotates about pole base */}
        <g transform={`translate(12, 56) rotate(${barrierAngle})`}>
          <rect x={0} y={-2} width={60} height={4} fill="#eeeae0" stroke={C.ink} strokeWidth="0.6"/>
          <rect x={6} y={-2} width={10} height={4} fill={C.ink}/>
          <rect x={26} y={-2} width={10} height={4} fill={C.ink}/>
          <rect x={46} y={-2} width={10} height={4} fill={C.ink}/>
        </g>

        {/* Right barrier pole (mirrored) */}
        <rect x={166} y={54} width={4} height={40} fill={C.ink}/>
        <rect x={160} y={44} width={16} height={14} fill={C.ink} stroke={C.ink2} strokeWidth="0.6"/>
        <circle cx={168} cy={51} r={3.2}
                fill={blink ? 'oklch(65% 0.2 25)' : 'oklch(40% 0.04 25)'}
                style={{filter: blink ? 'drop-shadow(0 0 6px oklch(65% 0.2 25))' : 'none'}}/>
        <g transform={`translate(168, 56) rotate(${-barrierAngle}) scale(-1, 1)`}>
          <rect x={0} y={-2} width={60} height={4} fill="#eeeae0" stroke={C.ink} strokeWidth="0.6"/>
          <rect x={6} y={-2} width={10} height={4} fill={C.ink}/>
          <rect x={26} y={-2} width={10} height={4} fill={C.ink}/>
          <rect x={46} y={-2} width={10} height={4} fill={C.ink}/>
        </g>
      </svg>

      {/* Tiny label */}
      <div style={{
        position:'absolute', left: 54, top: 100,
        fontFamily:'JetBrains Mono, monospace',
        fontSize: 8, fontWeight: 600, color: C.ink2, letterSpacing:'0.08em',
      }}>LC-04 · SIL-4</div>
    </div>
  );
}

// ── Road running diagonally into the scene at the crossing ──
function CrossingRoad() {
  return (
    <svg width={1920} height={160} style={{position:'absolute', left:0, top: 940}} viewBox="0 0 1920 160">
      {/* Road strip across tracks */}
      <rect x={870} y={0} width={180} height={60} fill="oklch(55% 0.01 260)"/>
      {/* Road marking */}
      <rect x={958} y={0} width={4} height={60} fill="oklch(85% 0.12 85)"/>
      {/* Sidewalk kerb lines */}
      <line x1={870} y1={0} x2={870} y2={60} stroke={C.ink} strokeWidth="1"/>
      <line x1={1050} y1={0} x2={1050} y2={60} stroke={C.ink} strokeWidth="1"/>
    </svg>
  );
}

// ── Station: solar-canopy stop on the right side of the scene ──
function Station() {
  const t = useTime();
  const opacity = interpolate([3.4, 4.6, 12], [0, 1, 1], Easing.easeOutCubic)(t);
  const solar = 0.5 + 0.5 * Math.sin(t * 1.1);
  return (
    <div style={{
      position:'absolute', left: 1420, top: 780,
      width: 440, height: 180, opacity,
    }}>
      <svg width="440" height="200" viewBox="0 0 440 200" style={{position:'absolute', inset:0}}>
        {/* Canopy roof */}
        <path d="M 8 44 L 432 22 L 432 56 L 8 78 Z" fill={C.ink}/>
        {/* PV panels on the canopy */}
        <g>
          {Array.from({length: 14}).map((_, i) => (
            <rect key={i}
              x={20 + i*29} y={32 - i*1.4}
              width={26} height={14}
              fill={`oklch(${30 + solar*14}% 0.08 240)`}
              stroke="oklch(48% 0.05 240)" strokeWidth="0.6"
              transform="skewY(-3)"/>
          ))}
        </g>
        {/* Columns */}
        <rect x={42} y={56} width={5} height={110} fill={C.ink}/>
        <rect x={398} y={36} width={5} height={130} fill={C.ink}/>
        {/* Bench */}
        <rect x={110} y={148} width={80} height={6} fill={C.ink2}/>
        <rect x={116} y={154} width={6} height={14} fill={C.ink2}/>
        <rect x={178} y={154} width={6} height={14} fill={C.ink2}/>
        {/* A passenger silhouette */}
        <g transform="translate(230, 130)">
          <circle cx={0} cy={0} r={5} fill={C.ink}/>
          <rect x={-5} y={5} width={10} height={18} fill={C.ink}/>
          <rect x={-5} y={23} width={4} height={14} fill={C.ink}/>
          <rect x={1} y={23} width={4} height={14} fill={C.ink}/>
        </g>
        {/* Platform */}
        <rect x={0} y={170} width={440} height={12} fill={C.ink2}/>
        <rect x={0} y={168} width={440} height={3} fill={C.muted}/>
        <line x1={0} y1={176} x2={440} y2={176} stroke={C.sun} strokeWidth="1.5" strokeDasharray="6 4"/>
      </svg>

      <div style={{
        position:'absolute', left: 60, top: 92,
        fontFamily:'JetBrains Mono, monospace',
        fontSize: 11, fontWeight: 700, color: C.ink, letterSpacing:'0.1em',
        padding: '3px 8px', background: C.bg, border:`1px solid ${C.ink}`,
      }}>HALQA · WEST</div>
      <div style={{
        position:'absolute', left: 260, top: 92,
        fontFamily:'JetBrains Mono, monospace',
        fontSize: 10, color: C.signal, background: C.ink, padding:'3px 6px',
      }}>PV {Math.round(120 + solar*70)}kW</div>
    </div>
  );
}

// ── Birds ──
function Birds() {
  const t = useTime();
  if (t < 1) return null;
  const birds = [
    { x0: 1700, y: 300, speed: -60, delay: 0.5 },
    { x0: 1760, y: 320, speed: -60, delay: 1.2 },
    { x0: 1820, y: 290, speed: -60, delay: 1.9 },
  ];
  return (
    <svg width={1920} height={400} style={{position:'absolute', left:0, top:200, pointerEvents:'none'}}>
      {birds.map((b, i) => {
        const tt = t - b.delay;
        if (tt < 0) return null;
        const x = b.x0 + tt * b.speed;
        const flap = Math.sin(tt * 8) * 4;
        return (
          <g key={i} transform={`translate(${x}, ${b.y + flap})`} opacity="0.55">
            <path d="M -8 0 Q -4 -4, 0 0 Q 4 -4, 8 0" fill="none" stroke={C.ink} strokeWidth="1.3" strokeLinecap="round"/>
          </g>
        );
      })}
    </svg>
  );
}

// ── Train ──
function Train() {
  const t = useTime();
  const x = interpolate([0, 4.8, 11, 12], [-760, -760, 1920, 2280],
    [Easing.linear, Easing.easeInOutCubic, Easing.easeInOutCubic])(t);
  const soc = Math.round(interpolate([4.8, 11], [64, 87])(t));
  const speed = Math.round(interpolate([4.8, 5.8, 10.3, 11], [0, 58, 58, 0], Easing.easeInOutQuad)(t));
  const carW = 240, carH = 82;
  const gap = 6;
  const bodyY = 878;
  return (
    <div style={{position:'absolute', left: x, top: bodyY, width: carW*3, height: 140}}>
      {[0,1].map(i => <Car key={i} x={i * (carW + gap) + 40} w={carW} h={carH} lead={i === 1}/>)}
      <div style={{
        position:'absolute', left: carW + gap + 40 + 40, top: -58,
        display:'flex', gap: 6,
        fontFamily:'JetBrains Mono, monospace', fontSize: 12, fontWeight: 700, letterSpacing:'0.04em',
      }}>
        <div style={{background: C.ink, color: C.bg, padding:'5px 9px'}}>{String(speed).padStart(2,'0')} km/h</div>
        <div style={{background: C.bg, color: C.ink, padding:'5px 9px', border:`1.2px solid ${C.ink}`}}>SoC {soc}%</div>
      </div>
    </div>
  );
}

function Car({ x, w, h, lead }) {
  return (
    <div style={{position:'absolute', left: x, top: 0, width: w, height: h + 26}}>
      <svg width={w} height={h + 26} viewBox={`0 0 ${w} ${h+26}`}>
        <ellipse cx={w/2} cy={h+20} rx={w/2-4} ry={3.5} fill="#000" opacity="0.16"/>
        {/* Body */}
        <path d={lead
          ? `M 0 ${h*0.42} Q 10 8, 30 4 L ${w-22} 4 Q ${w-4} 8, ${w} ${h*0.42} L ${w} ${h-4} Q ${w} ${h}, ${w-4} ${h} L 4 ${h} Q 0 ${h}, 0 ${h-4} Z`
          : `M 4 4 L ${w-4} 4 Q ${w} 4, ${w} 8 L ${w} ${h-4} Q ${w} ${h}, ${w-4} ${h} L 4 ${h} Q 0 ${h}, 0 ${h-4} L 0 8 Q 0 4, 4 4 Z`
        } fill="oklch(95% 0.01 80)" stroke="#1a1a1a" strokeWidth="1.8"/>
        {/* Accent stripe */}
        <rect x={0} y={h*0.60} width={w} height={7} fill="oklch(72% 0.15 60)"/>
        <rect x={0} y={h*0.60 + 7} width={w} height={2} fill="#1a1a1a"/>
        {/* Windshield */}
        {lead && <rect x={10} y={14} width={28} height={h*0.36} rx={5} fill="#1a1a1a" opacity="0.88"/>}
        {/* Side windows */}
        {Array.from({length: lead ? 4 : 5}).map((_, i) => {
          const wx = (lead ? 50 : 18) + i * 42;
          return <rect key={i} x={wx} y={16} width={34} height={h*0.30} rx={2.5} fill="#1a1a1a" opacity="0.82"/>;
        })}
        {/* Door */}
        <rect x={w*0.66} y={h*0.15} width={22} height={h*0.72} fill="none" stroke="#1a1a1a" strokeWidth="0.9" strokeDasharray="2 2"/>
        {/* OSR mark */}
        <text x={14} y={h-10} fontFamily="JetBrains Mono, monospace" fontSize="8" fontWeight="700"
              fill="#1a1a1a" letterSpacing="0.1em">
          {lead ? 'OSR-01' : 'OSR-02'}
        </text>
        {/* Bogies */}
        <g>
          <rect x={22} y={h+2} width={48} height={10} rx={2} fill="#1a1a1a"/>
          <rect x={w-70} y={h+2} width={48} height={10} rx={2} fill="#1a1a1a"/>
          <circle cx={32} cy={h+16} r={7} fill="#1a1a1a"/>
          <circle cx={62} cy={h+16} r={7} fill="#1a1a1a"/>
          <circle cx={w-62} cy={h+16} r={7} fill="#1a1a1a"/>
          <circle cx={w-32} cy={h+16} r={7} fill="#1a1a1a"/>
        </g>
        {/* Roof battery */}
        <g transform={`translate(${w/2 - 16}, 6)`}>
          <rect x={0} y={0} width={32} height={6} rx={1} fill="none" stroke="#1a1a1a" strokeWidth="1.1"/>
          <rect x={32} y={2} width={2} height={2} fill="#1a1a1a"/>
          <rect x={2} y={2} width={8} height={2} fill="oklch(62% 0.14 155)"/>
          <rect x={11} y={2} width={8} height={2} fill="oklch(62% 0.14 155)"/>
          <rect x={20} y={2} width={8} height={2} fill="oklch(62% 0.14 155)"/>
        </g>
        {/* Headlight for lead car */}
        {lead && (
          <circle cx={4} cy={h*0.48} r={3} fill="oklch(90% 0.14 90)"
                  style={{filter:'drop-shadow(0 0 8px oklch(88% 0.14 85))'}}/>
        )}
      </svg>
    </div>
  );
}

// ── Title card ──
function TitleCard() {
  const t = useTime();
  const appear = interpolate([7.4, 8.4], [0, 1], Easing.easeOutCubic)(t);
  const sub = interpolate([8.1, 9.1], [0, 1], Easing.easeOutCubic)(t);
  const meta = interpolate([8.9, 9.9], [0, 1], Easing.easeOutCubic)(t);
  return (
    <div style={{position:'absolute', left: 110, top: 110, width: 940}}>
      <div style={{
        opacity: appear, transform:`translateY(${(1-appear)*12}px)`,
        display:'flex', alignItems:'center', gap: 10,
        fontFamily:'JetBrains Mono, monospace', fontSize: 14, fontWeight: 600,
        color: C.ink2, letterSpacing:'0.18em', textTransform:'uppercase', marginBottom: 18,
      }}>
        <span style={{width: 28, height: 2, background: C.sun}}/>
        v0.1 · 38 crates · 542 tests green
      </div>

      <div style={{
        opacity: appear, transform: `translateY(${(1-appear)*18}px)`,
        fontFamily: 'Inter, system-ui, sans-serif',
        fontSize: 136, fontWeight: 700, lineHeight: 0.95, letterSpacing: '-0.035em', color: C.ink,
        textShadow: '0 1px 0 oklch(100% 0 0 / 0.5)',
      }}>
        OpenSource<span style={{color: C.sun}}>Rail</span>
      </div>

      <div style={{
        opacity: sub, transform: `translateY(${(1-sub)*10}px)`,
        marginTop: 22,
        fontFamily:'Inter, system-ui, sans-serif',
        fontSize: 26, fontWeight: 400, lineHeight: 1.35, color: C.ink2,
        maxWidth: 740, letterSpacing: '-0.005em',
      }}>
        An open-source stack for designing, building, and operating rail systems —
        <span style={{color: C.ink, fontWeight: 500}}> built to be owned by the countries that deploy it.</span>
      </div>

      <div style={{
        opacity: meta, transform:`translateY(${(1-meta)*8}px)`,
        marginTop: 32, display:'flex', gap: 10,
        fontFamily:'JetBrains Mono, monospace', fontSize: 12, fontWeight: 500, letterSpacing:'0.06em',
      }}>
        {['RUST · SIL-4', 'CATENARY-FREE', 'SOLAR-FIRST', 'DISTRIBUTED CTC', 'TLA+ VERIFIED'].map((s, i) => (
          <div key={i} style={{
            padding:'6px 12px', border:`1px solid ${C.ink}`,
            color: C.ink, background: 'oklch(96% 0.008 80 / 0.85)',
            backdropFilter: 'blur(2px)',
          }}>{s}</div>
        ))}
      </div>
    </div>
  );
}

// ── Chrome (top/bottom overlays) ──
function Chrome() {
  const t = useTime();
  const opacity = interpolate([0.5, 1.5], [0, 1], Easing.easeOutCubic)(t);
  const lines = [
    'sim::tick 03:42:18 · line1 6/6 trains · line2 4/4 trains · hold 0.0s',
    'consensus::raft term=42 leader=W03 log=18471 commit=18471 ✓',
    'interlocking::MA granted → OSR-01 [halqa-west → bridge-east]',
    'energy::site pv=1.82MW batt=64% grid=+0kW · net +312kW',
    'safety::chain nominal · ATP ok · vigilance ok · doors locked',
    'level-crossing::LC-04 lowering · road clear · train 620m out',
  ];
  const idx = Math.floor(t / 2.0) % lines.length;
  const lineT = (t % 2.0) / 2.0;
  const lineOp = interpolate([0, 0.1, 0.9, 1], [0, 1, 1, 0])(lineT);

  return (
    <>
      <div style={{
        position:'absolute', left: 48, top: 48, opacity,
        display:'flex', alignItems:'center', gap: 10,
        fontFamily:'JetBrains Mono, monospace', fontSize: 13, fontWeight: 500, color: C.ink2,
      }}>
        <svg width="16" height="16" viewBox="0 0 16 16" fill={C.ink}>
          <path d="M8 0a8 8 0 00-2.53 15.59c.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.19 0 .21.15.46.55.38A8.01 8.01 0 0016 8a8 8 0 00-8-8z"/>
        </svg>
        modernecotech / OpenSourceRail
        <span style={{width: 4, height: 4, borderRadius: '50%', background: C.signal, marginLeft: 6, boxShadow: `0 0 8px ${C.signal}`}}/>
        <span style={{color: C.muted, fontSize: 11}}>main · building</span>
      </div>

      <div style={{
        position:'absolute', left: 0, right: 0, bottom: 34,
        opacity: opacity * lineOp, textAlign:'center',
        fontFamily:'JetBrains Mono, monospace', fontSize: 14, color: C.ink2, letterSpacing:'0.03em',
      }}>
        <span style={{color: C.muted}}>$</span> {lines[idx]}
      </div>

      <div style={{
        position:'absolute', right: 48, bottom: 48, opacity,
        fontFamily:'JetBrains Mono, monospace', fontSize: 12, fontWeight: 500, color: C.muted, letterSpacing:'0.1em',
      }}>T+{t.toFixed(2).padStart(5,'0')}s</div>

      <div style={{
        position:'absolute', right: 48, top: 48, opacity,
        display:'flex', gap: 8,
        fontFamily:'JetBrains Mono, monospace', fontSize: 11, fontWeight: 500, color: C.ink2, letterSpacing:'0.08em',
      }}>
        <span>APACHE-2.0</span><span style={{color: C.muted}}>·</span>
        <span>CERN-OHL-S</span><span style={{color: C.muted}}>·</span>
        <span>CC-BY-SA</span>
      </div>
    </>
  );
}

// ── Motion lines ──
function MotionLines() {
  const t = useTime();
  if (t < 5 || t > 11) return null;
  const opacity = interpolate([5, 5.8, 10.2, 11], [0, 0.5, 0.5, 0])(t);
  return (
    <div style={{position:'absolute', inset:0, pointerEvents:'none', opacity}}>
      {[0,1,2,3,4].map(i => {
        const y = 930 + i * 10;
        const offset = ((t * 380 + i * 120) % 1920);
        return (
          <div key={i} style={{
            position:'absolute', left: 1920 - offset, top: y,
            width: 80, height: 1, background: C.muted, opacity: 0.35,
          }}/>
        );
      })}
    </div>
  );
}

// ── Scene composition ──
// Layer order matters: sky → sun → hills → houses (back) → trees → houses (mid) → ground → station → road → rails → crossing → nodes → train → title → chrome
function Scene() {
  const t = useTime();
  return (
    <>
      <Sky />
      <Sun />
      <FarHills />
      <BackRowHouses />
      <Trees />
      <MidRowHouses />
      <Birds />
      <Ground />
      <Station />
      <CrossingRoad />
      <RailTrack />
      <LevelCrossing />
      <WaysideNodes />
      <MotionLines />
      <Train />
      <TitleCard />
      <Chrome />
      <div data-screen-label={`T+${t.toFixed(1)}s`} style={{position:'absolute',inset:0,pointerEvents:'none'}}/>
    </>
  );
}

Object.assign(window, { Scene, C });
