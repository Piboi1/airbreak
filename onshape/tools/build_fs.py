#!/usr/bin/env python3
"""Build fs/airbrake_v1_v2.fs from the supplied original by exact, asserted string patches."""
import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
src = (ROOT / "fs" / "v0_original.fs").read_text()
patches = []


def P(old, new, count=1):
    patches.append((old, new, count))


# ------------------------------------------------------------------ header + helpers
P("// Screw-free cam kick-out prototype; all angles are physical, not a force simulation.",
  "// Cam kick-out airbrake, screwed assembly. V1 = inline housing, V2 = compact head inside the upper BT80 tube.\n"
  "// All angles are physical, not a force simulation. Hardware: M3 self-tapping, M4 hinge screws.")

HELPERS = r'''
// ---------------- fasteners (all dimensions mm) ----------------
const M3_CLR = 1.7;      // 3.4 mm clearance hole
const M3_PILOT = 1.3;    // 2.6 mm thread-forming pilot for PLA / PETG
const M3_CB = 3.0;       // 6.0 mm counterbore for a socket head
const M4_CLR = 2.25;     // 4.5 mm clearance hole
const M4_PILOT = 1.65;   // 3.3 mm thread-forming pilot
const HW_GREY = [.30, .31, .34];
const TUBE_TAN = [.86, .78, .55];

// Solid cylinder on an arbitrary axis: point p, unit direction d, from s0 to s1 along d.
function cylAlong(context is Context, id is Id, p is Vector, d is Vector, s0 is number, s1 is number, r is number) returns Query
{
    fCylinder(context, id, { "bottomCenter" : (p + d * s0) * millimeter, "topCenter" : (p + d * s1) * millimeter,
        "radius" : r * millimeter });
    return solid(id);
}

function drill(context is Context, id is Id, target is Query, p is Vector, d is Vector, s0 is number, s1 is number, r is number)
{
    var tool = cylAlong(context, id + "tool", p, d, s0, s1, r);
    subtract(context, id + "cut", target, tool);
}

// Radial hole at azimuth az, height z, from radius rIn to radius rOut.
function radialDrill(context is Context, id is Id, target is Query, az is ValueWithUnits, z is number, rIn is number, rOut is number, r is number)
{
    drill(context, id, target, vector(0, 0, z), vector(cos(az), sin(az), 0), rIn, rOut, r);
}

// Hardware screw. p = point under the head, d = thread direction (into the material).
// kind: M3BH button head, M3SC socket cap, M4BH button head.
function screwHW(context is Context, id is Id, p is Vector, d is Vector, kind is string, len is number, name is string) returns Query
{
    var hr = 2.85;
    var hh = 1.65;
    var sr = 1.5;
    if (kind == "M3SC")
    {
        hr = 2.75;
        hh = 3.0;
    }
    if (kind == "M4BH")
    {
        hr = 3.8;
        hh = 2.2;
        sr = 2.0;
    }
    var head = cylAlong(context, id + "head", p, d, -hh, 0, hr);
    var shaft = cylAlong(context, id + "shaft", p, d, 0, len, sr);
    drill(context, id + "hex", head, p, d, -hh - 0.1, -hh + 1.0, 1.2);
    opBoolean(context, id + "join", { "tools" : qUnion([head, shaft]), "operationType" : BooleanOperationType.UNION });
    label(context, head, name, HW_GREY);
    return head;
}

// Azimuth of the radial tube-retention screw in V2 support s (0..3). Always centred on the strip: an offset hole
// would leave only ~1.3 mm of 0.5 mm tube web beside the window. On the two seam strips the thread bites across the
// clamped seam.
function supportAz(s is number, lv is number) returns ValueWithUnits
{
    return (45 + 90 * s) * degree;
}

annotation { "Feature Type Name" : "Positive cam kick-out and cord-limited BT80 airbrake" }'''
P('\nannotation { "Feature Type Name" : "Positive cam kick-out and cord-limited BT80 airbrake" }', HELPERS)

# ------------------------------------------------------------------ camKickBrake preconditions + variables
P('''  definition.cords is boolean;
 }
 {
 var blue=[.18,.45,.65];var orange=[.95,.46,.12];var gold=[.8,.69,.25];''',
  '''  definition.cords is boolean;
  annotation { "Name" : "V2 compact head (fins inside upper BT80 tube)", "Default" : false }
  definition.compact is boolean;
  annotation { "Name" : "Show fastener hardware", "Default" : true }
  definition.hardware is boolean;
  annotation { "Name" : "Show BT80 tube references and cut-out pieces", "Default" : true }
  definition.tubes is boolean;
 }
 {
 var blue=[.18,.45,.65];var orange=[.95,.46,.12];var gold=[.8,.69,.25];
 var compact=definition.compact;
 // V2: the outer skin group (housing wall, fins, hook, stops) moves in 0.72 mm so the fin outer face is 64.6 mm OD
 // and the glued 0.52 mm BT80 cut-out brings it back to 66.04 mm.
 var dr=compact?-0.72:0;
 var rOut=33.02+dr;
 var camMax=compact?28.6:29;
 // V2: the latch stack (hook, crown arms, top bearing, knob) drops 22 mm into the fin height; the catch is an inward lug on the fin.
 var dzT=compact?22:0;
 var topZ=compact?58.8:67;''')

P(''' var carrier=tubeMM(context,id+"carrier",33.02,30.2,-15,67);
 var base=tubeMM(context,id+"base",33.02,18,-15,-11);
 var lower=tubeMM(context,id+"lowerShoulder",32.3,29.9,-33,-14.9);
 var upper=tubeMM(context,id+"upperShoulder",32.3,29.9,66.9,85);''',
  ''' var carrier=tubeMM(context,id+"carrier",rOut,30.2+dr,-15,topZ);
 var base=tubeMM(context,id+"base",33.02,18,-15,-11);
 var lower=tubeMM(context,id+"lowerShoulder",32.3,29.9,-33,-14.9);
 var joinParts=[carrier,base,lower];
 if(!compact) joinParts=append(joinParts,tubeMM(context,id+"upperShoulder",32.3,29.9,66.9,85));''')

P(''' var catchBelt=tubeMM(context,id+"recessCatchBelt",31,28.4,54.6,57.4);
 opBoolean(context,id+"recessCatchBeltJoin",{"tools":qUnion([carrier,catchBelt]),"operationType":BooleanOperationType.UNION});''',
  ''' if(!compact) {
  var catchBelt=tubeMM(context,id+"recessCatchBelt",31+dr,28.4+dr,54.6,57.4);
  opBoolean(context,id+"recessCatchBeltJoin",{"tools":qUnion([carrier,catchBelt]),"operationType":BooleanOperationType.UNION});
 }''')

P('var ring=cylinderMM(context,id+"rotorShaft",5,-10.5,78);', 'var ring=cylinderMM(context,id+"rotorShaft",5,-10.5,78-dzT);')
P('cylinderMM(context,id+"crownHub",9,58.6,61.6)', 'cylinderMM(context,id+"crownHub",9,58.6-dzT,61.6-dzT)')
P('cylinderMM(context,id+"highThrust",7,65.5,67.5)', 'cylinderMM(context,id+"highThrust",7,65.5-dzT,67.5-dzT)')
P('cylinderMM(context,id+"knob",10,74,78)', 'cylinderMM(context,id+"knob",10,74-dzT,78-dzT)')
P('sector(context,id+"finger",8,16,4,74,4)', 'sector(context,id+"finger",8,16,4,74-dzT,4)')
P('tubeMM(context,id+"topBearing",18,5.4,68,73)', 'tubeMM(context,id+"topBearing",18,5.4,68-dzT,73-dzT)')
P('radialBox(context,id+("topSpoke"~i),15,31,-2.5,2.5,68,4,a)', 'radialBox(context,id+("topSpoke"~i),15,31,-2.5,2.5,68-dzT,4,a)')
P('sector(context,id+("knobStop"~j),12,18,4,72.5,5.9)', 'sector(context,id+("knobStop"~j),12,18,4,72.5-dzT,5.9)')
P('sector(context,id+("bearingRelief"~i),8.5,15.5,29,70,3.1)', 'sector(context,id+("bearingRelief"~i),8.5,15.5,29,70-dzT,3.1)')
P('cylinderMM(context,id+"rotorLightTool",3,-8,78.1)', 'cylinderMM(context,id+"rotorLightTool",3,-8,78.1-dzT)')
P('''  if(phase>24 && phase<60) r=21+8*(phase-24)/36;
  if(phase>=60 && phase<=66) r=29;
  if(phase>66 && phase<78) r=29-8*(phase-66)/12;''',
  '''  if(phase>24 && phase<60) r=21+(camMax-21)*(phase-24)/36;
  if(phase>=60 && phase<=66) r=camMax;
  if(phase>66 && phase<78) r=camMax-(camMax-21)*(phase-66)/12;''')

