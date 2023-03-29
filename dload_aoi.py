import os
import requests
from io import BytesIO
from PIL import Image
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from typing import Tuple, List

BING_API_KEY = 'Aq7GavngTmmm8XO64OkUHrctc3sQ-B6F49y5mMnwzy3cjqyuET8Hii6uOltMdsPe'

def download_bing_imagery(aoi: Tuple[float, float, float, float], zoom: int) -> Image:
    min_lat, min_lon, max_lat, max_lon = aoi
    quadkey_base_url = f"https://dev.virtualearth.net/REST/v1/Imagery/Metadata/Aerial?mapArea={min_lat},{min_lon},{max_lat},{max_lon}&zl={zoom}&key={BING_API_KEY}"
    response = requests.get(quadkey_base_url)
    response.raise_for_status()
    data = response.json()

    if not data['resourceSets'] or not data['resourceSets'][0]['resources']:
        raise ValueError("No imagery available for this AOI at the specified zoom level.")

    resource = data['resourceSets'][0]['resources'][0]
    image_url = resource['imageUrl']

    image_data = requests.get(image_url)
    image_data.raise_for_status()

    return Image.open(BytesIO(image_data.content)).convert('RGB')

def tile_image(image: Image, tile_size: Tuple[int, int]) -> List[Image]:
    width, height = image.size
    tile_width, tile_height = tile_size
    tiles = []

    for y in range(0, height, tile_height):
        for x in range(0, width, tile_width):
            tile = image.crop((x, y, x + tile_width, y + tile_height))
            tiles.append(tile)

    return tiles

def save_geotiffs(tiles: List[Image], aoi: Tuple[float, float, float, float], output_folder: str):
    min_lat, min_lon, max_lat, max_lon = aoi
    num_tiles_x = len(tiles[0])
    num_tiles_y = len(tiles)
    tile_width_degrees = (max_lon - min_lon) / num_tiles_x
    tile_height_degrees = (max_lat - min_lat) / num_tiles_y

    os.makedirs(output_folder, exist_ok=True)

    for j, row in enumerate(tiles):
        for i, tile in enumerate(row):
            tile_min_lon = min_lon + i * tile_width_degrees
            tile_max_lon = min_lon + (i + 1) * tile_width_degrees
            tile_min_lat = max_lat - (j + 1) * tile_height_degrees
            tile_max_lat = max_lat - j * tile_height_degrees

            transform = from_bounds(tile_min_lon, tile_min_lat, tile_max_lon, tile_max_lat, 224, 224)
            with rasterio.open(
                os.path.join(output_folder, f'tile_{j}_{i}.tif'),
                'w',
                driver='GTiff',
                height=224,
                width=224,
                count=3,
                dtype=np.uint8,
                crs='EPSG:4326',
                transform=transform,
            ) as dst:
                dst.write(np.array(tile).transpose(2, 0, 1))

def main():
    # Define your AOI (Area of Interest) as a tuple of (min_latitude, min_longitude, max_latitude, max_longitude)
    aoi = (34.43861, 40.93056, 34.47861, 40.97056)

    # Define the zoom level. Higher zoom levels provide more detailed images but smaller coverage.
    zoom = 18

    # Define the output folder for the GeoTIFF tiles
    output_folder = 'geotiff_tiles'

    # Download the Bing imagery for the given AOI
    print("Downloading Bing imagery...")
    image = download_bing_imagery(aoi, zoom)

    # Tile the downloaded image into 224 x 224 tiles
    print("Tiling the image...")
    tiles = tile_image(image, (224, 224))

    # Save the tiles as GeoTIFF files
    print("Saving GeoTIFF tiles...")
    save_geotiffs(tiles, aoi, output_folder)

    print("Process completed successfully.")

if __name__ == "__main__":
    main()

