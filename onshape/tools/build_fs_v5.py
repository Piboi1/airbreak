"""V5 (mode 5) patches. Executed inside build_fs.py (uses its P()). Everything here is guarded by `mono` (camKickBrake) or
`mode==5` (modularBrake) so V1..V4 stay volume-identical. Frame: the V4 frame (rotor axis = z, module bottom z = -10, housing top 58.8)."""

V5HELPERS = r"""// ---------------- V5 helpers ----------------
// Hexagonal prism. p = centre of the first face, d = unit axis, af = across flats, len = length. Corners lie along the
// vertical (v) direction of the sketch plane, flats face the x direction (tangential for a radial axis).
function hexPrism(context is Context, id is Id, p is Vector, d is Vector, af is number, len is number) returns Query
{
    var xd = vector(1, 0, 0);
    if (abs(d[2]) < 0.9)
        xd = normalize(cross(d, vector(0, 0, 1)));
    var sk = newSketchOnPlane(context, id + "sk", { "sketchPlane" : plane(p * millimeter, d, xd) });
    var c = af / (2 * cos(30 * degree));
    var pts = [];
    for (var k = 0; k <= 6; k += 1)
        pts = append(pts, vector(c * cos((30 + k * 60) * degree), c * sin((30 + k * 60) * degree)) * millimeter);
    skPolyline(sk, "hex", { "points" : pts });
    skSolve(sk);
    opExtrude(context, id + "ex", { "entities" : qSketchRegion(id + "sk"), "direction" : d, "endBound" : BoundingType.BLIND,
        "endDepth" : len * millimeter });
    opDeleteBodies(context, id + "del", { "entities" : qCreatedBy(id + "sk", EntityType.BODY) });
    return solid(id + "ex");
}

// Hardware hex nut (reference, unthreaded). Sits from p along d.
function nutHW(context is Context, id is Id, p is Vector, d is Vector, af is number, len is number, hole is number, name is string) returns Query
{
    var b = hexPrism(context, id + "nut", p, d, af, len);
    drill(context, id + "hole", b, p, d, -0.1, len + 0.1, hole);
    label(context, b, name, HW_GREY);
    return b;
}

// Nut pocket for a radial bolt: hexagon (flats tangential) from radius r0 outward by depth, at height z and azimuth az.
function radialNutPocket(context is Context, id is Id, target is Query, az is ValueWithUnits, z is number, r0 is number, depth is number, af is number)
{
    var d = vector(cos(az), sin(az), 0);
    var tool = hexPrism(context, id + "pocket", vector(0, 0, z) + r0 * d, d, af, depth);
    subtract(context, id + "pocketCut", target, tool);
}

// One radial M3 bolt (button head under the tube outer face, tip inward) and its nut, as hardware references.
function radialBoltHW(context is Context, id is Id, az is ValueWithUnits, z is number, nutIn is number, name is string)
{
    var d = vector(cos(az), sin(az), 0);
    screwHW(context, id + "bolt", vector(0, 0, z) + 33.02 * d, -d, "M3BH", 8, "HW " ~ name ~ " bolt - M3x8 button head");
    nutHW(context, id + "nutHW", vector(0, 0, z) + (nutIn + 0.1) * d, d, 5.5, 2.4, 1.5, "HW " ~ name ~ " nut - M3 hex");
}

// Azimuth of the radial tube-retention screw in V2 support s (0..3)."""
P('// Azimuth of the radial tube-retention screw in V2 support s (0..3).', V5HELPERS)

# ---- camKickBrake: flag, dimensions
P('  annotation { "Name" : "V4 servo on top, bay at the bottom", "Default" : false }\n  definition.flip is boolean;\n',
  '  annotation { "Name" : "V4 servo on top, bay at the bottom", "Default" : false }\n  definition.flip is boolean;\n'
  '  annotation { "Name" : "V5 one-piece module (no seam, limiter above the ring, M3 bolts)", "Default" : false }\n  definition.mono is boolean;\n')
P(' var flip=definition.flip;\n', ' var flip=definition.flip;\n var mono=definition.mono;\n')
P(' var dr=compact?-0.72:0;', ' var dr=mono?-0.82:(compact?-0.72:0);')
P(''' var carrier=tubeMM(context,id+"carrier",rOut,30.2+dr,-15,topZ);
 var base=tubeMM(context,id+"base",33.02,flip?26:18,-15,-11);
 var lower=tubeMM(context,id+"lowerShoulder",32.3,29.9,flip?-37.5:-33,-14.9);
 var joinParts=[carrier,base,lower];
 if(!compact) joinParts=append(joinParts,tubeMM(context,id+"upperShoulder",32.3,29.9,66.9,85));
 opBoolean(context,id+"baseJoin",{"tools":qUnion(joinParts),"operationType":BooleanOperationType.UNION});''',
''' var carrier=tubeMM(context,id+"carrier",rOut,mono?29.48:30.2+dr,mono?-10.5:-15,topZ);
 if(!mono) {
  var base=tubeMM(context,id+"base",33.02,flip?26:18,-15,-11);
  var lower=tubeMM(context,id+"lowerShoulder",32.3,29.9,flip?-37.5:-33,-14.9);
  var joinParts=[carrier,base,lower];
  if(!compact) joinParts=append(joinParts,tubeMM(context,id+"upperShoulder",32.3,29.9,66.9,85));
  opBoolean(context,id+"baseJoin",{"tools":qUnion(joinParts),"operationType":BooleanOperationType.UNION});
 }''')
