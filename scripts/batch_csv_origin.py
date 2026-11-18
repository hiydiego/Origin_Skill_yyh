"""Origin 2021+ embedded Python: select a folder and plot all CSV files.
First column = numeric X; remaining numeric columns = Y. Includes subfolders.
No smoothing, interpolation, sorting or row sampling. Existing project is retained.
"""
from pathlib import Path
from datetime import datetime
import csv
import math
import re
import traceback
import originpro as op

# Set a path here to bypass the folder dialog; blank means choose on each run.
DATA_FOLDER = ""
RECURSIVE = True
COLORS = ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#E69F00', '#56B4E9', '#000000']

def choose_folder():
    if DATA_FOLDER:
        return Path(DATA_FOLDER).expanduser().resolve()
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    try:
        root.attributes('-topmost', True)
        chosen = filedialog.askdirectory(title='Select CSV data folder', initialdir=str(Path.cwd()), parent=root)
    finally:
        root.destroy()
    return Path(chosen) if chosen else None

def number(value):
    try:
        v = float(value.strip())
        return v if math.isfinite(v) else float('nan')
    except (ValueError, TypeError):
        return float('nan')

def read_csv(path):
    # Decode strictly: never replace undecodable characters silently.
    for encoding in ('utf-8-sig', 'gb18030', 'utf-16'):
        try:
            with path.open(encoding=encoding, newline='') as f:
                sample = f.read(8192)
                f.seek(0)
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=',;\t')
                except csv.Error:
                    dialect = csv.excel
                reader = csv.reader(f, dialect)
                first = next((r for r in reader if any(v.strip() for v in r)), None)
                if first is None or len(first) < 2:
                    raise ValueError('Need at least two columns')
                has_header = not math.isfinite(number(first[0]))
                headers = first if has_header else ['X'] + ['Y{}'.format(i) for i in range(1, len(first))]
                columns = [[] for _ in headers]
                def append(row):
                    if not any(v.strip() for v in row):
                        return
                    if len(row) > len(headers):
                        raise ValueError('Row has more fields than header')
                    for j in range(len(headers)):
                        columns[j].append(number(row[j]) if j < len(row) else float('nan'))
                if not has_header:
                    append(first)
                for row in reader:
                    append(row)
            return headers, columns
        except UnicodeError:
            continue
    raise ValueError('Cannot decode CSV as UTF-8, GB18030 or UTF-16')

