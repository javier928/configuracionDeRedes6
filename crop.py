import os
from PIL import Image

# ANSI Color Codes for terminal styling
CYAN = "\033[96m"
GREEN = "\033[92m"
RESET = "\033[0m"

def crop_to_square():
    # Ask the user for the filename of the original picture (colored cyan)
    filename = input(f"{CYAN}Enter the filename of the original picture: {RESET}").strip()
    
    try:
        # Open the image file
        with Image.open(filename) as img:
            width, height = img.size
            
            # The prompt specifies preserving the height starting size.
            # For the resulting file to be a square, the width must equal the height.
            target_size = height
            
            if width < height:
                print("Note: Original width is less than height. Adjusting crop to fit a square based on the smaller dimension.")
                target_size = width
                left = 0
                top = (height - width) // 2
                right = width
                bottom = top + width
            else:
                # Center crop horizontally to make width equal to height
                left = (width - height) // 2
                top = 0
                right = left + height
                bottom = height
            
            # Perform the crop
            cropped_img = img.crop((left, top, right, bottom))
            
            # Get current working directory (pwd) and preserve original file extension
            cwd = os.getcwd()
            ext = os.path.splitext(filename)[1] or ".jpg"
            output_filename = f"croppedPicture{ext}"
            output_path = os.path.join(cwd, output_filename)
            
            # Save the resulting cropped picture
            cropped_img.save(output_path)
            
            # Display the exact confirmation message requested (colored green)
            print(f'{GREEN}File cropped. Resulting file saved in folder ({cwd}) with filename "{output_filename}"{RESET}')
            
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found in the current directory.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    crop_to_square()