P('"tools":qUnion([carrier,base,lower,upper])', '"tools":qUnion(joinParts)')

# ------------------------------------------------------------------ panel loop
P('sector(context,sub+"window",29.5,34,33.5,-9.2,63.8)', 'sector(context,sub+"window",29.5+dr,34,33.5,-9.2,63.8)')
P('''  var tipSlot=sector(context,sub+"tipSlot",27.6,38,8,50.8,8.6);
  turn(context,sub+"tipSlotTurn",tipSlot,a);subtract(context,sub+"tipSlotCut",carrier,tipSlot);
  // Crown arms sweep above the fixed anchor belt; four remaining pillars carry the top.
  var sweepSlot=sector(context,sub+"crownSlot",29.5,37,41,57.3,6.1);
  turn(context,sub+"crownSlotTurn",sweepSlot,a+32.5*degree);
  subtract(context,sub+"crownSlotCut",carrier,sweepSlot);''',
  '''  if(!compact) {
   var tipSlot=sector(context,sub+"tipSlot",27.6+dr,38,8,50.8,8.6);
   turn(context,sub+"tipSlotTurn",tipSlot,a);subtract(context,sub+"tipSlotCut",carrier,tipSlot);
   // Crown arms sweep above the fixed anchor belt; four remaining pillars carry the top.
   var sweepSlot=sector(context,sub+"crownSlot",29.5+dr,37,41,57.3,6.1);
   turn(context,sub+"crownSlotTurn",sweepSlot,a+32.5*degree);
   subtract(context,sub+"crownSlotCut",carrier,sweepSlot);
  }''')

P('''  var catchArm=radialBox(context,sub+"catchArm",6,30,-2.5,2.5,58.6,3,0*degree);
  turn(context,sub+"catchTurn",catchArm,a);
  opBoolean(context,sub+"rotorCatchJoin",{"tools":qUnion([ring,catchArm]),"operationType":BooleanOperationType.UNION});
  // Install these four keyed catch caps radially AFTER closing the housing around the rotor.
  var catchCap=radialBox(context,sub+"catchCap",22,32.6,-4.2,4.2,57.4,5.4,0*degree);
  var catchHook=sector(context,sub+"catchHook",30.9,32.8,5.2,55.2,5.0);
  opBoolean(context,sub+"catchJoin",{"tools":qUnion([catchCap,catchHook]),"operationType":BooleanOperationType.UNION});
  var catchSocket=radialBox(context,sub+"catchSocket",21.9,30.4,-2.75,2.75,58.4,3.4,0*degree);
  subtract(context,sub+"catchSocketCut",catchCap,catchSocket);
  turn(context,sub+"capPosition",catchCap,a+definition.release*degree);
  label(context,catchCap,"L"~(i+1)~" Recessed catch cap - R32.8 outer limit - bond to rotor arm",[.20,.58,.34]);''',
  '''  var armEnd=compact?24.1:30+dr;var armZ=compact?58.6-dzT:58.6;var capR=compact?20.4:24.3;
  var catchArm=radialBox(context,sub+"catchArm",6,armEnd,-2.5,2.5,armZ,3,0*degree);
  turn(context,sub+"catchTurn",catchArm,a);
  opBoolean(context,sub+"rotorCatchJoin",{"tools":qUnion([ring,catchArm]),"operationType":BooleanOperationType.UNION});
  // M3 clearance hole through the rotor arm for the cap screw (axis Z).
  drill(context,sub+"armHole",ring,vector(capR*cos(a),capR*sin(a),0),vector(0,0,1),armZ-0.6,armZ+3.6,M3_CLR);
  // Open-top clip: the arm drops into the socket with the housing halves open; a boss under the arm takes the screw.
  var catchCap=undefined;var catchSocket=undefined;
  if(compact) {
   // V2: hook finger stands inside R26 and hooks the lug on the fin from inside (see fin lug), so it clears the fin shell.
   catchCap=radialBox(context,sub+"catchCap",18.0,26.0,-4.2,4.2,35.4,5.4,0*degree);
   var catchFinger=radialBox(context,sub+"catchFinger",23.6,26.0,-3.0,3.0,40.8,5.2,0*degree);
   var catchBoss=radialBox(context,sub+"catchBoss",18.0,24.2,-4.2,4.2,31.4,4.0,0*degree);
   opBoolean(context,sub+"catchJoin",{"tools":qUnion([catchCap,catchFinger,catchBoss]),"operationType":BooleanOperationType.UNION});
   catchSocket=radialBox(context,sub+"catchSocket",17.9,24.2,-2.75,2.75,36.4,5.0,0*degree);
  } else {
   catchCap=radialBox(context,sub+"catchCap",22,32.6+dr,-4.2,4.2,57.4,5.4,0*degree);
   var catchHook=sector(context,sub+"catchHook",30.9+dr,32.8+dr,5.2,55.2,5.0);
   var catchBoss=radialBox(context,sub+"catchBoss",21.8,26.6,-4.2,4.2,53.4,4.0,0*degree);
   opBoolean(context,sub+"catchJoin",{"tools":qUnion([catchCap,catchHook,catchBoss]),"operationType":BooleanOperationType.UNION});
   catchSocket=radialBox(context,sub+"catchSocket",21.9,30.4+dr,-2.75,2.75,58.4,5.0,0*degree);
  }
  subtract(context,sub+"catchSocketCut",catchCap,catchSocket);
  drill(context,sub+"capPilot",catchCap,vector(capR,0,0),vector(0,0,1),compact?32.0:54.0,compact?36.5:58.5,M3_PILOT);
  turn(context,sub+"capPosition",catchCap,a+definition.release*degree);
  label(context,catchCap,"L"~(i+1)~(compact?" Catch cap - open-top clip with inner hook finger, 1 x M3x8 screw to rotor arm":" Catch cap - open-top clip, 1 x M3x8 screw to rotor arm"),[.20,.58,.34]);
  if(definition.hardware) {
   var cs=screwHW(context,sub+"capScrew",vector(capR,0,armZ+3.0),vector(0,0,-1),"M3BH",8,"HW L"~(i+1)~" cap screw - M3x8 button head");
   turn(context,sub+"capScrewTurn",cs,a+definition.release*degree);
  }''')

P('subtract(context,sub+("earBore"~j),ear,yc(context,sub+("earTool"~j),2.45,y0-.1,y1+.1));',
  'subtract(context,sub+("earBore"~j),ear,yc(context,sub+("earTool"~j),(j==0?M4_CLR:M4_PILOT),y0-.1,y1+.1));')
P('radialBox(context,sub+"outerCompressionStop",27,32.8,-6,6,-15,7.6,0*degree)',
  'radialBox(context,sub+"outerCompressionStop",27,32.8+dr,-6,6,-15,7.6,0*degree)')
