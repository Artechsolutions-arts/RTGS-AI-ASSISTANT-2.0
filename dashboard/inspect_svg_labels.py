import re
import math

def parse_transform_vals(s):
    if not s: return None
    nums = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', s)]
    return nums

def apply_matrix(x, y, m):
    # m = [a, b, c, d, e, f]
    return (m[0]*x + m[2]*y + m[4]), (m[1]*x + m[3]*y + m[5])

def main():
    svg_path = r"C:/Users/ARTECH/Downloads/Map_of_all_Andhra_Pradesh_districts-en.svg"
    try:
        with open(svg_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    print(f"File size: {len(content)} bytes")

    # 1. Extract Text Labels
    img_width_match = re.search(r'width="([^"]+)"', content)
    img_height_match = re.search(r'height="([^"]+)"', content)
    print(f"SVG Size: {img_width_match.group(1) if img_width_match else '?'} x {img_height_match.group(1) if img_height_match else '?'}")

    # Find all text elements
    # Pattern: <text ... >Content</text>
    # Note: Content might be inside tspan
    
    start_pos = 0
    texts = []
    
    # Simple regex for text content
    # Look for >CONTENT</text> or >CONTENT</tspan>
    # We want to catch names like "Guntur", "Srikakulam"
    
    text_pattern = re.compile(r'>([^<]+)</(text|tspan)>', re.IGNORECASE)
    
    for m in text_pattern.finditer(content):
        val = m.group(1).strip()
        if len(val) > 2 and not val.isdigit(): # Filter out small artifacts or numbers
            texts.append(val)
            
    print(f"Found {len(texts)} potential text labels:")
    for t in texts:
        print(f" - {t}")

if __name__ == '__main__':
    main()
