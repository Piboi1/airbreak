FeatureScript 3095;
import(path : "onshape/std/geometry.fs", version : "3095.0");

// Cam kick-out airbrake, screwed assembly. V1 = inline housing, V2 = compact head inside the upper BT80 tube.
// All angles are physical, not a force simulation. Hardware: M3 self-tapping, M4 hinge screws.
function solid(id is Id) returns Query
{
    return qBodyType(qCreatedBy(id, EntityType.BODY), BodyType.SOLID);
}

function cylinderMM(context is Context, id is Id, radius is number, z0 is number, z1 is number) returns Query
{
    fCylinder(context, id, { "bottomCenter" : vector(0, 0, z0) * millimeter,
        "topCenter" : vector(0, 0, z1) * millimeter, "radius" : radius * millimeter });
    return solid(id);
}

function subtract(context is Context, id is Id, target is Query, tools is Query)
{
    try { opBoolean(context, id, { "targets" : target, "tools" : tools,
        "operationType" : BooleanOperationType.SUBTRACTION }); } catch { throw regenError("Subtraction failed at " ~ id); }
}

function tubeMM(context is Context, id is Id, ro is number, ri is number, z0 is number, z1 is number) returns Query
{
    var outer = cylinderMM(context, id + "outer", ro, z0, z1);
    var inner = cylinderMM(context, id + "inner", ri, z0 - 0.1, z1 + 0.1);
    subtract(context, id + "bore", outer, inner);
    return outer;
}

function polygonMM(context is Context, id is Id, points is array, z is number, height is number) returns Query
{
    var verts = [];
    for (var p in points)
        verts = append(verts, p * millimeter);
    verts = append(verts, verts[0]);
    var sketch = newSketchOnPlane(context, id + "sketch", {
        "sketchPlane" : plane(vector(0, 0, z) * millimeter, vector(0, 0, 1), vector(1, 0, 0)) });
    skPolyline(sketch, "outline", { "points" : verts });
    skSolve(sketch);
    opExtrude(context, id + "extrude", { "entities" : qSketchRegion(id + "sketch"),
        "direction" : vector(0, 0, 1), "endBound" : BoundingType.BLIND,
        "endDepth" : height * millimeter });
    opDeleteBodies(context, id + "deleteSketch", { "entities" : qCreatedBy(id + "sketch", EntityType.BODY) });
    return solid(id + "extrude");
}

function rotate2(p is Vector, angle is ValueWithUnits) returns Vector
{
    return vector(p[0] * cos(angle) - p[1] * sin(angle), p[0] * sin(angle) + p[1] * cos(angle));
}

function radialBox(context is Context, id is Id, r0 is number, r1 is number,
    y0 is number, y1 is number, z is number, h is number, angle is ValueWithUnits) returns Query
{
    var points = [];
    for (var p in [vector(r0, y0), vector(r1, y0), vector(r1, y1), vector(r0, y1)])
        points = append(points, rotate2(p, angle));
    return polygonMM(context, id, points, z, h);
}

function label(context is Context, q is Query, name is string, rgb is array)
{
    setProperty(context, { "entities" : q, "propertyType" : PropertyType.NAME, "value" : name });
    setProperty(context, { "entities" : q, "propertyType" : PropertyType.APPEARANCE,
        "value" : color(rgb[0], rgb[1], rgb[2]) });
}



