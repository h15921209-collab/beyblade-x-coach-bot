# -*- coding: utf-8 -*-
"""
BeybladeHub Automated Data Sync Pipeline
Scrapes https://beybladehub.app/parts (Blades, Ratchets, Bits),
detects new components, downloads images, enriches tactical specs via Gemini AI,
and updates data/parts_db.json.
"""

import os
import sys
import json
import re
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('beybladehub_sync')

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'data' / 'parts_db.json'
STATIC_IMG_DIR = BASE_DIR / 'web' / 'static' / 'images'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}

def clean_text(text: str) -> str:
    if not text:
        return ''
    return re.sub(r'\s+', ' ', text).strip()

def normalize_key(text: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

def download_image(url: str, dest_path: Path) -> bool:
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code == 200:
            with open(dest_path, 'wb') as f:
                f.write(resp.content)
            logger.info(f'Downloaded image to {dest_path.name} ({len(resp.content)} bytes)')
            return True
        else:
            logger.warning(f'Failed to download {url}: HTTP {resp.status_code}')
            return False
    except Exception as e:
        logger.warning(f'Error downloading {url}: {e}')
        return False

def call_gemini_enrichment(prompt: str, api_key: str) -> Optional[Dict[str, Any]]:
    if not api_key:
        return None
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}'
    headers = {'Content-Type': 'application/json'}
    payload = {
        'contents': [{'parts': [{'text': prompt}]}],
        'generationConfig': {
            'temperature': 0.2,
            'responseMimeType': 'application/json'
        }
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=25)
        if resp.status_code == 200:
            data = resp.json()
            raw_text = data['candidates'][0]['content']['parts'][0]['text']
            return json.loads(raw_text)
    except Exception as e:
        logger.warning(f'Gemini enrichment error: {e}')
    return None

def scrape_blades() -> List[Dict[str, Any]]:
    url = 'https://beybladehub.app/parts/blades'
    logger.info(f'Fetching blades from {url}...')
    resp = requests.get(url, headers=HEADERS, timeout=25)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    blades = []
    cards = soup.find_all('div', id=lambda x: x and x.startswith('blade-'))
    logger.info(f'Discovered {len(cards)} blade cards on BeybladeHub.')

    for card in cards:
        try:
            img = card.find('img')
            img_url = img.get('src') if img else ''
            
            title_div = card.find('div', class_=lambda c: c and 'text-sm' in c and 'font-bold' in c)
            name_zh = clean_text(title_div.get_text()) if title_div else ''
            
            type_val = 'Attack'
            code_val = ''
            weight_val = 35.0

            badges = card.find_all('span', class_=lambda c: c and 'text-[9px]' in c)
            for badge in badges:
                b_txt = clean_text(badge.get_text())
                if b_txt in ['攻擊', '持久', '防守', '防禦', '均衡']:
                    if b_txt == '攻擊': type_val = 'Attack'
                    elif b_txt == '持久': type_val = 'Stamina'
                    elif b_txt in ['防守', '防禦']: type_val = 'Defense'
                    elif b_txt == '均衡': type_val = 'Balance'
                elif re.match(r'^[B|U|C]X-[0-9A-Za-z]+', b_txt):
                    code_val = b_txt

            w_span = card.find('span', class_=lambda c: c and 'font-mono' in c)
            if w_span:
                m = re.search(r'([0-9]+\.?[0-9]*)', w_span.get_text())
                if m:
                    weight_val = float(m.group(1))

            # Filter out CX sub-blades / chips (< 22.0g)
            if weight_val < 22.0 and not code_val.startswith('BX') and not code_val.startswith('UX'):
                continue

            en_span = card.find('span', attrs={'translate': 'no'})
            name_en = clean_text(en_span.get_text()) if en_span else name_zh
            name_en = re.sub(r'([a-z])([A-Z])', r'\1 \2', name_en)

            desc_texts = []
            for p in card.find_all(['p', 'div']):
                txt = clean_text(p.get_text())
                if len(txt) > 20 and '重量' not in txt[:10]:
                    desc_texts.append(txt)
            description = desc_texts[0] if desc_texts else f'{name_zh}（{name_en}）戰鬥陀螺 X 世代刃部。'

            series = 'BX'
            if code_val.startswith('UX'): series = 'UX'
            elif code_val.startswith('CX'): series = 'CX'

            bid = normalize_key(name_en)
            if not bid:
                bid = normalize_key(name_zh)

            blades.append({
                'id': bid,
                'name': name_en,
                'name_zh': name_zh,
                'code': code_val,
                'series': series,
                'type': type_val,
                'weight_g': weight_val,
                'description': description,
                'image_url': img_url
            })
        except Exception as err:
            logger.debug(f'Error parsing blade card: {err}')

    return blades

