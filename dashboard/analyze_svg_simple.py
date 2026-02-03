import re
import json
import math

def parse_transform_vals(s):
    """Extracts numbers from matrix(...) or translate(...) string"""
    if not s: return None
    nums = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', s)]
    return nums

def apply_matrix(x, y, m):
    # m = [a, b, c, d, e, f]
    # x' = ax + cy + e
    # y' = bx + dy + f
    return (m[0]*x + m[2]*y + m[4]), (m[1]*x + m[3]*y + m[5])

def main():
    svg_path = r"d:\AI Assist\dashboard\ap-map-new.svg"
    with open(svg_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Get Main Group Transform (Paths)
    # <g id="g16055" transform="matrix(...)">
    main_group_match = re.search(r'<g[^>]*id="g16055"[^>]*transform="([^"]+)"', content)
    main_matrix = [1, 0, 0, 1, 0, 0]
    
    if main_group_match:
        t_str = main_group_match.group(1)
        vals = parse_transform_vals(t_str)
        if len(vals) == 6:
            main_matrix = vals
            print(f"Main Matrix: {main_matrix}")

    # 2. Extract Paths (id and d)
    # We look for path id and d. We assume they are inside the main group or we apply main matrix to all paths found (heuristic).
    # d="m 595.96141,462.7242 ..."
    paths = []
    path_pattern = re.compile(r'<path[^>]*d="[mM]\s*([\d\.-]+)[,\s]+([\d\.-]+)[^"]*"[^>]*id="([^"]+)"')
    
    for m in path_pattern.finditer(content):
        x = float(m.group(1))
        y = float(m.group(2))
        pid = m.group(3)
        
        # Apply main matrix
        tx, ty = apply_matrix(x, y, main_matrix)
        paths.append({'id': pid, 'x': tx, 'y': ty})

    print(f"Found {len(paths)} paths.")

    # 3. Extract Text Labels
    # <g ...><text ...>(number)</text></g>
    # Often text is inside a g with transform.
    # Regex: Look for g with transform, then text inside? Too complex for single regex.
    # Identify pattern: <g ... transform="...">...<text ...>NUM</text>
    
    # We will look for separate text blocks and assume they have local transforms.
    # This is slightly fragile if they are nested deep, but usually it's shallow.
    
    texts = []
    
    # Heuristic: Find all <text> blocks, check if they are digits.
    # Then look backwards for the nearest 'transform=' attribute.
    
    # Better: Split by </g> to isolate groups? No.
    # Let's try to match the whole block <g ...> ... <text ...> ... </text> ... </g>
    # It's usually small blocks at the end of file.
    
    # Strategy: Find "Transform" and "Text Content" in close proximity.
    text_matches = re.finditer(r'<g[^>]*transform="([^"]+)"[^>]*>\s*<text[^>]*>(\d+)</text>', content)
    
    count = 0
    start_pos = 0
    
    # We loop manually to find all occurences
    for m in text_matches:
        t_str = m.group(1)
        txt = m.group(2)
        
        # Parse transform
        # usually translate(x,y) or matrix
        # If it's a matrix [1.0007, 0, 0, 1, TX, TY], we take TX, TY
        vals = parse_transform_vals(t_str)
        tx, ty = 0, 0
        
        if "matrix" in t_str and len(vals) >= 6:
            tx, ty = vals[4], vals[5]
        elif "translate" in t_str and len(vals) >= 2:
            tx, ty = vals[0], vals[1]
            
        # The text element itself might have x, y or transform (scale).
        # Usually negligible for centroid matching if we have the group translation.
        
        texts.append({'val': txt, 'x': tx, 'y': ty})
        count += 1
        
    print(f"Found {count} labels from grouped text.")
    
    # Fallback: Check for text with matrix directly on it?
    if count < 100:
        print("Trying fallback text search...")
        # <text transform="matrix(...)" ...>NUM</text>
        alt_matches = re.finditer(r'<text[^>]*transform="([^"]+)"[^>]*>(\d+)</text>', content)
        for m in alt_matches:
            t_str = m.group(1)
            txt = m.group(2)
            vals = parse_transform_vals(t_str)
            if len(vals) >= 6:
                tx, ty = vals[4], vals[5]
                texts.append({'val': txt, 'x': tx, 'y': ty})
    
    print(f"Total Labels: {len(texts)}")
    
    # Debug bounds
    if paths:
        px = [p['x'] for p in paths]
        py = [p['y'] for p in paths]
        print(f"Path X: {min(px):.1f} to {max(px):.1f}, Y: {min(py):.1f} to {max(py):.1f}")
    
    if texts:
        tx = [t['x'] for t in texts]
        ty = [t['y'] for t in texts]
        print(f"Text X: {min(tx):.1f} to {max(tx):.1f}, Y: {min(ty):.1f} to {max(ty):.1f}")

    # 4. Map
    mapping = {}
    
    for path in paths:
        best_dist = float('inf')
        best_label = None
        
        for text in texts:
            dist = math.sqrt((path['x'] - text['x'])**2 + (path['y'] - text['y'])**2)
            if dist < best_dist:
                best_dist = dist
                best_label = text['val']
        
        # Threshold: 50 units (SVG coordinates)
        if best_label and best_dist < 50:
            mapping[path['id']] = best_label
            
    print(f"Mapped {len(mapping)} paths.")
    
    with open('svg_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=2)

if __name__ == '__main__':
    main()