def plot_one(path, output, index):
    headers, columns = read_csv(path)
    x = columns[0]
    usable = [j for j in range(1, len(columns)) if any(math.isfinite(a) and math.isfinite(b) for a,b in zip(x, columns[j]))]
    if not usable:
        raise ValueError('No valid numeric X/Y pairs; first column must be numeric X')
    wks = op.new_sheet('w', lname=path.stem)
    for j, values in enumerate(columns):
        wks.from_list(j, values, lname=headers[j], axis='X' if j == 0 else 'Y')
    graph = op.new_graph(lname=path.stem, template='line')
    layer = graph[0]
    for j in usable:
        plot = layer.add_plot(wks, coly=j, colx=0, type='l')
        plot.color = COLORS[(j-1) % len(COLORS)]
        plot.set_cmd('-w 2000')  # Origin uses 500 units per point: 4 pt = 2000
    layer.rescale()
    valid_x = [a for k,a in enumerate(x) if math.isfinite(a) and any(math.isfinite(columns[j][k]) for j in usable)]
    if min(valid_x) < max(valid_x):
        layer.xlim = (min(valid_x), max(valid_x))
    layer.axis('x').title = headers[0]
    yheaders = [headers[j] for j in usable]
    layer.axis('y').title = yheaders[0] if len(yheaders) == 1 else 'Value'
    layer.lt_exec('legend -r; layer.x.showAxes=3; layer.y.showAxes=3; layer.x.showLabels=1; layer.y.showLabels=1;')
    for axis in ('x', 'x2', 'y', 'y2'):
        layer.lt_exec('layer.{0}.thickness=5; layer.{0}.ticks=5; layer.{0}.tickthickness=1.6; layer.{0}.mtickthickness=1;'.format(axis))
    for axis in ('x', 'y'):
        layer.lt_exec('layer.{0}.minorTicks=1; layer.{0}.showGrids=3; layer.{0}.grid.majorWidth=0.8; layer.{0}.grid.minorWidth=0.4; layer.{0}.grid.majorColor=color(190,190,190); layer.{0}.grid.minorColor=color(225,225,225); layer.{0}.grid.majorType=2; layer.{0}.grid.minorType=2;'.format(axis))
    # Opposite borders remain visible, without ticks or numeric labels.
    layer.lt_exec('layer.x2.ticks=0; layer.y2.ticks=0; layer.x2.showlabel=0; layer.y2.showlabel=0;')
    for axis in ('x', 'x2', 'y', 'y2'):
        layer.lt_exec('layer.{0}.label.font=font(Times New Roman); layer.{0}.label.pt=23; layer.{0}.label.bold=1; layer.{0}.label.color=color(black);'.format(axis))
    for obj in ('xb', 'xt', 'yl', 'yr', 'legend'):
        layer.lt_exec('{0}.font=font(Times New Roman); {0}.fsize=23;'.format(obj))
    for obj in ('xb', 'xt', 'yl', 'yr'):
        layer.lt_exec(r'string boldText$={0}.text$; {0}.text$="\b(%(boldText$))"; {0}.color=color(black);'.format(obj))
    # Build each legend row explicitly: formatting must restart on every line.
    legend_rows = [r'\l(%d) \b(%s)' % (n, headers[j]) for n, j in enumerate(usable, 1)]
    legend_text = '\n'.join(legend_rows)
    layer.lt_exec('legend.text$="' + legend_text.replace('"', '\\"') + '"; legend.color=color(black);')
    layer.lt_exec('legend.fsize=19; legend.background=1; legend.x=layer.x.to-legend.dx/2-0.03*(layer.x.to-layer.x.from); legend.y=layer.y.to-legend.dy/2-0.03*(layer.y.to-layer.y.from);')
    layer.lt_exec('pfit2l margin:=tight;')
    safe = re.sub(r'[<>:"/\\|?*]', '_', path.stem)[:100]
    graph.save_fig(str(output / ('{:04d}_{}.png'.format(index, safe))), width=2400)
    counts = [sum(math.isfinite(a) and math.isfinite(b) for a,b in zip(x, columns[j])) for j in usable]
    return 'OK: {} | rows={} | plotted columns={} | valid pairs={}'.format(path, len(x), usable, counts)

def main():
    folder = choose_folder()
    if folder is None:
        print('Cancelled. No files changed.')
        return
    if not folder.is_dir():
        raise ValueError('Data folder does not exist: {}'.format(folder))
    iterator = folder.rglob('*') if RECURSIVE else folder.iterdir()
    files = sorted(p for p in iterator if p.is_file() and p.suffix.lower() == '.csv' and not any(part.startswith('Origin_Plots_') for part in p.relative_to(folder).parts[:-1]))
    if not files:
        print('No CSV files found: {}'.format(folder))
        return
    output = folder / ('Origin_Plots_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    output.mkdir()
    report = ['First column is numeric X, remaining numeric columns are Y. Missing/non-numeric cells become missing, no interpolation. All source files unchanged.']
    success = 0
    for index, path in enumerate(files, 1):
        try:
            message = plot_one(path, output, index)
            success += 1
        except Exception:
            message = 'FAILED: {}\n{}'.format(path, traceback.format_exc())
        report.append(message)
        print(message)
        (output / 'run_log.txt').write_text('\n\n'.join(report), encoding='utf-8')
    if success:
        op.save(str(output / 'CSV_plots.opju'))
    print('Finished: {} / {} CSV files plotted. Output: {}'.format(success, len(files), output))

if __name__ == '__main__':
    main()







