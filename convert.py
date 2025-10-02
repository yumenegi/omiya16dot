import os
import argparse
from PIL import Image
import numpy as np

def create_bmp(src, char_width = 64, dot_bmp_width = 16):
    if not os.path.exists(src):
        print(f"Error: Source image not found at '{src}'")
        print("A test image will be created. Please run the script again with the test image.")
        return
    
    try:
        img = Image.open(src).convert('L') # Convert to grayscale
    except Exception as e:
        print(f"Error opening or processing image: {e}")
        return


    # Number of characters in the font map
    num_chars = img.width // char_width

    # Size of the sub cell
    cell_size = char_width // dot_bmp_width

    # If half of the pixels in the cell are black then it's determined to be a dot
    threshold = (cell_size * cell_size) // 2

    # Threshold for black
    black_threshold = 128

    for i in range(num_chars):
        left = i * char_width
        top = 0
        right = left + char_width
        bottom = char_width

        char_img = img.crop((left, top, right, bottom))

        bitmap_data = np.zeros((dot_bmp_width,dot_bmp_width), dtype=int)
        for y in range(dot_bmp_width):
            for x in range(dot_bmp_width):
                cell_left = x * cell_size
                cell_top = y * cell_size
                cell_right = cell_left + cell_size
                cell_bottom = cell_top + cell_size

                cell_img = char_img.crop((cell_left, cell_top, cell_right, cell_bottom))

                black_pixel_count = 0
                for pixel in cell_img.getdata():
                    if pixel < black_threshold:
                        black_pixel_count += 1
                
                bitmap_data[y][x] = 1 if black_pixel_count > threshold else 0
        
        # flatten
        flat_bits = bitmap_data.flatten()
        
        # group into bytes
        byte_chunks = np.reshape(flat_bits, (-1, 8))

        byte_list = []
        for chunk in byte_chunks:
            # pack bits
            packed_byte = np.packbits(chunk, bitorder='big')[0]
            byte_list.append(packed_byte)
        
        binary_data = bytes(byte_list)

        with open("./out/%d.bin" % i, 'wb') as f_out:
            f_out.write(binary_data)
        



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="A utility to convert a graphical font map into a binary file for embedded use.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "input_file",
        help="The path to the source font map image (e.g., gothicdot16_font_map.png)."
    )

    parser.add_argument(
        "char_width",
        help="The width of each character in the font map."
    )

    parser.add_argument(
        "output_width",
        help="The output width of your bitmap for each character."
    )

    os.makedirs("out", exist_ok=True)

    args = parser.parse_args()

    src = args.input_file
    create_bmp(src, int(args.char_width), int(args.output_width))