# limiter finger above the bearing ring
P('radialBox(context,id+"limFinger",4,16,-3,3,-5.6,5.2,60*degree)', 'radialBox(context,id+"limFinger",4,16,-3,3,mono?6.4:-5.6,5.2,60*degree)')
# integral catch: no cap screw hole, no socket, cap merged into the rotor
P('  drill(context,sub+"armHole",ring,vector(capR*cos(a),capR*sin(a),0),vector(0,0,1),armZ-0.6,armZ+(flip?5.6:3.6),M3_CLR);',
  '  if(!mono) drill(context,sub+"armHole",ring,vector(capR*cos(a),capR*sin(a),0),vector(0,0,1),armZ-0.6,armZ+(flip?5.6:3.6),M3_CLR);')
P('''  subtract(context,sub+"catchSocketCut",catchCap,catchSocket);
  drill(context,sub+"capPilot",catchCap,vector(capR,0,0),vector(0,0,1),flip?28.8:(compact?32.0:54.0),flip?33.5:(compact?36.5:58.5),M3_PILOT);''',
'''  if(mono) {
   // V5: the catch cap is printed with the rotor (no cap screw, no socket).
   opDeleteBodies(context,sub+"deleteSocketTool",{"entities":catchSocket});
   turn(context,sub+"capPosition",catchCap,a);
   opBoolean(context,sub+"integralCatch",{"tools":qUnion([ring,catchCap]),"operationType":BooleanOperationType.UNION});
  } else {
  subtract(context,sub+"catchSocketCut",catchCap,catchSocket);
  drill(context,sub+"capPilot",catchCap,vector(capR,0,0),vector(0,0,1),flip?28.8:(compact?32.0:54.0),flip?33.5:(compact?36.5:58.5),M3_PILOT);''')
P('''   turn(context,sub+"capScrewTurn",cs,a+definition.release*degree);
  }''',
'''   turn(context,sub+"capScrewTurn",cs,a+definition.release*degree);
  }
  }''')
# hinge: M3 bolt + nut
P('subtract(context,sub+("earBore"~j),ear,yc(context,sub+("earTool"~j),(j==0?M4_CLR:M4_PILOT),y0-.1,y1+.1));',
  '''subtract(context,sub+("earBore"~j),ear,yc(context,sub+("earTool"~j),(mono?M3_CLR:(j==0?M4_CLR:M4_PILOT)),y0-.1,y1+.1));
   if(mono && j==1) {
    // M3 nut slot, open on the +Y face of the ear (the nut slides in from the window side).
    subtract(context,sub+"hingeNutCut",ear,radialBox(context,sub+"hingeNutSlot",22.1,27.9,9.2,12.2,-3.3,6.6,0*degree));
   }''')
P('subtract(context,sub+"leafBore",panel,yc(context,sub+"leafTool",M4_CLR,-7.5,7.5));',
  'subtract(context,sub+"leafBore",panel,yc(context,sub+"leafTool",mono?M3_CLR:M4_CLR,-7.5,7.5));')
P('var hs=screwHW(context,sub+"hingeScrew",vector(25,-12,0),vector(0,1,0),"M4BH",25,"HW H"~(i+1)~" hinge screw - M4x25 button head");',
  'var hs=screwHW(context,sub+"hingeScrew",vector(25,-12,0),vector(0,1,0),(mono?"M3BH":"M4BH"),25,"HW H"~(i+1)~(mono?" hinge bolt - M3x25 button head, nut in the +Y ear":" hinge screw - M4x25 button head"));')
P('   turn(context,sub+"hingeScrewTurn",hs,a);',
  '''   turn(context,sub+"hingeScrewTurn",hs,a);
   if(mono) {
    var hn=nutHW(context,sub+"hingeNut",vector(25,9.7,0),vector(0,1,0),5.5,2.4,1.5,"HW H"~(i+1)~" hinge nut - M3 hex");
    turn(context,sub+"hingeNutTurn",hn,a);
   }''')
# V4-only blocks are skipped for mono
P(' for(var side=0;side<2;side+=1) for(var lv=0;lv<(compact?1:2);lv+=1) {\n  var rsa=', ' for(var side=0;side<(mono?0:2);side+=1) for(var lv=0;lv<(compact?1:2);lv+=1) {\n  var rsa=')
P(' if(compact) for(var s=0;s<4;s+=1) {\n  // V2: thick supports', ' if(compact && !mono) for(var s=0;s<4;s+=1) {\n  // V2: thick supports')

MONOBLOCK = r""" if(mono) {
  // ---- V5 one-piece module housing -------------------------------------------------------------------------
  // Floor plate with a centre hole, cut flush at z=-10 (the module seat is the transition plug top).
  opBoolean(context,id+"v5FloorJoin",{"tools":qUnion([carrier,cylinderMM(context,id+"v5Floor",30.5,-10.5,-8)]),"operationType":BooleanOperationType.UNION});
  subtract(context,id+"v5FloorHole",carrier,cylinderMM(context,id+"v5FloorHoleTool",4,-11,-7.9));
  subtract(context,id+"v5BaseTrim",carrier,cylinderMM(context,id+"v5BaseTrimTool",40,-20,-10));
  // Rotation limiter stops stand on the bearing spokes, ABOVE the ring (V4 had them below). Same faces as V4.
  var v5LimA=radialBox(context,id+"v5LimStop1",10,12.8,-11,-3.4,0.4,13.6,60*degree);
  var v5LimB=radialBox(context,id+"v5LimStop2",10,19,3.4,11,0.4,13.6,125*degree);
  opBoolean(context,id+"v5LimStopsJoin",{"tools":qUnion([carrier,v5LimA,v5LimB]),"operationType":BooleanOperationType.UNION});
  // Set 2: four radial M3 bolts (from outside, through the tube) into nuts in the housing wall. The nut sits in a hexagon pocket
  // open to the inside (nuts are loaded before the rotor is dropped in). Boss R27.6..30.2, bolt axis z=12.
  for(var k=0;k<4;k+=1) {
   var v5az=(45+90*k)*degree;var v5s=id+("v5Bolt"~k);
   opBoolean(context,v5s+"boss",{"tools":qUnion([carrier,radialBox(context,v5s+"bossBox",27.6,30.2,-4.2,4.2,7.2,9.6,v5az)]),"operationType":BooleanOperationType.UNION});
   radialNutPocket(context,v5s+"np",carrier,v5az,12,27.0,3.2,5.7);
   radialDrill(context,v5s+"clr",carrier,v5az,12,29.5,33.5,M3_CLR);
   if(definition.hardware) radialBoltHW(context,v5s+"hw",v5az,12,27.6,"module "~(k+1));
  }
  // Hinge bolt access: a 6.6 mm channel along the hinge axis through the housing wall on the head side of each hinge (bench use, module out of the tube).
  for(var k=0;k<4;k+=1) {
   var v5ch=yc(context,id+("v5HingeAccess"~k),3.3,-25,-12.2);
   turn(context,id+("v5HingeAccessTurn"~k),v5ch,k*90*degree);
   subtract(context,id+("v5HingeAccessCut"~k),carrier,v5ch);
  }
 }
 if(flip && !mono) {
  // V4: SG90 flipped on top (shaft down)."""
