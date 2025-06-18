# Copyright (C) 2025 Bishoy Wadea
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import geopandas as gpd
from shapely.geometry import Polygon
import json
import os

def generate_regions_from_geojson(
    geojson_path, 
    output_name="regions",
    screen_width=800, 
    screen_height=600, 
    scale_factor=1.0,
    simplification_tolerance=None,
    filter_country=None,
    filter_field=None,
    filter_values=None,
    special_regions=None,
    special_region_config=None
):
    """
    Generate region data from any GeoJSON file.
    
    Args:
        geojson_path: Path to GeoJSON file
        output_name: Name for the output (used in function naming)
        screen_width: Target screen width
        screen_height: Target screen height
        scale_factor: Scale multiplier for the map
        simplification_tolerance: Tolerance for geometry simplification (auto-calculated if None)
        filter_country: Country name to filter (optional)
        filter_field: Field name to filter on (optional)
        filter_values: List of values to include (optional)
        special_regions: List of region names to handle specially (like Alaska/Hawaii)
        special_region_config: Dict with config for special regions {name: {scale: float, position: (x, y)}}
    """
    # Load GeoJSON
    gdf = gpd.read_file(geojson_path)
    
    print(f"Loaded {len(gdf)} features from {geojson_path}")
    print(f"Available columns: {list(gdf.columns)}")
    
    # Apply filters if specified
    if filter_country:
        country_fields = ['admin', 'ADMIN', 'country', 'COUNTRY', 'Admin', 'Country']
        for field in country_fields:
            if field in gdf.columns:
                gdf = gdf[gdf[field] == filter_country]
                print(f"Filtered by {field} == {filter_country}: {len(gdf)} features")
                break
    
    if filter_field and filter_values:
        if filter_field in gdf.columns:
            gdf = gdf[gdf[filter_field].isin(filter_values)]
            print(f"Filtered by {filter_field}: {len(gdf)} features")
    
    # Try to reproject to a suitable CRS
    original_crs = gdf.crs
    if original_crs and original_crs.to_epsg() == 4326:  # If in WGS84
        # Get the centroid to determine appropriate projection
        bounds = gdf.total_bounds
        center_lon = (bounds[0] + bounds[2]) / 2
        center_lat = (bounds[1] + bounds[3]) / 2
        
        # Choose projection based on location
        try:
            if -180 <= center_lon <= -20:  # Americas
                if center_lat > 45:  # North America
                    gdf = gdf.to_crs(epsg=5070)  # Albers North America
                else:  # South America
                    gdf = gdf.to_crs(epsg=5880)  # South America Albers Equal Area
            elif -20 <= center_lon <= 60:  # Europe/Africa
                if center_lat > 35:  # Europe
                    gdf = gdf.to_crs(epsg=3035)  # ETRS89-LAEA
                else:  # Africa
                    gdf = gdf.to_crs(epsg=4208)  # Africa Albers Equal Area
            else:  # Asia/Oceania
                gdf = gdf.to_crs(epsg=3857)  # Web Mercator as fallback
        except:
            print("Warning: Could not reproject, using original CRS")
    
    # Identify name field
    name_fields = ['NAME', 'name', 'Name', 'NAME_1', 'NAME_2', 'ADMIN', 'admin', 
                   'STATE_NAME', 'PROVINCE', 'REGION', 'region', 'State', 'Province']
    name_field = None
    for field in name_fields:
        if field in gdf.columns:
            name_field = field
            break
    
    # Separate special regions if specified
    special_gdfs = {}
    main_gdf = gdf
    
    if special_regions and name_field:
        for special in special_regions:
            special_gdf = gdf[gdf[name_field] == special]
            if len(special_gdf) > 0:
                special_gdfs[special] = special_gdf
                main_gdf = main_gdf[main_gdf[name_field] != special]
    
    # Process main regions
    minx, miny, maxx, maxy = main_gdf.total_bounds
    
    # Calculate scale
    width = maxx - minx
    height = maxy - miny
    
    # Calculate appropriate scale
    scale_x = (screen_width * 0.8) / width
    scale_y = (screen_height * 0.7) / height
    scale = min(scale_x, scale_y) * scale_factor
    
    # Center the map
    map_width = width * scale
    map_height = height * scale
    center_x_offset = (screen_width - map_width) / 2
    center_y_offset = (screen_height - map_height) / 2
    
    # Auto-calculate simplification tolerance if not provided
    if simplification_tolerance is None:
        # Base it on the size of the region
        avg_area = main_gdf.geometry.area.mean()
        simplification_tolerance = avg_area ** 0.5 / 100
    
    regions = []
    
    # Process main regions
    for idx, row in main_gdf.iterrows():
        geom = row.geometry
        
        # Handle MultiPolygon by taking the largest polygon
        if geom.geom_type == 'MultiPolygon':
            geom = max(geom.geoms, key=lambda g: g.area)
        elif geom.geom_type != 'Polygon':
            continue  # Skip non-polygon geometries
        
        # Simplify geometry
        geom = geom.simplify(tolerance=simplification_tolerance)
        
        # Convert coordinates
        coords = []
        for x, y in geom.exterior.coords:
            screen_x = int((x - minx) * scale + center_x_offset)
            screen_y = int((maxy - y) * scale + center_y_offset)
            coords.append((screen_x, screen_y))
        
        # Limit points if needed
        if len(coords) > 50:
            step = len(coords) // 50
            coords = coords[::step]
        
        # Get region name
        if name_field:
            name = str(row[name_field])
        else:
            name = f'Region {idx}'
        
        regions.append({
            'id': len(regions),
            'name': name,
            'points': coords,
            'geometry': geom,
            'original_geom': row.geometry
        })
    
    # Process special regions
    if special_region_config is None:
        special_region_config = {}
        # Default positioning for special regions
        y_offset = screen_height - 200
        x_offset = 50
        for i, special in enumerate(special_regions or []):
            special_region_config[special] = {
                'scale': 0.3,
                'position': (x_offset + i * 150, y_offset)
            }
    
    for special_name, special_gdf in special_gdfs.items():
        config = special_region_config.get(special_name, {'scale': 0.3, 'position': (50, screen_height - 200)})
        special_scale = scale * config['scale']
        pos_x, pos_y = config['position']
        
        for idx, row in special_gdf.iterrows():
            geom = row.geometry
            if geom.geom_type == 'MultiPolygon':
                geom = max(geom.geoms, key=lambda g: g.area)
            elif geom.geom_type != 'Polygon':
                continue
            
            geom = geom.simplify(tolerance=simplification_tolerance * 2)
            
            # Get bounds for this specific region
            spec_minx, spec_miny, spec_maxx, spec_maxy = geom.bounds
            
            coords = []
            for x, y in geom.exterior.coords:
                screen_x = int((x - spec_minx) * special_scale + pos_x)
                screen_y = int((spec_maxy - y) * special_scale + pos_y)
                coords.append((screen_x, screen_y))
            
            if len(coords) > 30:
                step = len(coords) // 30
                coords = coords[::step]
            
            regions.append({
                'id': len(regions),
                'name': special_name,
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
                try:
                    # Check if geometries touch or are very close
                    if region['original_geom'].touches(other['original_geom']) or \
                       region['original_geom'].distance(other['original_geom']) < simplification_tolerance * 10:
                        region['neighbors'].append(j)
                except:
                    pass  # Skip if geometry operation fails
    
    # Clean up - remove geometry objects
    for region in regions:
        del region['geometry']
        del region['original_geom']
    
    return regions


def write_regions_as_python_function(regions, output_name="regions", output_path=None):
    """Write regions data as a Python function."""
    if output_path is None:
        output_path = f"level_{output_name}.py"
    
    # Create a valid Python function name
    func_name = f"get_level_{output_name}".replace("-", "_").replace(" ", "_").lower()
    
    with open(output_path, "w") as f:
        f.write("from config import Config\n\n")
        f.write(f"def {func_name}():\n")
        f.write(f"    \"\"\"{output_name.replace('_', ' ').title()} map - auto-generated from GeoJSON.\"\"\"\n")
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


# Example configurations for different regions
REGION_CONFIGS = {
    'us_states': {
        'filter_country': 'United States of America',
        'special_regions': ['Alaska', 'Hawaii'],
        'special_region_config': {
            'Alaska': {'scale': 0.35, 'position': (50, 400)},
            'Hawaii': {'scale': 1.5, 'position': (200, 500)}
        },
        'scale_factor': 2.5
    },
    'world_countries': {
        'scale_factor': 1.0,
        'simplification_tolerance': 100000
    },
    'europe': {
        'filter_field': 'CONTINENT',
        'filter_values': ['Europe'],
        'scale_factor': 1.5
    },
    'canada_provinces': {
        'filter_country': 'Canada',
        'scale_factor': 1.2
    }
}


if __name__ == '__main__':
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python script.py <geojson_file> [region_type] [output_name]")
        print("Example: python script.py world.geojson world_countries world")
        print("Available region types:", list(REGION_CONFIGS.keys()))
        sys.exit(1)
    
    geojson_file = sys.argv[1]
    region_type = sys.argv[2] if len(sys.argv) > 2 else None
    output_name = sys.argv[3] if len(sys.argv) > 3 else os.path.splitext(os.path.basename(geojson_file))[0]
    
    # Get configuration
    config = REGION_CONFIGS.get(region_type, {}) if region_type else {}
    
    try:
        # Generate regions from GeoJSON
        regions = generate_regions_from_geojson(
            geojson_file,
            output_name=output_name,
            scale_factor=2.0,
            screen_width=800,
            screen_height=600,
            **config  # Unpack the configuration
        )
        
        # Write to Python file
        write_regions_as_python_function(regions, output_name)
        
        print(f"✅ Successfully generated level_{output_name}.py")
        print(f"📊 Total regions: {len(regions)}")
        if regions:
            print(f"🗺️  Regions included: {', '.join([r['name'] for r in regions[:5]])}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nTips:")
        print("- Make sure you have geopandas installed: pip install geopandas")
        print("- Check that your GeoJSON file exists and is valid")
        print("- Try examining the GeoJSON structure first")