P('sector(context,sub+"shell",30.62,33.02,32.5,4,50)', 'sector(context,sub+"shell",30.62+dr,rOut,32.5,4,50)')
P('radialBox(context,sub+"landing",29,32.4,-6,6,4,4,0*degree)', 'radialBox(context,sub+"landing",29,32.4+dr,-6,6,4,4,0*degree)')
P('radialBox(context,sub+"landingTool",32.4,35,-6,6,4,4,0*degree)', 'radialBox(context,sub+"landingTool",32.4+dr,35,-6,6,4,4,0*degree)')
P('yc(context,sub+"leafTool",2.45,-7.5,7.5)', 'yc(context,sub+"leafTool",M4_CLR,-7.5,7.5)')
P('''  subtract(context,sub+"tipRecessCut",panel,sector(context,sub+"tipRecessTool",30.42,34,5.8,51,3.1));
  var tip=sector(context,sub+"tip",27.9,30.42,5,51,6.0);
  var tipRoot=sector(context,sub+"recessTipRoot",27.9,33.02,6.8,47,4.2);
  opBoolean(context,sub+"recessTipRootJoin",{"tools":qUnion([panel,tipRoot]),"operationType":BooleanOperationType.UNION});''',
  '''  var tip=undefined;
  if(compact) {
   // V2 catch: an inward lug (plate + inner wall) inside the fin height. The rotor finger stands outside the wall,
   // so the fin cannot move out until the rotor swings the finger away (about 16 deg).
   var lugWall=radialBox(context,sub+"lugWall",20.0,22.8,-3,3,41.6,8.4,0*degree);
   var lugPlate=radialBox(context,sub+"lugPlate",20.0,30.6,-3,3,47,3,0*degree);
   opBoolean(context,sub+"lugJoin",{"tools":qUnion([lugPlate,lugWall]),"operationType":BooleanOperationType.UNION});
   tip=lugPlate;
  } else {
   subtract(context,sub+"tipRecessCut",panel,sector(context,sub+"tipRecessTool",30.42+dr,34,5.8,51,3.1));
   tip=sector(context,sub+"tip",27.9+dr,30.42+dr,5,51,6.0);
   var tipRoot=sector(context,sub+"recessTipRoot",27.9+dr,rOut,6.8,47,4.2);
   opBoolean(context,sub+"recessTipRootJoin",{"tools":qUnion([panel,tipRoot]),"operationType":BooleanOperationType.UNION});
  }''')

P('''  label(context,panel,"P"~(i+1)~" Cam-driven BT80 panel - solid shell - reinforced root - 90 degree stop",orange);
  var pin=yc(context,sub+"pin",2.1,-12.5,16);
  var head=yc(context,sub+"head",3.4,-14.7,-12.3);
  opBoolean(context,sub+"pinJoin",{"tools":qUnion([pin,head]),"operationType":BooleanOperationType.UNION});
  turn(context,sub+"pinTurn",pin,a);label(context,pin,"H"~(i+1)~" Printed hinge pin - 4.2 mm shaft",gold);
  var cap=yc(context,sub+"cap",3.4,12.5,16.8);
  subtract(context,sub+"capBore",cap,yc(context,sub+"capTool",2.35,12.4,16.2));
  turn(context,sub+"capTurn",cap,a);label(context,cap,"K"~(i+1)~" Deep pin end cap - 3.5 mm bond overlap - bond pin only",gold);''',
  '''  label(context,panel,"P"~(i+1)~" Cam-driven BT80 panel - solid shell - reinforced root - 90 degree stop",orange);
  // Hinge: M4x25 button-head screw, clearance in the -Y ear and the panel barrel, threads into the +Y ear.
  if(definition.hardware) {
   var hs=screwHW(context,sub+"hingeScrew",vector(25,-12,0),vector(0,1,0),"M4BH",25,"HW H"~(i+1)~" hinge screw - M4x25 button head");
   turn(context,sub+"hingeScrewTurn",hs,a);
  }
  // V2: the cut-out piece of the real BT80 tube is glued to the fin and rides with it.
  if(compact && definition.tubes) {
   var tp=sector(context,sub+"tubePiece",32.5,33.02,32.5,8,42);
   opTransform(context,sub+"tubePieceOpen",{"bodies":tp,"transform":rotationAround(line(vector(25,0,0)*millimeter,vector(0,1,0)),definition.opening*degree)});
   turn(context,sub+"tubePieceTurn",tp,a);
   label(context,tp,"TP"~(i+1)~" BT80 tube cut-out - glue to fin P"~(i+1)~" (cut from the real tube, not printed)",TUBE_TAN);
  }''')

P('sector(context,sub+"recessHookTrack",30.65,34,40,55.0,2.5)', 'sector(context,sub+"recessHookTrack",30.65+dr,34,40,55.0,2.5)')
P(' for(var i=0;i<4;i+=1) {\n  var sub=id+("finalHookTrack"~i);', ' for(var i=0;i<(compact?0:4);i+=1) {\n  var sub=id+("finalHookTrack"~i);')

P('''  var h=yc(context,id+("headPocket"~i),3.7,-15.1,-12.1);
  var c=yc(context,id+("capPocket"~i),3.7,12.2,17.1);
  turn(context,id+("hpTurn"~i),h,a);turn(context,id+("cpTurn"~i),c,a);
  subtract(context,id+("hpCut"~i),carrier,h);subtract(context,id+("cpCut"~i),carrier,c);''',
  '''  var h=yc(context,id+("headPocket"~i),4.2,-15.0,-12.0);
  turn(context,id+("hpTurn"~i),h,a);
  subtract(context,id+("hpCut"~i),carrier,h);''')

P('''  var up=sector(context,id+("upperRelief"~i),29.8,30.7,17,69,13.5);
  turn(context,id+("upperReliefTurn"~i),up,a);subtract(context,id+("upperReliefCut"~i),carrier,up);''',
  '''  if(!compact) {
   var up=sector(context,id+("upperRelief"~i),29.8,30.7,17,69,13.5);
   turn(context,id+("upperReliefTurn"~i),up,a);subtract(context,id+("upperReliefCut"~i),carrier,up);
  }''')

# ------------------------------------------------------------------ screw bosses, supports (before the split)
BOSSES = r''' // ---- screw bosses: seam clamp ribs, V1 sleeve pads, V2 thick supports between the fins ----
 for(var side=0;side<2;side+=1) for(var lv=0;lv<(compact?1:2);lv+=1) {
  var rsa=(45+side*180)*degree;var rzc=lv==0?8:44;
  var rib=radialBox(context,id+("seamRib"~side~lv),23.8,30.8+dr,-6.5,6.5,rzc-5,10,rsa);
  opBoolean(context,id+("seamRibJoin"~side~lv),{"tools":qUnion([carrier,rib]),"operationType":BooleanOperationType.UNION});
 }
 if(!compact) for(var k=0;k<4;k+=1) {
  // V1: pads behind the upper glue sleeve take 4 radial M3x6 screws through the BT80 tube.
  var paz=k*90*degree;var psub=id+("sleevePad"~k);
  var spad=radialBox(context,psub,26.2,30.2,-4.5,4.5,72.5,7,paz);
  opBoolean(context,psub+"join",{"tools":qUnion([carrier,spad]),"operationType":BooleanOperationType.UNION});
  radialDrill(context,psub+"pilot",carrier,paz,76,26.9,33.5,M3_PILOT);
  if(definition.hardware)
   screwHW(context,psub+"hw",vector(33.02*cos(paz),33.02*sin(paz),76),vector(-cos(paz),-sin(paz),0),"M3BH",6,"HW upper sleeve screw "~(k+1)~" - M3x6 button head");
 }
 if(compact) for(var s=0;s<4;s+=1) {
  // V2: thick supports in the solid strips between the fins. Two pieces leave the cam sweep band z 18.5..29.5 clear.
  var ssa=(45+90*s)*degree;
  for(var part=0;part<2;part+=1) {
   var sup=sector(context,id+("support"~s~part),27.4,30.6+dr,11.0,part==0?-11:29.5,part==0?29.5:25);
   turn(context,id+("supportTurn"~s~part),sup,ssa);
   opBoolean(context,id+("supportJoin"~s~part),{"tools":qUnion([carrier,sup]),"operationType":BooleanOperationType.UNION});
  }
  for(var lv=0;lv<2;lv+=1) {
   var saz=supportAz(s,lv);var sz=lv==0?12:36;
   radialDrill(context,id+("supportPilot"~s~lv),carrier,saz,sz,28.0,33.5,M3_PILOT);
   if(definition.hardware)
    screwHW(context,id+("supportScrew"~s~lv),vector(33.02*cos(saz),33.02*sin(saz),sz),vector(-cos(saz),-sin(saz),0),"M3BH",5,"HW top-tube support screw "~(s*2+lv+1)~" - M3x5 button head");
  }
 }
 // Four seam registration pins (slip fit; do not force). Split along 45 degrees, through fixed posts.'''
P(' // Four seam registration pins (slip fit; do not force). Split along 45 degrees, through fixed posts.', BOSSES)

P('radialBox(context,id+("seamBoss"~side),26,32.5,-3.5,3.5,63,4,a)', 'radialBox(context,id+("seamBoss"~side),26,32.5+dr,-3.5,3.5,compact?51.5:63.5,3.5,a)')
P('var r=level==0?24:29;var z=level==0?-13:65;', 'var r=level==0?24:29;var z=level==0?-13:(compact?53:65);')
P('" Split BT80 housing - align and bond stationary seams"', '" Split BT80 housing - clamp with 4 x M3 seam screws, peg-aligned"')