def scrape_ratchets() -> List[Dict[str, Any]]:
    url = 'https://beybladehub.app/parts/ratchets'
    logger.info(f'Fetching ratchets from {url}...')
    resp = requests.get(url, headers=HEADERS, timeout=25)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    ratchets = []
    cards = soup.find_all('div', id=lambda x: x and x.startswith('ratchet-'))
    logger.info(f'Discovered {len(cards)} ratchet cards on BeybladeHub.')

    for card in cards:
        try:
            img = card.find('img')
            img_url = img.get('src') if img else ''
            
            title_div = card.find('div', class_=lambda c: c and 'text-sm' in c and 'font-bold' in c)
            r_name = clean_text(title_div.get_text()) if title_div else ''
            r_name = re.sub(r'\s+', '', r_name)

            m = re.search(r'([0-9]+)-([0-9]+)', r_name)
            if not m:
                continue
            blades_count = int(m.group(1))
            height_val = float(m.group(2)) / 10.0

            desc = ''
            for div in card.find_all('div'):
                t = clean_text(div.get_text())
                if len(t) > 15 and ('刃' in t or '高度' in t or '防守' in t or '攻擊' in t):
                    desc = t
                    break
            if not desc:
                desc = f'{r_name} 戰鬥陀螺 X 官方規格固鎖墊片。'

            ratchets.append({
                'id': r_name,
                'name': r_name,
                'height_mm': height_val,
                'blades_count': blades_count,
                'weight_g': round(6.0 + (blades_count * 0.1), 1),
                'description': desc,
                'image_url': img_url
            })
        except Exception as err:
            logger.debug(f'Error parsing ratchet card: {err}')

    return ratchets

def scrape_bits() -> List[Dict[str, Any]]:
    url = 'https://beybladehub.app/parts/bits'
    logger.info(f'Fetching bits from {url}...')
    resp = requests.get(url, headers=HEADERS, timeout=25)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    bits = []
    cards = soup.find_all('div', id=lambda x: x and x.startswith('bit-'))
    logger.info(f'Discovered {len(cards)} bit cards on BeybladeHub.')

    for card in cards:
        try:
            img = card.find('img')
            img_url = img.get('src') if img else ''

            title_div = card.find('div', class_=lambda c: c and 'text-sm' in c and 'font-bold' in c)
            bit_id = clean_text(title_div.get_text()) if title_div else ''
            bit_id = re.sub(r'\s+', '', bit_id)
            if not bit_id or len(bit_id) > 4:
                continue

            en_span = card.find('span', attrs={'translate': 'no'})
            name_en = clean_text(en_span.get_text()) if en_span else bit_id
            
            type_val = 'Balance'
            badges = card.find_all('span', class_=lambda c: c and 'text-[9px]' in c)
            for badge in badges:
                b_txt = clean_text(badge.get_text())
                if b_txt == '攻擊': type_val = 'Attack'
                elif b_txt == '持久': type_val = 'Stamina'
                elif b_txt in ['防守', '防禦']: type_val = 'Defense'
                elif b_txt == '均衡': type_val = 'Balance'

            desc = ''
            for div in card.find_all('div'):
                t = clean_text(div.get_text())
                if len(t) > 15 and ('軸' in t or 'Dash' in t or 'Gear' in t or '性能' in t):
                    desc = t
                    break
            if not desc:
                desc = f'{bit_id}（{name_en}）戰鬥陀螺 X 官方軸心。'

            bits.append({
                'id': bit_id,
                'name': f'{name_en} ({bit_id}軸)',
                'name_zh': f'{name_en}軸',
                'type': type_val,
                'weight_g': 2.2,
                'description': desc,
                'image_url': img_url
            })
        except Exception as err:
            logger.debug(f'Error parsing bit card: {err}')

    return bits

