"""Kiểm chứng cấu trúc mạng và chạy xe mẫu; không đánh giá lợi ích làn sóng xanh."""
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from .model import binary, write_xml


def validate(root):
    net = ET.parse(root / "simulation/network/generated/corridor.net.xml").getroot()
    signals = ET.parse(root / "simulation/signals/fixed.add.xml").getroot()
    routes = ET.parse(root / "simulation/routes/source/sample.rou.xml").getroot()
    nodes = {n.get("id"): n for n in net.findall("junction")}
    assert {k for k,v in nodes.items() if v.get("type") == "traffic_light"} == set("ABCD"), "Cần đúng 4 nút đèn"
    edges = {e.get("id"): e for e in net.findall("edge") if e.get("function") != "internal"}
    assert len(edges) == 26 and all(len(e.findall("lane")) == 1 for e in edges.values())
    links = [c for c in net.findall("connection") if c.get("tl")]
    assert len(links) == 16
    allowed = {(c.get("from"), c.get("to")) for c in links}
    for route in routes.findall("route"):
        path = route.get("edges").split()
        assert all(e in edges for e in path)
        assert all(pair in allowed for pair in zip(path,path[1:])), "Tuyến bị đứt kết nối"
    for logic in signals.findall("tlLogic"):
        jid = logic.get("id")
        controlled = {int(c.get("linkIndex")): c for c in links if c.get("tl") == jid}
        assert set(controlled) == {0,1,2,3}
        phases = logic.findall("phase")
        assert logic.get("type") == "static" and logic.get("offset") == "0"
        assert [float(p.get("duration")) for p in phases] == [45,3,2,65,3,2]
        assert sum(float(p.get("duration")) for p in phases) == 120
        internal = nodes[jid].get("intLanes").split()
        requests = {int(q.get("index")): q for q in nodes[jid].findall("request")}
        for phase in phases:
            state = phase.get("state")
            assert len(state) == 4 and set(state) <= set("rGy")
            active = [c for index,c in controlled.items() if state[index] in "Gy"]
            for a in active:
                ia = internal.index(a.get("via"))
                foes = requests[ia].get("foes")[::-1]
                for b in active:
                    ib = internal.index(b.get("via"))
                    assert foes[ib] == "0", "Hai dòng xung đột cùng được bật"
        for index,c in controlled.items():
            main = c.get("from").split("_")[0] not in [jid+"N",jid+"S"]
            expected = ["G","y","r","r","r","r"] if main else ["r","r","r","G","y","r"]
            assert [p.get("state")[index] for p in phases] == expected
    assert {t.get("id") for t in signals.findall("tlLogic")} == set("ABCD")
    config = ET.parse(root / "simulation/scenarios/sample.sumocfg").getroot()
    for field in ["net-file","route-files","additional-files"]:
        ref = config.find("input/"+field).get("value")
        assert (root/"simulation/scenarios"/ref).is_file(), ref
    expected = sum(int(f.get("number")) for f in routes.findall("flow"))
    assert expected == 85
    return {"junctions": 4, "edges": len(edges), "controlled_connections": len(links), "sample_vehicles": expected}


def smoke_test(root):
    """Chạy SUMO, kiểm tra mọi xe về đích và trạng thái đèn thực theo từng giây."""
    checks = validate(root)
    with tempfile.TemporaryDirectory(prefix="greenwave-") as temp:
        out=Path(temp)
        events=ET.Element("additional")
        for jid in "ABCD":
            ET.SubElement(events,"timedEvent",type="SaveTLSStates",source=jid,dest=str(out/(jid+".xml")))
        write_xml(out/"events.add.xml",events)
        result=subprocess.run([binary("sumo"),"-c",str(root/"simulation/scenarios/sample.sumocfg"),"--additional-files",str(root/"simulation/signals/fixed.add.xml")+","+str(out/"events.add.xml"),"--tripinfo-output",str(out/"trips.xml"),"--summary-output",str(out/"summary.xml"),"--vehroute-output",str(out/"routes.xml"),"--no-step-log","true","--xml-validation","always"],capture_output=True,text=True,check=True)
        assert "Warning:" not in result.stderr and "Error:" not in result.stderr, result.stderr
        trips=ET.parse(out/"trips.xml").getroot().findall("tripinfo")
        assert len(trips) == checks["sample_vehicles"]
        steps=ET.parse(out/"summary.xml").getroot().findall("step")
        assert steps[-1].get("running") == "0" and steps[-1].get("waiting") == "0"
        assert all(int(s.get("collisions","0")) == 0 and int(s.get("teleports","0")) == 0 for s in steps)
        vehicles=ET.parse(out/"routes.xml").getroot().findall("vehicle")
        east=[v for v in vehicles if v.get("id").startswith("east.")]
        assert len(east)==30
        assert all(v.find("route").get("edges").split()==["W_A","A_B","B_C","C_D","D_E"] for v in east)
        signals=ET.parse(root/"simulation/signals/fixed.add.xml").getroot()
        for jid in "ABCD":
            recorded=ET.parse(out/(jid+".xml")).getroot().findall("tlsState")
            assert len(recorded)==1800
            phases=next(t for t in signals.findall("tlLogic") if t.get("id")==jid).findall("phase")
            for rec in recorded:
                t=float(rec.get("time"))%120
                index=next(i for i,stop in enumerate([45,48,50,115,118,120]) if t<stop)
                assert rec.get("programID")=="fixed" and int(rec.get("phase"))==index
                assert rec.get("state")==phases[index].get("state")
        return {**checks,"arrived":len(trips),"collisions":0,"teleports":0,"tls_samples_checked":7200,"sumo_version":subprocess.check_output([binary("sumo"),"--version"],text=True).splitlines()[0]}
