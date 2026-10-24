"""Tích hợp từ ZIP đã giải nén riêng; kiểm tra toàn bộ trước khi ghi và ghép README."""
import argparse,json,os,shutil
from pathlib import Path


def install(source,target):
    source,target=Path(source).resolve(),Path(target).resolve()
    required=['STAGE4.md','src/greenwave/controllers/fixed_plans.py',
              'src/greenwave/simulation/plan_validation.py','simulation/scenarios/sample.sumocfg',
              'simulation/network/generated/corridor.net.xml','simulation/routes/source/sample.rou.xml']
    missing=[n for n in required if not (target/n).is_file()]
    if missing:raise ValueError('Thiếu nền GĐ2–3: '+', '.join(missing))
    manifest=json.loads((source/'docs/stage5-file-manifest.json').read_text(encoding='utf-8'))
    writes=[]
    for entry in manifest['files']:
        name=entry['path'];src,dst=source/name,target/name
        if not src.resolve().is_relative_to(source) or not dst.resolve().is_relative_to(target):raise ValueError('Đường dẫn không an toàn')
        if not src.is_file():raise ValueError('Gói thiếu '+name)
        if name=='README.md':
            original=dst.read_text(encoding='utf-8') if dst.exists() else ''
            section=(source/'docs/stage5-readme-section.md').read_text(encoding='utf-8')
            if '<!-- STAGE5:BEGIN -->' in original:
                begin=original.index('<!-- STAGE5:BEGIN -->');end=original.find('<!-- STAGE5:END -->',begin)
                if end<0 or original[begin:end+len('<!-- STAGE5:END -->')].strip()!=section.strip():
                    raise ValueError('README có mục GĐ5 khác nội dung; giữ nguyên và dừng')
                continue
            writes.append((dst,(original.rstrip()+'\n\n'+section).encode('utf-8')));continue
        if dst.exists():
            if not dst.is_file() or dst.read_bytes()!=src.read_bytes():raise ValueError('Xung đột, chưa sao chép gì: '+name)
        else:writes.append((dst,src.read_bytes()))
    for dst,data in writes:
        dst.parent.mkdir(parents=True,exist_ok=True)
        temp=dst.with_name(dst.name+'.stage5.tmp');temp.write_bytes(data);os.replace(temp,dst)
    return len(writes)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',required=True);a=p.parse_args()
    try:print(f'Đã tích hợp {install(Path(__file__).resolve().parents[1],a.project)} tệp; README được ghép thêm, không mất nội dung cũ.')
    except ValueError as e:raise SystemExit(str(e))
