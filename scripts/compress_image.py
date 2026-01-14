import os
import sys
from PIL import Image

def compress_image(input_path, quality=50):
    """
    Compress an image to WebP format.
    
    Args:
        input_path (str): Path to the input image (PNG/JPG).
        quality (int): Compression quality (0-100). Default is 50.
    """
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        return

    # Generate output path
    filename = os.path.splitext(input_path)[0]
    output_path = f"{filename}.webp"

    try:
        # Open and convert image
        with Image.open(input_path) as img:
            # Convert to RGB if necessary (e.g., for PNGs with transparency)
            if img.mode in ('RGBA', 'LA'):
                # Keep transparency for WebP
                pass
            else:
                img = img.convert('RGB')
            
            # Save as WebP
            img.save(output_path, 'WEBP', quality=quality, method=6)
            
        # Calculate stats
        original_size = os.path.getsize(input_path)
        new_size = os.path.getsize(output_path)
        reduction = (original_size - new_size) / original_size * 100

        print(f"✅ Successfully compressed '{input_path}'")
        print(f"📍 Output: '{output_path}'")
        print(f"📊 Stats:")
        print(f"   Original size: {original_size / 1024:.2f} KB")
        print(f"   New size:      {new_size / 1024:.2f} KB")
        print(f"   Reduction:     {reduction:.2f}%")

    except Exception as e:
        print(f"❌ Error processing image: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 compress_image.py <image_path> [quality]")
        print("Example: python3 compress_image.py static/img/photo.png 75")
        sys.exit(1)

    input_file = sys.argv[1]
    
    # Optional quality argument
    quality_val = 50
    if len(sys.argv) > 2:
        try:
            quality_val = int(sys.argv[2])
        except ValueError:
            print("Warning: Quality must be an integer. Using default (50).")

    compress_image(input_file, quality_val)
