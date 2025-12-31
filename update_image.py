import re
import os
import json
import random

DIR_IMG = "img"
PATH_README = "README.md"
PATH_STATUS = "status.json"
START_MARKER = "<!-- START_SECTION:daily_meme -->"
END_MARKER = "<!-- END_SECTION:daily_meme -->"

def get_image_list(directory):
    """Mendapatkan daftar semua file gambar yang tersedia."""
    files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return files

def get_next_random_image(all_images):
    """Membaca status gambar yang sudah ditampilkan, memilih yang berikutnya secara acak, dan menyimpan status baru."""
    try:
        with open(PATH_STATUS, "r") as f:
            status_data = json.load(f)
            displayed_images = status_data.get("displayed_images", [])
    except FileNotFoundError:
        displayed_images = []

    remaining_images = [img for img in all_images if img not in displayed_images]

    if not remaining_images:
        print("Semua gambar sudah ditampilkan. Me-reset urutan acak.")
        remaining_images = all_images
        displayed_images = []

    if not remaining_images:
        return None

    selected_image = random.choice(remaining_images)

    displayed_images.append(selected_image)

    with open(PATH_STATUS, "w") as f:
        json.dump({"displayed_images": displayed_images}, f, indent=2)

    return selected_image


def update_readme_section(image_filename):
    """Memperbarui path gambar di README.md."""
    with open(PATH_README, "r", encoding="utf-8") as f:
        content = f.read()

    image_path_in_readme = os.path.join(DIR_IMG, image_filename).replace("\\", "/")

    new_content_block = f """{START_MARKER}
<p align="center">
  <img src="{image_path_in_readme}" alt="meme" style="max-width: 100%; height: auto; max-height: 800px;"/>
</p>
{END_MARKER}"""

    pattern = re.compile(f"{START_MARKER}.*?{END_MARKER}", re.DOTALL)
    updated_content = pattern.sub(new_content_block, content)

    with open(PATH_README, "w", encoding="utf-8") as f:
        f.write(updated_content)
    print(f"README.md diperbarui, menunjuk ke: {image_path_in_readme}")

try:
    all_image_files = get_image_list(DIR_IMG)
    if not all_image_files:
        print("Tidak ada gambar ditemukan. Skrip berhenti.")
        exit(1)

    selected_filename = get_next_random_image(all_image_files)
    
    if selected_filename:
        update_readme_section(selected_filename)
    
except Exception as e:
    print(f"Terjadi kesalahan: {e}")
    exit(1)