function yc(context is Context,id is Id,r is number,y0 is number,y1 is number) returns Query {
 fCylinder(context,id,{"bottomCenter":vector(25,y0,0)*millimeter,"topCenter":vector(25,y1,0)*millimeter,"radius":r*millimeter});return solid(id);
}
function sector(context is Context,id is Id,ri is number,ro is number,half is number,z is number,h is number) returns Query {
 var pts=[];
 for(var k=0;k<=80;k+=1) {var t=(-half+2*half*k/80)*degree;pts=append(pts,vector(ro*cos(t),ro*sin(t)));}
 for(var k=80;k>=0;k-=1) {var t=(-half+2*half*k/80)*degree;pts=append(pts,vector(ri*cos(t),ri*sin(t)));}
 return polygonMM(context,id,pts,z,h);
}
function arcRootBrace(context is Context,id is Id) returns Query {
 var sk=newSketchOnPlane(context,id+"sk",{"sketchPlane":plane(vector(0,7,0)*millimeter,vector(0,-1,0),vector(1,0,0))});
 var points=[];for(var p in [vector(25.5,1.5),vector(31.5,4),vector(31.5,18),vector(25.5,5),vector(25.5,1.5)]) points=append(points,p*millimeter);
 skPolyline(sk,"p",{"points":points});skSolve(sk);
 opExtrude(context,id+"ex",{"entities":qSketchRegion(id+"sk"),"direction":vector(0,-1,0),"endBound":BoundingType.BLIND,"endDepth":14*millimeter});
 opDeleteBodies(context,id+"del",{"entities":qCreatedBy(id+"sk",EntityType.BODY)});return solid(id+"ex");
}
function turn(context is Context,id is Id,b is Query,a is ValueWithUnits) {
 opTransform(context,id,{"bodies":b,"transform":rotationAround(line(vector(0,0,0)*millimeter,vector(0,0,1)),a)});
}
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
    if (kind == "M2BH")
    {
        hr = 2.0;
        hh = 1.3;
        sr = 1.0;
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

annotation { "Feature Type Name" : "Positive cam kick-out and cord-limited BT80 airbrake" }
export const camKickBrake = defineFeature(function(context is Context,id is Id,definition is map)
 precondition {
  annotation { "Name" : "Opening angle (degrees)", "Default" : 0 }
  isReal(definition.opening, { (unitless) : [0,0,90] } as RealBoundSpec);
  annotation { "Name" : "Top knob rotation - 0 locked, 65 kick", "Default" : 0 }
  isReal(definition.release, { (unitless) : [0,0,65] } as RealBoundSpec);
  annotation { "Name" : "Show cord reference lines", "Default" : false }
  definition.cords is boolean;
  annotation { "Name" : "V2 compact head (fins inside upper BT80 tube)", "Default" : false }
  definition.compact is boolean;
  annotation { "Name" : "V3 servo posts and tube pads", "Default" : false }
  definition.direct is boolean;
  annotation { "Name" : "V4 servo on top, bay at the bottom", "Default" : false }
  definition.flip is boolean;
  annotation { "Name" : "Show fastener hardware", "Default" : true }
  definition.hardware is boolean;
  annotation { "Name" : "Show BT80 tube references and cut-out pieces", "Default" : true }
  definition.tubes is boolean;
 }
 {
 var blue=[.18,.45,.65];var orange=[.95,.46,.12];var gold=[.8,.69,.25];
 var compact=definition.compact;
 var flip=definition.flip;
 // V2: the outer skin group (housing wall, fins, hook, stops) moves in 0.72 mm so the fin outer face is 64.6 mm OD
 // and the glued 0.52 mm BT80 cut-out brings it back to 66.04 mm.
 var dr=compact?-0.72:0;
 var rOut=33.02+dr;
 var camMax=compact?28.6:29;
 // V2: the latch stack (hook, crown arms, top bearing, knob) drops 22 mm into the fin height; the catch is an inward lug on the fin.
 var dzT=compact?22:0;
 var topZ=compact?58.8:67;
 // Inline BT80 housing. Two 18 mm glue shoulders, 64.6 mm OD.
 var carrier=tubeMM(context,id+"carrier",rOut,30.2+dr,-15,topZ);
 var base=tubeMM(context,id+"base",33.02,flip?26:18,-15,-11);
 var lower=tubeMM(context,id+"lowerShoulder",32.3,29.9,flip?-35.5:-33,-14.9);
 var joinParts=[carrier,base,lower];
 if(!compact) joinParts=append(joinParts,tubeMM(context,id+"upperShoulder",32.3,29.9,66.9,85));
 opBoolean(context,id+"baseJoin",{"tools":qUnion(joinParts),"operationType":BooleanOperationType.UNION});
 // Inward belt preserves a substantial fixed load path behind the recessed hook track.
 if(!compact) {
  var catchBelt=tubeMM(context,id+"recessCatchBelt",31+dr,28.4+dr,54.6,57.4);
  opBoolean(context,id+"recessCatchBeltJoin",{"tools":qUnion([carrier,catchBelt]),"operationType":BooleanOperationType.UNION});
 }
 // Single rotor: 10 mm shaft, root cams, top capture crown, accessible knob.
 var ring=cylinderMM(context,id+"rotorShaft",5,flip?-6.4:(definition.direct?-8.7:-10.5),flip?44.6:78-dzT);
 var points=[];
 for(var k=0;k<720;k+=1) {
  var theta=k*.5;var phase=90-(theta%90);if(phase==90) phase=0;
  var r=21.0;
  if(phase>24 && phase<60) r=21+(camMax-21)*(phase-24)/36;
  if(phase>=60 && phase<=66) r=camMax;
  if(phase>66 && phase<78) r=camMax-(camMax-21)*(phase-66)/12;
  points=append(points,vector(r*cos(theta*degree),r*sin(theta*degree)));
 }
 var cam=polygonMM(context,id+"camProfile",points,flip?22.5:22,flip?5.5:3);
 var crownHub=cylinderMM(context,id+"crownHub",9,flip?33.6:58.6-dzT,flip?44.6:61.6-dzT);
 var lowThrust=cylinderMM(context,id+"lowThrust",7,flip?3.9:(definition.direct?2.7:-5.5),flip?5.9:(definition.direct?4.7:-3.5));
 var rotorParts=[ring,cam,crownHub,lowThrust];
 if(flip) {
  // V4: the rotation limiter moves to the bottom of the rotor, flipped and thick (6 mm finger, below the lower bearing).
  rotorParts=append(rotorParts,radialBox(context,id+"limFinger",4,16,-3,3,-5.6,5.2,60*degree));
 } else {
  rotorParts=append(rotorParts,cylinderMM(context,id+"highThrust",7,65.5-dzT,67.5-dzT));
  rotorParts=append(rotorParts,cylinderMM(context,id+"knob",10,74-dzT,78-dzT));
  rotorParts=append(rotorParts,sector(context,id+"finger",8,16,4,74-dzT,4));
 }
 opBoolean(context,id+"rotorJoin",{"tools":qUnion(rotorParts),"operationType":BooleanOperationType.UNION});
 // Split fixed bearing bridge and bottom bearing, assembled around the rotor.
 var topBearing=undefined;
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
 }
 for(var i=0;i<4;i+=1) {
  var sub=id+("panel"~i);var a=i*90*degree;
  var window=sector(context,sub+"window",29.5+dr,34,33.5,-9.2,63.8);
  turn(context,sub+"windowTurn",window,a);subtract(context,sub+"windowCut",carrier,window);
  // A narrow passage admits only the raised panel tab through the fixed upper rim.
  if(!compact) {
   var tipSlot=sector(context,sub+"tipSlot",27.6+dr,38,8,50.8,8.6);
   turn(context,sub+"tipSlotTurn",tipSlot,a);subtract(context,sub+"tipSlotCut",carrier,tipSlot);
   // Crown arms sweep above the fixed anchor belt; four remaining pillars carry the top.
   var sweepSlot=sector(context,sub+"crownSlot",29.5+dr,37,41,57.3,6.1);
   turn(context,sub+"crownSlotTurn",sweepSlot,a+32.5*degree);
   subtract(context,sub+"crownSlotCut",carrier,sweepSlot);
  }
  var armEnd=compact?24.1:30+dr;var armZ=flip?33.6:(compact?58.6-dzT:58.6);var capR=flip?19.5:(compact?20.4:24.3);
  var catchArm=radialBox(context,sub+"catchArm",6,armEnd,flip?-4:-2.5,flip?4:2.5,armZ,flip?5:3,0*degree);
  turn(context,sub+"catchTurn",catchArm,a);
  opBoolean(context,sub+"rotorCatchJoin",{"tools":qUnion([ring,catchArm]),"operationType":BooleanOperationType.UNION});
  // M3 clearance hole through the rotor arm for the cap screw (axis Z).
  drill(context,sub+"armHole",ring,vector(capR*cos(a),capR*sin(a),0),vector(0,0,1),armZ-0.6,armZ+(flip?5.6:3.6),M3_CLR);
  // Open-top clip: the arm drops into the socket with the housing halves open; a boss under the arm takes the screw.
  var catchCap=undefined;var catchSocket=undefined;
  if(compact) {
   // V2: hook finger stands inside R26 and hooks the lug on the fin from inside (see fin lug), so it clears the fin shell.
   catchCap=radialBox(context,sub+"catchCap",flip?16.5:18.0,26.0,flip?-7.2:-4.2,flip?7.2:4.2,flip?29.4:35.4,flip?9.5:5.4,0*degree);
   var catchFinger=radialBox(context,sub+"catchFinger",23.6,26.0,-3.0,3.0,flip?38.9:40.8,flip?5.9:5.2,0*degree);
   var catchBoss=radialBox(context,sub+"catchBoss",flip?16.5:18.0,flip?22.5:24.2,flip?-5.2:-4.2,flip?5.2:4.2,flip?28.6:31.4,flip?5.0:4.0,0*degree);
   opBoolean(context,sub+"catchJoin",{"tools":qUnion([catchCap,catchFinger,catchBoss]),"operationType":BooleanOperationType.UNION});
   catchSocket=radialBox(context,sub+"catchSocket",flip?16.4:17.9,24.2,flip?-4.3:-2.75,flip?4.3:2.75,flip?33.4:36.4,flip?6.0:5.0,0*degree);
  } else {
   catchCap=radialBox(context,sub+"catchCap",22,32.6+dr,-4.2,4.2,57.4,5.4,0*degree);
   var catchHook=sector(context,sub+"catchHook",30.9+dr,32.8+dr,5.2,55.2,5.0);
   var catchBoss=radialBox(context,sub+"catchBoss",21.8,26.6,-4.2,4.2,53.4,4.0,0*degree);
   opBoolean(context,sub+"catchJoin",{"tools":qUnion([catchCap,catchHook,catchBoss]),"operationType":BooleanOperationType.UNION});
   catchSocket=radialBox(context,sub+"catchSocket",21.9,30.4+dr,-2.75,2.75,58.4,5.0,0*degree);
  }
  subtract(context,sub+"catchSocketCut",catchCap,catchSocket);
  drill(context,sub+"capPilot",catchCap,vector(capR,0,0),vector(0,0,1),flip?28.8:(compact?32.0:54.0),flip?33.5:(compact?36.5:58.5),M3_PILOT);
  turn(context,sub+"capPosition",catchCap,a+definition.release*degree);
  label(context,catchCap,"L"~(i+1)~(compact?" Catch cap - open-top clip with inner hook finger, 1 x M3x8 screw to rotor arm":" Catch cap - open-top clip, 1 x M3x8 screw to rotor arm"),[.20,.58,.34]);
  if(definition.hardware) {
   var cs=screwHW(context,sub+"capScrew",vector(capR,0,armZ+(flip?5.0:3.0)),vector(0,0,-1),"M3BH",flip?10:8,"HW L"~(i+1)~" cap screw - "~(flip?"M3x10":"M3x8")~" button head");
   turn(context,sub+"capScrewTurn",cs,a+definition.release*degree);
  }
  var ears=[];
  for(var j=0;j<2;j+=1) {
   var y0=j==0?-12:7.8;var y1=y0+4.2;
   var ear=yc(context,sub+("ear"~j),5.2,y0,y1);
   var arm=radialBox(context,sub+("arm"~j),20.5,28.5,y0,y1,-15,15,0*degree);
   opBoolean(context,sub+("earJoin"~j),{"tools":qUnion([ear,arm]),"operationType":BooleanOperationType.UNION});
   subtract(context,sub+("earBore"~j),ear,yc(context,sub+("earTool"~j),(j==0?M4_CLR:M4_PILOT),y0-.1,y1+.1));
   ears=append(ears,ear);
  }
  var stop=radialBox(context,sub+"stop",22,28,-13,13,-15,8.5,0*degree);
  opBoolean(context,sub+"bracketJoin",{"tools":qUnion(append(ears,stop)),"operationType":BooleanOperationType.UNION});
  var stopPad=radialBox(context,sub+"wideStop",26,28.8,-7,7,-15,8.5,0*degree);
  opBoolean(context,sub+"wideStopJoin",{"tools":qUnion([ears[0],stopPad]),"operationType":BooleanOperationType.UNION});
  var outerStop=radialBox(context,sub+"outerCompressionStop",27,32.8+dr,-6,6,-15,7.6,0*degree);
  opBoolean(context,sub+"outerStopJoin",{"tools":qUnion([ears[0],outerStop]),"operationType":BooleanOperationType.UNION});
  var bracket=ears[0];turn(context,sub+"bracketTurn",bracket,a);
  opBoolean(context,sub+"carrierJoin",{"tools":qUnion([carrier,bracket]),"operationType":BooleanOperationType.UNION});
  var panel=sector(context,sub+"shell",30.62+dr,rOut,32.5,4,50);
  var barrel=yc(context,sub+"barrel",4.8, -7.4,7.4);
  var web=radialBox(context,sub+"web",24,31.5,-7.4,7.4,0,10,0*degree);
  var pad=sector(context,sub+"rootPad",28.8,31.3,22,4,14);
  var brace=arcRootBrace(context,sub+"brace");
  opBoolean(context,sub+"leafJoin",{"tools":qUnion([panel,barrel,web,pad,brace]),"operationType":BooleanOperationType.UNION});
  // A recessed flat root landing transfers 90-degree load to the broad outer stop.
  var landing=radialBox(context,sub+"landing",29,32.4+dr,-6,6,4,4,0*degree);
  opBoolean(context,sub+"landingJoin",{"tools":qUnion([panel,landing]),"operationType":BooleanOperationType.UNION});
  subtract(context,sub+"landingFlat",panel,radialBox(context,sub+"landingTool",32.4+dr,35,-6,6,4,4,0*degree));
  subtract(context,sub+"leafBore",panel,yc(context,sub+"leafTool",M4_CLR,-7.5,7.5));
  subtract(context,sub+"earClearA",panel,yc(context,sub+"earClearToolA",5.5,-12.3,-7.7));
  subtract(context,sub+"earClearB",panel,yc(context,sub+"earClearToolB",5.5,7.7,12.3));
  // Set the narrow held tab 2.6 mm inward; retain full thickness with a stepped root.
  var tip=undefined;
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
  }
  // Broad inward follower: root cam acts here, well below the airflow opening.
  var follower=radialBox(context,sub+"follower",23,31.3,-4,4,20,9,0*degree);
  opBoolean(context,sub+"solidPanelJoin",{"tools":qUnion([panel,tip,follower]),"operationType":BooleanOperationType.UNION});
  opTransform(context,sub+"open",{"bodies":panel,"transform":rotationAround(line(vector(25,0,0)*millimeter,vector(0,1,0)),definition.opening*degree)});
  turn(context,sub+"leafTurn",panel,a);
  label(context,panel,"P"~(i+1)~" Cam-driven BT80 panel - solid shell - reinforced root - 90 degree stop",orange);
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
  }
 }
 // Clear the complete hook path AFTER fixed cord anchors have been joined.
 for(var i=0;i<(compact?0:4);i+=1) {
  var sub=id+("finalHookTrack"~i);var a=i*90*degree;
  // Recessed hook travels inside the skin; leave the inner belt intact.
  var hookTrack=sector(context,sub+"recessHookTrack",30.65+dr,34,40,55.0,2.5);
  turn(context,sub+"recessHookTrackTurn",hookTrack,a+32.5*degree);
  subtract(context,sub+"recessHookTrackCut",carrier,hookTrack);
 }
 // Local access pockets for larger pin heads and deep caps, inside the tube envelope.
 for(var i=0;i<4;i+=1) {
  var a=i*90*degree;
  var h=yc(context,id+("headPocket"~i),4.2,-15.0,-12.0);
  turn(context,id+("hpTurn"~i),h,a);
  subtract(context,id+("hpCut"~i),carrier,h);
 }
 // Lightweight internal relief. Exterior skins, hinge brackets and stop faces remain.
 for(var i=0;i<8;i+=1) {
  var a=(22.5+45*i)*degree;
  // Leave axial ribs and full end bands on the tube glue shoulders.
  if(!compact) {
   var up=sector(context,id+("upperRelief"~i),29.8,30.7,17,69,13.5);
   turn(context,id+("upperReliefTurn"~i),up,a);subtract(context,id+("upperReliefCut"~i),carrier,up);
  }
  // Lower collar bond occupies z=-35..-20; do not thin that interface.
  var lo=sector(context,id+("lowerRelief"~i),29.8,30.7,17,-19.5,3);
  turn(context,id+("lowerReliefTurn"~i),lo,a);subtract(context,id+("lowerReliefCut"~i),carrier,lo);
 }
 for(var i=0;i<4;i+=1) {
  var a=i*90*degree;
  // Bearing diaphragm has a 2 mm skin, radial spokes and a full shaft boss.
  var topPocket=sector(context,id+("bearingRelief"~i),8.5,15.5,29,70-dzT,3.1);
  turn(context,id+("bearingReliefTurn"~i),topPocket,a);subtract(context,id+("bearingReliefCut"~i),carrier,topPocket);
  // Between hinge brackets: blind underside pockets leave a 2 mm base skin.
  var bottomPocket=sector(context,id+("baseRelief"~i),18.5,29,15,-15.1,2.1);
  turn(context,id+("baseReliefTurn"~i),bottomPocket,a+45*degree);subtract(context,id+("baseReliefCut"~i),carrier,bottomPocket);
  // Remove only the central underside of each stop block; retain a 3.5 mm roof.
  var pocket=radialBox(context,id+("stopRelief"~i),23.5,26.5,-8,8,-15.1,5.1,a);
  subtract(context,id+("stopReliefCut"~i),carrier,pocket);
  // Cam windows leave an 8 mm hub, four spokes and at least 3 mm outer track.
  var camPocket=sector(context,id+("camRelief"~i),8,18,30,flip?22.4:21.9,flip?5.7:3.2);
  turn(context,id+("camReliefTurn"~i),camPocket,a);subtract(context,id+("camReliefCut"~i),ring,camPocket);
 }
 // Open axial bore is printable without trapped support; solid D extension is added later.
 subtract(context,id+"rotorLightBore",ring,cylinderMM(context,id+"rotorLightTool",3,flip?-7:-8,flip?41.6:78.1-dzT));
 // ---- screw bosses: seam clamp ribs, V1 sleeve pads, V2 thick supports between the fins ----
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
 if(definition.direct) {
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
 if(flip) {
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
 // Four seam registration pins (slip fit; do not force). Split along 45 degrees, through fixed posts.
 for(var side=0;side<2;side+=1) {
  var a=(45+side*180)*degree;
  var seamBoss=radialBox(context,id+("seamBoss"~side),26,32.5+dr,-3.5,3.5,compact?51.5:63.5,3.5,a);
  opBoolean(context,id+("seamBossJoin"~side),{"tools":qUnion([carrier,seamBoss]),"operationType":BooleanOperationType.UNION});
 }
 var seamNormal=normalize(vector(1,-1,0));
 opSplitPart(context,id+"housingSplit",{"targets":carrier,"tool":plane(vector(0,0,0)*millimeter,seamNormal)});
 var halves=evaluateQuery(context,carrier);
 for(var j=0;j<size(halves);j+=1) label(context,halves[j],"C"~(j+1)~" Split BT80 housing - clamp with 4 x M3 seam screws, peg-aligned",blue);
 // Identify the two sides using their volume centroids, independent of topology order.
 var negative=halves[0];var positive=halves[1];
 if(dot(evApproximateCentroid(context,{"entities":negative})/millimeter,seamNormal)>0) {negative=halves[1];positive=halves[0];}
 for(var side=0;side<2;side+=1) for(var level=0;level<2;level+=1) {
  var a=(45+side*180)*degree;var r=level==0?(flip?28.5:24):29;var z=level==0?-13:(compact?53:65);
  var p=vector(r*cos(a),r*sin(a),z);var sub=id+("key"~side~level);
  fCylinder(context,sub+"peg",{"bottomCenter":(p-1.6*seamNormal)*millimeter,"topCenter":(p+2.2*seamNormal)*millimeter,"radius":1.5*millimeter});
  opBoolean(context,sub+"pegJoin",{"tools":qUnion([negative,solid(sub+"peg")]),"operationType":BooleanOperationType.UNION});
  fCylinder(context,sub+"socket",{"bottomCenter":(p-.1*seamNormal)*millimeter,"topCenter":(p+2.6*seamNormal)*millimeter,"radius":1.8*millimeter});
  subtract(context,sub+"socketCut",positive,solid(sub+"socket"));
 }
 // Seam clamp screws: counterbore + clearance in the negative half, thread-forming pilot in the positive half.
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
 turn(context,id+"releaseTurn",ring,definition.release*degree);
 label(context,ring,"R Top knob + keyed crown arms + four kick cams - 0 LOCK 65 OPEN",[.28,.68,.42]);
 // Reference lines are schematic loaded cord paths, not printable parts or elastic ropes.
 if(definition.cords) for(var i=0;i<4;i+=1) for(var side=0;side<2;side+=1) {
  var a=i*90*degree;var sign=side==0?-1:1;var t=definition.opening*degree;
  var xp=25+2*cos(t)+40*sin(t);var zp=-2*sin(t)+40*cos(t);
  var start=vector(25.3*cos(a)-sign*12*sin(a),25.3*sin(a)+sign*12*cos(a),52)*millimeter;
  var end=vector(xp*cos(a)-sign*13.5*sin(a),xp*sin(a)+sign*13.5*cos(a),zp)*millimeter;
  fCylinder(context,id+("cordRef"~i~"s"~side),{"bottomCenter":start,"topCenter":end,"radius":.35*millimeter});
  label(context,solid(id+("cordRef"~i~"s"~side)),"V CORD REFERENCE - not for printing",[.7,.2,.65]);
 }
 });