P(' if(flip) {\n  // V4: SG90 flipped on top (shaft down).', MONOBLOCK)
P(' if(flip) {\n  // Fill the tiny closed voids', ' if(flip && !mono) {\n  // Fill the tiny closed voids')
P(' for(var side=0;side<2;side+=1) {\n  var a=(45+side*180)*degree;\n  var seamBoss', ' for(var side=0;side<(mono?0:2);side+=1) {\n  var a=(45+side*180)*degree;\n  var seamBoss')
P(' opSplitPart(context,id+"housingSplit",{"targets":carrier,"tool":plane(vector(0,0,0)*millimeter,seamNormal)});',
  ' if(!mono) opSplitPart(context,id+"housingSplit",{"targets":carrier,"tool":plane(vector(0,0,0)*millimeter,seamNormal)});')
P(' for(var j=0;j<size(halves);j+=1) label(context,halves[j],"C"~(j+1)~" Split BT80 housing - clamp with 4 x M3 seam screws, peg-aligned",blue);',
  ' for(var j=0;j<size(halves);j+=1) label(context,halves[j],mono ? "C V5 module housing - one piece, no seam, 4 radial M3 nuts, limiter above the ring" : ("C"~(j+1)~" Split BT80 housing - clamp with 4 x M3 seam screws, peg-aligned"),blue);')
P(' var negative=halves[0];var positive=halves[1];\n if(dot(evApproximateCentroid(context,{"entities":negative})/millimeter,seamNormal)>0) {negative=halves[1];positive=halves[0];}',
  ' var negative=halves[0];var positive=mono?halves[0]:halves[1];\n if(!mono && dot(evApproximateCentroid(context,{"entities":negative})/millimeter,seamNormal)>0) {negative=halves[1];positive=halves[0];}')
P(' for(var side=0;side<2;side+=1) for(var level=0;level<2;level+=1) {', ' for(var side=0;side<(mono?0:2);side+=1) for(var level=0;level<2;level+=1) {')
P(' for(var side=0;side<2;side+=1) for(var lv=0;lv<2;lv+=1) {\n  var ssa2', ' for(var side=0;side<(mono?0:2);side+=1) for(var lv=0;lv<2;lv+=1) {\n  var ssa2')
P('label(context,ring,"R Top knob + keyed crown arms + four kick cams - 0 LOCK 65 OPEN",[.28,.68,.42]);',
  'label(context,ring,mono ? "R V5 rotor - integral catch caps, four kick cams, limiter finger above the ring" : "R Top knob + keyed crown arms + four kick cams - 0 LOCK 65 OPEN",[.28,.68,.42]);')

# ---- modularBrake
P('annotation {"Name":"Module: 0 spring, 1 direct servo, 2 unloaded spring samples, 3 V3 servo straight on the rotor, 4 V4 servo on top","Default":0} isInteger(definition.mode,{(unitless):[0,0,4]} as IntegerBoundSpec);',
  'annotation {"Name":"Module: 0 spring, 1 direct servo, 2 unloaded spring samples, 3 V3 servo straight on the rotor, 4 V4 servo on top, 5 V5 modular","Default":0} isInteger(definition.mode,{(unitless):[0,0,5]} as IntegerBoundSpec);')
P('"flip":definition.mode==4,"hardware":definition.hardware,"tubes":definition.tubes});',
  '"flip":definition.mode>=4,"mono":definition.mode==5,"hardware":definition.hardware,"tubes":definition.tubes && definition.mode!=5});')

