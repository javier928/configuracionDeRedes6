import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

# ANSI Color Codes for terminal styling
CYAN = "\033[96m"
GREEN = "\033[92m"
RESET = "\033[0m"


def crop_to_square_interactive():
    filename = input(f"{CYAN}Enter the filename of the original picture: {RESET}").strip()

    try:
        with Image.open(filename) as img:
            # Convert to RGB/RGBA for consistent display and saving
            base_img = img.convert("RGBA")
            width, height = base_img.size

            # Preserve height as the square size when width >= height;
            # fall back to width if the original image is narrower than tall.
            square_size = min(width, height)
            max_left = max(0, width - square_size)
            step = max(1, square_size // 20)

            # 1. Preview the original picture once loaded
            fig, ax = plt.subplots()
            fig.canvas.manager.set_window_title("Original Picture Preview")
            ax.imshow(base_img)
            ax.set_title("Original Picture (Close window or press Enter to start cropping)")
            ax.axis("off")

            def on_initial_key(event):
                if event.key in ("enter", "return"):
                    plt.close(fig)

            fig.canvas.mpl_connect("key_press_event", on_initial_key)
            plt.show()

            # 2. Interactive square selection & preview over dimmed original
            state = {
                "left": max_left // 2,
                "confirmed": False,
            }
            top = (height - square_size) // 2

            # Create a dimmed ("lower intensity") version of the original image
            dimmed_img = base_img.copy()
            dim_factor = 0.35
            r, g, b, a = dimmed_img.split()
            r = r.point(lambda px: int(px * dim_factor))
            g = g.point(lambda px: int(px * dim_factor))
            b = b.point(lambda px: int(px * dim_factor))
            dimmed_img = Image.merge("RGBA", (r, g, b, a))

            fig, ax = plt.subplots()
            fig.canvas.manager.set_window_title("Interactive Square Crop")
            ax.imshow(dimmed_img)
            ax.set_xlim(0, width)
            ax.set_ylim(height, 0)
            ax.axis("off")
            ax.set_title(
                "Use Left / Right arrows to move square  |  Press Enter to save"
            )

            # Active cropped region drawn at full intensity on top of the dimmed image
            crop_overlay = ax.imshow(
                base_img.crop((state["left"], top, state["left"] + square_size, top + square_size)),
                extent=(state["left"], state["left"] + square_size, top + square_size, top),
                zorder=2,
            )

            # Highlight border around the square crop region
            border_rect = patches.Rectangle(
                (state["left"], top),
                square_size,
                square_size,
                linewidth=2,
                edgecolor="#00FF88",
                facecolor="none",
                zorder=3,
            )
            ax.add_patch(border_rect)

            def refresh_preview():
                left = state["left"]
                right = left + square_size
                cropped_patch = base_img.crop((left, top, right, top + square_size))
                crop_overlay.set_data(cropped_patch)
                crop_overlay.set_extent((left, right, top + square_size, top))
                border_rect.set_x(left)
                fig.canvas.draw_idle()

            def on_crop_key(event):
                if event.key == "left":
                    state["left"] = max(0, state["left"] - step)
                    refresh_preview()
                elif event.key == "right":
                    state["left"] = min(max_left, state["left"] + step)
                    refresh_preview()
                elif event.key in ("enter", "return"):
                    state["confirmed"] = True
                    plt.close(fig)

            fig.canvas.mpl_connect("key_press_event", on_crop_key)
            plt.show()

            if not state["confirmed"]:
                print("Cropping cancelled (Enter was not pressed).")
                return

            # 3. Perform final crop and save in current working directory (pwd)
            final_left = state["left"]
            final_box = (final_left, top, final_left + square_size, top + square_size)
            cropped_img = img.crop(final_box)

            cwd = os.getcwd()
            ext = os.path.splitext(filename)[1] or ".jpg"
            output_filename = f"croppedPicture{ext}"
            output_path = os.path.join(cwd, output_filename)

            cropped_img.save(output_path)

            print(
                f'{GREEN}file cropped. resulting file saved in folder ({cwd}) with filename "{output_filename}"{RESET}'
            )

    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found in the current directory.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    crop_to_square_interactive()