# ------------------------------------------------------------------ seam screws, tube references (after pegs)
AFTER = r''' // Seam clamp screws: counterbore + clearance in the negative half, thread-forming pilot in the positive half.
 for(var side=0;side<2;side+=1) for(var lv=0;lv<2;lv+=1) {
  var ssa2=(45+side*180)*degree;var szc=lv==0?8:44;
  var srr=(compact&&lv==1)?29.6:27;var sp0=vector(srr*cos(ssa2),srr*sin(ssa2),szc);var ssub=id+("seamScrew"~side~lv);
  drill(context,ssub+"cb",negative,sp0,seamNormal,-7,-3.1,M3_CB);
  drill(context,ssub+"clr",negative,sp0,seamNormal,-3.2,0.3,M3_CLR);
  drill(context,ssub+"pilot",positive,sp0,seamNormal,-0.3,6.0,M3_PILOT);
  if(definition.hardware)
   screwHW(context,ssub+"hw",sp0-3.1*seamNormal,seamNormal,"M3SC",8,"HW seam screw "~(side*2+lv+1)~" - M3x8 socket head");
 }
 // Reference BT80 upper tube. V1: sits on the upper sleeve. V2: runs over the whole fin zone with 4 slits.
 if(definition.tubes) {
  var ut=compact?tubeMM(context,id+"upperTube",33.02,32.5,-11,100):tubeMM(context,id+"upperTube",33.02,32.5,67,110);
  if(compact) {
   for(var i=0;i<4;i+=1) {
    var tw=sector(context,id+("tubeWindow"~i),32.0,34,33.5,-9.2,63.8);
    turn(context,id+("tubeWindowTurn"~i),tw,i*90*degree);
    subtract(context,id+("tubeWindowCut"~i),ut,tw);
    for(var lv=0;lv<2;lv+=1)
     radialDrill(context,id+("tubeHole"~i~lv),ut,supportAz(i,lv),lv==0?12:36,32.0,33.5,M3_CLR);
   }
   label(context,ut,"REF BT80 upper tube - 4 slits (windows) cut for the fins, 8 screw holes - cut from real tube",TUBE_TAN);
  } else {
   for(var k=0;k<4;k+=1) radialDrill(context,id+("tubeHole"~k),ut,k*90*degree,76,32.0,33.5,M3_CLR);
   label(context,ut,"REF BT80 upper tube - 4 screw holes at z=76 - drill using the sleeve pads",TUBE_TAN);
  }
 }
 turn(context,id+"releaseTurn",ring,definition.release*degree);'''
P(' turn(context,id+"releaseTurn",ring,definition.release*degree);', AFTER)

# ------------------------------------------------------------------ modularBrake
P('''  annotation {"Name":"Upward trigger stroke mm","Default":0} isReal(definition.button,{(unitless):[0,0,4.5]} as RealBoundSpec);
 }''',
  '''  annotation {"Name":"Upward trigger stroke mm","Default":0} isReal(definition.button,{(unitless):[0,0,4.5]} as RealBoundSpec);
  annotation {"Name":"V2 compact head (fins inside upper BT80 tube)","Default":false} definition.compact is boolean;
  annotation {"Name":"Show fastener hardware","Default":true} definition.hardware is boolean;
  annotation {"Name":"Show BT80 tube references and cut-out pieces","Default":true} definition.tubes is boolean;
 }''')

P(' var stage="initial";try {', ' var stage="initial";var rpAz=[90,200,340];try {')

P('camKickBrake(context,id+"brake",{"opening":definition.opening,"release":definition.release,"cords":false});',
  'camKickBrake(context,id+"brake",{"opening":definition.opening,"release":definition.release,"cords":false,\n  "compact":definition.compact,"hardware":definition.hardware,"tubes":definition.tubes});')

P('  var foot=radialBox(context,id+("dockFoot"~k),30,32,-2.5,2.5,77,34,a);',
  '  var foot=radialBox(context,id+("dockFoot"~k),30,32,-2.5,2.5,75.5,35.5,a);')

DOCKPADS = r''' opBoolean(context,id+"dockBondJoin",{"tools":qUnion([dock,bondRing]),"operationType":BooleanOperationType.UNION});
 // Radial M3x10 screws pass through the lower BT80 tube and the housing sleeve into pads on the dock ring.
 stage="ring pads";
 for(var k=0;k<3;k+=1) {
  var raz=rpAz[k]*degree;var rsub=id+("ringPad"~k);
  var rpad=radialBox(context,rsub,24.2,27.4,-4.5,4.5,115,7,raz);
  opBoolean(context,rsub+"join",{"tools":qUnion([dock,rpad]),"operationType":BooleanOperationType.UNION});
  radialDrill(context,rsub+"pilot",dock,raz,118.5,24.6,29.6,M3_PILOT);
  radialDrill(context,rsub+"sleeveHole",solid(id+"brake"+"carrier"+"outer"),raz,-26.5,29.5,33.5,M3_CLR);
  if(definition.hardware)
   screwHW(context,rsub+"hw",vector(33.02*cos(raz),33.02*sin(raz),118.5),vector(-cos(raz),-sin(raz),0),"M3BH",10,"HW dock ring screw "~(k+1)~" - M3x10 button head");
 }
 for(var k=0;k<4;k+=1) radialDrill(context,id+("footHole"~k),dock,(45+90*k)*degree,77.8,29.6,32.6,M3_CLR);'''
P(' opBoolean(context,id+"dockBondJoin",{"tools":qUnion([dock,bondRing]),"operationType":BooleanOperationType.UNION});', DOCKPADS)

CASEBOSS = r''' // Lid screw bosses on the casing flange (M3x10 vertical, R24.7).
 stage="case boss";var lidAz=[145,215,335];
 for(var k=0;k<3;k+=1) {
  var laz=lidAz[k]*degree;
  var cboss=radialBox(context,id+("caseBoss"~k),22.0,26.6,-4.2,4.2,96,4.0,laz);
  opBoolean(context,id+("caseBossJoin"~k),{"tools":qUnion([casing,cboss]),"operationType":BooleanOperationType.UNION});
  drill(context,id+("casePilot"~k),casing,vector(24.7*cos(laz),24.7*sin(laz),0),vector(0,0,1),94.6,100.0,M3_PILOT);
 }
 stage="lid";'''
P(' stage="lid";', CASEBOSS)

LIDEARS = r''' for(var k=0;k<3;k+=1) subtract(context,id+("lidClipSlot"~k),lid,radialBox(context,id+("lidClipTool"~k),19.2,23.3,-2.8,2.8,99.9,4.2,(60+120*k)*degree));
 stage="lid ears";
 for(var k=0;k<3;k+=1) {
  var laz2=lidAz[k]*degree;
  var lear=radialBox(context,id+("lidEar"~k),22.5,26.8,-4.2,4.2,100,4,laz2);
  opBoolean(context,id+("lidEarJoin"~k),{"tools":qUnion([lid,lear]),"operationType":BooleanOperationType.UNION});
  drill(context,id+("lidHole"~k),lid,vector(24.7*cos(laz2),24.7*sin(laz2),0),vector(0,0,1),99.8,104.2,M3_CLR);
  if(definition.hardware)
   screwHW(context,id+("lidScrew"~k),vector(24.7*cos(laz2),24.7*sin(laz2),104),vector(0,0,-1),"M3BH",10,"HW lid screw "~(k+1)~" - M3x10 button head");
 }'''
P(''' for(var k=0;k<3;k+=1) subtract(context,id+("lidClipSlot"~k),lid,radialBox(context,id+("lidClipTool"~k),19.2,23.3,-2.8,2.8,99.9,4.2,(60+120*k)*degree));''', LIDEARS)

P('''   var pad=radialBox(context,id+("mountPad"~k),28.5,30,-2.5,2.5,76,3.7,(45+90*k)*degree);
   opBoolean(context,id+("mountPadJoin"~k),{"tools":qUnion([mount,pad]),"operationType":BooleanOperationType.UNION});''',
  '''   var paz2=(45+90*k)*degree;
   var pad=radialBox(context,id+("mountPad"~k),26.0,30,-3.0,3.0,76,3.7,paz2);
   opBoolean(context,id+("mountPadJoin"~k),{"tools":qUnion([mount,pad]),"operationType":BooleanOperationType.UNION});
   radialDrill(context,id+("padPilot"~k),mount,paz2,77.8,26.4,30.4,M3_PILOT);
   if(definition.hardware)
    screwHW(context,id+("footScrew"~k),vector(33.02*cos(paz2),33.02*sin(paz2),77.8),vector(-cos(paz2),-sin(paz2),0),"M3BH",10,"HW cradle screw "~(k+1)~" - M3x10 button head");''')