V5MODE = r""" if(definition.mode==5) {
  stage="v5 rotor top";
  var hz=0.0;   // vertical shift of the head stack (kept as a parameter; 0 after the V5.6 redesign)
  var es5=vector(cos(135*degree),sin(135*degree),0);
  // Horn pocket + arm slot open at the top of the hub, with a three-step tapered lead-in (slot +-2.2 widening to +-4.3 mm) so the horn finds the slot and turns the free rotor into line (about +-10 deg).
  var pocket5=cylinderMM(context,id+"v5HornPocket",4.5,41.3,45.0);
  var slot5=radialBox(context,id+"v5HornSlot",0,13,-2.2,2.2,41.3,3.7,0*degree);
  var lead5a=radialBox(context,id+"v5LeadA",0,13,-2.9,2.9,42.9,2.1,0*degree);
  var lead5b=radialBox(context,id+"v5LeadB",0,13,-3.6,3.6,43.6,1.4,0*degree);
  var lead5c=radialBox(context,id+"v5LeadC",0,13,-4.3,4.3,44.3,0.7,0*degree);
  try { opBoolean(context,id+"v5PocketJoin",{"tools":qUnion([pocket5,slot5,lead5a,lead5b,lead5c]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"v5PocketJoin"); }
  turn(context,id+"v5PocketTurn",pocket5,(45+definition.release)*degree);
  subtract(context,id+"v5HornPocketCut",rotor,pocket5);
  var hornHub5=cylinderMM(context,id+"v5HornHub",4,41.5,43.3);
  var hornArm5=radialBox(context,id+"v5HornArm",0,11,-1.7,1.7,41.5,1.8,0*degree);
  try { opBoolean(context,id+"v5HornJoin",{"tools":qUnion([hornHub5,hornArm5]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"v5HornJoin"); }
  turn(context,id+"v5HornTurn",hornHub5,(45+definition.release)*degree);
  label(context,hornHub5,"EH SG90 horn REFERENCE - fit the socket to your actual horn",[.8,.69,.25]);
  if(definition.hardware)
   screwHW(context,id+"v5HornScrew",vector(0,0,41.5),vector(0,0,1),"M2BH",6,"HW horn screw - M2x6 (the one supplied with the servo), fitted from below while the head is out");
  stage="v5 servo";
  var sBody5=radialBox(context,id+"v5ServoBody",-6.5,16.0,-6.1,6.1,45.2+hz,22.7,135*degree);
  var sTab5=radialBox(context,id+"v5ServoTab",-11.5,21.0,-5.9,5.9,49.4+hz,2.5,135*degree);
  var sSpl5=cylinderMM(context,id+"v5Spline",2.4,41.5,45.2);
  try { opBoolean(context,id+"v5ServoJoin",{"tools":qUnion([sBody5,sTab5,sSpl5]),"operationType":BooleanOperationType.UNION}); } catch { throw regenError("Boolean failed at " ~ id+"v5ServoJoin"); }
  for(var k=0;k<2;k+=1) {
   var hs5=k==0?18.8:-9.3;
   drill(context,id+("v5TabHole"~k),sBody5,vector(hs5*es5[0],hs5*es5[1],49.0+hz),vector(0,0,1),0,3.6,1.1);
  }
  label(context,sBody5,"E SG90 servo REFERENCE - shaft down, flange screwed to the two head ledges - measure your servo",[.35,.38,.43]);
  stage="v5 head";
  // ---- HEAD cup: sleeve R29.9..32.2, floor under the electronics, two servo ledge posts hanging into the housing top at 135 / 315 deg.
  var head5=tubeMM(context,id+"v5Sleeve",32.2,29.9,59.0,88.3);
  opBoolean(context,id+"v5FloorJoin",{"tools":qUnion([head5,cylinderMM(context,id+"v5HeadFloor",30.1,68.5+hz,70.3+hz)]),"operationType":BooleanOperationType.UNION});
  for(var k=0;k<2;k+=1) {
   var pa=(135+180*k)*degree;var ps5=id+("v5Post"~k);
   // V5.7 (arm broke at the cup): each arm is now a wide curved web (+-11 deg, about 10 mm across) that follows the sleeve and is buried 1.1 mm into the sleeve wall for its whole 18 mm height, instead of a 7 mm post touching the wall by 0.2 mm.
   var postLow=sector(context,ps5+"low",25.5,28.9,11,51.9+hz,7.6-hz);
   turn(context,ps5+"lowT",postLow,pa);
   var postUp=sector(context,ps5+"up",25.5,31.0,11,59.0,11.0+hz);
   turn(context,ps5+"upT",postUp,pa);
   var ledge5=radialBox(context,ps5+"ledge",k==0?16.3:6.8,28.0,-4.5,4.5,51.9+hz,4.3,pa);
   opBoolean(context,ps5+"join",{"tools":qUnion([head5,postLow,postUp,ledge5]),"operationType":BooleanOperationType.UNION});
   // M2 nut recess in the UNDERSIDE of the ledge (the servo tab then covers it), clearance hole up through the ledge.
   var hr5=k==0?18.8:9.3;
   var np5=hexPrism(context,ps5+"nutTool",vector(hr5,0,51.8+hz),vector(0,0,1),4.2,2.0);
   turn(context,ps5+"nutTurn",np5,pa);
   subtract(context,ps5+"nutCut",head5,np5);
   var ch5=cylinderMM(context,ps5+"holeTool",1.1,51.8+hz,56.3+hz);
   opTransform(context,ps5+"holeMove",{"bodies":ch5,"transform":transform(vector(hr5,0,0)*millimeter)});
   turn(context,ps5+"holeTurn",ch5,pa);
   subtract(context,ps5+"holeCut",head5,ch5);
   // V5.6: no screwdriver holes in the floor any more: the servo is pushed up into the cup from below, its tabs against the UNDERSIDE of the ledges, screws from below.
   if(definition.hardware) {
    var sc5=screwHW(context,ps5+"hw",vector(hr5*cos(pa),hr5*sin(pa),49.4+hz),vector(0,0,1),"M2BH",8,"HW servo flange bolt "~(k+1)~" - M2x8 button head, from below, head under the servo tab");
    var sn5=nutHW(context,ps5+"nutHW",vector(hr5,0,51.95+hz),vector(0,0,1),4.0,1.6,1.0,"HW servo flange nut "~(k+1)~" - M2 hex");
    turn(context,ps5+"nutHWTurn",sn5,pa);
   }
  }
  // Servo cable slot through the floor (provisional position).
  subtract(context,id+"v5CableSlot",head5,radialBox(context,id+"v5CableTool",2,10,-1.75,1.75,68.4+hz,2,135*degree));
  // Component pockets (rims) on the floor: battery, Mercury V1, regulator on its edge. All inside R29.0 (checked in the script).
  var v5Comp=[[-21.4,21.4,-20.4,-1.0,12.4],[-15.4,15.4,0.0,17.3,11.2],[-12.9,12.9,18.1,26.5,15.4]];
  for(var k=0;k<3;k+=1) {
   var c5=v5Comp[k];
   var rim5=radialBox(context,id+("v5Rim"~k),c5[0]-.8,c5[1]+.8,c5[2]-.8,c5[3]+.8,70.3+hz,2.7,0*degree);
   subtract(context,id+("v5RimCut"~k),rim5,radialBox(context,id+("v5RimTool"~k),c5[0],c5[1],c5[2],c5[3],70.2+hz,3,0*degree));
   opBoolean(context,id+("v5RimJoin"~k),{"tools":qUnion([head5,rim5]),"operationType":BooleanOperationType.UNION});
  }
  // Vents (static pressure for the Mercury), USB-C window and switch slot: provisional positions, also cut in the tube.
  for(var k=0;k<3;k+=1) radialDrill(context,id+("v5Vent"~k),head5,[0,180,315][k]*degree,75+hz,29.5,33.5,1.5);
  subtract(context,id+"v5Usb",head5,radialBox(context,id+"v5UsbTool",29.5,33.5,-4.6,4.6,74.3+hz,3.4,90*degree));
  subtract(context,id+"v5Switch",head5,radialBox(context,id+"v5SwitchTool",29.5,33.5,-6,6,75+hz,6,270*degree));
  // Set 1: four radial M3 bolts through the tube and the sleeve wall into nuts in the LID bosses.
  var v5HeadAz=[45,135,250,290];
  for(var k=0;k<4;k+=1) radialDrill(context,id+("v5HeadClr"~k),head5,v5HeadAz[k]*degree,82+hz,29.0,33.5,M3_CLR);
  label(context,head5,"H V5 head cup - sleeve, floor, servo ledges, electronics pockets (reusable)",[.2,.45,.75]);
  // ---- LID: disc under the top of the sleeve, four bosses with hexagon nut pockets open to the inside. The set-1 bolts clamp sleeve and lid.
  var lid5=cylinderMM(context,id+"v5Lid",29.7,86.3+hz,88.3+hz);
  for(var k=0;k<4;k+=1) {
   var la=v5HeadAz[k]*degree;var ls=id+("v5LidBoss"~k);
   opBoolean(context,ls+"join",{"tools":qUnion([lid5,radialBox(context,ls+"box",24.4,29.6,-3.8,3.8,77.7+hz,8.7,la)]),"operationType":BooleanOperationType.UNION});
   radialNutPocket(context,ls+"np",lid5,la,82+hz,23.9,3.1,5.7);
   radialDrill(context,ls+"clr",lid5,la,82+hz,26.5,33.5,M3_CLR);
   if(definition.hardware) radialBoltHW(context,ls+"hw",la,82+hz,24.4,"head "~(k+1));
  }
  label(context,lid5,"K V5 head lid - four nut bosses, held by the set-1 bolts",[.2,.45,.75]);
  // Electronics (references): Mercury V1 30 x 16.9 x 10.8, regulator 25 x 15 x 8 stood on its edge, Spektrum 300 mAh 2S 42 x 19 x 12.
  var batt5=radialBox(context,id+"v5Battery",-21,21,-20.2,-1.2,70.6+hz,12,0*degree);
  label(context,batt5,"E4 Servo battery Spektrum 300 mAh 2S LiPo REFERENCE (42 x 19 x 12, as listed - measure yours)",[.95,.83,.36]);
  var merc5=radialBox(context,id+"v5Mercury",-15,15,0.2,17.1,70.6+hz,10.8,0*degree);
  label(context,merc5,"E2 Mercury V1 altimeter REFERENCE (30 x 16.9 x 10.8)",[.55,.35,.75]);
  var reg5=radialBox(context,id+"v5Regulator",-12.5,12.5,18.3,26.3,70.6+hz,15,0*degree);
  label(context,reg5,"E3 5 V 3 A regulator REFERENCE (placeholder 25 x 15 x 8, stood on its 8 mm edge)",[.94,.54,.63]);
  stage="v5 transition";
  // ---- TRANSITION, BT80 side only: plug (module seat), shoulder inside the tube, set-3 nut pockets. Cone is a placeholder; the BT70 side is not designed here.
  var tr5=tubeMM(context,id+"v5Shoulder",32.2,26.0,-34,-22);
  opBoolean(context,id+"v5PlugJoin",{"tools":qUnion([tr5,tubeMM(context,id+"v5Plug",29.6,26.0,-22.1,-10.2)]),"operationType":BooleanOperationType.UNION});
  for(var k=0;k<4;k+=1) {
   var ta=(45+90*k)*degree;var ts=id+("v5TransBolt"~k);
   radialNutPocket(context,ts+"np",tr5,ta,-28,25.5,3.1,5.7);
   radialDrill(context,ts+"clr",tr5,ta,-28,28.0,33.5,M3_CLR);
   if(definition.hardware) radialBoltHW(context,ts+"hw",ta,-28,26.0,"transition "~(k+1));
  }
  var cone5=newSketchOnPlane(context,id+"v5ConeSk",{"sketchPlane":plane(vector(0,0,0)*millimeter,vector(0,-1,0),vector(1,0,0))});
  var conePts=[];for(var p5 in [vector(32.2,-33.9),vector(28.15,-69),vector(26.15,-69),vector(30.2,-33.9),vector(32.2,-33.9)]) conePts=append(conePts,p5*millimeter);
  skPolyline(cone5,"p",{"points":conePts});skSolve(cone5);
  opRevolve(context,id+"v5Cone",{"entities":qSketchRegion(id+"v5ConeSk"),"axis":line(vector(0,0,0)*millimeter,vector(0,0,1)),"angleForward":2*PI*radian});
  opDeleteBodies(context,id+"v5ConeSkDel",{"entities":qCreatedBy(id+"v5ConeSk",EntityType.BODY)});
  opBoolean(context,id+"v5ConeJoin",{"tools":qUnion([tr5,solid(id+"v5Cone")]),"operationType":BooleanOperationType.UNION});
  label(context,tr5,"T V5 transition, BT80 side (plug + shoulder + 4 nut pockets). Cone is a PLACEHOLDER: the BT70 side is not touched or designed here",[.86,.78,.55]);
  if(definition.tubes) {
   stage="v5 tube";
   // ---- reference BT80 tube: one piece, four windows 67 deg x 63.8 mm, 12 clearance holes, vents, USB-C window and switch slot.
   var tube5=tubeMM(context,id+"v5Tube",33.02,32.51,-34,100);
   for(var k=0;k<4;k+=1) {
    var tw5=sector(context,id+("v5Win"~k),32.0,34,33.5,-9.2,63.8);
    turn(context,id+("v5WinTurn"~k),tw5,k*90*degree);
    subtract(context,id+("v5WinCut"~k),tube5,tw5);
    radialDrill(context,id+("v5TubeMod"~k),tube5,(45+90*k)*degree,12,32.0,33.5,M3_CLR);
    radialDrill(context,id+("v5TubeTr"~k),tube5,(45+90*k)*degree,-28,32.0,33.5,M3_CLR);
    radialDrill(context,id+("v5TubeHead"~k),tube5,v5HeadAz[k]*degree,82+hz,32.0,33.5,M3_CLR);
   }
   for(var k=0;k<3;k+=1) radialDrill(context,id+("v5TubeVent"~k),tube5,[0,180,315][k]*degree,75+hz,32.0,33.5,1.5);
   subtract(context,id+"v5TubeUsb",tube5,radialBox(context,id+"v5TubeUsbTool",32.0,33.5,-4.6,4.6,74.3+hz,3.4,90*degree));
   subtract(context,id+"v5TubeSwitch",tube5,radialBox(context,id+"v5TubeSwitchTool",32.0,33.5,-6,6,75+hz,6,270*degree));
   label(context,tube5,"REF BT80 tube - one piece: 4 windows, 12 M3 clearance holes (4 head z 82, 4 module z 12, 4 transition z -28), 3 vents, USB-C window and switch slot (provisional) - cut once from the real tube",TUBE_TAN);
  }
  return;
 }
 if(definition.mode==4) {"""
