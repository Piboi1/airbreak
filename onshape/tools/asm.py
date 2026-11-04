"""Build assembly mate groups / connectors / mates by cloning the user's Assembly 23 definitions."""
import copy, json, osapi, run

USER = dict(did='6193289111e752b62699c37d', wid='ac364bd1a753715c132e3c3c', eid='3e8c606f5c7627b828b8947f')


def strip_ids(o):
    if isinstance(o, dict):
        return {k: strip_ids(v) for k, v in o.items() if k not in ('nodeId', 'featureId')}
    if isinstance(o, list):
        return [strip_ids(x) for x in o]
    return o


def template_features():
    f = osapi.get(f"/assemblies/d/{USER['did']}/w/{USER['wid']}/e/{USER['eid']}/features")['features']
    return {x['name']: x for x in f}


def occ(inst_id):
    return {"btType": "BTMIndividualOccurrenceQuery-626", "path": [inst_id]}


def post_feature(did, wid, aid, feat):
    r = osapi.post(f"/assemblies/d/{did}/w/{wid}/e/{aid}/features", {
        "feature": feat, "serializationVersion": "1.2.23", "sourceMicroversion": "", "rejectMicroversionSkew": False})
    return r['feature']['featureId'] if 'feature' in r else r['featureId']


def mate_group(did, wid, aid, name, inst_ids):
    feat = {"btType": "BTMMateGroup-65", "featureType": "mateGroup", "name": name, "namespace": "", "version": 2,
            "suppressed": False, "subFeatures": [], "returnAfterSubfeatures": False, "parameterLibraries": [],
            "parameters": [{"btType": "BTMParameterQueryWithOccurrenceList-67", "libraryRelationType": "DEFAULT",
                            "queries": [occ(i) for i in inst_ids], "parameterId": "occurrencesQuery", "parameterName": ""}]}
    return post_feature(did, wid, aid, feat)


def clone_connector(tmpl, inst_id, name):
    f = strip_ids(copy.deepcopy(tmpl))
    f['name'] = name
    for p in f['parameters']:
        if p['parameterId'] == 'originQuery':
            p['queries'][0]['path'] = [inst_id]
    return f


def clone_mate(tmpl, name, cids):
    f = strip_ids(copy.deepcopy(tmpl))
    f['name'] = name
    for p in f['parameters']:
        if p['parameterId'] == 'mateConnectorsQuery':
            p['queries'] = [{"btType": "BTMFeatureQueryWithOccurrence-157", "path": [], "featureId": c, "queryData": ""} for c in cids]
    return f


def states(did, wid, aid):
    f = osapi.get(f"/assemblies/d/{did}/w/{wid}/e/{aid}/features")
    bad = {k: v['featureStatus'] for k, v in f['featureStates'].items() if v['featureStatus'] != 'OK'}
    return bad, f


def instances(did, wid, aid):
    asm = osapi.get(f"/assemblies/d/{did}/w/{wid}/e/{aid}")
    out = {}
    for i in asm['rootAssembly']['instances']:
        n = i['name']
        key = n.split(' ')[0]
        if key == 'HW':
            key = 'HW ' + ' '.join(n.split(' ')[1:4])
        if key == 'REF':
            key = 'REF ' + n.split(' ')[2]
        out[key] = i['id']
        out[n] = i['id']
    return out, asm


