"""Từ thư mục ZIP đã giải nén riêng, thêm file GĐ3; từ chối ghi đè file khác nội dung."""
import argparse
import json
from pathlib import Path
import shutil


def install(source, target):
    source, target = Path(source).resolve(), Path(target).resolve()
    prerequisites = ['config/network.json','config/signals.json',
                     'simulation/network/generated/corridor.net.xml',
                     'simulation/scenarios/sample.sumocfg',
                     'simulation/routes/source/sample.rou.xml',
                     'src/greenwave/simulation/model.py','src/greenwave/simulation/validation.py']
    missing = [name for name in prerequisites if not (target/name).is_file()]
    if missing:
        raise ValueError('Project đích thiếu Giai đoạn 2: '+', '.join(missing))
    manifest=json.loads((source/'docs/stage3-file-manifest.json').read_text(encoding='utf-8'))
    copies=[]
    for name in manifest['files']:
        local, destination=source/name, target/name
        if not local.resolve().is_relative_to(source) or not destination.resolve().is_relative_to(target):
            raise ValueError('Đường dẫn không an toàn: '+name)
        if not local.is_file():raise ValueError('Gói thiếu tệp: '+name)
        if destination.exists():
            if not destination.is_file() or destination.read_bytes()!=local.read_bytes():
                raise ValueError('Dừng trước khi sao chép: tệp đích đã có nội dung khác: '+name)
        else:copies.append((local,destination))
    # Chỉ bắt đầu ghi sau khi kiểm tra toàn bộ xung đột.
    for local,destination in copies:
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(local,destination)
    return len(copies)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',required=True,help='Thư mục gốc project đã có Giai đoạn 2')
    args=parser.parse_args()
    try:
        print(f'Đã thêm {install(Path(__file__).resolve().parents[1], args.project)} tệp; giữ nguyên file khác.')
    except ValueError as error:
        raise SystemExit(str(error))