P(' if(definition.mode==4) {', V5MODE)

# V5: the hard-stop block corner must stay inside the R32.2 housing surface (a rectangular box of R32.08 reaches R32.64 at its corners)
P('radialBox(context,sub+"outerCompressionStop",27,32.8+dr,-6,6,-15,7.6,0*degree)', 'radialBox(context,sub+"outerCompressionStop",27,mono?31.6:32.8+dr,-6,6,-15,7.6,0*degree)')

# V5: hinge ear cylinders (R5.2 about x=25, out to y=12) reach R32.49; trim to R4.9 so the housing stays inside R32.2 + 0.02
P('var ear=yc(context,sub+("ear"~j),5.2,y0,y1);', 'var ear=yc(context,sub+("ear"~j),mono?4.9:5.2,y0,y1);')

# V5: the integral catch finger top is flush with the hub top (z 44.6) so the rotor prints hub-down on one flat plane (V4 finger stood 0.2 mm proud)
P('var catchFinger=radialBox(context,sub+"catchFinger",23.6,26.0,-3.0,3.0,flip?38.9:40.8,flip?5.9:5.2,0*degree);',
  'var catchFinger=radialBox(context,sub+"catchFinger",23.6,26.0,-3.0,3.0,flip?38.9:40.8,mono?5.7:(flip?5.9:5.2),0*degree);')