# labels that used to say "bond"
P('"D Shared stationary cartridge dock - bond feet to fixed bridge"', '"D Shared stationary cartridge dock - 3 ring screws to housing sleeve, 4 foot screws to cradle"')
P('"S Reinforced tangential SG90 cradle - roof and separate keeper"', '"S Reinforced tangential SG90 cradle - 4 pad screws to dock feet, roof and separate keeper"')
P('"F Upper latch guide and spring cartridge lid - lower servo is separate"', '"F Upper latch guide and spring cartridge lid - 3 M3 lid screws to casing"')

# lower BT80 tube reference, created in final coordinates after the module has been moved
P(''' opTransform(context,id+"moduleBelowHousing",{"bodies":moduleBodies,"transform":transform(vector(0,0,-145)*millimeter)});''',
  ''' opTransform(context,id+"moduleBelowHousing",{"bodies":moduleBodies,"transform":transform(vector(0,0,-145)*millimeter)});
 if(definition.tubes) {
  var lt=tubeMM(context,id+"lowerTube",33.02,32.5,-100,-15);
  for(var k=0;k<3;k+=1) radialDrill(context,id+("lowerTubeHoleA"~k),lt,rpAz[k]*degree,-26.5,32.0,33.5,M3_CLR);
  if(definition.mode==0) for(var k=0;k<4;k+=1) radialDrill(context,id+("lowerTubeHoleB"~k),lt,(45+90*k)*degree,-67.2,32.0,33.5,M3_CLR);
  label(context,lt,"REF BT80 lower tube - 3 ring-screw holes at z=-26.5, 4 cradle-screw holes at z=-67.2 - cut from real tube",TUBE_TAN);
 }''')

# ------------------------------------------------------------------ V3: SG90 straight on the rotor (module mode 3)
# No spring cartridge, trigger, pushrod or latch cartridge: the servo hangs under the rotor from two posts and drives it
# through its own horn, which sits in a socket in the rotor underside. The rotor-mounted latch and the cams are unchanged.
P('  annotation { "Name" : "Show fastener hardware", "Default" : true }\n  definition.hardware is boolean;',
  '  annotation { "Name" : "V3 servo posts and tube pads", "Default" : false }\n  definition.direct is boolean;\n'
  '  annotation { "Name" : "Show fastener hardware", "Default" : true }\n  definition.hardware is boolean;')

P('    if (kind == "M4BH")\n    {',
  '    if (kind == "M2BH")\n    {\n        hr = 2.0;\n        hh = 1.3;\n        sr = 1.0;\n    }\n    if (kind == "M4BH")\n    {')

P(' // Four seam registration pins (slip fit; do not force). Split along 45 degrees, through fixed posts.',
  r''' if(definition.direct) {
  // V3: SG90 hangs from its flange under two posts that grow out of the low spokes at azimuth 135 / 315 (off the seam).
  // Servo long axis s runs along azimuth 135; shaft on the rotor axis; tab holes at s=+18.8 and s=-9.3 (measure your servo).
  var es=vector(cos(135*degree),sin(135*degree),0);
  // The servo is flush with the housing bottom (z -33): its tab top (z -14.5) is 0.5 mm above the base ring underside, so relieve the ring there.
  subtract(context,id+"servoTabNotch",carrier,radialBox(context,id+"servoNotchTool",15.0,23.0,-6.5,6.5,-15.1,0.7,135*degree));
  for(var k=0;k<2;k+=1) {
   var hs=k==0?18.8:-9.3;
   var post=radialBox(context,id+("servoPost"~k),k==0?16.3:-11.8,k==0?21.3:-6.8,-3,3,-14.5,15.0,135*degree);
   opBoolean(context,id+("servoPostJoin"~k),{"tools":qUnion([carrier,post]),"operationType":BooleanOperationType.UNION});
   drill(context,id+("servoPostPilot"~k),carrier,vector(hs*es[0],hs*es[1],-14.5),vector(0,0,1),0,5.5,0.8);
   if(definition.hardware)
    screwHW(context,id+("servoScrew"~k),vector(hs*es[0],hs*es[1],-17.0),vector(0,0,1),"M2BH",8,"HW servo flange screw "~(k+1)~" - M2x8 button head");
  }
  var rpAz3=[90,200,340];
  for(var k=0;k<3;k+=1) {
   // Pads on the inside of the lower glue sleeve take 3 radial M3x10 screws through the BT80 tube and the sleeve.
   var raz3=rpAz3[k]*degree;var rs3=id+("sleeveScrewPad"~k);
   var rpad3=radialBox(context,rs3,23.2,30.4,-4.5,4.5,-30.5,8,raz3);
   opBoolean(context,rs3+"join",{"tools":qUnion([carrier,rpad3]),"operationType":BooleanOperationType.UNION});
   radialDrill(context,rs3+"pilot",carrier,raz3,-26.5,23.6,29.9,M3_PILOT);
   radialDrill(context,rs3+"clear",carrier,raz3,-26.5,29.9,33.5,M3_CLR);
   if(definition.hardware)
    screwHW(context,rs3+"hw",vector(33.02*cos(raz3),33.02*sin(raz3),-26.5),vector(-cos(raz3),-sin(raz3),0),"M3BH",10,"HW sleeve screw "~(k+1)~" - M3x10 button head");
  }
 }
 // Four seam registration pins (slip fit; do not force). Split along 45 degrees, through fixed posts.''')

P('annotation {"Name":"Module: 0 spring, 1 direct servo, 2 unloaded spring samples","Default":0} isInteger(definition.mode,{(unitless):[0,0,2]} as IntegerBoundSpec);',
  'annotation {"Name":"Module: 0 spring, 1 direct servo, 2 unloaded spring samples, 3 V3 servo straight on the rotor","Default":0} isInteger(definition.mode,{(unitless):[0,0,3]} as IntegerBoundSpec);')

P('"compact":definition.compact,"hardware":definition.hardware,"tubes":definition.tubes});',
  '"compact":definition.compact,"direct":definition.mode==3,"hardware":definition.hardware,"tubes":definition.tubes});')