def sync_database(dry_run: bool = False, api_key: Optional[str] = None) -> Dict[str, Any]:
    if not DB_PATH.exists():
        raise FileNotFoundError(f'Parts database not found at {DB_PATH}')

    with open(DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)

    existing_blades: List[Dict[str, Any]] = db.get('blades', [])
    existing_ratchets: List[Dict[str, Any]] = db.get('ratchets', [])
    existing_bits: List[Dict[str, Any]] = db.get('bits', [])

    existing_blade_keys = set()
    for b in existing_blades:
        existing_blade_keys.add(normalize_key(b['id']))
        existing_blade_keys.add(normalize_key(b['name']))
        existing_blade_keys.add(normalize_key(b.get('name_zh', '')))
        if b.get('code'):
            existing_blade_keys.add(normalize_key(b['code']))
        for alias in b.get('aliases', []):
            existing_blade_keys.add(normalize_key(alias))

    existing_ratchet_names = {normalize_key(r['name']) for r in existing_ratchets}
    existing_bit_ids = {normalize_key(bit['id']) for bit in existing_bits}

    logger.info(f'Currently in DB: {len(existing_blades)} blades, {len(existing_ratchets)} ratchets, {len(existing_bits)} bits.')

    hub_blades = scrape_blades()
    hub_ratchets = scrape_ratchets()
    hub_bits = scrape_bits()

    new_blades = []
    new_ratchets = []
    new_bits = []

    for hb in hub_blades:
        k_code = normalize_key(hb['code']) if hb['code'] else None
        k_name = normalize_key(hb['name'])
        k_zh = normalize_key(hb['name_zh'])
        if (k_code and k_code in existing_blade_keys) or k_name in existing_blade_keys or k_zh in existing_blade_keys:
            continue
        new_blades.append(hb)
        if k_code: existing_blade_keys.add(k_code)
        existing_blade_keys.add(k_name)
        existing_blade_keys.add(k_zh)

    for hr in hub_ratchets:
        k_r = normalize_key(hr['name'])
        if k_r in existing_ratchet_names:
            continue
        new_ratchets.append(hr)
        existing_ratchet_names.add(k_r)

    for hbit in hub_bits:
        k_bit = normalize_key(hbit['id'])
        if k_bit in existing_bit_ids:
            continue
        new_bits.append(hbit)
        existing_bit_ids.add(k_bit)

    logger.info(f'Diff found: {len(new_blades)} new blades, {len(new_ratchets)} new ratchets, {len(new_bits)} new bits.')

    if not new_blades and not new_ratchets and not new_bits:
        logger.info('Database is already 100% up-to-date with BeybladeHub. No changes made.')
        return {'status': 'up_to_date', 'added': {'blades': [], 'ratchets': [], 'bits': []}}

    if dry_run:
        logger.info('[DRY RUN] Would add:')
        for b in new_blades: logger.info(f'  Blade: {b.get("code")} {b["name_zh"]} ({b["name"]})')
        for r in new_ratchets: logger.info(f'  Ratchet: {r["name"]}')
        for bit in new_bits: logger.info(f'  Bit: {bit["id"]} ({bit["name"]})')
        return {
            'status': 'dry_run',
            'added': {
                'blades': [f"{b.get('code')} {b['name_zh']}" for b in new_blades],
                'ratchets': [r['name'] for r in new_ratchets],
                'bits': [bit['id'] for bit in new_bits]
            }
        }

    # Process and enrich new blades
    for b in new_blades:
        safe_id = re.sub(r'[^a-zA-Z0-9_]', '_', b['id'].lower())
        local_img_rel = f'/static/images/blade_{safe_id}.webp'
        local_img_path = STATIC_IMG_DIR / f'blade_{safe_id}.webp'
        
        if b.get('image_url'):
            download_image(b['image_url'], local_img_path)

        ai_data = None
        if api_key:
            prompt = (
                f'你是一位《戰鬥陀螺 X》職業戰術分析師。請針對新發布的零件提供物理重心與戰術分析：\n'
                f'名稱：{b["name"]}\n中文：{b["name_zh"]}\n代碼：{b["code"]}\n類型：{b["type"]}\n重量：{b["weight_g"]}g\n'
                f'說明：{b["description"]}\n\n'
                f'請回傳 JSON：{{"cg": "重心 (英文+繁中)", "burst_resistance": "High/Medium/Low", "x_dash_capability": "性能評定", "tier": "S/A+/A/B+", "meta_analysis": "戰術分析繁體中文", "aliases": ["別名"]}}'
            )
            ai_data = call_gemini_enrichment(prompt, api_key)

        cg_val = ai_data.get('cg', 'Balanced Center (標準平衡重心)') if ai_data else 'Balanced Center (標準平衡重心)'
        burst_val = ai_data.get('burst_resistance', 'High') if ai_data else 'High'
        xdash_val = ai_data.get('x_dash_capability', 'High') if ai_data else 'High'
        tier_val = ai_data.get('tier', 'A') if ai_data else 'A'
        meta_val = ai_data.get('meta_analysis', f'具備 {b["weight_g"]}g 良好重量分佈，在 {b["type"]} 流派中具備改裝潛力。') if ai_data else f'具備 {b["weight_g"]}g 良好重量分佈，在 {b["type"]} 流派中具備改裝潛力。'
        aliases_val = ai_data.get('aliases', [b['name_zh'], b['name']]) if ai_data else [b['name_zh'], b['name']]
        if b['name_zh'] not in aliases_val: aliases_val.insert(0, b['name_zh'])
        if b['name'] not in aliases_val: aliases_val.append(b['name'])

        enriched_blade = {
            'id': safe_id,
            'name': b['name'],
            'name_zh': b['name_zh'],
            'code': b['code'],
            'series': b['series'],
            'type': b['type'],
            'weight_g': b['weight_g'],
            'cg': cg_val,
            'burst_resistance': burst_val,
            'x_dash_capability': xdash_val,
            'tier': tier_val,
            'description': b['description'],
            'meta_analysis': meta_val,
            'image_url': b['image_url'],
            'card_image_url': b['image_url'],
            'image_local': local_img_rel,
            'aliases': aliases_val
        }
        existing_blades.append(enriched_blade)

    # Process new ratchets
    for r in new_ratchets:
        r_name = r['name']
        local_img_rel = f'/static/images/ratchet_{r_name}.webp'
        local_img_path = STATIC_IMG_DIR / f'ratchet_{r_name}.webp'
        if r.get('image_url'):
            download_image(r['image_url'], local_img_path)

        enriched_ratchet = {
            'id': r_name,
            'name': r_name,
            'height_mm': r['height_mm'],
            'blades_count': r['blades_count'],
            'weight_g': r['weight_g'],
            'cg': f'Standard {r["blades_count"]}-Blade Height {r["height_mm"]}mm',
            'burst_resistance': 'High' if r['blades_count'] >= 5 else 'Medium-High',
            'tier': 'A',
            'description': r['description'],
            'tactical_effect': f'提供 {r["height_mm"]}mm 重心高度與 {r["blades_count"]} 刃緩衝防爆。',
            'image_url': r['image_url'],
            'image_local': local_img_rel
        }
        existing_ratchets.append(enriched_ratchet)

    # Process new bits
    for bit in new_bits:
        bit_id = bit['id']
        local_img_rel = f'/static/images/bit_{bit_id.lower()}.webp'
        local_img_path = STATIC_IMG_DIR / f'bit_{bit_id.lower()}.webp'
        if bit.get('image_url'):
            download_image(bit['image_url'], local_img_path)

        enriched_bit = {
            'id': bit_id,
            'name': bit['name'],
            'name_zh': bit['name_zh'],
            'type': bit['type'],
            'weight_g': bit['weight_g'],
            'burst_resistance': 'High' if bit['type'] == 'Attack' else 'Medium',
            'gear_teeth': 16,
            'x_dash_capability': 'High' if bit['type'] == 'Attack' else 'Controlled',
            'tier': 'A',
            'description': bit['description'],
            'tactical_effect': f'專屬 {bit_id} 特性軸心，優化 {bit["type"]} 軌道接觸與迴旋平衡。',
            'image_url': bit['image_url'],
            'image_local': local_img_rel
        }
        existing_bits.append(enriched_bit)

    db['blades'] = existing_blades
    db['ratchets'] = existing_ratchets
    db['bits'] = existing_bits

    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    logger.info(f'Successfully updated {DB_PATH}. Total blades: {len(existing_blades)}, ratchets: {len(existing_ratchets)}, bits: {len(existing_bits)}.')

    return {
        'status': 'updated',
        'added': {
            'blades': [f"{b.get('code')} {b['name_zh']}" for b in new_blades],
            'ratchets': [r['name'] for r in new_ratchets],
            'bits': [bit['id'] for bit in new_bits]
        }
    }