# ================================================================== V5.1: stiffer fin root + wide stop (from the FEA of the printed fin)
P('// Azimuth of the radial tube-retention screw in V2 support s (0..3).', r"""// V5.1: wide tapered root gusset (yHalf = half width), triangle in the radial (x) - height (z) plane, ends at z 22.5 below the cam band.
function rootGusset(context is Context, id is Id, yHalf is number, zb is number) returns Query
{
    var sk = newSketchOnPlane(context, id + "sk", { "sketchPlane" : plane(vector(0, yHalf, 0) * millimeter, vector(0, -1, 0), vector(1, 0, 0)) });
    var points = [];
    for (var p in [vector(25.5, zb), vector(31.5, zb), vector(31.5, 22.5), vector(25.5, zb + 3.2), vector(25.5, zb)])
        points = append(points, p * millimeter);
    skPolyline(sk, "p", { "points" : points });
    skSolve(sk);
    opExtrude(context, id + "ex", { "entities" : qSketchRegion(id + "sk"), "direction" : vector(0, -1, 0), "endBound" : BoundingType.BLIND, "endDepth" : 2 * yHalf * millimeter });
    opDeleteBodies(context, id + "del", { "entities" : qCreatedBy(id + "sk", EntityType.BODY) });
    return solid(id + "ex");
}

// Azimuth of the radial tube-retention screw in V2 support s (0..3).""")
P('var brace=arcRootBrace(context,sub+"brace");\n  opBoolean(context,sub+"leafJoin",{"tools":qUnion([panel,barrel,web,pad,brace]),"operationType":BooleanOperationType.UNION});',
  'var brace=arcRootBrace(context,sub+"brace");\n  var leafParts=[panel,barrel,web,pad,brace];\n  if(mono) leafParts=append(leafParts,rootGusset(context,sub+"braceWide",12,6.0));\n  opBoolean(context,sub+"leafJoin",{"tools":qUnion(leafParts),"operationType":BooleanOperationType.UNION});')