P(' var rotor=solid(id+"brake"+"rotorShaft");\n stage="shaft extension";',
  r''' var rotor=solid(id+"brake"+"rotorShaft");
 if(definition.mode==3) {
  stage="v3 rotor hub";
  var es3=vector(cos(135*degree),sin(135*degree),0);
  // Round stub through the low bearing, then a 6.2 mm hub below it; the horn sits in a socket in the hub underside.
  var hub=cylinderMM(context,id+"v3Hub",6.2,-8.7,-1.7);
  try { opBoolean(context,id+"v3HubJoin",{"tools":qUnion([rotor,hub]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"v3HubJoin"); }
  var pocket=cylinderMM(context,id+"v3HornPocket",4.5,-8.9,-6.5);
  var slot=radialBox(context,id+"v3HornSlot",0,13,-2.2,2.2,-8.9,2.4,0*degree);
  try { opBoolean(context,id+"v3PocketJoin",{"tools":qUnion([pocket,slot]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"v3PocketJoin"); }
  turn(context,id+"v3PocketTurn",pocket,(100+definition.release)*degree);
  subtract(context,id+"v3HornPocketCut",rotor,pocket);
  label(context,rotor,"R Top knob + keyed crown arms + four kick cams + servo horn socket - 0 LOCK 65 OPEN",[.28,.68,.42]);
  // SG90 horn (reference) in the socket: hub + one arm, 1.8 mm thick.
  var hornHub=cylinderMM(context,id+"v3HornHub",4,-8.5,-6.7);
  var hornArm=radialBox(context,id+"v3HornArm",0,11,-1.7,1.7,-8.5,1.8,0*degree);
  try { opBoolean(context,id+"v3HornJoin",{"tools":qUnion([hornHub,hornArm]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"v3HornJoin"); }
  turn(context,id+"v3HornTurn",hornHub,(100+definition.release)*degree);
  label(context,hornHub,"EH SG90 horn REFERENCE - fit the socket to your actual horn",[.8,.69,.25]);
  if(definition.hardware)
   screwHW(context,id+"v3HornScrew",vector(0,0,-6.7),vector(0,0,-1),"M2BH",6,"HW horn screw - M2x6 (the one supplied with the servo)");
  // SG90 envelope (reference): shaft up on the rotor axis, long axis at azimuth 135, flange 4.2 mm below the shaft-end face.
  stage="v3 servo";
  var sBody=radialBox(context,id+"v3ServoBody",-6.5,16.0,-6.1,6.1,-33.0,22.7,135*degree);
  var sTab=radialBox(context,id+"v3ServoTab",-11.5,21.0,-5.9,5.9,-17.0,2.5,135*degree);
  var sSpline=cylinderMM(context,id+"v3Spline",2.4,-10.5,-6.6);
  try { opBoolean(context,id+"v3ServoJoin",{"tools":qUnion([sBody,sTab,sSpline]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"v3ServoJoin"); }
  for(var k=0;k<2;k+=1) {
   var hs3=k==0?18.8:-9.3;
   drill(context,id+("v3TabHole"~k),sBody,vector(hs3*es3[0],hs3*es3[1],-17.5),vector(0,0,1),0,3.6,1.1);
  }
  label(context,sBody,"E SG90 servo REFERENCE - shaft up, flange under the two housing posts - measure your servo",[.35,.38,.43]);
  if(definition.tubes) {
   var lt3=tubeMM(context,id+"lowerTube",33.02,32.5,-85,-15);
   for(var k=0;k<3;k+=1) radialDrill(context,id+("lowerTubeHole"~k),lt3,[90,200,340][k]*degree,-26.5,32.0,33.5,M3_CLR);
   label(context,lt3,"REF BT80 lower tube - 3 sleeve-screw holes at z=-26.5 - cut from real tube",TUBE_TAN);
  }
  return;
 }
 stage="shaft extension";''')

# V3: lower bearing, collar and spokes move up above the horn so the servo can sit flush with the housing bottom.
P('var ring=cylinderMM(context,id+"rotorShaft",5,-10.5,78-dzT);','var ring=cylinderMM(context,id+"rotorShaft",5,definition.direct?-8.7:-10.5,78-dzT);')
P('var lowThrust=cylinderMM(context,id+"lowThrust",7,-5.5,-3.5);','var lowThrust=cylinderMM(context,id+"lowThrust",7,definition.direct?2.7:-5.5,definition.direct?4.7:-3.5);')
P('var lowBearing=tubeMM(context,id+"lowBearing",8,5.4,-15,-6);','var lowBearing=tubeMM(context,id+"lowBearing",8,5.4,definition.direct?-0.8:-15,definition.direct?2.2:-6);')
P('var lowSpoke=radialBox(context,id+("lowSpoke"~i),6,20,-2.5,2.5,-15,4,a);','var lowSpoke=radialBox(context,id+("lowSpoke"~i),6,definition.direct?30.6:20,-2.5,2.5,definition.direct?-0.8:-15,definition.direct?3.0:4,a);')

# ------------------------------------------------------------------ V4: servo on top (flipped), bay at the bottom (module mode 4)
P('  annotation { "Name" : "V3 servo posts and tube pads", "Default" : false }\n  definition.direct is boolean;\n',
  '  annotation { "Name" : "V3 servo posts and tube pads", "Default" : false }\n  definition.direct is boolean;\n  annotation { "Name" : "V4 servo on top, bay at the bottom", "Default" : false }\n  definition.flip is boolean;\n')
P(' var compact=definition.compact;\n', ' var compact=definition.compact;\n var flip=definition.flip;\n')
P(' var topZ=compact?58.8:67;', ' var topZ=compact?58.8:67;')
P('var lower=tubeMM(context,id+"lowerShoulder",32.3,29.9,-33,-14.9);', 'var lower=tubeMM(context,id+"lowerShoulder",32.3,29.9,flip?-35.5:-33,-14.9);')
P('var base=tubeMM(context,id+"base",33.02,18,-15,-11);', 'var base=tubeMM(context,id+"base",33.02,flip?26:18,-15,-11);')
P('var ring=cylinderMM(context,id+"rotorShaft",5,definition.direct?-8.7:-10.5,78-dzT);',
  'var ring=cylinderMM(context,id+"rotorShaft",5,flip?-6.4:(definition.direct?-8.7:-10.5),flip?44.6:78-dzT);')
P('var cam=polygonMM(context,id+"camProfile",points,22,3);', 'var cam=polygonMM(context,id+"camProfile",points,flip?22.5:22,flip?5.5:3);')
P('var crownHub=cylinderMM(context,id+"crownHub",9,58.6-dzT,61.6-dzT);', 'var crownHub=cylinderMM(context,id+"crownHub",9,flip?33.6:58.6-dzT,flip?44.6:61.6-dzT);')
P('var lowThrust=cylinderMM(context,id+"lowThrust",7,definition.direct?2.7:-5.5,definition.direct?4.7:-3.5);',
  'var lowThrust=cylinderMM(context,id+"lowThrust",7,flip?3.9:(definition.direct?2.7:-5.5),flip?5.9:(definition.direct?4.7:-3.5));')
P(''' var highThrust=cylinderMM(context,id+"highThrust",7,65.5-dzT,67.5-dzT);
 var knob=cylinderMM(context,id+"knob",10,74-dzT,78-dzT);
 var finger=sector(context,id+"finger",8,16,4,74-dzT,4);
 opBoolean(context,id+"rotorJoin",{"tools":qUnion([ring,cam,crownHub,lowThrust,highThrust,knob,finger]),"operationType":BooleanOperationType.UNION});''',
  ''' var rotorParts=[ring,cam,crownHub,lowThrust];
 if(flip) {
  // V4: the rotation limiter moves to the bottom of the rotor, flipped and thick (6 mm finger, below the lower bearing).
  rotorParts=append(rotorParts,radialBox(context,id+"limFinger",4,16,-3,3,-5.6,5.2,60*degree));
 } else {
  rotorParts=append(rotorParts,cylinderMM(context,id+"highThrust",7,65.5-dzT,67.5-dzT));
  rotorParts=append(rotorParts,cylinderMM(context,id+"knob",10,74-dzT,78-dzT));
  rotorParts=append(rotorParts,sector(context,id+"finger",8,16,4,74-dzT,4));
 }
 opBoolean(context,id+"rotorJoin",{"tools":qUnion(rotorParts),"operationType":BooleanOperationType.UNION});''')
P(''' var topBearing=tubeMM(context,id+"topBearing",18,5.4,68-dzT,73-dzT);
 var lowBearing=tubeMM(context,id+"lowBearing",8,5.4,definition.direct?-0.8:-15,definition.direct?2.2:-6);
 for(var i=0;i<4;i+=1) {
  var a=(45+i*90)*degree;
  var spoke=radialBox(context,id+("topSpoke"~i),15,31,-2.5,2.5,68-dzT,4,a);
  var lowSpoke=radialBox(context,id+("lowSpoke"~i),6,definition.direct?30.6:20,-2.5,2.5,definition.direct?-0.8:-15,definition.direct?3.0:4,a);
  opBoolean(context,id+("topSpokeJoin"~i),{"tools":qUnion([topBearing,spoke]),"operationType":BooleanOperationType.UNION});
  opBoolean(context,id+("lowSpokeJoin"~i),{"tools":qUnion([lowBearing,lowSpoke]),"operationType":BooleanOperationType.UNION});
 }
 opBoolean(context,id+"bearingsJoin",{"tools":qUnion([carrier,topBearing,lowBearing]),"operationType":BooleanOperationType.UNION});
 for(var j=0;j<2;j+=1) {
  var stop=sector(context,id+("knobStop"~j),12,18,4,72.5-dzT,5.9);
  turn(context,id+("knobStopTurn"~j),stop,(j==0?-8:73)*degree);
  opBoolean(context,id+("knobStopJoin"~j),{"tools":qUnion([carrier,stop]),"operationType":BooleanOperationType.UNION});
 }''',
  ''' var topBearing=undefined;
 if(!flip) topBearing=tubeMM(context,id+"topBearing",18,5.4,68-dzT,73-dzT);
 var lowBearing=tubeMM(context,id+"lowBearing",8,5.4,flip?0.4:(definition.direct?-0.8:-15),flip?3.4:(definition.direct?2.2:-6));
 for(var i=0;i<4;i+=1) {
  var a=(45+i*90)*degree;
  var lowSpoke=radialBox(context,id+("lowSpoke"~i),6,(flip||definition.direct)?30.6:20,-2.5,2.5,flip?0.4:(definition.direct?-0.8:-15),flip?3.0:(definition.direct?3.0:4),a);
  if(!flip) {
   var spoke=radialBox(context,id+("topSpoke"~i),15,31,-2.5,2.5,68-dzT,4,a);
   opBoolean(context,id+("topSpokeJoin"~i),{"tools":qUnion([topBearing,spoke]),"operationType":BooleanOperationType.UNION});
  }
  opBoolean(context,id+("lowSpokeJoin"~i),{"tools":qUnion([lowBearing,lowSpoke]),"operationType":BooleanOperationType.UNION});
 }
 opBoolean(context,id+"bearingsJoin",{"tools":qUnion(flip ? [carrier,lowBearing] : [carrier,topBearing,lowBearing]),"operationType":BooleanOperationType.UNION});
 if(!flip) for(var j=0;j<2;j+=1) {
  var stop=sector(context,id+("knobStop"~j),12,18,4,72.5-dzT,5.9);
  turn(context,id+("knobStopTurn"~j),stop,(j==0?-8:73)*degree);
  opBoolean(context,id+("knobStopJoin"~j),{"tools":qUnion([carrier,stop]),"operationType":BooleanOperationType.UNION});
 }''')