def build(aid, compact):
    d = run.ids(); did, wid = d['did'], d['wid']
    inst, asm = instances(did, wid, aid)
    names = [i['name'] for i in asm['rootAssembly']['instances']]
    T = template_features()

    def ids_where(pred):
        return [i['id'] for i in asm['rootAssembly']['instances'] if pred(i['name'])]

    stationary = ids_where(lambda n: (n.split(' ')[0] in ('C1', 'C2', 'D', 'N', 'I', 'M', 'F', 'V', 'W', 'E', 'S', 'G') or n.startswith('REF')
                                      or (n.startswith('HW') and not n.startswith('HW L'))))
    rotor = ids_where(lambda n: n.split(' ')[0] in ('R', 'L1', 'L2', 'L3', 'L4', 'U', 'Q', 'T', 'X') or n.startswith('HW L'))
    print('stationary', len(stationary), 'rotor', len(rotor))
    mate_group(did, wid, aid, 'Stationary structure, hardware, tube references and elastic reference bodies', stationary)
    mate_group(did, wid, aid, 'Keyed rotor, output hub, thrust collar, catch caps, winding cap and adapter', rotor)
    mate_group(did, wid, aid, 'Short pushrod seated in yoke cup - contact representation', [inst['B'], inst['A']])
    if compact:
        for i in range(1, 5):
            mate_group(did, wid, aid, f'Fin P{i} with its glued BT80 cut-out TP{i}', [inst[f'P{i}'], inst[f'TP{i}']])
    c1 = inst['C1']
    # hinges
    for i in range(1, 5):
        a = clone_connector(T[f'Fixed hinge axis {i}'], c1, f'Fixed hinge axis {i}')
        b = clone_connector(T[f'Panel hinge axis {i}'], inst[f'P{i}'], f'Panel hinge axis {i}')
        ca, cb = post_feature(did, wid, aid, a), post_feature(did, wid, aid, b)
        mname = [n for n in T if n.startswith(f'Panel {i} - hinge')][0]
        post_feature(did, wid, aid, clone_mate(T[mname], f'Panel {i} - hinge - 0 to 90 deg (hard stop)', [cb, ca]))
    # cam shaft revolute
    a = post_feature(did, wid, aid, clone_connector(T['Fixed cam shaft axis'], c1, 'Fixed cam shaft axis'))
    b = post_feature(did, wid, aid, clone_connector(T['Rotating cam shaft axis'], inst['R'], 'Rotating cam shaft axis'))
    post_feature(did, wid, aid, clone_mate(T['Top knob - 0 LOCKED to 65 deg KICK'], 'Rotor - 0 LOCKED to 65 deg KICK', [b, a]))
    # button slider
    a = post_feature(did, wid, aid, clone_connector(T['Fixed button slide axis'], c1, 'Fixed button slide axis'))
    b = post_feature(did, wid, aid, clone_connector(T['Button slide axis'], inst['B'], 'Button slide axis'))
    post_feature(did, wid, aid, clone_mate(T['Lower trigger - lift UP 4.5 mm'], 'Lower trigger - lift UP 4.5 mm', [b, a]))
    # servo pusher
    a = post_feature(did, wid, aid, clone_connector(T['Fixed servo pusher axis'], c1, 'Fixed servo pusher axis'))
    b = post_feature(did, wid, aid, clone_connector(T['Moving servo pusher axis'], inst['J'], 'Moving servo pusher axis'))
    post_feature(did, wid, aid, clone_mate(T['Lower servo pusher - rotate upward'], 'Lower servo pusher - rotate upward', [b, a]))
    bad, f = states(did, wid, aid)
    print('feature count', len(f['features']), 'non-OK:', bad)
    return bad


def build_v3(aid):
    """V3: servo straight on the rotor. Stationary group (housing, servo, tube refs, hardware), rotor group (rotor, horn,
    catch caps), fin + cut-out groups, four hinge revolutes and the rotor revolute (the SG90 itself is the driver)."""
    d = run.ids(); did, wid = d['did'], d['wid']
    inst, asm = instances(did, wid, aid)
    T = template_features()

    def ids_where(pred):
        return [i['id'] for i in asm['rootAssembly']['instances'] if pred(i['name'])]

    rotor = ids_where(lambda n: n.split(' ')[0] in ('R', 'EH', 'L1', 'L2', 'L3', 'L4') or n.startswith('HW L') or n.startswith('HW horn'))
    stationary = ids_where(lambda n: n.split(' ')[0] in ('C1', 'C2', 'E') or n.startswith('REF')
                           or (n.startswith('HW') and not n.startswith('HW L') and not n.startswith('HW horn')))
    print('stationary', len(stationary), 'rotor', len(rotor))
    mate_group(did, wid, aid, 'Stationary housing halves, SG90 servo, hardware and tube references', stationary)
    mate_group(did, wid, aid, 'Rotor with horn, catch caps and horn screw (driven by the SG90)', rotor)
    for i in range(1, 5):
        mate_group(did, wid, aid, f'Fin P{i} with its glued BT80 cut-out TP{i}', [inst[f'P{i}'], inst[f'TP{i}']])
    c1 = inst['C1']
    for i in range(1, 5):
        a = clone_connector(T[f'Fixed hinge axis {i}'], c1, f'Fixed hinge axis {i}')
        b = clone_connector(T[f'Panel hinge axis {i}'], inst[f'P{i}'], f'Panel hinge axis {i}')
        ca, cb = post_feature(did, wid, aid, a), post_feature(did, wid, aid, b)
        mname = [n for n in T if n.startswith(f'Panel {i} - hinge')][0]
        post_feature(did, wid, aid, clone_mate(T[mname], f'Panel {i} - hinge - 0 to 90 deg (hard stop)', [cb, ca]))
    a = post_feature(did, wid, aid, clone_connector(T['Fixed cam shaft axis'], c1, 'Fixed cam shaft axis'))
    b = post_feature(did, wid, aid, clone_connector(T['Rotating cam shaft axis'], inst['R'], 'Rotating cam shaft axis'))
    post_feature(did, wid, aid, clone_mate(T['Top knob - 0 LOCKED to 65 deg KICK'], 'Servo horn / rotor - 0 LOCKED to 65 deg KICK', [b, a]))
    bad, f = states(did, wid, aid)
    print('feature count', len(f['features']), 'non-OK:', bad)
    return bad