P('var pad=sector(context,sub+"rootPad",28.8,31.3,22,4,14);', 'var pad=mono?sector(context,sub+"rootPad",27.8,31.3,27,4,16):sector(context,sub+"rootPad",28.8,31.3,22,4,14);')
P('var landing=radialBox(context,sub+"landing",29,32.4+dr,-6,6,4,4,0*degree);', 'var landing=mono?sector(context,sub+"landing",29,31.5,24,4,4):radialBox(context,sub+"landing",29,32.4+dr,-6,6,4,4,0*degree);')
P('var outerStop=radialBox(context,sub+"outerCompressionStop",27,mono?31.6:32.8+dr,-6,6,-15,7.6,0*degree);',
  'var outerStop=mono?sector(context,sub+"outerCompressionStop",27,31.9,24,-15,8.4):radialBox(context,sub+"outerCompressionStop",27,32.8+dr,-6,6,-15,7.6,0*degree);')

# ================================================================== V5.2: under-hinge tail lock (mentor-inspired): tail on the fin, U pocket in the stop blocks, keeper towers + pads
# A tail below the hinge swings inboard and up as the fin opens; at 90 deg its top face meets keeper pads in the housing, so the stop (outboard, below the pin)
# and the keeper (inboard, above the tail) form a force couple instead of loading the pin and the web alone.
P('  if(mono) leafParts=append(leafParts,rootGusset(context,sub+"braceWide",12,6.0));',
  '  if(mono) leafParts=append(leafParts,rootGusset(context,sub+"braceWide",12,6.0));\n  if(mono) leafParts=append(leafParts,radialBox(context,sub+"lockTail",22.0,26.5,-6,6,-7.6,4.6,0*degree));')
P('  opBoolean(context,sub+"leafJoin",{"tools":qUnion(leafParts),"operationType":BooleanOperationType.UNION});',
  '  opBoolean(context,sub+"leafJoin",{"tools":qUnion(leafParts),"operationType":BooleanOperationType.UNION});\n  if(mono) subtract(context,sub+"rootClip",panel,tubeMM(context,sub+"rootClipTool",45,32.21,2,26));')
P('  opBoolean(context,sub+"carrierJoin",{"tools":qUnion([carrier,bracket]),"operationType":BooleanOperationType.UNION});',
  '''  opBoolean(context,sub+"carrierJoin",{"tools":qUnion([carrier,bracket]),"operationType":BooleanOperationType.UNION});
  if(mono) {
   // U pocket for the tail, open to the outside (the fin goes in radially through the window): through the hard-stop blocks, z -8.3 .. -6.4.
   var tailPocket=radialBox(context,sub+"tailPocket",21.6,33.5,-6.5,6.5,-8.3,1.9,0*degree);
   turn(context,sub+"tailPocketTurn",tailPocket,a);
   subtract(context,sub+"tailPocketCut",carrier,tailPocket);
  }''')
P('var v5LimB=radialBox(context,id+"v5LimStop2",10,19,3.4,11,0.4,13.6,125*degree);', 'var v5LimB=radialBox(context,id+"v5LimStop2",10,16.5,3.4,8.0,0.4,13.6,125*degree);')
P('''  // Hinge bolt access: a 6.6 mm channel along the hinge axis''',
  '''  // Keeper towers (on the floor, beside the tail path) and pads over the tail at 90 deg: tail top face z +3.0, pad underside z 3.4 (0.4 mm gap).
  for(var k=0;k<4;k+=1) {
   var v5ka=k*90*degree;var v5ks=id+("v5Keeper"~k);
   for(var sy=0;sy<2;sy+=1) {
    var y0=sy==0?7.8:-11.2;var y1=sy==0?11.2:-7.8;var p0=sy==0?4.6:-7.8;var p1=sy==0?7.8:-4.6;
    opBoolean(context,v5ks+("tw"~sy),{"tools":qUnion([carrier,radialBox(context,v5ks+("towerBox"~sy),17.5,21.4,y0,y1,-9.0,15.4,v5ka)]),"operationType":BooleanOperationType.UNION});
    opBoolean(context,v5ks+("pd"~sy),{"tools":qUnion([carrier,radialBox(context,v5ks+("padBox"~sy),17.5,20.0,p0,p1,3.4,3.0,v5ka)]),"operationType":BooleanOperationType.UNION});
   }
  }
  // Hinge bolt access: a 6.6 mm channel along the hinge axis''')

# ================================================================== V5.3: the head must seat fully (photos: it stood about 5 mm proud)
# Likely cause: a real SG90 has a raised gear boss (about O11.8 x 4.5) round the shaft plus a longer spline (about 4 mm); the model had a plain box and a 3.7 mm stub,
# so with the shaft down the real boss sat on the rotor hub top. Fix: model the boss and spline, counterbore the hub for the boss, deepen the horn socket,
# loosen the head outer diameter (R32.2 -> R31.95) and chamfer the lower edges.
P('crownHub=cylinderMM(context,id+"crownHub",9,flip?33.6:58.6-dzT,flip?44.6:61.6-dzT);', 'crownHub=cylinderMM(context,id+"crownHub",mono?10.5:9,flip?33.6:58.6-dzT,flip?44.6:61.6-dzT);')
P('''  var pocket5=cylinderMM(context,id+"v5HornPocket",4.5,41.3,45.0);
  var slot5=radialBox(context,id+"v5HornSlot",0,13,-2.2,2.2,41.3,3.7,0*degree);''',
'''  var pocket5=cylinderMM(context,id+"v5HornPocket",4.5,35.0,45.0);
  var slot5=radialBox(context,id+"v5HornSlot",0,13,-2.2,2.2,35.0,10.0,0*degree);
  // Counterbore for the servo gear boss (about O11.8 x 4.5) with a stepped lead-in.
  var cbore5=cylinderMM(context,id+"v5Cbore",6.6,38.6,45.0);
  var cstep5a=cylinderMM(context,id+"v5CboreA",7.1,43.0,45.0);
  var cstep5b=cylinderMM(context,id+"v5CboreB",7.7,43.9,45.0);''')