P('var camPocket=sector(context,id+("camRelief"~i),8,18,30,21.9,3.2);','var camPocket=sector(context,id+("camRelief"~i),8,18,30,flip?22.4:21.9,flip?5.7:3.2);')
P('subtract(context,id+"rotorLightBore",ring,cylinderMM(context,id+"rotorLightTool",3,-8,78.1-dzT));','subtract(context,id+"rotorLightBore",ring,cylinderMM(context,id+"rotorLightTool",3,flip?-7:-8,flip?41.6:78.1-dzT));')
P(' var armEnd=compact?24.1:30+dr;var armZ=compact?58.6-dzT:58.6;var capR=compact?20.4:24.3;',
  ' var armEnd=compact?24.1:30+dr;var armZ=flip?33.6:(compact?58.6-dzT:58.6);var capR=flip?19.5:(compact?20.4:24.3);')
P('var catchArm=radialBox(context,sub+"catchArm",6,armEnd,-2.5,2.5,armZ,3,0*degree);','var catchArm=radialBox(context,sub+"catchArm",6,armEnd,flip?-4:-2.5,flip?4:2.5,armZ,flip?5:3,0*degree);')
P('vector(0,0,1),armZ-0.6,armZ+3.6,M3_CLR);','vector(0,0,1),armZ-0.6,armZ+(flip?5.6:3.6),M3_CLR);')
P('catchCap=radialBox(context,sub+"catchCap",18.0,26.0,-4.2,4.2,35.4,5.4,0*degree);','catchCap=radialBox(context,sub+"catchCap",flip?16.5:18.0,26.0,flip?-7.2:-4.2,flip?7.2:4.2,flip?29.4:35.4,flip?9.5:5.4,0*degree);')
P('var catchFinger=radialBox(context,sub+"catchFinger",23.6,26.0,-3.0,3.0,40.8,5.2,0*degree);','var catchFinger=radialBox(context,sub+"catchFinger",23.6,26.0,-3.0,3.0,flip?38.9:40.8,flip?5.9:5.2,0*degree);')
P('var catchBoss=radialBox(context,sub+"catchBoss",18.0,24.2,-4.2,4.2,31.4,4.0,0*degree);','var catchBoss=radialBox(context,sub+"catchBoss",flip?16.5:18.0,flip?22.5:24.2,flip?-5.2:-4.2,flip?5.2:4.2,flip?28.6:31.4,flip?5.0:4.0,0*degree);')
P('catchSocket=radialBox(context,sub+"catchSocket",17.9,24.2,-2.75,2.75,36.4,5.0,0*degree);','catchSocket=radialBox(context,sub+"catchSocket",flip?16.4:17.9,24.2,flip?-4.3:-2.75,flip?4.3:2.75,flip?33.4:36.4,flip?6.0:5.0,0*degree);')
P('vector(0,0,1),compact?32.0:54.0,compact?36.5:58.5,M3_PILOT);','vector(0,0,1),flip?28.8:(compact?32.0:54.0),flip?33.5:(compact?36.5:58.5),M3_PILOT);')
P('var cs=screwHW(context,sub+"capScrew",vector(capR,0,armZ+3.0),vector(0,0,-1),"M3BH",8,"HW L"~(i+1)~" cap screw - M3x8 button head");',
  'var cs=screwHW(context,sub+"capScrew",vector(capR,0,armZ+(flip?5.0:3.0)),vector(0,0,-1),"M3BH",flip?10:8,"HW L"~(i+1)~" cap screw - "~(flip?"M3x10":"M3x8")~" button head");')
P(' // Four seam registration pins (slip fit; do not force). Split along 45 degrees, through fixed posts.',
  r''' if(flip) {
  // V4: SG90 flipped on top (shaft down). Ledges at azimuth 135 / 315 grow out of the support strips under its flange tabs.
  var esF=vector(cos(135*degree),sin(135*degree),0);
  for(var k=0;k<2;k+=1) {
   var hsF=k==0?18.8:-9.3;
   var ledge=radialBox(context,id+("servoLedge"~k),k==0?16.3:-30.6,k==0?30.6:-6.8,-3.5,3.5,45.1,4.3,135*degree);
   opBoolean(context,id+("servoLedgeJoin"~k),{"tools":qUnion([carrier,ledge]),"operationType":BooleanOperationType.UNION});
   drill(context,id+("ledgePilot"~k),carrier,vector(hsF*esF[0],hsF*esF[1],49.4),vector(0,0,-1),0,3.5,0.8);
   if(definition.hardware)
    screwHW(context,id+("servoScrew"~k),vector(hsF*esF[0],hsF*esF[1],51.9),vector(0,0,-1),"M2BH",6,"HW servo flange screw "~(k+1)~" - M2x6 button head");
  }
  // Rotation limiter stops (thick, 8 mm) at the bottom, hanging from the lower spokes. Faces are 0.4 mm clear of the 6 mm finger at both ends of the 65 deg travel.
  var limA=radialBox(context,id+"limStop1",10,19,-11,-3.4,-6.4,9.8,60*degree);
  var limB=radialBox(context,id+"limStop2",10,19,3.4,11,-6.4,9.8,125*degree);
  opBoolean(context,id+"limStop1Join",{"tools":qUnion([carrier,limA]),"operationType":BooleanOperationType.UNION});
  opBoolean(context,id+"limStop2Join",{"tools":qUnion([carrier,limB]),"operationType":BooleanOperationType.UNION});
  // Bay ceiling (wires come down the hollow rotor and through the centre hole), and four bosses that take the screws into the transition.
  var bayCeil=cylinderMM(context,id+"bayCeiling",30.5,-10,-8);
  opBoolean(context,id+"bayCeilingJoin",{"tools":qUnion([carrier,bayCeil]),"operationType":BooleanOperationType.UNION});
  subtract(context,id+"bayWireHole",carrier,cylinderMM(context,id+"bayWireTool",4,-10.1,-7.9));
  for(var k=0;k<4;k+=1) {
   var baz=(45+90*k)*degree;var bsub=id+("transBoss"~k);
   var tboss=radialBox(context,bsub,23.5,30.2,-4.5,4.5,-35.5,6.0,baz);
   opBoolean(context,bsub+"join",{"tools":qUnion([carrier,tboss]),"operationType":BooleanOperationType.UNION});
   var bp=vector(27*cos(baz),27*sin(baz),-29.5);
   drill(context,bsub+"cb",carrier,bp,vector(0,0,-1),0,2.0,3.1);
   drill(context,bsub+"clr",carrier,bp,vector(0,0,-1),0,6.2,1.7);
   if(definition.hardware)
    screwHW(context,bsub+"hw",vector(27*cos(baz),27*sin(baz),-31.5),vector(0,0,-1),"M3BH",12,"HW transition screw "~(k+1)~" - M3x12 button head");
  }
 }
 // Four seam registration pins (slip fit; do not force). Split along 45 degrees, through fixed posts.''')