def build_v4(aid):
    """V4: servo on top, bay at the bottom. Rotor group (rotor, horn, catch caps, their screws), one group per fin with its cut-out,
    everything else stationary; four hinge revolutes and the rotor revolute (the SG90 is the driver)."""
    d = run.ids(); did, wid = d['did'], d['wid']
    inst, asm = instances(did, wid, aid)
    T = template_features()

    def ids_where(pred):
        return [i['id'] for i in asm['rootAssembly']['instances'] if pred(i['name'])]

    is_rotor = lambda n: n.split(' ')[0] in ('R', 'EH', 'L1', 'L2', 'L3', 'L4') or n.startswith('HW L') or n.startswith('HW horn')
    is_fin = lambda n: n.split(' ')[0] in ('P1', 'P2', 'P3', 'P4', 'TP1', 'TP2', 'TP3', 'TP4')
    rotor = ids_where(is_rotor)
    stationary = ids_where(lambda n: not is_rotor(n) and not is_fin(n))
    print('stationary', len(stationary), 'rotor', len(rotor))
    mate_group(did, wid, aid, 'Stationary housing halves, SG90 servo, electronics, sled, transition, hardware and tube references', stationary)
    mate_group(did, wid, aid, 'Rotor with horn, catch caps and horn screw (driven by the SG90)', rotor)
    for i in range(1, 5):
        mate_group(did, wid, aid, f'Fin P{i} with its glued BT80 cut-out TP{i}', [inst[f'P{i}'], inst[f'TP{i}']])
    c1 = inst['C1']
    for i in range(1, 5):
        a = clone_connector(T[f'Fixed hinge axis {i}'], c1, f'Fixed hinge axis {i}')
        b = clone_connector(T[f'Panel hinge axis {i}'], inst[f'P{i}'], f'Panel hinge axis {i}')
        ca, cb = post_feature(did, wid, aid, a), post_feature(did, wid, aid, b)
        mname = [n for n in T if n.startswith(f'Panel {i} - hinge')][0]
        post_feature(did, wid, aid, clone_mate(T[mname], f'Panel {i} - hinge - 0 to 90 deg (hard stop)', [cb, ca]))
    a = post_feature(did, wid, aid, clone_connector(T['Fixed cam shaft axis'], c1, 'Fixed cam shaft axis'))
    b = post_feature(did, wid, aid, clone_connector(T['Rotating cam shaft axis'], inst['R'], 'Rotating cam shaft axis'))
    post_feature(did, wid, aid, clone_mate(T['Top knob - 0 LOCKED to 65 deg KICK'], 'Servo horn / rotor - 0 LOCKED to 65 deg KICK', [b, a]))
    bad, f = states(did, wid, aid)
    print('feature count', len(f['features']), 'non-OK:', bad)
    return bad


def clear_assembly_features(aid):
    """Delete every feature of an assembly (keeps the instances), newest first. Uses the assembly features endpoint (not the rate-limited part studio one)."""
    d = run.ids(); did, wid = d['did'], d['wid']
    f = osapi.get(f"/assemblies/d/{did}/w/{wid}/e/{aid}/features")['features']
    for x in reversed(f):
        from urllib.parse import quote
        osapi.delete(f"/assemblies/d/{did}/w/{wid}/e/{aid}/features/featureid/{quote(x['featureId'], safe='')}")
    return len(f)


def slider_mate(T, name, cids, zmin_mm, zmax_mm):
    f = strip_ids(copy.deepcopy(T['Lower trigger - lift UP 4.5 mm']))
    f['name'] = name
    for p in f['parameters']:
        if p['parameterId'] == 'mateConnectorsQuery':
            p['queries'] = [{"btType": "BTMFeatureQueryWithOccurrence-157", "path": [], "featureId": c, "queryData": ""} for c in cids]
        if p['parameterId'] == 'limitZMin':
            p['expression'] = f'{zmin_mm} mm'; p['value'] = zmin_mm / 1000.0
        if p['parameterId'] == 'limitZMax':
            p['expression'] = f'{zmax_mm} mm'; p['value'] = zmax_mm / 1000.0
    return f