P('qUnion([pocket5,slot5,lead5a,lead5b,lead5c])','qUnion([pocket5,slot5,lead5a,lead5b,lead5c,cbore5,cstep5a,cstep5b])')
P('''  var hornHub5=cylinderMM(context,id+"v5HornHub",4,41.5,43.3);
  var hornArm5=radialBox(context,id+"v5HornArm",0,11,-1.7,1.7,41.5,1.8,0*degree);''',
'''  var hornHub5=cylinderMM(context,id+"v5HornHub",3.9,36.9+hz,40.4+hz);
  var hornArm5=radialBox(context,id+"v5HornArm",0,11,-1.7,1.7,36.9+hz,1.8,0*degree);''')
P('screwHW(context,id+"v5HornScrew",vector(0,0,41.5),vector(0,0,1),"M2BH",6,','screwHW(context,id+"v5HornScrew",vector(0,0,36.9+hz),vector(0,0,1),"M2BH",6,')
P('''  var sSpl5=cylinderMM(context,id+"v5Spline",2.4,41.5,45.2);
  try { opBoolean(context,id+"v5ServoJoin",{"tools":qUnion([sBody5,sTab5,sSpl5]),''',
'''  var sSpl5=cylinderMM(context,id+"v5Spline",2.4,36.7+hz,45.2+hz);
  var sBoss5=cylinderMM(context,id+"v5GearBoss",5.9,40.7+hz,45.2+hz);
  try { opBoolean(context,id+"v5ServoJoin",{"tools":qUnion([sBody5,sTab5,sSpl5,sBoss5]),''')
P('label(context,sBody5,"E SG90 servo REFERENCE - shaft down, flange screwed to the two head ledges - measure your servo",[.35,.38,.43]);',
  'label(context,sBody5,"E SG90 servo REFERENCE - shaft down, gear boss O11.8 x 4.5 and 4 mm spline modelled (typical SG90: MEASURE YOURS), flange screwed to the two head ledges",[.35,.38,.43]);')
# head sleeve a little smaller, with a lower-edge chamfer; module lower edge chamfer
P('var head5=tubeMM(context,id+"v5Sleeve",32.2,29.9,59.0,88.3);',
  '''var head5=tubeMM(context,id+"v5Sleeve",31.95,29.9,59.0,88.3+hz);
  v5Chamfer(context,id+"v5SleeveCh",head5,31.95,59.0,0.8);''')
P('''  subtract(context,id+"v5BaseTrim",carrier,cylinderMM(context,id+"v5BaseTrimTool",40,-20,-10));''',
  '''  subtract(context,id+"v5BaseTrim",carrier,cylinderMM(context,id+"v5BaseTrimTool",40,-20,-10));
  v5Chamfer(context,id+"v5BaseCh",carrier,32.2,-10.0,0.8);''')
P('// V5.1: wide tapered root gusset', r"""// V5.3: 45 deg lead-in chamfer on an outer bottom edge (radius r, height z, size c): cut a revolved triangle.
function v5Chamfer(context is Context, id is Id, target is Query, r is number, z is number, c is number)
{
    var sk = newSketchOnPlane(context, id + "sk", { "sketchPlane" : plane(vector(0, 0, 0) * millimeter, vector(0, -1, 0), vector(1, 0, 0)) });
    var pts = [];
    for (var p in [vector(r + 0.3, z - 0.3), vector(r - c, z - 0.3), vector(r - c, z), vector(r, z + c), vector(r + 0.3, z + c), vector(r + 0.3, z - 0.3)])
        pts = append(pts, p * millimeter);
    skPolyline(sk, "p", { "points" : pts });
    skSolve(sk);
    opRevolve(context, id + "rev", { "entities" : qSketchRegion(id + "sk"), "axis" : line(vector(0, 0, 0) * millimeter, vector(0, 0, 1)), "angleForward" : 2 * PI * radian });
    opDeleteBodies(context, id + "del", { "entities" : qCreatedBy(id + "sk", EntityType.BODY) });
    subtract(context, id + "cut", target, solid(id + "rev"));
}

// V5.1: wide tapered root gusset""")

# ================================================================== V5.4: ribs on the inner face of the fin (spine + two edge ribs), clear of the cam band (z 22.5..28, R<28.6) and the catch cap (R<26)
P('  if(mono) subtract(context,sub+"rootClip",panel,tubeMM(context,sub+"rootClipTool",45,32.21,2,26));',
  '''  if(mono) subtract(context,sub+"rootClip",panel,tubeMM(context,sub+"rootClipTool",45,32.21,2,26));
  if(mono) {
   // spine: z 4..20.5 and 28.5..47 (the follower fills z 20..29 between them); edge ribs: z 4..20 and 30..54 at +-27.5 deg, 2.2 deep from the shell
   var ribs=[radialBox(context,sub+"ribSpineA",26.8,30.0,-0.9,0.9,4,16.5,0*degree),radialBox(context,sub+"ribSpineB",27.5,30.0,-0.9,0.9,28.5,18.5,0*degree)];
   for(var rs=0;rs<2;rs+=1) for(var rz=0;rz<2;rz+=1) {
    var er=sector(context,sub+("ribEdge"~rs~rz),27.8,30.0,3.0,rz==0?4:30,rz==0?16:24);
    turn(context,sub+("ribEdgeTurn"~rs~rz),er,(rs==0?27.5:-27.5)*degree);
    ribs=append(ribs,er);
   }
   var ribAll=[panel];
   for(var rb in ribs) ribAll=append(ribAll,rb);
   opBoolean(context,sub+"ribJoin",{"tools":qUnion(ribAll),"operationType":BooleanOperationType.UNION});
  }''')