P('annotation {"Name":"Module: 0 spring, 1 direct servo, 2 unloaded spring samples, 3 V3 servo straight on the rotor","Default":0} isInteger(definition.mode,{(unitless):[0,0,3]} as IntegerBoundSpec);',
  'annotation {"Name":"Module: 0 spring, 1 direct servo, 2 unloaded spring samples, 3 V3 servo straight on the rotor, 4 V4 servo on top","Default":0} isInteger(definition.mode,{(unitless):[0,0,4]} as IntegerBoundSpec);')
P('var a=(45+side*180)*degree;var r=level==0?24:29;var z=level==0?-13:(compact?53:65);','var a=(45+side*180)*degree;var r=level==0?(flip?28.5:24):29;var z=level==0?-13:(compact?53:65);')
P('"compact":definition.compact,"direct":definition.mode==3,"hardware"','"compact":definition.compact,"direct":definition.mode==3,"flip":definition.mode==4,"hardware"')
P(' stage="shaft extension";',
  r''' if(definition.mode==4) {
  stage="v4 rotor top";
  var es4=vector(cos(135*degree),sin(135*degree),0);
  // Horn pocket + arm slot open at the top of the rotor hub; the servo (with its horn) comes down from above.
  var pocketF=cylinderMM(context,id+"v4HornPocket",4.5,41.3,45.0);
  var slotF=radialBox(context,id+"v4HornSlot",0,13,-2.2,2.2,41.3,3.7,0*degree);
  try { opBoolean(context,id+"v4PocketJoin",{"tools":qUnion([pocketF,slotF]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"v4PocketJoin"); }
  turn(context,id+"v4PocketTurn",pocketF,(45+definition.release)*degree);
  subtract(context,id+"v4HornPocketCut",rotor,pocketF);
  label(context,rotor,"R Cam rotor - servo horn socket at the top, thick limiter finger at the bottom - 0 LOCK 65 OPEN",[.28,.68,.42]);
  var hornHubF=cylinderMM(context,id+"v4HornHub",4,41.5,43.3);
  var hornArmF=radialBox(context,id+"v4HornArm",0,11,-1.7,1.7,41.5,1.8,0*degree);
  try { opBoolean(context,id+"v4HornJoin",{"tools":qUnion([hornHubF,hornArmF]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"v4HornJoin"); }
  turn(context,id+"v4HornTurn",hornHubF,(45+definition.release)*degree);
  label(context,hornHubF,"EH SG90 horn REFERENCE - fit the socket to your actual horn",[.8,.69,.25]);
  if(definition.hardware)
   screwHW(context,id+"v4HornScrew",vector(0,0,41.5),vector(0,0,1),"M2BH",6,"HW horn screw - M2x6 (the one supplied with the servo), from below through the rotor bore");
  stage="v4 servo";
  var sBody4=radialBox(context,id+"v4ServoBody",-6.5,16.0,-6.1,6.1,45.2,22.7,135*degree);
  var sTab4=radialBox(context,id+"v4ServoTab",-11.5,21.0,-5.9,5.9,49.4,2.5,135*degree);
  var sSpl4=cylinderMM(context,id+"v4Spline",2.4,41.5,45.2);
  try { opBoolean(context,id+"v4ServoJoin",{"tools":qUnion([sBody4,sTab4,sSpl4]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"v4ServoJoin"); }
  for(var k=0;k<2;k+=1) {
   var hs4=k==0?18.8:-9.3;
   drill(context,id+("v4TabHole"~k),sBody4,vector(hs4*es4[0],hs4*es4[1],49.0),vector(0,0,1),0,3.6,1.1);
  }
  label(context,sBody4,"E SG90 servo REFERENCE - flipped on top, shaft down, flange screwed to the two housing ledges - measure your servo",[.35,.38,.43]);
  stage="v4 bay";
  // Electronics: Mercury V1 altimeter (30 x 16.9 x 10.8) and a 5 V regulator (25 x 15 x 8, placeholder) in the upper layer, a 2S LiPo (40 x 18 x 10, placeholder) in the lower layer.
  var merc=radialBox(context,id+"v4Mercury",-15,15,-17.45,-0.55,-21.2,10.8,0*degree);
  label(context,merc,"E2 Mercury V1 altimeter REFERENCE (30 x 16.9 x 10.8, Altimeter Cloud)",[.55,.35,.75]);
  var regu=radialBox(context,id+"v4Regulator",-12.5,12.5,2.5,17.5,-21.2,8.0,0*degree);
  label(context,regu,"E3 5 V 3 A regulator REFERENCE (placeholder 25 x 15 x 8)",[.94,.54,.63]);
  var batt=radialBox(context,id+"v4Battery",-20,20,-9,9,-34.5,10.0,0*degree);
  label(context,batt,"E4 Servo battery 2S LiPo REFERENCE (placeholder 40 x 18 x 10)",[.95,.83,.36]);
  // Electronics sled: slides in from below, held between the bay ceiling and the transition.
  // Skeletal sled: a block round the upper layer, a block round the battery, and four thin centring ribs; pockets cut after.
  var sled=radialBox(context,id+"v4SledA",-17.0,17.0,-19.2,19.2,-23.0,12.8,0*degree);
  var sledB=radialBox(context,id+"v4SledB",-22.4,22.4,-11.4,11.4,-35.3,14.3,0*degree);
  opBoolean(context,id+"v4SledJoinB",{"tools":qUnion([sled,sledB]),"operationType":BooleanOperationType.UNION});
  for(var k=0;k<4;k+=1) {
   var sribk=radialBox(context,id+("v4SledRib"~k),16,29.3,-1.0,1.0,-35.3,19.5,(90*k)*degree);
   opBoolean(context,id+("v4SledRibJoin"~k),{"tools":qUnion([sled,sribk]),"operationType":BooleanOperationType.UNION});
  }
  subtract(context,id+"v4SledPocketA1",sled,radialBox(context,id+"v4PocketA1",-15.2,15.2,-17.65,-0.35,-21.2,11.3,0*degree));
  subtract(context,id+"v4SledPocketA2",sled,radialBox(context,id+"v4PocketA2",-12.7,12.7,2.3,17.7,-21.2,11.3,0*degree));
  subtract(context,id+"v4SledPocketB",sled,radialBox(context,id+"v4PocketB",-20.4,20.4,-9.4,9.4,-35.4,10.9,0*degree));
  subtract(context,id+"v4SledWire",sled,cylinderMM(context,id+"v4SledWireTool",4,-24.6,-21.1));
  label(context,sled,"N Electronics sled - slides in from below, clamped between the bay ceiling and the transition",[.30,.60,.55]);
  // Transition on the BT80 side: bond inside the lower BT80 tube; the module is screwed down onto it.
  var trans=tubeMM(context,id+"v4TransTube",32.3,23.5,-43.5,-35.5);
  for(var k=0;k<4;k+=1) drill(context,id+("v4TransPilot"~k),trans,vector(27*cos((45+90*k)*degree),27*sin((45+90*k)*degree),-35.5),vector(0,0,-1),0,7.0,M3_PILOT);
  subtract(context,id+"v4TransWire",trans,atC(context,id+"v4TransWireTool",4,-43.6,-35.4,0,-26));
  label(context,trans,"T Transition ring (BT80 side) - bond inside the lower BT80 tube, 4 M3 pilots take the module screws",[.86,.78,.55]);
  if(definition.tubes) {
   var lt4=tubeMM(context,id+"lowerTube",33.02,32.5,-95,-15);
   label(context,lt4,"REF BT80 lower tube - bonded to the sleeve and the transition",TUBE_TAN);
  }
  return;
 }
 stage="shaft extension";''')

# ------------------------------------------------------------------ apply
import os
if os.environ.get('PATCH_LIMIT'): patches = patches[:int(os.environ['PATCH_LIMIT'])]
out = src
for old, new, cnt in patches:
    n = out.count(old)
    if n != cnt:
        print("PATCH MISMATCH (%d found, %d expected):\n%s" % (n, cnt, old[:200]))
        sys.exit(1)
    out = out.replace(old, new)

dest = ROOT / "fs" / "airbrake_v1_v2.fs"
dest.write_text(out)
print("wrote", dest, len(out), "chars,", out.count("\n"), "lines,", len(patches), "patches")
