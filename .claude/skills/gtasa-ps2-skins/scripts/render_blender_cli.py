"""Render real DFF/TXD geometry with local Blender CLI; no image generation API."""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from vanilla_rw_kitbash import parse_ped_dff, read_txd_textures
from render_ps2_vibesheet import posed_vertices


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dff', required=True)
    p.add_argument('--txd', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--blender', default='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe')
    args = p.parse_args()
    output = Path(args.output).resolve()
    shots = output.parent / 'blender_screenshots'
    shots.mkdir(parents=True, exist_ok=True)
    mesh = parse_ped_dff(Path(args.dff).read_bytes())
    texture = dict(read_txd_textures(Path(args.txd).read_bytes()))[mesh['texture_name']]
    payload = shots / 'actual_dff_txd.npz'
    np.savez(payload, vertices=mesh['vertices'], uvs=mesh['uvs'],
             triangles=mesh['triangles'][:, [1, 0, 3]], texture=texture, posed=posed_vertices(mesh))
    worker = Path(__file__).with_name('render_blender_worker.py').resolve()
    command = [args.blender, '--background', '--factory-startup', '--threads', '4', '--python-exit-code', '1',
               '--python', str(worker), '--', str(payload), str(shots)]
    with (shots / 'blender.log').open('w', encoding='utf-8') as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        try:
            process.wait(timeout=180)
            if process.returncode:
                raise RuntimeError(f'Blender failed; see {shots / "blender.log"}')
        finally:
            if process.poll() is None:
                subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True, timeout=10)
                process.wait(timeout=10)
    if 'BLENDER_SCREENSHOTS_COMPLETE' not in (shots/'blender.log').read_text(encoding='utf-8'):
        raise RuntimeError('Blender did not confirm all screenshots and the scene were saved')
    sheet = Image.new('RGB', (2000, 650), (22, 25, 31))
    draw = ImageDraw.Draw(sheet)
    font_path = 'C:/Windows/Fonts/consola.ttf'
    font = ImageFont.truetype(font_path, 21)
    draw.text((22, 14), 'SINDACO + LSV2 | BLENDER CLI | ACTUAL DFF / TXD', font=font, fill=(235, 225, 205))
    for i, name in enumerate(['Front', 'Side', 'Back', 'ThreeQuarter', 'PoseTest']):
        image = Image.open(shots / (name+'.png')).convert('RGB')
        image.thumbnail((400, 550))
        sheet.paste(image, (i*400, 70))
        draw.text((i*400+18, 45), name, font=font, fill=(220, 220, 220))
    draw.text((22, 621), 'Local Blender renders. PoseTest: exported weights + diagnostic bone rotations.', font=font, fill=(180, 190, 200))
    sheet.save(output)
    print(json.dumps({'renderer': 'Blender CLI', 'output': str(output), 'screenshots': str(shots)}, indent=2))


if __name__ == '__main__':
    main()
