import urllib.request
import json
import math

# Target Districts for normalization
DISTRICT_MAPPING = {
    'Srikakulam': 'srikakulam',
    'Parvathipuram Manyam': 'parvathipuram-manyam',
    'Vizianagaram': 'vizianagaram',
    'Visakhapatnam': 'visakhapatnam',
    'Anakapalli': 'anakapalli',
    'Alluri Sitharama Raju': 'alluri-sitharama-raju',
    'Kakinada': 'kakinada',
    'East Godavari': 'east-godavari',
    'Konaseema': 'konaseema',
    'Dr. B.R. Ambedkar Konaseema': 'konaseema', # Variant
    'West Godavari': 'west-godavari',
    'Eluru': 'eluru',
    'Krishna': 'krishna',
    'NTR': 'ntr',
    'Guntur': 'guntur',
    'Palnadu': 'palnadu',
    'Bapatla': 'bapatla',
    'Prakasam': 'prakasam',
    'Sri Potti Sriramulu Nellore': 'nellore',
    'Nellore': 'nellore', # Variant
    'Tirupati': 'tirupati',
    'Chittoor': 'chittoor',
    'Annamayya': 'annamayya',
    'YSR': 'ysr',
    'Y.S.R.': 'ysr', # Variant
    'Kadapa': 'ysr', # Variant
    'Nandyal': 'nandyal',
    'Kurnool': 'kurnool',
    'Anantapuramu': 'anantapur',
    'Ananthapuramu': 'anantapur', # Variant spelling
    'Anantapur': 'anantapur', # Variant
    'Sri Sathya Sai': 'satya-sai'
}

PASTEL_COLORS = [
    "#FFB7B2", "#FFDAC1", "#E2F0CB", "#B5EAD7", "#C7CEEA", 
    "#F0E6EF", "#D6E2E9", "#FAD2E1", "#FFF1E6", "#E0BBE4"
]

URLS = [
    "https://raw.githubusercontent.com/satishvmadala/andhrapradesh_opendata_locations/main/AndhraPradesh_Districts.geojson",
    "https://raw.githubusercontent.com/satishvmadala/andhrapradesh_opendata_locations/master/AndhraPradesh_Districts.geojson"
]

def mercator_project(lon, lat):
    x = lon
    lat_rad = math.radians(lat)
    y = math.log(math.tan(math.pi/4 + lat_rad/2))
    return x, y

def convert_coordinates(coords, bounds, scale, offset_x, offset_y, height):
    path_cmds = []
    start_pt = True
    for pt in coords:
        lon, lat = pt[0], pt[1]
        mx, my = mercator_project(lon, lat)
        
        # SVG Y is down, Mercator Y is up. Flip Y: (height - (...))
        sx = (mx - bounds['min_x']) * scale + offset_x
        sy = height - ((my - bounds['min_y']) * scale + offset_y)
        
        cmd = "M" if start_pt else "L"
        path_cmds.append(f"{cmd} {sx:.2f},{sy:.2f}")
        start_pt = False
        
    path_cmds.append("Z")
    return " ".join(path_cmds)

def main():
    data = None
    for url in URLS:
        try:
            print(f"Trying {url}...")
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    print("Success!")
                    break
        except Exception as e:
            print(f"Failed: {e}")
            
    if not data:
        print("Could not download GeoJSON.")
        return

    features = data.get('features', [])
    print(f"Found {len(features)} features.")
    
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = float('-inf'), float('-inf')
    
    valid_features = []
    
    for f in features:
        props = f.get('properties', {})
        # Try multiple known property keys used by common AP district GeoJSON sources
        name = (
            props.get('district', '') or
            props.get('DISTRICT', '') or
            props.get('District', '') or
            props.get('dist_name', '') or
            props.get('distname', '') or
            props.get('DIST_NAME', '') or
            props.get('district_name', '') or
            props.get('Name', '') or
            props.get('NAME_2', '') or
            props.get('NAME_1', '') or
            props.get('name', '') or
            ''
        )
        
        # Normalize
        norm_id = None
        canonical_name = None
        for k, v in DISTRICT_MAPPING.items():
            if k.lower() in name.lower():
                norm_id = v
                canonical_name = k
                break
        if not norm_id:
            # Ignore unknown/empty features (strictly target AP 26 districts)
            continue
        
        geom = f.get('geometry', {})
        gtype = geom.get('type')
        coords = geom.get('coordinates')
        
        all_points = []
        if gtype == 'Polygon':
            for ring in coords:
                all_points.extend(ring)
        elif gtype == 'MultiPolygon':
            for poly in coords:
                for ring in poly:
                    all_points.extend(ring)
                    
        if not all_points: continue

        for pt in all_points:
            mx, my = mercator_project(pt[0], pt[1])
            min_x = min(min_x, mx)
            min_y = min(min_y, my)
            max_x = max(max_x, mx)
            max_y = max(max_y, my)
            
        valid_features.append({
            'id': norm_id,
            'geometry': geom,
            'name': canonical_name or name
        })

    # Deduplicate by district id (keep first occurrence)
    deduped = {}
    for vf in valid_features:
        if vf['id'] in deduped:
            continue
        deduped[vf['id']] = vf
    valid_features = list(deduped.values())

    print(f"Using {len(valid_features)} normalized district features.")

    WIDTH = 800
    HEIGHT = 600
    PADDING = 20
    
    geo_width = max_x - min_x
    geo_height = max_y - min_y
    if geo_height == 0: geo_height = 1
    if geo_width == 0: geo_width = 1
    
    scale_x = (WIDTH - 2*PADDING) / geo_width
    scale_y = (HEIGHT - 2*PADDING) / geo_height
    scale = min(scale_x, scale_y)
    
    offset_x = PADDING + (WIDTH - 2*PADDING - geo_width*scale)/2
    offset_y = PADDING + (HEIGHT - 2*PADDING - geo_height*scale)/2
    
    bounds = {'min_x': min_x, 'min_y': min_y}
    
    svg_out = []
    svg_out.append(f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg">')
    # Background for contrast
    svg_out.append(f'  <desc>Andhra Pradesh 26 Districts Map</desc>')
    svg_out.append('  <g id="andhra-pradesh">')
    
    color_idx = 0
    for vf in sorted(valid_features, key=lambda x: x['id']):
        geom = vf['geometry']
        gtype = geom.get('type')
        coords = geom.get('coordinates')
        feat_id = vf['id']
        feat_name = vf['name']
        
        d_path = ""
        if gtype == 'Polygon':
            for ring in coords:
                d_path += convert_coordinates(ring, bounds, scale, offset_x, offset_y, HEIGHT) + " "
        elif gtype == 'MultiPolygon':
            for poly in coords:
                for ring in poly:
                    d_path += convert_coordinates(ring, bounds, scale, offset_x, offset_y, HEIGHT) + " "
                    
        color = PASTEL_COLORS[color_idx % len(PASTEL_COLORS)]
        color_idx += 1
        
        svg_out.append(f'    <path id="{feat_id}" data-name="{feat_name}" d="{d_path.strip()}" fill="{color}" stroke="#333" stroke-width="0.5" vector-effect="non-scaling-stroke" />')
        
    svg_out.append('  </g>')
    svg_out.append('</svg>')
    
    with open(r'd:\AI Assist\dashboard\ap-map-clean.svg', 'w', encoding='utf-8') as f:
        f.write("\n".join(svg_out))
        
    print("Successfully generated ap-map-clean.svg from GeoJSON")

if __name__ == '__main__':
    main()