function atC(context is Context,id is Id,r is number,z0 is number,z1 is number,x is number,y is number) returns Query {
 fCylinder(context,id,{"bottomCenter":vector(x,y,z0)*millimeter,"topCenter":vector(x,y,z1)*millimeter,"radius":r*millimeter});return solid(id);
}
function dKey(context is Context,id is Id,r is number,flat is number,z0 is number,z1 is number) returns Query {
 var b=cylinderMM(context,id+"body",r,z0,z1);
 subtract(context,id+"flatCut",b,radialBox(context,id+"flat",flat,r+1,-r-1,r+1,z0-.1,z1-z0+.2,0*degree));return b;
}
function springCore(context is Context,id is Id,q is number,t is number,printable is boolean) returns Query {
 var frame=tubeMM(context,id+"rim",20.5,19,90,98);
 var hub=cylinderMM(context,id+"hub",10,90,98);
 var left=[];var right=[];
 for(var k=0;k<=240;k+=1) {
  var u=k/240;var r=10.5+7.5*u;var a=(720*u+q*(1-u))*degree;var da=(720-q)*degree/radian;
  var tangent=vector(7.5*cos(a)-r*da*sin(a),7.5*sin(a)+r*da*cos(a));var n=normalize(vector(-tangent[1],tangent[0]));var p=vector(r*cos(a),r*sin(a));
  left=append(left,p+t/2*n);right=append(right,p-t/2*n);
 }
 var outline=left;for(var k=size(right)-1;k>=0;k-=1)outline=append(outline,right[k]);
 var beam=polygonMM(context,id+"beam",outline,90,8);
 var anchor=radialBox(context,id+"anchor",17,20.4,-2,2,90,8,0*degree);
 try { opBoolean(context,id+"join",{"tools":qUnion([frame,hub,beam,anchor]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"join"); }
 var key=dKey(context,id+"socket",6.3,5.1,89.9,98.1);turn(context,id+"keyTurn",key,q*degree);subtract(context,id+"socketCut",frame,key);
 for(var k=0;k<3;k+=1) {
  var tab=radialBox(context,id+("tab"~k),19.5,21.7,-1.4,1.4,90,8,k*120*degree);
  try { opBoolean(context,id+("tabJoin"~k),{"tools":qUnion([frame,tab]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+("tabJoin"~k)); }
 }
 label(context,frame,(printable?"S UNLOADED PRINTABLE spiral - ":"V LOADED SPIRAL REFERENCE - NOT FOR PRINT - ")~t~" mm beam",[.58,.35,.8]);return frame;
}
function returnLeaf(context is Context,id is Id,stroke is number) returns Query {
 var dir=normalize(vector(24,19,0));var normal=normalize(vector(19,-24,0));var length=sqrt(24*24+19*19);
 var points=[];
 for(var k=0;k<=40;k+=1) {var t=k/40;points=append(points,vector(length*t,-stroke*(3*t*t-t*t*t)/2)*millimeter);}
 for(var k=40;k>=0;k-=1) {var t=k/40;points=append(points,vector(length*t,.8-stroke*(3*t*t-t*t*t)/2)*millimeter);}
 points=append(points,points[0]);
 var sk=newSketchOnPlane(context,id+"sk",{"sketchPlane":plane((vector(-6,-19,121)-normal*3.5)*millimeter,normal,dir)});
 skPolyline(sk,"p",{"points":points});skSolve(sk);
 opExtrude(context,id+"ex",{"entities":qSketchRegion(id+"sk"),"direction":normal,"endBound":BoundingType.BLIND,"endDepth":7*millimeter});
 opDeleteBodies(context,id+"del",{"entities":qCreatedBy(id+"sk",EntityType.BODY)});
 var b=solid(id+"ex");subtract(context,id+"fork",b,atC(context,id+"forkTool",2.4,115,123,18,0));
 label(context,b,"W Button return leaf - flat at rest - elastic motion not solved",[.58,.35,.8]);return b;
}
annotation { "Feature Type Name" : "BT80 modular spring or direct SG90 drive" }
export const modularBrake = defineFeature(function(context is Context,id is Id,definition is map)
 precondition {
  annotation {"Name":"Module: 0 spring, 1 direct servo, 2 unloaded spring samples, 3 V3 servo straight on the rotor, 4 V4 servo on top","Default":0} isInteger(definition.mode,{(unitless):[0,0,4]} as IntegerBoundSpec);
  annotation {"Name":"Panel opening degrees","Default":0} isReal(definition.opening,{(unitless):[0,0,90]} as RealBoundSpec);
  annotation {"Name":"Drive rotation degrees","Default":0} isReal(definition.release,{(unitless):[0,0,65]} as RealBoundSpec);
  annotation {"Name":"Upward trigger stroke mm","Default":0} isReal(definition.button,{(unitless):[0,0,4.5]} as RealBoundSpec);
  annotation {"Name":"V2 compact head (fins inside upper BT80 tube)","Default":false} definition.compact is boolean;
  annotation {"Name":"Show fastener hardware","Default":true} definition.hardware is boolean;
  annotation {"Name":"Show BT80 tube references and cut-out pieces","Default":true} definition.tubes is boolean;
 }
 {
 var stage="initial";var rpAz=[90,200,340];try {
 if(definition.mode==2) {
  for(var k=0;k<3;k+=1) {
   var b=springCore(context,id+("sample"~k),90,1.6+.4*k,true);
   opTransform(context,id+("sampleMove"~k),{"bodies":b,"transform":transform(vector(65*k,0,-90)*millimeter)});
  }
  var leaf=returnLeaf(context,id+"unloadedReturn",1);
  label(context,leaf,"W UNLOADED return leaf - 1 mm installation preload - bond root only",[.58,.35,.8]);
  opTransform(context,id+"unloadedReturnMove",{"bodies":leaf,"transform":transform(vector(195,0,-120)*millimeter)});
  return;
 }
 stage="base feature";
 camKickBrake(context,id+"brake",{"opening":definition.opening,"release":definition.release,"cords":false,
  "compact":definition.compact,"direct":definition.mode==3,"flip":definition.mode==4,"hardware":definition.hardware,"tubes":definition.tubes});
 stage="base query";
 var baseBodies=qUnion(evaluateQuery(context,qBodyType(qEverything(EntityType.BODY),BodyType.SOLID)));
 var rotor=solid(id+"brake"+"rotorShaft");
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
 if(definition.mode==4) {
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
 stage="shaft extension";
 var key=dKey(context,id+"commonKey",5,3.8,-24,-10.4);turn(context,id+"commonKeyTurn",key,definition.release*degree);
 try { opBoolean(context,id+"commonKeyJoin",{"tools":qUnion([rotor,key]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"commonKeyJoin"); }
 label(context,rotor,"R Ribbed lightweight cam rotor - 2 mm shaft wall - solid bottom D-drive",[.28,.68,.42]);
 // Stationary common dock. Bond its four feet onto the fixed bearing bridge.
 stage="dock";
 var dock=tubeMM(context,id+"dock",29.5,27.8,80,94);
 for(var k=0;k<4;k+=1) {
  var a=(45+90*k)*degree;
  var foot=radialBox(context,id+("dockFoot"~k),30,32,-2.5,2.5,75.5,35.5,a);
  var bridge=radialBox(context,id+("dockBridge"~k),27,32,-2.5,2.5,80,3,a);
  var top=radialBox(context,id+("dockTop"~k),27,32,-2.5,2.5,108,3,a);
  opBoolean(context,id+("dockFootJoin"~k),{"tools":qUnion([dock,foot,bridge,top]),"operationType":BooleanOperationType.UNION});
 }
 var bondRing=tubeMM(context,id+"dockBondRing",29.4,26.8,110,125);
 opBoolean(context,id+"dockBondJoin",{"tools":qUnion([dock,bondRing]),"operationType":BooleanOperationType.UNION});
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
 for(var k=0;k<4;k+=1) radialDrill(context,id+("footHole"~k),dock,(45+90*k)*degree,77.8,29.6,32.6,M3_CLR);
 subtract(context,id+"bayonetChannel",dock,tubeMM(context,id+"channelTool",30,28.5,89.5,92.5));
 for(var k=0;k<3;k+=1) {
  var slot=sector(context,id+("entry"~k),26.8,30,8,89.4,4.7);turn(context,id+("entryTurn"~k),slot,k*90*degree);subtract(context,id+("entryCut"~k),dock,slot);
 }
 subtract(context,id+"indexSlot",dock,radialBox(context,id+"indexTool",26.8,30,-2.3,2.3,83.8,10.3,180*degree));
 stage="retainer";
 var lock=tubeMM(context,id+"lockRing",32,30,88,98.5);
 var flange=tubeMM(context,id+"lockFlange",32,27.8,96.5,98.5);
 try { opBoolean(context,id+"lockFlangeJoin",{"tools":qUnion([lock,flange]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"lockFlangeJoin"); }
 for(var k=0;k<3;k+=1) {
  var lug=sector(context,id+("lockLug"~k),28.8,30.5,6,90,2);turn(context,id+("lockLugTurn"~k),lug,(20+90*k)*degree);
  try { opBoolean(context,id+("lockLugJoin"~k),{"tools":qUnion([lock,lug]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+("lockLugJoin"~k)); }
 }
 for(var k=0;k<4;k+=1) {
 var tool=sector(context,id+("legTool"~k),29.7,33,16,87.9,10.8);
 turn(context,id+("legToolTurn"~k),tool,(55+90*k)*degree);
 subtract(context,id+("legClear"~k),lock,tool);
 }

 var px=28.7*cos(90*degree);var py=28.7*sin(90*degree);
 subtract(context,id+"dockLockHole",dock,atC(context,id+"dockDrill",1.9,92.4,94.1,px,py));
 subtract(context,id+"ringLockHole",lock,atC(context,id+"ringDrill",1.9,89,99,px,py));
 var lockPin=atC(context,id+"lockPin",1.6,92.8,99,px,py);
 var pinHead=atC(context,id+"lockHead",3.2,98.6,99.8,px,py);
 try { opBoolean(context,id+"lockPinJoin",{"tools":qUnion([lockPin,pinHead]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"lockPinJoin"); }
 label(context,dock,"D Shared stationary cartridge dock - 3 ring screws to housing sleeve, 4 foot screws to cradle",[.18,.45,.65]);
 label(context,lock,"N Independent bayonet retaining collar - turn 20 deg to unlock",[.8,.69,.25]);
 label(context,lockPin,"I Quarter-turn cartridge locking pin - wing capture - witness mark",[.8,.69,.25]);
 // Same casing and mounting datums for both cartridges.
 stage="casing";
 var casing=tubeMM(context,id+"caseFloor",23,8.4,84,87);
 var wall=tubeMM(context,id+"caseWall",23,20.8,86.5,100);
 var rim=tubeMM(context,id+"caseFlange",28.6,20.8,94,96);
 var index=radialBox(context,id+"caseIndex",22,28.4,-2,2,84,5,180*degree);
 try { opBoolean(context,id+"caseJoin",{"tools":qUnion([casing,wall,rim,index]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"caseJoin"); }
 subtract(context,id+"caseLockHole",casing,atC(context,id+"caseDrill",1.9,92.4,100.1,px,py));
 subtract(context,id+"lockHeadAccess",casing,atC(context,id+"headAccessTool",3.5,98.4,100.1,px,py));
 // Quarter-turn keyed pin: align wing with slot to insert, then turn 90 degrees.
 var wing=radialBox(context,id+"lockWing",px-3.1,px+3.1,py-.8,py+.8,95,1.2,0*degree);
 opBoolean(context,id+"lockWingJoin",{"tools":qUnion([lockPin,wing]),"operationType":BooleanOperationType.UNION});
 subtract(context,id+"wingCaseClear",casing,atC(context,id+"wingCaseTool",3.5,94.8,96.4,px,py));
 subtract(context,id+"wingCollarSweep",lock,atC(context,id+"wingSweepTool",3.4,94.8,96.4,px,py));
 subtract(context,id+"wingEntry",lock,radialBox(context,id+"wingEntryTool",px-1.1,px+1.1,py-3.4,py+3.4,96.3,2.3,0*degree));
 // Rigid locating posts: lid slips on and is bonded; no forced PLA snaps.
 for(var k=0;k<3;k+=1) {
  var a=(60+120*k)*degree;
  var post=radialBox(context,id+("post"~k),19.5,23,-2.5,2.5,98.8,6.7,a);
  opBoolean(context,id+("postJoin"~k),{"tools":qUnion([casing,post]),"operationType":BooleanOperationType.UNION});
  var a2=k*120*degree;
  subtract(context,id+("springKeySlot"~k),casing,radialBox(context,id+("springKeyTool"~k),20.3,23.1,-1.7,1.7,89.8,10.3,a2));
 }
 // Lid screw bosses on the casing flange (M3x10 vertical, R24.7).
 stage="case boss";var lidAz=[145,215,335];
 for(var k=0;k<3;k+=1) {
  var laz=lidAz[k]*degree;
  var cboss=radialBox(context,id+("caseBoss"~k),22.0,26.6,-4.2,4.2,96,4.0,laz);
  opBoolean(context,id+("caseBossJoin"~k),{"tools":qUnion([casing,cboss]),"operationType":BooleanOperationType.UNION});
  drill(context,id+("casePilot"~k),casing,vector(24.7*cos(laz),24.7*sin(laz),0),vector(0,0,1),94.6,100.0,M3_PILOT);
 }
 stage="lid";
 var lid=tubeMM(context,id+"lid",23,definition.mode==1?14:8.4,100,104);
 for(var k=0;k<3;k+=1) subtract(context,id+("lidClipSlot"~k),lid,radialBox(context,id+("lidClipTool"~k),19.2,23.3,-2.8,2.8,99.9,4.2,(60+120*k)*degree));
 stage="lid ears";
 for(var k=0;k<3;k+=1) {
  var laz2=lidAz[k]*degree;
  var lear=radialBox(context,id+("lidEar"~k),22.5,26.8,-4.2,4.2,100,4,laz2);
  opBoolean(context,id+("lidEarJoin"~k),{"tools":qUnion([lid,lear]),"operationType":BooleanOperationType.UNION});
  drill(context,id+("lidHole"~k),lid,vector(24.7*cos(laz2),24.7*sin(laz2),0),vector(0,0,1),99.8,104.2,M3_CLR);
  if(definition.hardware)
   screwHW(context,id+("lidScrew"~k),vector(24.7*cos(laz2),24.7*sin(laz2),104),vector(0,0,-1),"M3BH",10,"HW lid screw "~(k+1)~" - M3x10 button head");
 }
 label(context,casing,"M Interchangeable cartridge casing - common mounting flange",[.23,.55,.70]);
 stage="drive hub";
 var drive=cylinderMM(context,id+"driveSleeve",8,81,90);
 var bottomLip=tubeMM(context,id+"bottomLip",10,8.25,81,83.5);
 label(context,bottomLip,"Q Separate lower thrust collar - bond to hub after insertion",[.28,.68,.42]);
 var topLip=tubeMM(context,id+"topLip",10,7.9,87.5,89.5);
 try { opBoolean(context,id+"driveLipJoin",{"tools":qUnion([drive,topLip]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"driveLipJoin"); }
 subtract(context,id+"driveSocket",drive,dKey(context,id+"driveTool",5.3,4.1,80.9,89.2));
 stage="spring branch";
 if(definition.mode==0) {
  var stem=dKey(context,id+"springDriveStem",6,4.8,89.5,120);
  // Separate adapter permits lid and winding cap installation over the 12 mm D stem.
  var coupler=cylinderMM(context,id+"upperCoupler",8.5,113.5,120.5);
  var nose=cylinderMM(context,id+"couplerNose",7,120.4,129.5);
  opBoolean(context,id+"couplerNoseJoin",{"tools":qUnion([coupler,nose]),"operationType":BooleanOperationType.UNION});
  subtract(context,id+"upperSocket",coupler,dKey(context,id+"upperSocketTool",5.3,4.1,120.5,129.6));
  subtract(context,id+"lowerSocket",coupler,dKey(context,id+"lowerSocketTool",6.25,5.05,113.4,120.2));
  turn(context,id+"couplerTurn",coupler,definition.release*degree);
  label(context,coupler,"X Separate double-D adapter - fit last - axially captured between shafts",[.28,.68,.42]);
  var latchDisk=cylinderMM(context,id+"latchDisk",14,106,109);
  subtract(context,id+"latchNotch",latchDisk,sector(context,id+"latchNotchTool",10.5,15,9,105.9,3.2));
  var windKnob=cylinderMM(context,id+"windKnob",9,110,113);
  opBoolean(context,id+"driveStemJoin",{"tools":qUnion([drive,stem]),"operationType":BooleanOperationType.UNION});
  var capNeck=cylinderMM(context,id+"capNeck",7,108.8,110.2);
  opBoolean(context,id+"capJoin",{"tools":qUnion([latchDisk,capNeck,windKnob]),"operationType":BooleanOperationType.UNION});
  subtract(context,id+"capSocket",latchDisk,dKey(context,id+"capSocketTool",6.25,5.05,105.9,113.1));
  turn(context,id+"capTurn",latchDisk,definition.release*degree);
  label(context,latchDisk,"T Separate keyed winding and latch cap - attach after lid",[.28,.68,.42]);
 stage="loaded spiral";
  springCore(context,id+"loadedSpring",definition.release,2.0,false);
  // Upward-only latch: tooth withdraws above the disk. +Z points toward the nose.
 stage="upward latch";
  var plunger=atC(context,id+"plunger",2,104,125,18,0);
  var yoke=radialBox(context,id+"plungerFoot",10.5,24,-3,3,115,4,0*degree);
  var tooth=radialBox(context,id+"latchTooth",11,13.5,-1.7,1.7,106,9.2,0*degree);
  var seat=atC(context,id+"returnSeat",3.5,122.2,123.2,18,0);
  opBoolean(context,id+"upLatchJoin",{"tools":qUnion([plunger,yoke,tooth,seat]),"operationType":BooleanOperationType.UNION});
  var sideYoke=radialBox(context,id+"sideYoke",20.2,26.8,-1,9.5,115,4,0*degree);
  opBoolean(context,id+"sideYokeJoin",{"tools":qUnion([plunger,sideYoke]),"operationType":BooleanOperationType.UNION});
  var cup=atC(context,id+"rodCup",3.3,115,120,23.5,9.5);
  opBoolean(context,id+"cupJoin",{"tools":qUnion([plunger,cup]),"operationType":BooleanOperationType.UNION});
  subtract(context,id+"rodSocket",plunger,atC(context,id+"rodSocketTool",2.05,114.9,117.5,23.5,9.5));
  // Separate side rod inserts from below into the blind yoke cup.
  var button=atC(context,id+"button",1.8,75.3,117.5,23.5,9.5);
  var pad=atC(context,id+"buttonPad",3,73.3,75.5,23.5,9.5);
  opBoolean(context,id+"rodPadJoin",{"tools":qUnion([button,pad]),"operationType":BooleanOperationType.UNION});
  if(definition.button>0) {
   opTransform(context,id+"buttonHeadPress",{"bodies":button,"transform":transform(vector(0,0,definition.button)*millimeter)});
   opTransform(context,id+"buttonPress",{"bodies":plunger,"transform":transform(vector(0,0,definition.button)*millimeter)});
  }
  label(context,button,"A Short side pushrod - 3.6 mm - unbonded blind cup",[.88,.26,.32]);
  label(context,plunger,"B Upward release yoke - lift 4.5 mm - square locking tooth",[.88,.26,.32]);
  var guide=atC(context,id+"guide",4,108,115,18,0);
  subtract(context,id+"guideBore",guide,atC(context,id+"guideDrill",2.4,107.9,115.1,18,0));
  var bridge=radialBox(context,id+"guideBridge",18,25,-5,5,112,3,0*degree);
  subtract(context,id+"bridgeBore",bridge,atC(context,id+"bridgeDrill",2.4,111.9,115.1,18,0));
  var post=radialBox(context,id+"guidePost",21.5,26,-5,5,102.8,12.2,0*degree);
  var leafRoot=radialBox(context,id+"leafRoot",-10,-2,-23,-15,102.8,20.4,0*degree);
  opBoolean(context,id+"lidGuideJoin",{"tools":qUnion([lid,guide,bridge,post,leafRoot]),"operationType":BooleanOperationType.UNION});
  var returnSpring=returnLeaf(context,id+"buttonReturn",-definition.button);
  opTransform(context,id+"returnHeight",{"bodies":returnSpring,"transform":transform(vector(0,0,2.2)*millimeter)});
  label(context,returnSpring,"W Return leaf LOADED REFERENCE - use preloaded printable sample",[.58,.35,.8]);
 stage="lower servo cradle";
  var servo=radialBox(context,id+"servo",-15.6,-3.4,3,27,-57.5,23,0*degree);
  label(context,servo,"E SG90 envelope REFERENCE - below entire housing - measure actual servo",[.35,.38,.43]);
  var mount=tubeMM(context,id+"lowerMountRing",29.4,26.8,-35,-30);
  var cradle=radialBox(context,id+"cradleBase",-18.4,-.6,2.5,29.5,-60.5,3,0*degree);
  var rail1=radialBox(context,id+"cradleRail1",-18.4,-16,2.5,27.4,-58,23.5,0*degree);
  var rail2=radialBox(context,id+"cradleRail2",-3,-.6,4.5,27.4,-58,23.5,0*degree);
  var back=radialBox(context,id+"cradleBack",-18.4,-.6,27.2,29.5,-58,23.5,0*degree);
  var post1=radialBox(context,id+"lowerPost1",-7.5,-4.5,27,28.3,-58,28,0*degree);
  var post2=radialBox(context,id+"lowerPost2",-28,-26,0,8,-58,28,0*degree);
  var outrigger=radialBox(context,id+"lowerOutrigger",-28,-15,2,6,-60.5,3,0*degree);
  var rodGuide=atC(context,id+"lowerRodGuide",4,-34.3,-30,0,0);
  subtract(context,id+"lowerRodBore",rodGuide,atC(context,id+"lowerRodDrill",2.05,-34.4,-29.9,0,0));
  var crossbar=radialBox(context,id+"lowerCrossbar",-28,0,-2,2,-34,4,0*degree);
  subtract(context,id+"crossbarBore",crossbar,atC(context,id+"crossbarDrill",2.05,-34.1,-29.9,0,0));
 stage="lower mount union";
  opBoolean(context,id+"lowerCradleJoin",{"tools":qUnion([mount,cradle,rail1,rail2,back,post1,post2,outrigger,rodGuide,crossbar]),"operationType":BooleanOperationType.UNION});
 stage="mount envelope";
  opBoolean(context,id+"mountEnvelope",{"tools":qUnion([mount,cylinderMM(context,id+"mountEnvelopeTool",32,-60.6,-29.9)]),"operationType":BooleanOperationType.INTERSECTION});
  mount=solid(id+"mountEnvelope");
  subtract(context,id+"servoFitPocket",mount,radialBox(context,id+"servoFitTool",-16,-3,2.6,27.4,-57.7,23.6,0*degree));
  // Rotate the servo tangentially to fit the BT80 bore; axis points inward along -X.
  var orient=rotationAround(line(vector(0,0,0)*millimeter,vector(0,0,1)),90*degree);
  var shift=transform(vector(23.5,9.5,112)*millimeter);
  opTransform(context,id+"servoMove",{"bodies":servo,"transform":shift*orient});
  // Retain just the reinforced cradle before attaching to the stationary lower frame.
  opBoolean(context,id+"cradleTrim",{"tools":qUnion([mount,radialBox(context,id+"cradleTrimTool",-20,0,2,30,-60.6,26.2,0*degree)]),"operationType":BooleanOperationType.INTERSECTION});
  mount=solid(id+"cradleTrim");
  opTransform(context,id+"mountMove",{"bodies":mount,"transform":shift*orient});
  var support=tubeMM(context,id+"servoFrame",29.4,26.5,76,79.7);
  var strut=radialBox(context,id+"servoStrut",-7,-4.2,-8.5,.5,53,26.7,0*degree);
  var cross=radialBox(context,id+"servoCross",-27,-4.2,-8.5,.5,76,3.7,0*degree);
  opBoolean(context,id+"servoFrameJoin",{"tools":qUnion([mount,support,strut,cross]),"operationType":BooleanOperationType.UNION});
  var guideWeb=radialBox(context,id+"compactGuideWeb",18,21,7,12,78,5.5,0*degree);
  var rg=atC(context,id+"sideRodGuide",3,81,86,23.5,9.5);
  subtract(context,id+"sideRodBore",rg,atC(context,id+"sideRodDrill",2.4,80.9,86.1,23.5,9.5));

  subtract(context,id+"completeRodGuideBore",mount,atC(context,id+"completeRodTool",2.4,58,118,23.5,9.5));
  subtract(context,id+"padTravelClear",mount,atC(context,id+"padTravelTool",3.25,58,80.3,23.5,9.5));
  var roof=radialBox(context,id+"servoRoof",-6,20.9,-8.5,8.9,77.9,2.6,0*degree);
  opBoolean(context,id+"servoRoofJoin",{"tools":qUnion([mount,roof]),"operationType":BooleanOperationType.UNION});
  opBoolean(context,id+"sideRodGuideJoin",{"tools":qUnion([mount,rg,guideWeb]),"operationType":BooleanOperationType.UNION});
  subtract(context,id+"roofPadClear",mount,atC(context,id+"roofPadTool",3.25,58,80.3,23.5,9.5));
  for(var k=0;k<4;k+=1) {
   var paz2=(45+90*k)*degree;
   var pad=radialBox(context,id+("mountPad"~k),26.0,30,-3.0,3.0,76,3.7,paz2);
   opBoolean(context,id+("mountPadJoin"~k),{"tools":qUnion([mount,pad]),"operationType":BooleanOperationType.UNION});
   radialDrill(context,id+("padPilot"~k),mount,paz2,77.8,26.4,30.4,M3_PILOT);
   if(definition.hardware)
    screwHW(context,id+("footScrew"~k),vector(33.02*cos(paz2),33.02*sin(paz2),77.8),vector(-cos(paz2),-sin(paz2),0),"M3BH",10,"HW cradle screw "~(k+1)~" - M3x10 button head");
  }
  subtract(context,id+"compactHubClear",mount,cylinderMM(context,id+"compactHubTool",10.5,80.7,90));
  subtract(context,id+"compactHornSweep",mount,radialBox(context,id+"compactHornTool",20,26.3,-14,14,70,8,0*degree));
  var gate=radialBox(context,id+"servoGate",21,22.5,-4.5,4.5,53,5,0*degree);
  label(context,gate,"G Servo lower keeper - fit after servo - bond to cradle floor",[.8,.69,.25]);
  label(context,mount,"S Reinforced tangential SG90 cradle - 4 pad screws to dock feet, roof and separate keeper",[.23,.55,.70]);
 stage="lower pusher";
  var horn=radialBox(context,id+"pusher",-20,1,-2.4,2.4,-45.5,6.6,0*degree);
  fCylinder(context,id+"hornBoss",{"bottomCenter":vector(-9.5,-2.4,-42.2)*millimeter,"topCenter":vector(-9.5,2.4,-42.2)*millimeter,"radius":5.5*millimeter});
  opBoolean(context,id+"hornJoin",{"tools":qUnion([horn,solid(id+"hornBoss")]),"operationType":BooleanOperationType.UNION});
  // Double-arm horn lies in XZ, perpendicular to its Y output shaft.
  subtract(context,id+"hornSlotCut",horn,radialBox(context,id+"doubleHornSlot",-20.1,1.1,-.2,2.5,-44.5,4.6,0*degree));
  fCylinder(context,id+"hornHubPocket",{"bottomCenter":vector(-9.5,-.2,-42.2)*millimeter,"topCenter":vector(-9.5,2.5,-42.2)*millimeter,"radius":4.3*millimeter});
  subtract(context,id+"hornHubCut",horn,solid(id+"hornHubPocket"));
  fCylinder(context,id+"hornScrewAccess",{"bottomCenter":vector(-9.5,-2.5,-42.2)*millimeter,"topCenter":vector(-9.5,2.5,-42.2)*millimeter,"radius":2.2*millimeter});
  subtract(context,id+"hornAccessCut",horn,solid(id+"hornScrewAccess"));
  opTransform(context,id+"hornMove",{"bodies":horn,"transform":shift*orient});
  label(context,horn,"J Double-arm SG90 horn saddle - measure horn before print",[.8,.69,.25]);
  // Side rod clearance through stationary cartridge interfaces.
  subtract(context,id+"rodDockClear",dock,atC(context,id+"rodDockTool",2.4,58,118,23.5,9.5));
  subtract(context,id+"rodCollarClear",lock,atC(context,id+"rodCollarTool",2.4,58,118,23.5,9.5));
  subtract(context,id+"rodCaseClear",casing,atC(context,id+"rodCaseTool",2.4,58,118,23.5,9.5));
  subtract(context,id+"compactDockGuideClear",dock,atC(context,id+"compactDockGuideTool",3.3,80,86.3,23.5,9.5));
  subtract(context,id+"compactGuideClear",casing,atC(context,id+"compactGuideTool",3.3,80,86.3,23.5,9.5));
  subtract(context,id+"compactYokeClear",dock,radialBox(context,id+"compactYokeTool",20,27.1,-3.3,13.1,114.7,10.1,0*degree));


  // Dock collar: preserve full bonding skin, end bands, leg roots and latch window.
  for(var k=0;k<4;k+=1) {
   var a=(45+90*k)*degree;
   var relief=sector(context,id+("dockSkinPocket"~k),26.7,27.8,24,113,9);
   turn(context,id+("dockSkinTurn"~k),relief,a);
   subtract(context,id+("dockSkinCut"~k),dock,relief);
  }
  // Continuous ring still connects four mount pads; blind recess reduces duplicate ring material.
  for(var k=0;k<4;k+=1) {
   var a=(45+90*k)*degree;
   var relief=sector(context,id+("cradleRingPocket"~k),27.3,28.6,26,75.9,2.3);
   turn(context,id+("cradleRingTurn"~k),relief,a);
   subtract(context,id+("cradleRingCut"~k),mount,relief);
  }
  // Blind underside floor pockets leave 1.8 mm skin and radial spring-anchor ribs.
  for(var k=0;k<3;k+=1) {
   var a=(60+120*k)*degree;
   var relief=sector(context,id+("caseFloorPocket"~k),11,19,40,83.9,1.3);
   turn(context,id+("caseFloorTurn"~k),relief,a);
   subtract(context,id+("caseFloorCut"~k),casing,relief);
  }

 } else {
  var stem=cylinderMM(context,id+"directStem",8,89.5,107);
  var adapter=cylinderMM(context,id+"hornAdapter",13,103.5,107);
  try { opBoolean(context,id+"directJoin",{"tools":qUnion([drive,stem,adapter]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"directJoin"); }
  var pocket=cylinderMM(context,id+"hornPocket",4.5,105.8,107.2);
  var slot=radialBox(context,id+"hornSlot",-2,12,-2,2,105.8,1.4,0*degree);
  try { opBoolean(context,id+"hornToolJoin",{"tools":qUnion([pocket,slot]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"hornToolJoin"); }subtract(context,id+"hornPocketCut",drive,pocket);
  var horn=cylinderMM(context,id+"servoHorn",4,106,107.8);
  var arm=radialBox(context,id+"servoHornArm",0,11,-1.7,1.7,106,1.8,0*degree);
  try { opBoolean(context,id+"servoHornJoin",{"tools":qUnion([horn,arm]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"servoHornJoin"); }
  turn(context,id+"directHornTurn",horn,definition.release*degree);label(context,horn,"J Original SG90 horn REFERENCE - fit adapter to actual horn",[.8,.69,.25]);
 stage="servo cradle";
  var servo=radialBox(context,id+"servo",-6.1,6.1,-6.5,16.5,110,24,0*degree);
  label(context,servo,"E SG90 envelope REFERENCE - output axis down",[.35,.38,.43]);
  var saddle=radialBox(context,id+"servoSaddle",-18,18,-11,22,108,2,0*degree);
  subtract(context,id+"saddleShaftHole",saddle,cylinderMM(context,id+"saddleDrill",3,107.9,110.1));
  var rail1=radialBox(context,id+"servoRail1",-9,-6.6,-7,17,108,22.8,0*degree);
  var rail2=radialBox(context,id+"servoRail2",6.6,9,-7,17,108,22.8,0*degree);
  var outer1=radialBox(context,id+"outerPost1",-18,-15,-4,4,102.8,7,0*degree);
  var outer2=radialBox(context,id+"outerPost2",15,18,-4,4,102.8,7,0*degree);
  try { opBoolean(context,id+"servoCradleJoin",{"tools":qUnion([lid,saddle,rail1,rail2,outer1,outer2]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"servoCradleJoin"); }
 }
 turn(context,id+"moduleDriveTurn",drive,definition.release*degree);
 label(context,drive,"U Cartridge output hub - same D socket in both modes",[.28,.68,.42]);
 label(context,lid,"F Upper latch guide and spring cartridge lid - 3 M3 lid screws to casing",[.23,.55,.70]);
 var moduleBodies=qSubtraction(qBodyType(qEverything(EntityType.BODY),BodyType.SOLID),baseBodies);
 opTransform(context,id+"moduleBelowHousing",{"bodies":moduleBodies,"transform":transform(vector(0,0,-145)*millimeter)});
 if(definition.tubes) {
  var lt=tubeMM(context,id+"lowerTube",33.02,32.5,-100,-15);
  for(var k=0;k<3;k+=1) radialDrill(context,id+("lowerTubeHoleA"~k),lt,rpAz[k]*degree,-26.5,32.0,33.5,M3_CLR);
  if(definition.mode==0) for(var k=0;k<4;k+=1) radialDrill(context,id+("lowerTubeHoleB"~k),lt,(45+90*k)*degree,-67.2,32.0,33.5,M3_CLR);
  label(context,lt,"REF BT80 lower tube - 3 ring-screw holes at z=-26.5, 4 cradle-screw holes at z=-67.2 - cut from real tube",TUBE_TAN);
 }

 } catch(error) {throw regenError(stage ~ " : " ~ error);}
 });
