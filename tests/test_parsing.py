from core.database import db

queries = [
    'Phoenix Wing 9-60O',
    'Wizard Rod 7-60B',
    'Dran Buster 1-60F',
    'Cobalt Dragoon 2-60C',
    'Shark Edge 3-60LF',
    '鳳凰羽翼 9-60O',
    '魔導權杖 7-60B',
    '龍之爆裂 1-60F',
    '蒼白龍騎士 2-60C',
    '鯊魚之刃 3-60LF',
    '9-60',
    'Shark Edge'
]

print("=== COMBO PARSING TEST ===")
for q in queries:
    res = db.parse_combo_from_text(q)
    if res:
        b, r, bit = res
        stats = db.calculate_combo_stats(b, r, bit)
        print(f"[OK] {q} => {stats['combo_name']} - {stats['total_weight_g']}g")
        print(f"   Blade: {b.get('image_local')}, Ratchet: {r.get('image_local')}, Bit: {bit.get('image_local')}")
    else:
        part = db.find_part(q)
        if part:
            print(f"[PART] {q} => {part.get('name')} ({part.get('image_local')})")
        else:
            print(f"[FAIL] {q} NOT FOUND")
