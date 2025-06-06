import geopandas as gpd
from shapely.geometry import Polygon
import json

def generate_us_states_regions(geojson_path, screen_width=800, screen_height=600, scale_factor=2.5):
    # Load GeoJSON
    gdf = gpd.read_file(geojson_path)
    
    # If this is a world dataset, filter for US
    if 'admin' in gdf.columns:
        gdf = gdf[gdf['admin'] == 'United States of America']
    elif 'ADMIN' in gdf.columns:
        gdf = gdf[gdf['ADMIN'] == 'United States of America']
    elif 'country' in gdf.columns:
        gdf = gdf[gdf['country'] == 'United States']
    elif 'NAME' in gdf.columns and len(gdf) > 60:  # Likely a world dataset
        # Try to filter by common US state names
        us_states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 
                     'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 
                     'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 
                     'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 
                     'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 
                     'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 
                     'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 
                     'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 
                     'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 
                     'West Virginia', 'Wisconsin', 'Wyoming']
        gdf = gdf[gdf['NAME'].isin(us_states)]
    
    print(f"Processing {len(gdf)} regions")
    
    # Project to Albers Equal Area for better US representation
    gdf = gdf.to_crs(epsg=5070)  # US Albers Equal Area
    
    # Separate Alaska and Hawaii for special handling
    alaska = None
    hawaii = None
    continental = gdf
    
    if 'NAME' in gdf.columns:
        alaska = gdf[gdf['NAME'] == 'Alaska']
        hawaii = gdf[gdf['NAME'] == 'Hawaii']
        continental = gdf[~gdf['NAME'].isin(['Alaska', 'Hawaii'])]
    elif 'name' in gdf.columns:
        alaska = gdf[gdf['name'] == 'Alaska']
        hawaii = gdf[gdf['name'] == 'Hawaii']
        continental = gdf[~gdf['name'].isin(['Alaska', 'Hawaii'])]
    
    # Process continental US
    minx, miny, maxx, maxy = continental.total_bounds
    
    # Calculate scale for continental US to fill most of the screen
    width = maxx - minx
    height = maxy - miny
    
    # Use a larger portion of the screen
    scale_x = (screen_width * 0.9) / width
    scale_y = (screen_height * 0.8) / height
    
    # Use the smaller scale to maintain aspect ratio, then apply scale factor
    scale = min(scale_x, scale_y) * scale_factor
    
    # Center the map
    map_width = width * scale
    map_height = height * scale
    center_x_offset = (screen_width - map_width) / 2
    center_y_offset = (screen_height - map_height) / 2
    
    regions = []
    
    # Process continental states
    for idx, row in continental.iterrows():
        geom = row.geometry
        
        # Handle MultiPolygon by taking the largest polygon
        if geom.geom_type == 'MultiPolygon':
            geom = max(geom.geoms, key=lambda g: g.area)
        
        # Simplify geometry to reduce points
        geom = geom.simplify(tolerance=5000)  # Reduced tolerance for more detail
        
        # Convert coordinates
        coords = []
        for x, y in geom.exterior.coords:
            screen_x = int((x - minx) * scale + center_x_offset)
            screen_y = int((maxy - y) * scale + center_y_offset)
            coords.append((screen_x, screen_y))
        
        # Limit points if needed
        if len(coords) > 30:
            step = len(coords) // 30
            coords = coords[::step]
        
        # Get state name
        name = row.get('NAME', row.get('name', row.get('NAME_1', f'State {idx}')))
        
        regions.append({
            'id': len(regions),
            'name': name,
            'points': coords,
            'geometry': geom,
            'original_geom': row.geometry
        })
    
    # Process Alaska - scale down and position in bottom left
    if alaska is not None and len(alaska) > 0:
        for idx, row in alaska.iterrows():
            geom = row.geometry
            if geom.geom_type == 'MultiPolygon':
                geom = max(geom.geoms, key=lambda g: g.area)
            
            geom = geom.simplify(tolerance=50000)
            
            # Scale Alaska down and position it
            alaska_scale = scale * 0.35  # Make Alaska smaller
            alaska_minx, alaska_miny, alaska_maxx, alaska_maxy = geom.bounds
            
            coords = []
            for x, y in geom.exterior.coords:
                # Position in bottom left
                screen_x = int((x - alaska_minx) * alaska_scale + 50)
                screen_y = int((alaska_maxy - y) * alaska_scale + screen_height - 200)
                coords.append((screen_x, screen_y))
            
            if len(coords) > 20:
                step = len(coords) // 20
                coords = coords[::step]
            
            regions.append({
                'id': len(regions),
                'name': 'Alaska',
                'points': coords,
                'geometry': geom,
                'original_geom': row.geometry
            })
    
    # Process Hawaii - scale and position in bottom left
    if hawaii is not None and len(hawaii) > 0:
        for idx, row in hawaii.iterrows():
            geom = row.geometry
            if geom.geom_type == 'MultiPolygon':
                # For Hawaii, we might want to keep multiple islands
                largest = max(geom.geoms, key=lambda g: g.area)
                geom = largest
            
            geom = geom.simplify(tolerance=5000)
            
            # Scale Hawaii and position it
            hawaii_scale = scale * 1.5  # Make Hawaii visible
            hawaii_minx, hawaii_miny, hawaii_maxx, hawaii_maxy = geom.bounds
            
            coords = []
            for x, y in geom.exterior.coords:
                # Position below Alaska
                screen_x = int((x - hawaii_minx) * hawaii_scale + 200)
                screen_y = int((hawaii_maxy - y) * hawaii_scale + screen_height - 100)
                coords.append((screen_x, screen_y))
            
            regions.append({
                'id': len(regions),
                'name': 'Hawaii',
                'points': coords,
                'geometry': geom,
                'original_geom': row.geometry
            })
    
    # Determine neighbors
    print("Calculating neighbors...")
    for i, region in enumerate(regions):
        region['neighbors'] = []
        for j, other in enumerate(regions):
            if i != j:
                # Check if geometries touch or are very close
                if region['original_geom'].touches(other['original_geom']) or \
                   region['original_geom'].distance(other['original_geom']) < 1000:
                    region['neighbors'].append(j)
    
    # Clean up - remove geometry objects
    for region in regions:
        del region['geometry']
        del region['original_geom']
    
    return regions


