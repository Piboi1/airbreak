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

function nutV5(context is Context,id is Id,p is Vector,d is Vector) returns Query {
 var x=abs(d[2])<0.9?normalize(cross(d,vector(0,0,1))):vector(1,0,0);
 var sk=newSketchOnPlane(context,id+"sk",{"sketchPlane":plane(p*millimeter,d,x)});
 var pts=[];for(var k=0;k<=6;k+=1)pts=append(pts,vector(3.175*cos((30+k*60)*degree),3.175*sin((30+k*60)*degree))*millimeter);
 skPolyline(sk,"hex",{"points":pts});skSolve(sk);
 opExtrude(context,id+"ex",{"entities":qSketchRegion(id+"sk"),"direction":d,"endBound":BoundingType.BLIND,"endDepth":2.4*millimeter});
 opDeleteBodies(context,id+"del",{"entities":qCreatedBy(id+"sk",EntityType.BODY)});
 var b=solid(id+"ex");drill(context,id+"hole",b,p,d,-.1,2.5,1.5);label(context,b,"HW M3 hex nut - schematic unthreaded",HW_GREY);return b;
}
function radialBoltV5(context is Context,id is Id,b is Query,a is ValueWithUnits,z is number,nr is number,hw is boolean) {
 radialDrill(context,id+"clearance",b,a,z,23,34,1.7);
 // Tangential insertion from inward opening; square pocket allows insertion with flats held.
 var slot=radialBox(context,id+"slot",nr,nr+2.6,-2.9,2.9,z-3.3,8.0,a);
 subtract(context,id+"slotCut",b,slot);
 // Open inward from the pocket at one axial end for nut loading.
 var entry=radialBox(context,id+"entry",23,nr+2.6,-2.9,2.9,z+2.8,1.8,a);
 subtract(context,id+"entryCut",b,entry);
 if(hw) {
  var d=vector(cos(a),sin(a),0);
  screwHW(context,id+"bolt",vector(0,0,z)+33.02*d,-d,"M3BH",8,"HW radial M3x8 bolt");
  nutV5(context,id+"nut",vector(0,0,z)+(nr+.1)*d,d);
 }
}
function hookRampV6(context is Context, id is Id, rotor is Query) {
 for(var i=0;i<4;i+=1) {
  var sub=id+("arm"~i);
  var points=[];
  for(var phase=42;phase<=79;phase+=1) {
   var r=phase<=62 ? 17.5+8.5*(phase-42)/20 : (phase<=67 ? 26 : 26-8.5*(phase-67)/12);
   var a=(90*i-phase)*degree;
   points=append(points,vector(r*cos(a),r*sin(a)));
  }
  for(var phase=79;phase>=42;phase-=1) {
   var a=(90*i-phase)*degree;
   points=append(points,vector(16*cos(a),16*sin(a)));
  }
  var ramp=polygonMM(context,sub+"profile",points,41.4,2.9);
  var rib=radialBox(context,sub+"rib",7.8,21,-1.9,1.9,38.8,3.1,(90*i-60)*degree);
  opBoolean(context,sub+"join",{"tools":qUnion([rotor,rib,ramp]),"operationType":BooleanOperationType.UNION});
 }
}
annotation { "Feature Type Name" : "Positive cam kick-out and cord-limited BT80 airbrake" }
const v5Core = defineFeature(function(context is Context,id is Id,definition is map)
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
 var dr=-0.82;
 var rOut=33.02+dr;
 var camMax=compact?28.6:29;
 // V2: the latch stack (hook, crown arms, top bearing, knob) drops 22 mm into the fin height; the catch is an inward lug on the fin.
 var dzT=compact?22:0;
 var topZ=compact?58.8:67;
 // Inline BT80 housing. Two 18 mm glue shoulders, 64.6 mm OD.
 var carrier=tubeMM(context,id+"carrier",32.2,29.48,-10,topZ);
 // Inward belt preserves a substantial fixed load path behind the recessed hook track.
 if(!compact) {
  var catchBelt=tubeMM(context,id+"recessCatchBelt",31+dr,28.4+dr,54.6,57.4);
  opBoolean(context,id+"recessCatchBeltJoin",{"tools":qUnion([carrier,catchBelt]),"operationType":BooleanOperationType.UNION});
 }
 // Single rotor: 10 mm shaft, root cams, top capture crown, accessible knob.
 var ring=cylinderMM(context,id+"rotorShaft",5,flip?-6.4:(definition.direct?-8.7:-10.5),flip?44.6:78-dzT);
 var crownHub=cylinderMM(context,id+"crownHub",9,flip?33.6:58.6-dzT,flip?44.6:61.6-dzT);
 var lowThrust=cylinderMM(context,id+"lowThrust",7,flip?3.9:(definition.direct?2.7:-5.5),flip?5.9:(definition.direct?4.7:-3.5));
 var rotorParts=[ring,crownHub,lowThrust];
 if(flip) {
  // V4: the rotation limiter moves to the bottom of the rotor, flipped and thick (6 mm finger, below the lower bearing).
  rotorParts=append(rotorParts,radialBox(context,id+"limFinger",4,16,-3,3,6.4,5.2,60*degree));
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
  var lowSpoke=radialBox(context,id+("lowSpoke"~i),6,(flip||definition.direct)?30.6:20,flip?-3.5:-2.5,flip?3.5:2.5,flip?0.4:(definition.direct?-0.8:-15),flip?3.0:(definition.direct?3.0:4),a);
  if(!flip) {
   var spoke=radialBox(context,id+("topSpoke"~i),15,31,-2.5,2.5,68-dzT,4,a);
   opBoolean(context,id+("topSpokeJoin"~i),{"tools":qUnion([topBearing,spoke]),"operationType":BooleanOperationType.UNION});
  }
  if(flip) {
   var spokeFlare=radialBox(context,id+("lowSpokeFlare"~i),22,30.6,-4.5,4.5,0.4,3.0,a);
   opBoolean(context,id+("lowSpokeFlareJoin"~i),{"tools":qUnion([lowSpoke,spokeFlare]),"operationType":BooleanOperationType.UNION});
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
  // Open-top clip: the arm drops into the socket with the housing halves open; a boss under the arm takes the screw.
  var catchCap=undefined;var catchSocket=undefined;
  if(compact) {
   // V2: hook finger stands inside R26 and hooks the lug on the fin from inside (see fin lug), so it clears the fin shell.
   catchCap=radialBox(context,sub+"catchCap",flip?22.4:18.0,26.0,flip?-3.0:-4.2,flip?3.0:4.2,flip?36.5:35.4,flip?2.4:5.4,0*degree);
   var catchFinger=radialBox(context,sub+"catchFinger",23.6,26.0,-3.0,3.0,flip?38.9:40.8,flip?5.9:5.2,0*degree);

   opBoolean(context,sub+"catchJoin",{"tools":qUnion([catchCap,catchFinger]),"operationType":BooleanOperationType.UNION});
   if(flip) {
    // Taper from the horizontal arm into the upright, below the fin lug.
    var gusset=polygonMM(context,sub+"rootGusset",
      [vector(19.6,38.5),vector(23.9,38.5),vector(23.9,41.0),vector(23.5,41.0)],-3,6);
    opTransform(context,sub+"orientGusset",{"bodies":gusset,
      "transform":rotationAround(line(vector(0,0,0)*millimeter,vector(1,0,0)),90*degree)});
    opBoolean(context,sub+"joinGusset",{"tools":qUnion([catchCap,gusset]),"operationType":BooleanOperationType.UNION});
   }
   catchSocket=radialBox(context,sub+"catchSocket",flip?16.4:17.9,24.2,flip?-4.3:-2.75,flip?4.3:2.75,flip?33.4:36.4,flip?6.0:5.0,0*degree);
  } else {
   catchCap=radialBox(context,sub+"catchCap",22,32.6+dr,-4.2,4.2,57.4,5.4,0*degree);
   var catchHook=sector(context,sub+"catchHook",30.9+dr,32.8+dr,5.2,55.2,5.0);
   var catchBoss=radialBox(context,sub+"catchBoss",21.8,26.6,-4.2,4.2,53.4,4.0,0*degree);
   opBoolean(context,sub+"catchJoin",{"tools":qUnion([catchCap,catchHook,catchBoss]),"operationType":BooleanOperationType.UNION});
   catchSocket=radialBox(context,sub+"catchSocket",21.9,30.4+dr,-2.75,2.75,58.4,5.0,0*degree);
  }
  opDeleteBodies(context,sub+"deleteSocketTool",{"entities":catchSocket});
  turn(context,sub+"capPosition",catchCap,a);
  opBoolean(context,sub+"integralCatch",{"tools":qUnion([ring,catchCap]),"operationType":BooleanOperationType.UNION});
  var ears=[];
  for(var j=0;j<2;j+=1) {
   var y0=j==0?-12:7.8;var y1=y0+4.2;
   var ear=yc(context,sub+("ear"~j),5.2,y0,y1);
   var arm=radialBox(context,sub+("arm"~j),20.5,28.5,y0,y1,-15,15,0*degree);
   opBoolean(context,sub+("earJoin"~j),{"tools":qUnion([ear,arm]),"operationType":BooleanOperationType.UNION});
   subtract(context,sub+("earBore"~j),ear,yc(context,sub+("earTool"~j),M3_CLR,y0-.1,y1+.1));
   if(j==1) {
    var nt=radialBox(context,sub+"hingeNutSlot",22.1,27.9,9.2,12.2,-3.3,6.6,0*degree);
    subtract(context,sub+"hingeNutCut",ear,nt);
   }
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
  subtract(context,sub+"leafBore",panel,yc(context,sub+"leafTool",M3_CLR,-7.5,7.5));
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
  opBoolean(context,sub+"solidPanelJoin",{"tools":qUnion([panel,tip]),"operationType":BooleanOperationType.UNION});
  opTransform(context,sub+"open",{"bodies":panel,"transform":rotationAround(line(vector(25,0,0)*millimeter,vector(0,1,0)),definition.opening*degree)});
  turn(context,sub+"leafTurn",panel,a);
  label(context,panel,"P"~(i+1)~" Cam-driven BT80 panel - solid shell - reinforced root - 90 degree stop",orange);
  // Hinge: M4x25 button-head screw, clearance in the -Y ear and the panel barrel, threads into the +Y ear.
  if(definition.hardware) {
   var hs=screwHW(context,sub+"hingeScrew",vector(25,-12,0),vector(0,1,0),"M3BH",25,"HW H"~(i+1)~" hinge bolt M3x25 - tangential axis");
   turn(context,sub+"hingeScrewTurn",hs,a);
   var hn=nutV5(context,sub+"hingeNut",vector(25,9.3,0),vector(0,1,0));turn(context,sub+"hingeNutTurn",hn,a);
  }
  // V2: the cut-out piece of the real BT80 tube is glued to the fin and rides with it.
  if(false) {
   var tp=sector(context,sub+"tubePiece",32.5,33.02,32.5,8,42);
   opTransform(context,sub+"tubePieceOpen",{"bodies":tp,"transform":rotationAround(line(vector(25,0,0)*millimeter,vector(0,1,0)),definition.opening*degree)});
   turn(context,sub+"tubePieceTurn",tp,a);
   label(context,tp,"TP"~(i+1)~" BT80 tube cut-out - glue to fin P"~(i+1)~" (cut from the real tube, not printed)",TUBE_TAN);
  }
 }
 hookRampV6(context,id+"upperRamps",ring);
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
 }
 // Open axial bore is printable without trapped support; solid D extension is added later.
 subtract(context,id+"rotorLightBore",ring,cylinderMM(context,id+"rotorLightTool",3,flip?-7:-8,flip?41.6:78.1-dzT));
 // V5 one-piece carrier. Limiter stands ABOVE bearing spokes.
 var limA=radialBox(context,id+"limStop1",10,12.8,-11,-3.4,0.4,13.6,60*degree);
 var limB=radialBox(context,id+"limStop2",10,19,3.4,11,0.4,13.6,125*degree);
 opBoolean(context,id+"limStopsJoin",{"tools":qUnion([carrier,limA,limB]),"operationType":BooleanOperationType.UNION});
 // Clip the lower base to the module seat; a through-opening retains insertion access.
 subtract(context,id+"baseTrim",carrier,cylinderMM(context,id+"baseTrimTool",40,-20,-10));
 for(var k=0;k<4;k+=1) {
  var a=(45+90*k)*degree;
  var boss=radialBox(context,id+("nutBoss"~k),27.0,30.2,-4.0,4.0,7.5,9,a);
  opBoolean(context,id+("nutBossJoin"~k),{"tools":qUnion([carrier,boss]),"operationType":BooleanOperationType.UNION});
  radialBoltV5(context,id+("moduleBolt"~k),carrier,a,12,27.2,definition.hardware);
 }
 subtract(context,id+"carrierEnvelope",carrier,tubeMM(context,id+"carrierEnvelopeTool",40,32.2,-10.1,59));
 label(context,carrier,"C V5 ONE PIECE module housing - radial M3 nuts - top inserted rotor",blue);
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

annotation {"Feature Type Name":"V7 transition electronics airbrake"}
export const transitionBrakeV7=defineFeature(function(context is Context,id is Id,definition is map)
 precondition {
 annotation {"Name":"Show hinge and tube hardware","Default":true} definition.hardware is boolean;
 annotation {"Name":"Rotor angle (degrees)"} isReal(definition.release,{(unitless):[0,0,65]} as RealBoundSpec);
 annotation {"Name":"Fin angle (degrees)"} isReal(definition.opening,{(unitless):[0,0,90]} as RealBoundSpec);
 }
 {
 v5Core(context,id+"core",{"opening":definition.opening,"release":definition.release,"cords":false,"compact":true,"direct":false,"flip":true,"hardware":definition.hardware,"tubes":false});
 var rotor=solid(id+"core"+"rotorShaft");
 var coupling=cylinderMM(context,id+"coupling",12.5,-14.5,-5.8);
 opBoolean(context,id+"couple",{"tools":qUnion([rotor,coupling]),"operationType":BooleanOperationType.UNION});
 var hornPocket=cylinderMM(context,id+"pocket",4.4,-14.6,-12);
 var phase=definition.release*degree;
 var key=radialBox(context,id+"key",0,11.5,-2.1,2.1,-14.6,2.6,phase);
 opBoolean(context,id+"joinKey",{"tools":qUnion([hornPocket,key]),"operationType":BooleanOperationType.UNION});
 subtract(context,id+"cutKey",rotor,hornPocket);
 var horn=cylinderMM(context,id+"horn",4,-14.3,-12.4);
 var arm=radialBox(context,id+"arm",0,11,-1.7,1.7,-14.3,1.9,phase);
 opBoolean(context,id+"hornJoin",{"tools":qUnion([horn,arm]),"operationType":BooleanOperationType.UNION});
 label(context,horn,"REF SG90 horn - bottom drive",[.8,.7,.3]);
 var servo=radialBox(context,id+"servo",-6.5,16,-6.1,6.1,-41.5,22.7,0*degree);
 var tabs=radialBox(context,id+"tabs",-11.5,21,-5.9,5.9,-25.5,2.5,0*degree);
 var boss=cylinderMM(context,id+"servoBoss",5.9,-18.9,-15.0);
 var spline=cylinderMM(context,id+"spline",2.4,-15.1,-14.3);
 opBoolean(context,id+"servoJoin",{"tools":qUnion([servo,tabs,boss,spline]),"operationType":BooleanOperationType.UNION});
 label(context,servo,"REF SG90 - output up",[.32,.34,.4]);
 var shell=tubeMM(context,id+"shoulder",32.2,26.7,-30.2,-10.2);
 fCone(context,id+"cone",{"bottomCenter":vector(0,0,-73)*millimeter,"topCenter":vector(0,0,-30)*millimeter,"bottomRadius":28.15*millimeter,"topRadius":33.02*millimeter});
 fCone(context,id+"coneBore",{"bottomCenter":vector(0,0,-73.1)*millimeter,"topCenter":vector(0,0,-29.9)*millimeter,"bottomRadius":26.2*millimeter,"topRadius":31*millimeter});
 var cone=solid(id+"cone");subtract(context,id+"coneHollow",cone,solid(id+"coneBore"));
 var lower=tubeMM(context,id+"bt70",27.45,25.5,-88,-72.7);
 opBoolean(context,id+"transitionJoin",{"tools":qUnion([shell,cone,lower]),"operationType":BooleanOperationType.UNION});
 for(var k=0;k<4;k+=1) radialBoltV5(context,id+("tubeBolt"~k),shell,(45+90*k)*degree,-21,28,definition.hardware);
 for(var k=0;k<2;k+=1){
 var x=k==0?-9.3:18.8;
 var ledge=radialBox(context,id+("ledge"~k),k==0?-28:16.4,k==0?-6.9:28,-4,4,-23,3.4,0*degree);
 opBoolean(context,id+("ledgeJoin"~k),{"tools":qUnion([shell,ledge]),"operationType":BooleanOperationType.UNION});
 drill(context,id+("servoPilot"~k),shell,vector(x,0,-23.1),vector(0,0,1),0,3.7,.85);
 drill(context,id+("tabHole"~k),servo,vector(x,0,-25.6),vector(0,0,1),0,2.7,1.1);
 }
 // Side-facing static ports open into the instrumentation compartment.
 for(var k=0;k<3;k+=1)radialDrill(context,id+("vent"~k),shell,(30+k*120)*degree,-56,24,35,.8);
 var tray=cylinderMM(context,id+"tray",25.1,-72.8,-70.8);
 var stem=tubeMM(context,id+"stem",25.1,22.7,-84,-72.6);
 opBoolean(context,id+"trayJoin",{"tools":qUnion([tray,stem]),"operationType":BooleanOperationType.UNION});
 for(var k=0;k<2;k+=1){
 radialDrill(context,id+("trayClear"~k),shell,k*180*degree,-78,24,29,1.15);
 radialDrill(context,id+("trayPilot"~k),tray,k*180*degree,-78,21,26,.85);
 }
 var battery=radialBox(context,id+"battery",-21,21,-8.5,10.5,-70.8,12,0*degree);
 var board=radialBox(context,id+"board",-15,15,-20,-9.2,-70.8,16.9,0*degree);
 var reg=radialBox(context,id+"reg",-12.5,12.5,11.2,19.2,-70.8,15,0*degree);
 label(context,battery,"REF 300 mAh battery - strap to tray",[.9,.8,.3]);
 label(context,board,"REF Mercury board - edge mount",[.45,.65,.7]);
 label(context,reg,"REF regulator - edge mount",[.75,.48,.6]);
 for(var k=0;k<2;k+=1){
 subtract(context,id+("tieCut"~k),tray,radialBox(context,id+("tie"~k),-3,3,k==0?-9.2:10.6,k==0?-8.6:11.2,-73,2.4,0*degree));
 }
 // Check the removable payload against the smallest access bore as an axial extrusion.
 var payload=qUnion([battery,board,reg]);
 var gauge=tubeMM(context,id+"accessGauge",36,25.5,-88,-40);
 var passage=evDistance(context,{"side0":payload,"side1":gauge}).distance;
 if(passage<0.45*millimeter) throw regenError("Loaded electronics exceed the insertion envelope.");
 opDeleteBodies(context,id+"clearGauge",{"entities":gauge});
 var packGap=evDistance(context,{"side0":payload,"side1":servo}).distance;
 if(packGap<10*millimeter) throw regenError("Electronics clearance below the servo is insufficient.");
 if(evDistance(context,{"side0":payload,"side1":shell}).distance<0.4*millimeter) throw regenError("Electronics are too close to transition wall.");
 label(context,shell,"V7 vented transition with SG90 mounting ledges",[.27,.5,.72]);
 label(context,tray,"V7 removable electronics tray - adhesive board mounts",[.34,.62,.54]);
 label(context,rotor,"V7 lower-driven gusseted hook rotor",[.29,.64,.41]);
 });