def send_line_notification(summary: Dict[str, Any], access_token: str, admin_user_id: str):
    if not access_token or not admin_user_id:
        return
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    blades = summary['added']['blades'][:5]
    ratchets = summary['added']['ratchets'][:5]
    bits = summary['added']['bits'][:5]
    
    text = (
        f'📢 【戰鬥陀螺 X 資料庫自動更新報告】\n\n'
        f'今日自 BeybladeHub 成功同步最新零件：\n'
        f'• 刃部 ({len(summary["added"]["blades"])} 款)：{", ".join(blades) if blades else "無"}\n'
        f'• 墊片 ({len(summary["added"]["ratchets"])} 款)：{", ".join(ratchets) if ratchets else "無"}\n'
        f'• 軸心 ({len(summary["added"]["bits"])} 款)：{", ".join(bits) if bits else "無"}\n\n'
        f'系統已完成 AI 物理重心推演、圖片本地化與雲端重載，選手可立即在 LINE 上查詢！'
    )
    payload = {
        'to': admin_user_id,
        'messages': [{'type': 'text', 'text': text}]
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        logger.info(f'LINE push notification status: {resp.status_code}')
    except Exception as e:
        logger.warning(f'Failed to send LINE notification: {e}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sync parts database with BeybladeHub')
    parser.add_argument('--dry-run', action='store_true', help='Check for diff without writing')
    parser.add_argument('--api-key', type=str, default=os.getenv('GEMINI_API_KEY'), help='Gemini API key for enrichment')
    parser.add_argument('--line-token', type=str, default=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'), help='LINE Channel Access Token')
    parser.add_argument('--line-user', type=str, default=os.getenv('ADMIN_LINE_USER_ID'), help='LINE Admin User ID for notifications')
    args = parser.parse_args()

    result = sync_database(dry_run=args.dry_run, api_key=args.api_key)
    if result['status'] == 'updated' and args.line_token and args.line_user:
        send_line_notification(result, args.line_token, args.line_user)
