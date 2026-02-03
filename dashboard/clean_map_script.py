import xml.etree.ElementTree as ET
import re
import math

# Target Districts (Normalized) -> Search Terms
DISTRICTS = {
    "srikakulam": ["Srikakulam"],
    "parvathipuram-manyam": ["Parvathipuram Manyam"],
    "vizianagaram": ["Vizianagaram"],
    "visakhapatnam": ["Visakhapatnam"],
    "anakapalli": ["Anakapalli"],
    "alluri-sitharama-raju": ["Alluri Sitharama Raju"],
    "kakinada": ["Kakinada"],
    "east-godavari": ["East Godavari"],
    "konaseema": ["Konaseema"],
    "west-godavari": ["West Godavari"],
    "eluru": ["Eluru"],
    "krishna": ["Krishna"],
    "ntr": ["NTR"],
    "guntur": ["Guntur"],
    "palnadu": ["Palnadu"],
    "bapatla": ["Bapatla"],
    "prakasam": ["Prakasam"],
    "nellore": ["Sri Potti Sriramulu Nellore", "Nellore"],
    "tirupati": ["Tirupati"],
    "chittoor": ["Chittoor"],
    "annamayya": ["Annamayya"],
    "ysr": ["YSR", "Kadapa"],
    "nandyal": ["Nandyal"],
    "kurnool": ["Kurnool"],
    "anantapur": ["Ananthapuramu", "Anantapur"],
    "satya-sai": ["Sri Sathya Sai"]
}

PASTEL_COLORS = [
    "#FFB7B2", "#FFDAC1", "#E2F0CB", "#B5EAD7", "#C7CEEA", 
    "#F0E6EF", "#D6E2E9", "#FAD2E1", "#FFF1E6", "#E0BBE4"
]

def get_path_centroid(d_str):
    nums = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', d_str)]
    if not nums or len(nums) < 2: return None
    # Just take the first point (MoveTo) as a rough anchor for matching labels
    return nums[0], nums[1]

def parse_transform(transform_str):
    if not transform_str: return [1, 0, 0, 1, 0, 0]
    nums = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', transform_str)]
    if len(nums) == 6: return nums
    if "translate" in transform_str and len(nums) == 2: return [1, 0, 0, 1, nums[0], nums[1]]
    return [1, 0, 0, 1, 0, 0]

def apply_matrix(x, y, m):
    return (m[0]*x + m[2]*y + m[4]), (m[1]*x + m[3]*y + m[5])

