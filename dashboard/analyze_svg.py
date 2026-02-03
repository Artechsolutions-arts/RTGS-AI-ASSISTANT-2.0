import xml.etree.ElementTree as ET
import re
import json
import math

def parse_matrix(transform_str):
    """Parses matrix(a, b, c, d, e, f) and returns list of floats.
       Returns Identity [1, 0, 0, 1, 0, 0] if not found."""
    if not transform_str:
        return [1, 0, 0, 1, 0, 0]
    
    matrix_match = re.search(r'matrix\s*\(([^)]+)\)', transform_str)
    if matrix_match:
        vals = [float(x) for x in re.split(r'[,\s]+', matrix_match.group(1).strip())]
        if len(vals) == 6:
            return vals
            
    # Handle translate(x, y) -> matrix(1, 0, 0, 1, x, y)
    translate_match = re.search(r'translate\s*\(([^)]+)\)', transform_str)
    if translate_match:
        vals = [float(x) for x in re.split(r'[,\s]+', translate_match.group(1).strip())]
        tx = vals[0]
        ty = vals[1] if len(vals) > 1 else 0
        return [1, 0, 0, 1, tx, ty]
        
    # Handle scale(sx, sy) -> matrix(sx, 0, 0, sy, 0, 0)
    scale_match = re.search(r'scale\s*\(([^)]+)\)', transform_str)
    if scale_match:
        vals = [float(x) for x in re.split(r'[,\s]+', scale_match.group(1).strip())]
        sx = vals[0]
        sy = vals[1] if len(vals) > 1 else sx
        return [sx, 0, 0, sy, 0, 0]

    return [1, 0, 0, 1, 0, 0]

def apply_matrix(x, y, m):
    """Applies affine transform:
       x' = a*x + c*y + e
       y' = b*x + d*y + f
       m = [a, b, c, d, e, f]
    """
    return (m[0]*x + m[2]*y + m[4]), (m[1]*x + m[3]*y + m[5])

def get_path_centroid(d_str):
    """Averages all points in d attribute."""
    nums = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', d_str)]
    if not nums or len(nums) < 2:
        return None
    xs = nums[0::2]
    ys = nums[1::2]
    if not xs or not ys: return None
    return sum(xs)/len(xs), sum(ys)/len(ys)

def get_element_position(elem, parent_matrix=[1,0,0,1,0,0]):
    """Calculates position closer to visual center."""
    # If it's a path, get centroid of 'd'
    d = elem.get('d')
    local_x, local_y = 0, 0
    
    if d:
        cent = get_path_centroid(d)
        if cent:
            local_x, local_y = cent
    else:
        # If text, look for x, y
        # Text often has x,y attributes but they might be 0 if transform handles placement
        local_x = float(elem.get('x', 0))
        local_y = float(elem.get('y', 0))

    # Apply element's own transform
    tf = elem.get('transform')
    elem_matrix = parse_matrix(tf)
    
    # Combined transform: Parent * Element
    # But for a point, we just apply Element then Parent?
    # Yes, point P in local space -> Apply M_elem -> Apply M_parent -> Screen
    
    # M_elem applied to local point
    mx, my = apply_matrix(local_x, local_y, elem_matrix)
    
    # M_parent applied to result
    fx, fy = apply_matrix(mx, my, parent_matrix)
    
    return fx, fy

def main():
    svg_path = r"d:\AI Assist\dashboard\ap-map-new.svg"
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Error: {e}")
        return

    ns = {'svg': 'http://www.w3.org/2000/svg'}
    ET.register_namespace('', ns['svg'])

    paths = []
    texts = []

    # Iterate mainly over groups because our target structure is <g transform><path/text></g>
    # Root level scan
    for child in root:
        # Get tag without namespace
        tag = child.tag.split('}')[-1]
        
        if tag == 'g':
            g_matrix = parse_matrix(child.get('transform'))
            
            # Look for paths
            for p in child.findall('{http://www.w3.org/2000/svg}path'):
                pid = p.get('id')
                if pid:
                    px, py = get_element_position(p, g_matrix)
                    paths.append({'id': pid, 'x': px, 'y': py})
            
            # Look for texts
            for t in child.findall('{http://www.w3.org/2000/svg}text'):
                content = t.text
                if content and content.strip().isdigit():
                    tx, ty = get_element_position(t, g_matrix)
                    texts.append({'content': content.strip(), 'x': tx, 'y': ty})
                    
        elif tag == 'path':
            pid = child.get('id')
            if pid:
                px, py = get_element_position(child)
                paths.append({'id': pid, 'x': px, 'y': py})
                
        elif tag == 'text':
            content = child.text
            if content and content.strip().isdigit():
                tx, ty = get_element_position(child)
                texts.append({'content': content.strip(), 'x': tx, 'y': ty})

    print(f"Paths: {len(paths)}, Labels: {len(texts)}")
    
    # Debug bounds
    if paths:
        pxs = [p['x'] for p in paths]
        pys = [p['y'] for p in paths]
        print(f"Path Bounds: X[{min(pxs):.1f}, {max(pxs):.1f}], Y[{min(pys):.1f}, {max(pys):.1f}]")
    if texts:
        txs = [t['x'] for t in texts]
        tys = [t['y'] for t in texts]
        print(f"Text Bounds: X[{min(txs):.1f}, {max(txs):.1f}], Y[{min(tys):.1f}, {max(tys):.1f}]")

    mapping = {}
    used_texts = set()
    
    for path in paths:
        best_text = None
        min_dist = float('inf')
        
        for i, text in enumerate(texts):
            dist = math.sqrt((path['x'] - text['x'])**2 + (path['y'] - text['y'])**2)
            if dist < min_dist:
                min_dist = dist
                best_text = text
        
        if best_text and min_dist < 500: # Threshold increased
            mapping[path['id']] = best_text['content']
            
    with open('svg_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=2)
        
    print(f"Mapped {len(mapping)} paths.")
    print("Sample:", list(mapping.items())[:5])

if __name__ == '__main__':
    main()
