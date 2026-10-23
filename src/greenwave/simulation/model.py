"""Tạo nguồn mô hình SUMO đơn giản; các thông số là giả định thiết kế."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET


def binary(name):
    """Tìm SUMO trên PATH hoặc SUMO_HOME/bin (hỗ trợ Windows)."""
    found = shutil.which(name)
    if found:
        return found
    home = os.environ.get("SUMO_HOME")
    if home:
        path = Path(home) / "bin" / (name + (".exe" if os.name == "nt" else ""))
        if path.is_file():
            return str(path)
    raise FileNotFoundError(f"Không tìm thấy {name}. Cài SUMO và thêm bin vào PATH hoặc đặt SUMO_HOME.")


def write_xml(path, root):
    path.parent.mkdir(parents=True, exist_ok=True)
    schemas = {"nodes":"nodes_file.xsd", "edges":"edges_file.xsd", "connections":"connections_file.xsd", "additional":"additional_file.xsd", "routes":"routes_file.xsd", "configuration":"sumoConfiguration.xsd"}
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("xsi:noNamespaceSchemaLocation", "http://sumo.dlr.de/xsd/" + schemas[root.tag])
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def generate_sources(root):
    """Sinh topology (cấu trúc nối đường), pha cố định và xe mẫu từ config."""
    network = json.loads((root / "config/network.json").read_text(encoding="utf-8"))
    signals = json.loads((root / "config/signals.json").read_text(encoding="utf-8"))
    ids = network["junctions"]
    spacing = network["intersections_spacing_m"]
    if ids != ["A", "B", "C", "D"] or len(spacing) != 3 or any(v <= 0 for v in spacing):
        raise ValueError("Mô hình giai đoạn 2 yêu cầu A–B–C–D và ba khoảng cách dương")
    speed = network["speed_target_kmh"] / 3.6
    if speed <= 0 or network["simulation_step_s"] <= 0:
        raise ValueError("Tốc độ và bước mô phỏng phải dương")
    keys = ["main_green_s", "main_yellow_s", "all_red_after_main_s", "cross_green_s", "cross_yellow_s", "all_red_after_cross_s"]
    durations = [signals[k] for k in keys]
    if any(v <= 0 for v in durations) or sum(durations) != signals["cycle_s"]:
        raise ValueError("Các pha phải dương và tổng bằng chu kỳ")
    if signals["baseline_offsets_s"] != [0, 0, 0, 0]:
        raise ValueError("Giai đoạn 2 chỉ tạo chương trình đồng thời offset 0")
    nodes, edges, connections = ET.Element("nodes"), ET.Element("edges"), ET.Element("connections")
    x = 0
    positions = {}
    for i, node in enumerate(ids):
        if i:
            x += spacing[i-1]
        positions[node] = x
        ET.SubElement(nodes, "node", id=node, x=str(x), y="0", type="traffic_light", tlType="static")
    for node, px, py in [("W", -200, 0), ("E", x+200, 0)] + [(j+s, positions[j], y) for j in ids for s,y in [("N",150),("S",-150)]]:
        ET.SubElement(nodes,"node",id=node,x=str(px),y=str(py),type="priority")
    def edge(a,b,priority):
        ET.SubElement(edges,"edge",{"id":a+"_"+b,"from":a,"to":b,"numLanes":"1","speed":str(speed),"priority":str(priority),"spreadType":"right"})
    corridor = ["W"] + ids + ["E"]
    for a,b in zip(corridor,corridor[1:]):
        edge(a,b,2); edge(b,a,2)
    for j in ids:
        for s in ["N","S"]:
            edge(j+s,j,1); edge(j,j+s,1)
    for i,j in enumerate(ids):
        west,east = corridor[i],corridor[i+2]
        pairs=[(west+"_"+j,j+"_"+east),(east+"_"+j,j+"_"+west),(j+"N_"+j,j+"_"+j+"S"),(j+"S_"+j,j+"_"+j+"N")]
        for index,(a,b) in enumerate(pairs):
            ET.SubElement(connections,"connection",{"from":a,"to":b,"fromLane":"0","toLane":"0"})
    source=root/"simulation/network/source"
    for name,tree in [("corridor.nod.xml",nodes),("corridor.edg.xml",edges),("corridor.con.xml",connections)]:
        write_xml(source/name,tree)
    routes=ET.Element("routes")
    ET.SubElement(routes,"vType",id="car",vClass="passenger",accel="2.6",decel="4.5",sigma="0",length="5",minGap="2.5",maxSpeed=str(speed),speedFactor="1")
    def route(rid,path):
        ET.SubElement(routes,"route",id=rid,edges=" ".join(path))
    route("main_east",[a+"_"+b for a,b in zip(corridor,corridor[1:])])
    reverse=list(reversed(corridor))
    route("main_west",[a+"_"+b for a,b in zip(reverse,reverse[1:])])
    for j in ids:
        route(j+"_south",[j+"N_"+j,j+"_"+j+"S"])
        route(j+"_north",[j+"S_"+j,j+"_"+j+"N"])
    for fid,rid,n,color in [("east","main_east",30,"1,0.7,0"),("west","main_west",15,"0,0.6,1")]+[(j+s,j+"_"+d,5,"0.5,0.8,0.5") for j in ids for s,d in [("S","south"),("N","north")]]:
        ET.SubElement(routes,"flow",id=fid,type="car",route=rid,begin="0",end="360",number=str(n),departLane="0",departSpeed="max",color=color)
    write_xml(root/"simulation/routes/source/sample.rou.xml",routes)
    cfg=ET.Element("configuration")
    inp=ET.SubElement(cfg,"input")
    for key,value in [("net-file","../network/generated/corridor.net.xml"),("route-files","../routes/source/sample.rou.xml"),("additional-files","../signals/fixed.add.xml")]:
        ET.SubElement(inp,key,value=value)
    timing=ET.SubElement(cfg,"time")
    for k,v in [("begin",0),("end",1800),("step-length",network["simulation_step_s"])]:
        ET.SubElement(timing,k,value=str(v))
    processing=ET.SubElement(cfg,"processing")
    ET.SubElement(processing,"time-to-teleport",value="-1")
    random=ET.SubElement(cfg,"random_number")
    ET.SubElement(random,"seed",value="11")
    write_xml(root/"simulation/scenarios/sample.sumocfg",cfg)


def build(root):
    """Dùng NETCONVERT sinh net.xml; không tự viết mạng đầu ra bằng tay."""
    generate_sources(root)
    target=root/"simulation/network/generated/corridor.net.xml"
    target.parent.mkdir(parents=True,exist_ok=True)
    src=root/"simulation/network/source"
    subprocess.run([binary("netconvert"),"--node-files",str(src/"corridor.nod.xml"),"--edge-files",str(src/"corridor.edg.xml"),"--connection-files",str(src/"corridor.con.xml"),"--no-turnarounds","true","--output-file",str(target)],check=True)
    # NETCONVERT tự gán linkIndex: đọc ánh xạ thực, không đoán thứ tự tín hiệu.
    net = ET.parse(target).getroot()
    signals = json.loads((root / "config/signals.json").read_text(encoding="utf-8"))
    durations = [signals[k] for k in ["main_green_s", "main_yellow_s", "all_red_after_main_s", "cross_green_s", "cross_yellow_s", "all_red_after_cross_s"]]
    additional = ET.Element("additional")
    for junction in ["A", "B", "C", "D"]:
        links = [c for c in net.findall("connection") if c.get("tl") == junction]
        if sorted(int(c.get("linkIndex")) for c in links) != [0, 1, 2, 3]:
            raise ValueError("Mỗi nút cần đúng bốn kết nối có đèn độc lập")
        logic = ET.SubElement(additional, "tlLogic", id=junction, type="static", programID="fixed", offset="0")
        for phase, duration in enumerate(durations):
            state = ["r"] * 4
            for link in links:
                # Các nhánh N/S có tiền tố AN_, AS_, BN_...; đường trục không có.
                incoming = link.get("from").split("_")[0]
                main = incoming not in [junction + "N", junction + "S"]
                color = (["G", "y", "r", "r", "r", "r"] if main else ["r", "r", "r", "G", "y", "r"])[phase]
                state[int(link.get("linkIndex"))] = color
            ET.SubElement(logic, "phase", duration=str(duration), state="".join(state))
    write_xml(root / "simulation/signals/fixed.add.xml", additional)
    return target