def main():
    svg_path = r"C:/Users/ARTECH/Downloads/Map_of_all_Andhra_Pradesh_districts-en.svg"
    
    # Register namespaces to avoid "ns0:" prefixes
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing SVG: {e}")
        return

    # Namespaces usually present in SVG
    ns = {'svg': 'http://www.w3.org/2000/svg'}

    # 1. Collect all Paths with their global coordinates
    # We need to traverse and accumulate transforms?
    # Or just grab the known groups.
    # Root -> g id="Map 1: ap-districts" -> g -> path
    
    parsed_paths = []
    
    # Global transform from inspection: translate(-529.74485,-200.77405)
    # Inner transform: matrix(0.999751,0,0,0.999751,395.242,72.1097)
    
    # Combined transform logic:
    # P_final = T_outer * T_inner * P_local
    
    # T_outer = [1, 0, 0, 1, -529.74485, -200.77405]
    # T_inner = [0.999751, 0, 0, 0.999751, 395.242, 72.1097]
    
    # Let's perform the matrix multiplication for the combined transform:
    # a = a1*a2 + c1*b2 = 1*0.999... + 0 = 0.999751
    # b = ...
    # Simplified since T_outer is just translation:
    # combined_scale_x = 0.999751
    # combined_scale_y = 0.999751
    # combined_trans_x = 1*395.242 + 0 + (-529.74485) = -134.50285
    # combined_trans_y = 0 + 1*72.1097 + (-200.77405) = -128.66435
    
    combined_matrix = [0.999751, 0, 0, 0.999751, -134.50285, -128.66435]

    # Find paths
    # We'll just look for ALL paths and filter by validity/size later if needed
    for path in root.iter('{http://www.w3.org/2000/svg}path'):
        d = path.get('d')
        if not d: continue
        
        cent = get_path_centroid(d)
        if cent:
            global_x, global_y = apply_matrix(cent[0], cent[1], combined_matrix)
            parsed_paths.append({
                'd': d,
                'x': global_x,
                'y': global_y
            })
            
    print(f"Parsed {len(parsed_paths)} paths.")

    # 2. Collect Texts and Match
    mapped_districts = {}
    
    # Text elements might be separate. 
    # They usually have transforms too.
    # Text coordinates in this specific file seemed to be "transformed" by the group too?
    # Or are they absolute?
    # Inspection suggests text labels are likely absolute or have their own matrix.
    
    for text in root.iter('{http://www.w3.org/2000/svg}text'):
        # Get content (might be nested in tspan)
        content = "".join(text.itertext()).strip()
        if not content: continue
        
        # Match District Name
        matched_key = None
        for key, aliases in DISTRICTS.items():
            if content in aliases:
                matched_key = key
                break
        
        if not matched_key: continue
        
        # Get Coords
        # Check for transform
        trans = text.get('transform')
        x_attr = text.get('x')
        y_attr = text.get('y')
        
        tx, ty = 0, 0
        
        if trans:
            m = parse_transform(trans)
            # If matrix, the translation part is index 4, 5
            tx, ty = m[4], m[5]
        elif x_attr and y_attr:
            try:
                tx = float(x_attr)
                ty = float(y_attr)
            except: pass
            
        # IMPORTANT: Applying T_outer to text?
        # If the text is ALSO inside the "translate(-529...)" group, we must apply it.
        # But looking at XML structure, text usually comes AFTER or OUTSIDE map paths in layers.
        # Let's assume text coordinates are closer to "screen space" or at least 
        # need the -529,-200 offset if they are in the same main group.
        # Given the previous script output (Srikakulam at -529, -200), it implies 
        # the text coordinates retrieved were 0,0 relative to a group? No.
        
        # Let's adjust text by the GLOBAL translation T1 only (-529, -200)
        # assuming they are largely in the same coordinate space frame.
        
        final_tx = tx - 529.74485
        final_ty = ty - 200.77405
        
        # Find closes path
        best_path = None
        min_dist = float('inf')
        
        for p in parsed_paths:
            dist = math.sqrt((p['x'] - final_tx)**2 + (p['y'] - final_ty)**2)
            if dist < min_dist:
                min_dist = dist
                best_path = p
                
        if best_path:
            # Check for duplicates? Or simple override?
            # Ideally avoid assigning same path to multiple.
            # But overlapping labels might occur. srikakulam logic seemed to work.
            mapped_districts[matched_key] = best_path['d']

    print(f"Mapped {len(mapped_districts)} districts.")

    # 3. Write Clean SVG
    with open(r'd:\AI Assist\dashboard\ap-map-clean.svg', 'w', encoding='utf-8') as f:
        f.write(f'<svg viewBox="0 0 2488 2067" xmlns="http://www.w3.org/2000/svg">\n')
        # We wrap in the combined matrix to place them correctly in viewport
        f.write(f'  <g id="andhra-pradesh" transform="matrix(0.999751, 0, 0, 0.999751, -134.50285, -128.66435)">\n')
        
        color_idx = 0
        for key in sorted(mapped_districts.keys()):
            d_path = mapped_districts[key]
            # Clean up newlines in path data
            d_path = " ".join(d_path.split())
            color = PASTEL_COLORS[color_idx % len(PASTEL_COLORS)]
            color_idx += 1
            
            f.write(f'    <path id="{key}" d="{d_path}" fill="{color}" stroke="#FFFFFF" stroke-width="2" vector-effect="non-scaling-stroke" />\n')
            
        f.write('  </g>\n')
        f.write('</svg>')
    
    print("Clean SVG generated.")

if __name__ == '__main__':
    main()