def build_v5(aid):
    """V5 with service slides. Groups: tube + radial bolts (fixed), head (cup, lid, SG90, electronics, head nuts, servo bolts and nuts), horn (+ screw),
    module (housing, module nuts, hinge bolts and nuts), transition (+ nuts); rotor and the four fins are single parts.
    Mates: three sliders on the tube z axis (head up, transition down, module down or up), rotor revolute 0..65 on the housing, horn revolute 0..65 on the servo
    (set it to the same angle as the rotor), four fin hinges 0..90."""
    import re
    d = run.ids(); did, wid = d['did'], d['wid']
    inst, asm = instances(did, wid, aid)
    T = template_features()
    names = {i['id']: i['name'] for i in asm['rootAssembly']['instances']}

    def ids_where(pred):
        return [i for i, n in names.items() if pred(n)]

    first = lambda n: n.split(' ')[0]
    is_fixed = lambda n: n.startswith('REF') or re.match(r'HW (head|module|transition) \d bolt', n)
    is_head = lambda n: first(n) in ('H', 'K', 'E', 'E2', 'E3', 'E4') or re.match(r'HW head \d nut', n) or n.startswith('HW servo flange')
    is_horn = lambda n: first(n) == 'EH' or n.startswith('HW horn')
    is_module = lambda n: first(n) == 'C' or re.match(r'HW module \d nut', n) or re.match(r'HW H\d ', n)
    is_trans = lambda n: first(n) == 'T' or re.match(r'HW transition \d nut', n)
    groups = [('Tube (fixed) with the 12 radial bolts', is_fixed), ('Head: cup, lid, SG90, electronics, head nuts, servo bolts and nuts', is_head),
              ('SG90 horn and horn screw', is_horn), ('Module housing with its nuts and the hinge bolts and nuts', is_module), ('Transition (BT80 side) with its nuts', is_trans)]
    covered = set()
    for gname, pred in groups:
        ids = ids_where(pred)
        covered |= set(ids)
        print(gname[:40], len(ids))
        mate_group(did, wid, aid, gname, ids)
    rest = [names[i].split(' ')[0] for i in names if i not in covered]
    print('ungrouped (rotor + fins expected):', sorted(rest))
    tube = [i for i, n in names.items() if n.startswith('REF')][0]
    c1, hh, tt, rr = inst['C'], inst['H'], inst['T'], inst['R']

    def pair(fixed_inst, moving_inst, fixed_tmpl, moving_tmpl, fname, mname):
        a = post_feature(did, wid, aid, clone_connector(T[fixed_tmpl], fixed_inst, fname))
        b = post_feature(did, wid, aid, clone_connector(T[moving_tmpl], moving_inst, mname))
        return a, b

    for nm, mv, lo, hi in (('Head removal upward (take the 4 head bolts out first)', hh, 0, 140),
                           ('Transition removal downward (take the 4 transition bolts out first)', tt, -120, 0),
                           ('Module service slide: down with the transition off, or up with the head off (take the 4 module bolts out first)', c1, -130, 140)):
        a, b = pair(tube, mv, 'Fixed cam shaft axis', 'Fixed cam shaft axis', 'Tube axis for ' + nm[:30], 'Slide axis for ' + nm[:30])
        post_feature(did, wid, aid, slider_mate(T, nm, [b, a], lo, hi))
    for i in range(1, 5):
        a = clone_connector(T[f'Fixed hinge axis {i}'], c1, f'Fixed hinge axis {i}')
        b = clone_connector(T[f'Panel hinge axis {i}'], inst[f'P{i}'], f'Panel hinge axis {i}')
        ca, cb = post_feature(did, wid, aid, a), post_feature(did, wid, aid, b)
        mname = [n for n in T if n.startswith(f'Panel {i} - hinge')][0]
        post_feature(did, wid, aid, clone_mate(T[mname], f'Panel {i} - hinge - 0 to 90 deg (hard stop)', [cb, ca]))
    a, b = pair(c1, rr, 'Fixed cam shaft axis', 'Rotating cam shaft axis', 'Fixed cam shaft axis', 'Rotating cam shaft axis')
    post_feature(did, wid, aid, clone_mate(T['Top knob - 0 LOCKED to 65 deg KICK'], 'Rotor - 0 LOCKED to 65 deg KICK (on the housing)', [b, a]))
    a, b = pair(inst['E'], inst['EH'], 'Fixed cam shaft axis', 'Rotating cam shaft axis', 'SG90 shaft axis', 'Horn axis')
    post_feature(did, wid, aid, clone_mate(T['Top knob - 0 LOCKED to 65 deg KICK'], 'SG90 horn - 0 to 65 deg (set it to the same angle as the rotor)', [b, a]))
    bad, f = states(did, wid, aid)
    print('feature count', len(f['features']), 'non-OK:', bad)
    return bad


if __name__ == '__main__':
    import sys
    key, compact = sys.argv[1], sys.argv[2] == 'v2'
    build(run.ids()[key], compact)