def write_regions_as_python_function(regions, output_path="level_us_states.py"):
    with open(output_path, "w") as f:
        f.write("from config import Config\n\n")
        f.write("def get_level_us_states():\n")
        f.write("    \"\"\"US States map - auto-generated from GeoJSON.\"\"\"\n")
        f.write("    center_x = Config.SCREEN_WIDTH // 2\n")
        f.write("    center_y = Config.SCREEN_HEIGHT // 2\n\n")
        f.write("    regions_data = [\n")
        
        for region in regions:
            f.write("        {\n")
            f.write(f"            'id': {region['id']},\n")
            f.write(f"            'name': '{region['name']}',\n")
            f.write(f"            'points': [\n")
            
            # Write points relative to center
            for x, y in region['points']:
                offset_x = x - 400  # Assuming 800 width
                offset_y = y - 300  # Assuming 600 height
                f.write(f"                (center_x + {offset_x}, center_y + {offset_y}),\n")
            
            f.write("            ],\n")
            f.write(f"            'neighbors': {region['neighbors']}\n")
            f.write("        },\n")
        
        f.write("    ]\n\n")
        f.write("    return regions_data\n")


if __name__ == '__main__':
    # Configuration
    geojson_file = "us.geojson"  # Your US states GeoJSON file
    output_file = "level_us_states.py"
    
    try:
        # Generate regions from GeoJSON with larger scale
        # Increase scale_factor to make it even bigger (default is now 2.5)
        regions = generate_us_states_regions(
            geojson_file, 
            screen_width=800, 
            screen_height=600,
            scale_factor=2.5  # Adjust this to make it bigger/smaller
        )
        
        # Write to Python file
        write_regions_as_python_function(regions, output_file)
        
        print(f"✅ Successfully generated {output_file}")
        print(f"📊 Total regions: {len(regions)}")
        print(f"🗺️  States included: {', '.join([r['name'] for r in regions[:5]])}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your GeoJSON file contains US states data.")