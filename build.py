from pathlib import Path
from datetime import date
import csv, json, math, re
root = Path(__file__).resolve().parent
cycles = []
seen = set()
for path in sorted((root / 'data').iterdir()):
    if path.suffix.lower() not in ('.csv', '.txt'):
        continue
    match = re.fullmatch(r'cycle_(\d+)(?:_(\d{4}-\d{2}-\d{2}))?\.(?:csv|txt)', path.name, re.I)
    if not match:
        raise ValueError(f'Неверное имя файла: {path.name}')
    number = int(match[1]); day = match[2]
    if number in seen or (number != 0 and not day):
        raise ValueError(f'Повтор номера или отсутствует дата: {path.name}')
    if day: date.fromisoformat(day)
    seen.add(number); points = {}
    for row in csv.reader(path.read_text(encoding='utf-8-sig').splitlines()):
        if not row or not any(x.strip() for x in row): continue
        if len(row) != 5: raise ValueError(f'{path.name}: требуется 5 полей: {row}')
        key = row[0].strip().upper()
        if key not in {f'X{i}' for i in range(1,9)} or key in points: raise ValueError(f'{path.name}: неверная/повторная точка {key}')
        values = [float(x) for x in row[1:4]]
        if not all(math.isfinite(x) for x in values): raise ValueError(f'{path.name}: некорректные координаты')
        points[key] = values
    if len(points) != 8: raise ValueError(f'{path.name}: требуется 8 точек')
    cycles.append(dict(number=number,date=day or 'Дата не указана',p=[points[f'X{i}'] for i in range(1,9)]))
cycles.sort(key=lambda x:x['number'])
if not cycles or cycles[0]['number'] != 0: raise ValueError('Отсутствует нулевой цикл')
if any(c['number']!=i for i,c in enumerate(cycles)): raise ValueError('Пропущен номер цикла')
known_dates=[c['date'] for c in cycles if c['date']!='Дата не указана']
if known_dates!=sorted(known_dates): raise ValueError('Даты не соответствуют порядку циклов')
s = (root/'index.html').read_text(encoding='utf-8')
s,n = re.subn(r'/\* DATA_START \*/.*?/\* DATA_END \*/',lambda _: '/* DATA_START */'+json.dumps(cycles,ensure_ascii=False,allow_nan=False)+'/* DATA_END */',s,flags=re.S)
if n!=1: raise ValueError('Не найден блок данных')
(root/'_site').mkdir(exist_ok=True)
(root/'_site/index.html').write_text(s,encoding='utf-8')
print(f'Validated and built {len(cycles)} cycles')
