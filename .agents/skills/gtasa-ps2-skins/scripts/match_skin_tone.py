"""Apply an explicit UV-mask color transfer; keep the reference head untouched.

Profiles are recipe-specific. This is a local texture operation, with no image
generation service. Keep source shading/tattoo detail instead of painting flat skin.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image


def load_profile(head_model, body_model):
    name = f'{head_model}_{body_model}.json'
    base = Path(__file__).resolve().parent.parent
    for folder in [base/'assets/tone_profiles', base/'.agents/skills/gtasa-ps2-skins/assets/tone_profiles']:
        path = folder/name
        if path.is_file():
            return json.loads(path.read_text(encoding='utf-8'))
    raise ValueError(f'No inspected skin UV profile for {head_model}/{body_model}; create a mask and samples for that pair first')


def samples(image, boxes):
    return np.concatenate([image[y0:y1, x0:x1].reshape(-1, 3) for x0, y0, x1, y1 in boxes])


def palette_for_skin_edit(baseline_rgba, recolored_atlas, mask):
    """Reserve exact protected colors, then spend remaining slots on new skin tones."""
    baseline = np.asarray(baseline_rgba)[:, :, :3]
    protected = np.unique(baseline[~mask], axis=0)
    free = 256-len(protected)
    if free < 1:
        raise ValueError('No palette slots remain for skin tones while preserving protected pixels')
    compressed = np.clip(np.rint(12+np.asarray(recolored_atlas, dtype=float)/255*223), 12, 235).astype(np.uint8)
    skin_strip = Image.fromarray(compressed[mask].reshape(1, -1, 3))
    new_skin = skin_strip.quantize(colors=free, method=Image.Quantize.MEDIANCUT)
    new_colors = np.array(new_skin.getpalette()[:free*3], dtype=np.uint8).reshape(-1, 3)
    palette = Image.new('P', (1, 1))
    palette.putpalette(np.vstack([protected, new_colors]).ravel().tolist())
    return palette


def match_body_skin(body, head, profile):
    if list(body.shape[1::-1]) != profile['body_dimensions'] or list(head.shape[1::-1]) != profile['head_dimensions']:
        raise ValueError('Profile dimensions do not match the vanilla atlases')
    body_float = body.astype(float)
    source = np.median(samples(body, profile['body_samples']), axis=0)
    target = np.median(samples(head, profile['head_samples']), axis=0)
    gain = target/np.maximum(source, 1)
    mask = np.zeros(body.shape[:2], dtype=bool)
    for x0, y0, x1, y1 in profile['skin_regions']:
        mask[y0:y1, x0:x1] = True
    chroma = ((body_float[:, :, 0]-body_float[:, :, 1] > profile['minimum_red_green']) &
              (body_float[:, :, 1]-body_float[:, :, 2] > profile['minimum_green_blue']))
    for x0, y0, x1, y1 in profile['skin_chroma_regions']:
        mask[y0:y1, x0:x1] |= chroma[y0:y1, x0:x1]
    # Deep tattoo ink remains unchanged; full correction applies to midtone skin.
    brightness = body_float @ np.array([.2126, .7152, .0722])
    alpha = np.clip((brightness-35)/45, 0, 1)*mask
    corrected = body_float*(1 + alpha[:, :, None]*(gain-1))
    result = np.clip(np.rint(corrected), 0, 255).astype(np.uint8)
    matched = np.median(samples(result, profile['body_samples']), axis=0)
    if not np.array_equal(result[~mask], body[~mask]):
        raise AssertionError('Color transfer changed pixels outside the skin mask')
    return result, mask, {
        'profile': profile['name'], 'reference': 'head', 'changed_material': 'body_skin',
        'body_base_rgb_before': source.tolist(), 'head_reference_rgb': target.tolist(),
        'body_base_rgb_after': matched.tolist(), 'channel_gains': gain.tolist(),
        'masked_pixels': int(mask.sum()), 'outside_mask_pixels_changed': 0,
        'mean_reference_error_before': float(np.abs(source-target).mean()),
        'mean_reference_error_after': float(np.abs(matched-target).mean()),
    }
