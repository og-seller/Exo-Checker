import os
import json
import math
import colorsys
import urllib.request
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps

class FortniteCache:
    def __init__(self):
        self.cache_dir = "cache"
        self.cache = {}
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.load_cache_from_directory()
    
    def load_cache_from_directory(self):
        """Load cached cosmetic icons from directory"""
        for filename in os.listdir(self.cache_dir):
            if filename.endswith(".png"):
                id = os.path.splitext(filename)[0]
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    image = Image.open(file_path).convert('RGBA')
                    self.cache[id] = image
                except Exception as e:
                    continue
    
    def get_cosmetic_icon_from_cache(self, url, id):
        """Get cosmetic icon from cache or download if not available"""
        if not url:
            print(f"Error: No URL provided for ID: {id}")
            return None
        
        cache_path = os.path.join(self.cache_dir, f"{id}.png")
        if id in self.cache:
            return self.cache[id]

        if os.path.exists(cache_path):
            try:
                image = Image.open(cache_path).convert('RGBA')
                self.cache[id] = image
                return image
            except Exception as e:
                print(f"Error loading {cache_path}: {e}")

        try:
            import urllib.request
            with urllib.request.urlopen(url) as response:
                image_data = response.read()
                image = Image.open(BytesIO(image_data)).convert('RGBA')
                try:
                    image.save(cache_path)
                except Exception as e:
                    print(f"Error saving {cache_path}: {e}")
                
                self.cache[id] = image
                return image 
        except Exception as e:
            print(f"Error downloading image from {url}: {e}")
            return None

# Global cache instance
fortnite_cache = FortniteCache()

def draw_gradient_text(gradient_type, draw, position, text, font, fill=(255, 255, 255)):
    """Draw text with gradient effects"""
    import colorsys
    num_colors = len(text)
    if gradient_type == 0:
        gradient_colors = [(255, 255, 255)] * num_colors
    elif gradient_type == 1:
        gradient_colors = [
            tuple(int(c * 255) for c in colorsys.hsv_to_rgb(i / num_colors, 1, 1))
            for i in range(num_colors)
        ]
    elif gradient_type == 2:
        gradient_colors = [
            tuple(int(c * 255) for c in colorsys.hsv_to_rgb(0.13, 0.5 + (i / num_colors) * 0.5, 0.8 + (i / num_colors) * 0.2))
            for i in range(num_colors)
        ]
    elif gradient_type == 3:
        gradient_colors = [
            tuple(int(c * 255) for c in colorsys.hsv_to_rgb(0, 0 + (i / num_colors) * 0.2, 0.6 + (i / num_colors) * 0.4))
            for i in range(num_colors)
        ]
    
    x, y = position
    for i, char in enumerate(text):
        color = gradient_colors[i]
        char_width = font.getbbox(char)[2]
        draw.text((x, y), char, font=font, fill=color)
        x += char_width

def render_exo_style(header: str, user_data: json, arr: list[str], nametosave: str) -> None:
    # calculating cosmetics per row
    cosmetic_per_row = 6
    total_cosmetics = len(arr)
    num_rows = math.ceil(total_cosmetics / cosmetic_per_row)
    if total_cosmetics > 30:
        num_rows = int(math.sqrt(total_cosmetics))
        cosmetic_per_row = math.ceil(total_cosmetics / num_rows)
        
        while cosmetic_per_row * num_rows < total_cosmetics:
            num_rows += 1
            cosmetic_per_row = math.ceil(total_cosmetics / num_rows)

    # setup for our image, thumbnails
    padding = 30
    thumbnail_width = 128
    thumbnail_height = 128
    image_width = int(cosmetic_per_row * thumbnail_width)
    image_height = int(thumbnail_height + 5 + thumbnail_width * num_rows + 180)
    font_path = 'styles/exo/font.ttf'
    font_size = 16
    font = ImageFont.truetype(font_path, font_size)
    image = Image.new('RGB', (image_width, image_height), (0, 0, 0))
    
    # custom background
    custom_background_path = f"users/backgrounds/{user_data['ID']}.png"
    if os.path.isfile(custom_background_path):
        custom_background = Image.open(custom_background_path).resize((image_width, image_height), Image.Resampling.BILINEAR)
        image.paste(custom_background, (0, 0))
        
    current_row = 0
    current_column = 0
    sortarray = ['mythic', 'legendary', 'dark', 'slurp', 'starwars', 'marvel', 'lava', 'frozen', 'gaminglegends', 'shadow', 'icon', 'dc', 'epic', 'rare', 'uncommon', 'common']
    arr.sort(key=lambda x: sortarray.index(x.rarity_value))

    # had some issues with exclusives rendering in wrong order, so i'm sorting them
    try:
        with open('exclusive.txt', 'r', encoding='utf-8') as f:
            exclusive_cosmetics = [i.strip() for i in f.readlines()]
        
        with open('most_wanted.txt', 'r', encoding='utf-8') as f:
            popular_cosmetics = [i.strip() for i in f.readlines()]
    except FileNotFoundError:
        print("Error: 'exclusive.txt' or 'most_wanted.txt' not found.")
        exclusive_cosmetics = []
        popular_cosmetics = []

    mythic_items = [item for item in arr if item.rarity_value == 'mythic']
    other_items = [item for item in arr if item.rarity_value != 'mythic']
    mythic_items.sort(
        key=lambda x: exclusive_cosmetics.index(x.cosmetic_id) 
        if x.cosmetic_id in exclusive_cosmetics else float('inf')
    )
        
    if header == "Popular":
        other_items.sort(
            key=lambda x: popular_cosmetics.index(x.cosmetic_id) 
            if x.cosmetic_id in popular_cosmetics else float('inf')
        )
        
    arr = mythic_items + other_items
    draw = ImageDraw.Draw(image)

    # top
    icon_logo = Image.open(f'cosmetic_icons/{header}.png')
    icon_logo.thumbnail((thumbnail_width, thumbnail_height)) 
    image.paste(icon_logo, (5, 0), mask=icon_logo)
    draw.text((thumbnail_width + 12, 14), '{}'.format(len(arr)), font=ImageFont.truetype(font_path, 70), fill=(0, 0, 0)) # shadow
    draw.text((thumbnail_width + 12, 82), '{}'.format(header), font=ImageFont.truetype(font_path, 40), fill=(0, 0, 0)) # shadow
    draw.text((thumbnail_width + 8, 10), '{}'.format(len(arr)), font=ImageFont.truetype(font_path, 70), fill=(255, 255, 255))
    draw.text((thumbnail_width + 8, 78), '{}'.format(header), font=ImageFont.truetype(font_path, 40), fill=(200, 200, 200))
        
    special_items = {
        "CID_029_Athena_Commando_F_Halloween": "cache/pink_ghoul.png",
        "CID_030_Athena_Commando_M_Halloween": "cache/purple_skull.png",
        "CID_116_Athena_Commando_M_CarbideBlack": "cache/omega_max.png",
        "CID_694_Athena_Commando_M_CatBurglar": "cache/gold_midas.png",
        "CID_693_Athena_Commando_M_BuffCat": "cache/gold_cat.png",
        "CID_691_Athena_Commando_F_TNTina": "cache/gold_tntina.png",
        "CID_690_Athena_Commando_F_Photographer": "cache/gold_skye.png",
        "CID_701_Athena_Commando_M_BananaAgent": "cache/gold_peely.png",
        "CID_315_Athena_Commando_M_TeriyakiFish": "cache/worldcup_fish.png",
        "CID_971_Athena_Commando_M_Jupiter_S0Z6M": "cache/black_masterchief.png",
        "CID_028_Athena_Commando_F": "cache/og_rene.png",
        "CID_017_Athena_Commando_M": "cache/og_aat.png"
    }
        
    for cosmetic in arr:
        special_icon = False
        is_banner = cosmetic.is_banner
        photo = None
        if cosmetic.rarity_value.lower() == "mythic" and cosmetic.cosmetic_id in special_items:
            special_icon = True
            icon_path = special_items[cosmetic.cosmetic_id]
            if os.path.exists(icon_path):
                try:
                    photo = Image.open(icon_path)
                except Exception as e:
                    special_icon = False
            else:
                special_icon = False
        else:
            photo = fortnite_cache.get_cosmetic_icon_from_cache(cosmetic.small_icon, cosmetic.cosmetic_id)
            
        if is_banner:
            scaled_width = int(photo.width * 1.5)
            scaled_height = int(photo.height * 1.5)
            photo = photo.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
            x_offset = 32
            y_offset = 10
                
            new_img = Image.open(f'styles/exo/rarity/{cosmetic.rarity_value.lower()}.png').convert('RGBA')
            new_img.paste(photo, (x_offset, y_offset), mask=photo)
            photo = new_img
            photo.thumbnail((thumbnail_width, thumbnail_height))
        else:
            new_img = Image.open(f'styles/exo/rarity/{cosmetic.rarity_value.lower()}.png').convert('RGBA').resize(photo.size)    
            new_img.paste(photo, mask=photo)
            photo = new_img
            photo.thumbnail((thumbnail_width, thumbnail_height))

        # black box for cosmetic name
        box = Image.new('RGBA', (128, 28), (0, 0, 0, 100))
        photo.paste(box, (0, new_img.size[1] - 28), mask=box)
            
        if header != "Exclusives" and cosmetic.cosmetic_id in popular_cosmetics:
            star_image = Image.open('cosmetic_icons/WantedStar.png').resize((128, 128), Image.BILINEAR)
            photo.paste(star_image, (0, 0), star_image.convert("RGBA"))

        x = thumbnail_width * current_column
        y = thumbnail_width + thumbnail_height * current_row
        image.paste(photo, (x, y))

        name = cosmetic.name.upper()
        max_text_width = thumbnail_width - 10
        max_text_height = 20
            
        # fixed font size
        font_size = 16
        offset = 9
        while True:
            font = ImageFont.truetype(font_path, font_size)
            bbox = draw.textbbox((0, 0), name, font=font)
            name_width = bbox[2] - bbox[0]
            name_height = bbox[3] - bbox[1]

            if name_width > max_text_width or name_height > max_text_height:
                font_size -= 1
                offset += 0.5
            else:
                break

        # cosmetic name
        bbox = draw.textbbox((0, 0), name, font=font)
        name_width = bbox[2] - bbox[0]
        draw.text((x + (thumbnail_width - name_width) // 2, y + (thumbnail_height - padding + offset)), name, font=font, fill=(255, 255, 255))
            
        # make the cosmetics show ordered in rows(cosmetic_per_row is hardcoded)
        current_column += 1
        if current_column >= cosmetic_per_row:
            current_row += 1
            current_column = 0

    # footer
    current_date = datetime.now().strftime('%B %d, %Y')
    
    # custom logo
    custom_logo_path = f"users/logos/{user_data['ID']}.png"
    if os.path.isfile(custom_logo_path):
        custom_logo = Image.open(custom_logo_path).resize((150, 150), Image.Resampling.BILINEAR)
        image.paste(custom_logo, (10, image_height - 165), mask=custom_logo)
    else:
        # original logo if not found
        logo = Image.open('img/logo.png').resize((150, 150), Image.Resampling.BILINEAR)     
        image.paste(logo, (10, image_height - 165), mask=logo)
    
    draw.text((174, image_height - 40 * 3 - 24), '{}'.format(current_date), font=ImageFont.truetype(font_path, 40), fill=(0, 0, 0)) # shadow
    draw.text((170, image_height - 40 * 3 - 28), '{}'.format(current_date), font=ImageFont.truetype(font_path, 40), fill=(255, 255, 255))
    draw.text((174, image_height - 40 * 2 - 24), '@{}'.format(user_data['username']), font=ImageFont.truetype(font_path, 40), fill=(0, 0, 0)) # shadow
    draw_gradient_text(user_data['gradient_type'], draw, (170, image_height - 40 * 2 - 28), '@{}'.format(user_data['username']), font=ImageFont.truetype(font_path, 40))
    # badges
    font_size = 40
    font = ImageFont.truetype(font_path, font_size)
    username_width = font.getbbox(f"@{user_data['username']}")[2]
    offset_badge = 170 + username_width + 8

    if user_data['epic_badge_active'] == True and user_data['epic_badge'] == True:
        # epic games badge(special people only)
        alpha_badge = Image.open('badges/epic.png').resize((40, 40), Image.BILINEAR)
        image.paste(alpha_badge, (offset_badge, image_height - 40 * 2 - 28), alpha_badge.convert("RGBA"))
        offset_badge += 45

    if user_data['alpha_tester_3_badge_active'] == True and user_data['alpha_tester_3_badge'] == True:
        # alpha tester 3 badge
        alpha_badge = Image.open('badges/alpha3.png').resize((40, 40), Image.BILINEAR)
        image.paste(alpha_badge, (offset_badge, image_height - 40 * 2 - 28), alpha_badge.convert("RGBA"))
        offset_badge += 45
        
    if user_data['alpha_tester_2_badge_active'] == True and user_data['alpha_tester_2_badge'] == True:
        # alpha tester 2 badge
        alpha_badge = Image.open('badges/alpha2.png').resize((40, 40), Image.BILINEAR)
        image.paste(alpha_badge, (offset_badge, image_height - 40 * 2 - 28), alpha_badge.convert("RGBA"))
        offset_badge += 45
        
    if user_data['alpha_tester_1_badge_active'] == True and user_data['alpha_tester_1_badge'] == True:
        # alpha tester 1 badge
        alpha_badge = Image.open('badges/alpha1.png').resize((40, 40), Image.BILINEAR)
        image.paste(alpha_badge, (offset_badge, image_height - 40 * 2 - 28), alpha_badge.convert("RGBA"))
        offset_badge += 45

    draw.text((174, image_height - 61), "ExoCheckBot.gg", font=ImageFont.truetype(font_path, 40), fill=(0, 0, 0)) # shadow       
    draw.text((170, image_height - 65), "ExoCheckBot.gg", font=ImageFont.truetype(font_path, 40), fill=(255, 255, 255))
    image.save(nametosave)

def render_easy_style(header:str, user_data: json, arr: list[str], nametosave:str) -> None:
    # calculating cosmetics per row
    cosmetic_per_row = 6
    total_cosmetics = len(arr)
    num_rows = math.ceil(total_cosmetics / cosmetic_per_row)
    if total_cosmetics > 30:
        num_rows = int(math.sqrt(total_cosmetics))
        cosmetic_per_row = math.ceil(total_cosmetics / num_rows)
        
        while cosmetic_per_row * num_rows < total_cosmetics:
            num_rows += 1
            cosmetic_per_row = math.ceil(total_cosmetics / num_rows)

    # setup for our image, thumbnails
    padding_height = 10
    padding_width = 50
    thumbnail_width = 128
    thumbnail_height = 128
    image_width = int(cosmetic_per_row * thumbnail_width + padding_width * 2)
    image_height = int(padding_width + (padding_height + thumbnail_width) * num_rows + padding_width * 2)
    font_path = 'styles/easy/font.ttf'
    font_size = 16
    font = ImageFont.truetype(font_path, font_size)
    image = Image.new('RGB', (image_width, image_height), (58, 58, 58))

    current_row = 0
    current_column = 0
    sortarray = ['mythic', 'legendary', 'dark', 'slurp', 'starwars', 'marvel', 'lava', 'frozen', 'gaminglegends', 'shadow', 'icon', 'dc', 'epic', 'rare', 'uncommon', 'common']
    arr.sort(key=lambda x: sortarray.index(x.rarity_value))

    # had some issues with exclusives rendering in wrong order, so i'm sorting them
    try:
        with open('exclusive.txt', 'r', encoding='utf-8') as f:
            exclusive_cosmetics = [i.strip() for i in f.readlines()]
        
        with open('most_wanted.txt', 'r', encoding='utf-8') as f:
            popular_cosmetics = [i.strip() for i in f.readlines()]
    except FileNotFoundError:
        print("Error: 'exclusive.txt' or 'most_wanted.txt' not found.")
        exclusive_cosmetics = []
        popular_cosmetics = []

    mythic_items = [item for item in arr if item.rarity_value == 'mythic']
    other_items = [item for item in arr if item.rarity_value != 'mythic']
    mythic_items.sort(
        key=lambda x: exclusive_cosmetics.index(x.cosmetic_id) 
        if x.cosmetic_id in exclusive_cosmetics else float('inf')
    )
        
    if header == "Popular":
        other_items.sort(
            key=lambda x: popular_cosmetics.index(x.cosmetic_id) 
            if x.cosmetic_id in popular_cosmetics else float('inf')
        )
        
    arr = mythic_items + other_items
    draw = ImageDraw.Draw(image)

    # cosmetics count
    cosmetics = '{} count: {}'.format(header, len(arr))
    max_text_width = image_width - 20
    max_text_height = 40
    min_font_size = 10
            
    font_size = 40
    while True:
        bbox = draw.textbbox((0, 0), cosmetics, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        if text_width > max_text_width or font_size > image_height - 2:
            font_size -= 1
            if font_size < min_font_size:
                font_size = min_font_size
                break
            font = ImageFont.truetype(font_path, font_size)
        else:
            break


    font = ImageFont.truetype(font_path, font_size)
    bbox = draw.textbbox((0, 0), cosmetics, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (image_width - text_width) // 2
    draw.text((text_x, 9), cosmetics, font=font, fill=(255, 255, 255))
        
    special_items = {
        "CID_029_Athena_Commando_F_Halloween": "cache/pink_ghoul.png",
        "CID_030_Athena_Commando_M_Halloween": "cache/purple_skull_old.png",
        "CID_116_Athena_Commando_M_CarbideBlack": "cache/omega_max.png",
        "CID_694_Athena_Commando_M_CatBurglar": "cache/gold_midas.png",
        "CID_693_Athena_Commando_M_BuffCat": "cache/gold_cat.png",
        "CID_691_Athena_Commando_F_TNTina": "cache/gold_tntina.png",
        "CID_690_Athena_Commando_F_Photographer": "cache/gold_skye.png",
        "CID_701_Athena_Commando_M_BananaAgent": "cache/gold_peely.png",
        "CID_315_Athena_Commando_M_TeriyakiFish": "cache/worldcup_fish.png",
        "CID_971_Athena_Commando_M_Jupiter_S0Z6M": "cache/black_masterchief.png",
        "CID_028_Athena_Commando_F": "cache/og_rene.png",
        "CID_017_Athena_Commando_M": "cache/og_aat.png"
    }
        
    for cosmetic in arr:
        special_icon = False
        is_banner = cosmetic.is_banner
        photo = None
        if cosmetic.rarity_value.lower() == "mythic" and cosmetic.cosmetic_id in special_items:
            special_icon = True
            icon_path = special_items[cosmetic.cosmetic_id]
            if os.path.exists(icon_path):
                try:
                    photo = Image.open(icon_path)
                except Exception as e:
                    special_icon = False
            else:
                special_icon = False
        else:
            photo = fortnite_cache.get_cosmetic_icon_from_cache(cosmetic.small_icon, cosmetic.cosmetic_id)
            
        if is_banner:
            scaled_width = int(photo.width * 1.5)
            scaled_height = int(photo.height * 1.5)
            photo = photo.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
            x_offset = 32
            y_offset = 10
                
            new_img = Image.open(f'styles/easy/rarity/{cosmetic.rarity_value.lower()}.png').convert('RGBA')
            new_img.paste(photo, (x_offset, y_offset), mask=photo)
            photo = new_img
            photo.thumbnail((thumbnail_width, thumbnail_height))
        else:
            new_img = Image.open(f'styles/easy/rarity/{cosmetic.rarity_value.lower()}.png').convert('RGBA').resize(photo.size)    
            new_img.paste(photo, mask=photo)
            photo = new_img
            photo.thumbnail((thumbnail_width, thumbnail_height))

        # black box for cosmetic name
        box = Image.new('RGBA', (128, 20), (0, 0, 0, 75))
        photo.paste(box, (0, new_img.size[1] - 40), mask=box)
        
        border = Image.open(f'styles/easy/border/{cosmetic.rarity_value.lower()}.png').convert('RGBA').resize(photo.size)    
        photo.paste(border, mask=border)
        
        x = padding_width + thumbnail_width * current_column
        y = padding_width + (thumbnail_height + padding_height) * current_row
        image.paste(photo, (x, y))

        name = cosmetic.name
        max_text_width = thumbnail_width - 10
        max_text_height = 20
        offset_y = 38
        font_size = 18
        while True:
            font = ImageFont.truetype(font_path, font_size)
            bbox = draw.textbbox((0, 0), name, font=font)
            name_width = bbox[2] - bbox[0]
            name_height = bbox[3] - bbox[1]

            if name_width > max_text_width or name_height > max_text_height:
                font_size -= 1
                offset_y -= 0.5
            else:
                break

        # cosmetic name
        bbox = draw.textbbox((0, 0), name, font=font)
        name_width = bbox[2] - bbox[0]
        draw.text((x + (thumbnail_width - name_width) // 2, y + (thumbnail_height - offset_y)), name, font=font, fill=(255, 255, 255))
            
        # make the cosmetics show ordered in rows(cosmetic_per_row is hardcoded)
        current_column += 1
        if current_column >= cosmetic_per_row:
            current_row += 1
            current_column = 0

    # footer
    current_date = datetime.now().strftime('%d/%m/%Y')
    footer = 'Submitted by @{} on {}'.format(user_data['username'], current_date)
    max_text_width = image_width - 20
    max_text_height = 40
    min_font_size = 15
            
    font_size = 40
    while True:
        bbox = draw.textbbox((0, 0), footer, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        if text_width > max_text_width or font_size > image_height - 2:
            font_size -= 1
            if font_size < min_font_size:
                font_size = min_font_size
                break
            
            font = ImageFont.truetype(font_path, font_size)
        else:
            break
        
    font = ImageFont.truetype(font_path, font_size)
    bbox = draw.textbbox((0, 0), footer, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (image_width - text_width) // 2
    text_y = image_height - font_size - 52
    draw.text((text_x, text_y), footer, font=font, fill=(255, 255, 255))
    
    # bot advertisment
    footer2 = 'ExoCheckBot.gg'
    max_text_width = image_width - 20
    max_text_height = 40
    min_font_size = 15
            
    font_size = 40
    while True:
        bbox = draw.textbbox((0, 0), footer2, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        if text_width > max_text_width or font_size > image_height - 2:
            font_size -= 1
            if font_size < min_font_size:
                font_size = min_font_size
                break
            
            font = ImageFont.truetype(font_path, font_size)
        else:
            break


    font = ImageFont.truetype(font_path, font_size)
    bbox = draw.textbbox((0, 0), footer2, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (image_width - text_width) // 2
    text_y = image_height - font_size - 8
    draw.text((text_x, text_y), footer2, font=font, fill=(255, 255, 255))
     
    image.save(nametosave)

def render_raika_style(header:str, user_data: json, arr: list[str], nametosave:str) -> None:
    # calculating cosmetics per row
    cosmetic_per_row = 6
    total_cosmetics = len(arr)
    num_rows = math.ceil(total_cosmetics / cosmetic_per_row)
    if total_cosmetics > 30:
        num_rows = int(math.sqrt(total_cosmetics))
        cosmetic_per_row = math.ceil(total_cosmetics / num_rows)
        
        while cosmetic_per_row * num_rows < total_cosmetics:
            num_rows += 1
            cosmetic_per_row = math.ceil(total_cosmetics / num_rows)

    # setup for our image, thumbnails
    padding = 30
    thumbnail_width = 128
    thumbnail_height = 128
    image_width = int(cosmetic_per_row * thumbnail_width)
    image_height = int(thumbnail_height + 5 + thumbnail_width * num_rows + 180)
    font_path = 'styles/raika/font.ttf'
    font_size = 16
    font = ImageFont.truetype(font_path, font_size)
    image = Image.new('RGB', (image_width, image_height), (0, 0, 0))
    
    # custom background
    custom_background_path = f"users/backgrounds/{user_data['ID']}.png"
    if os.path.isfile(custom_background_path):
        custom_background = Image.open(custom_background_path).resize((image_width, image_height), Image.Resampling.BILINEAR)
        image.paste(custom_background, (0, 0))
        
    current_row = 0
    current_column = 0
    sortarray = ['mythic', 'legendary', 'dark', 'slurp', 'starwars', 'marvel', 'lava', 'frozen', 'gaminglegends', 'shadow', 'icon', 'dc', 'epic', 'rare', 'uncommon', 'common']
    arr.sort(key=lambda x: sortarray.index(x.rarity_value))

    # had some issues with exclusives rendering in wrong order, so i'm sorting them
    try:
        with open('exclusive.txt', 'r', encoding='utf-8') as f:
            exclusive_cosmetics = [i.strip() for i in f.readlines()]
        
        with open('most_wanted.txt', 'r', encoding='utf-8') as f:
            popular_cosmetics = [i.strip() for i in f.readlines()]
    except FileNotFoundError:
        print("Error: 'exclusive.txt' or 'most_wanted.txt' not found.")
        exclusive_cosmetics = []
        popular_cosmetics = []

    mythic_items = [item for item in arr if item.rarity_value == 'mythic']
    other_items = [item for item in arr if item.rarity_value != 'mythic']
    mythic_items.sort(
        key=lambda x: exclusive_cosmetics.index(x.cosmetic_id) 
        if x.cosmetic_id in exclusive_cosmetics else float('inf')
    )
        
    if header == "Popular":
        other_items.sort(
            key=lambda x: popular_cosmetics.index(x.cosmetic_id) 
            if x.cosmetic_id in popular_cosmetics else float('inf')
        )
        
    arr = mythic_items + other_items
    draw = ImageDraw.Draw(image)

    # top
    icon_logo = Image.open(f'cosmetic_icons/{header}.png')
    icon_logo.thumbnail((thumbnail_width, thumbnail_height)) 
    image.paste(icon_logo, (5, 0), mask=icon_logo)
    draw.text((thumbnail_width + 12, 14), '{}'.format(len(arr)), font=ImageFont.truetype(font_path, 70), fill=(0, 0, 0)) # shadow
    draw.text((thumbnail_width + 12, 82), '{}'.format(header), font=ImageFont.truetype(font_path, 40), fill=(0, 0, 0)) # shadow
    draw.text((thumbnail_width + 8, 10), '{}'.format(len(arr)), font=ImageFont.truetype(font_path, 70), fill=(255, 255, 255))
    draw.text((thumbnail_width + 8, 78), '{}'.format(header), font=ImageFont.truetype(font_path, 40), fill=(200, 200, 200))
        
    special_items = {
        "CID_029_Athena_Commando_F_Halloween": "cache/pink_ghoul.png",
        "CID_030_Athena_Commando_M_Halloween": "cache/purple_skull_old.png",
        "CID_116_Athena_Commando_M_CarbideBlack": "cache/omega_max.png",
        "CID_694_Athena_Commando_M_CatBurglar": "cache/gold_midas.png",
        "CID_693_Athena_Commando_M_BuffCat": "cache/gold_cat.png",
        "CID_691_Athena_Commando_F_TNTina": "cache/gold_tntina.png",
        "CID_690_Athena_Commando_F_Photographer": "cache/gold_skye.png",
        "CID_701_Athena_Commando_M_BananaAgent": "cache/gold_peely.png",
        "CID_315_Athena_Commando_M_TeriyakiFish": "cache/worldcup_fish.png",
        "CID_971_Athena_Commando_M_Jupiter_S0Z6M": "cache/black_masterchief.png",
        "CID_028_Athena_Commando_F": "cache/og_rene.png",
        "CID_017_Athena_Commando_M": "cache/og_aat.png"
    }
        
    for cosmetic in arr:
        special_icon = False
        is_banner = cosmetic.is_banner
        photo = None
        if cosmetic.rarity_value.lower() == "mythic" and cosmetic.cosmetic_id in special_items:
            special_icon = True
            icon_path = special_items[cosmetic.cosmetic_id]
            if os.path.exists(icon_path):
                try:
                    photo = Image.open(icon_path)
                except Exception as e:
                    special_icon = False
            else:
                special_icon = False
        else:
            photo = fortnite_cache.get_cosmetic_icon_from_cache(cosmetic.small_icon, cosmetic.cosmetic_id)
            
        if is_banner:
            scaled_width = int(photo.width * 1.5)
            scaled_height = int(photo.height * 1.5)
            photo = photo.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
            x_offset = 32
            y_offset = 10
                
            new_img = Image.open(f'styles/raika/rarity/{cosmetic.rarity_value.lower()}.png').convert('RGBA')
            new_img.paste(photo, (x_offset, y_offset), mask=photo)
            photo = new_img
            photo.thumbnail((thumbnail_width, thumbnail_height))
        else:
            new_img = Image.open(f'styles/raika/rarity/{cosmetic.rarity_value.lower()}.png').convert('RGBA').resize(photo.size)    
            new_img.paste(photo, mask=photo)
            photo = new_img
            photo.thumbnail((thumbnail_width, thumbnail_height))

        # black box for cosmetic name
        box = Image.new('RGBA', (128, 28), (0, 0, 0, 100))
        photo.paste(box, (0, new_img.size[1] - 28), mask=box)
            
        if header != "Exclusives" and cosmetic.cosmetic_id in popular_cosmetics:
            star_image = Image.open('cosmetic_icons/WantedStar.png').resize((128, 128), Image.BILINEAR)
            photo.paste(star_image, (0, 0), star_image.convert("RGBA"))

        x = thumbnail_width * current_column
        y = thumbnail_width + thumbnail_height * current_row
        image.paste(photo, (x, y))

        name = cosmetic.name.upper()
        max_text_width = thumbnail_width - 10
        max_text_height = 20
            
        # fixed font size
        font_size = 16
        offset = 6
        while True:
            font = ImageFont.truetype(font_path, font_size)
            bbox = draw.textbbox((0, 0), name, font=font)
            name_width = bbox[2] - bbox[0]
            name_height = bbox[3] - bbox[1]

            if name_width > max_text_width or name_height > max_text_height:
                font_size -= 1
                offset += 0.5
            else:
                break

        # cosmetic name
        bbox = draw.textbbox((0, 0), name, font=font)
        name_width = bbox[2] - bbox[0]
        draw.text((x + (thumbnail_width - name_width) // 2, y + (thumbnail_height - padding + offset)), name, font=font, fill=(255, 255, 255))
            
        # make the cosmetics show ordered in rows(cosmetic_per_row is hardcoded)
        current_column += 1
        if current_column >= cosmetic_per_row:
            current_row += 1
            current_column = 0

    # footer
    current_date = datetime.now().strftime('%B %d, %Y')
    
    # custom logo
    custom_logo_path = f"users/logos/{user_data['ID']}.png"
    if os.path.isfile(custom_logo_path):
        custom_logo = Image.open(custom_logo_path).resize((150, 150), Image.Resampling.BILINEAR)
        image.paste(custom_logo, (10, image_height - 165), mask=custom_logo)
    else:
        # original logo if not found
        logo = Image.open('img/logo.png').resize((150, 150), Image.Resampling.BILINEAR)     
        image.paste(logo, (10, image_height - 165), mask=logo)

    draw.text((174, image_height - 40 * 3 - 24), '{}'.format(current_date), font=ImageFont.truetype(font_path, 40), fill=(0, 0, 0)) # shadow
    draw.text((170, image_height - 40 * 3 - 28), '{}'.format(current_date), font=ImageFont.truetype(font_path, 40), fill=(255, 255, 255))  
    draw.text((174, image_height - 40 * 2 - 24), '@{}'.format(user_data['username']), font=ImageFont.truetype(font_path, 40), fill=(0, 0, 0)) # shadow 
    draw_gradient_text(user_data['gradient_type'], draw, (170, image_height - 40 * 2 - 28), '@{}'.format(user_data['username']), font=ImageFont.truetype(font_path, 40))
        
    # badges
    font_size = 40
    font = ImageFont.truetype(font_path, font_size)
    username_width = font.getbbox(f"@{user_data['username']}")[2]
    offset_badge = 170 + username_width + 8

    if user_data['epic_badge_active'] == True and user_data['epic_badge'] == True:
        # epic games badge(special people only)
        alpha_badge = Image.open('badges/epic.png').resize((40, 40), Image.BILINEAR)
        image.paste(alpha_badge, (offset_badge, image_height - 40 * 2 - 28), alpha_badge.convert("RGBA"))
        offset_badge += 45

    if user_data['alpha_tester_3_badge_active'] == True and user_data['alpha_tester_3_badge'] == True:
        # alpha tester 3 badge
        alpha_badge = Image.open('badges/alpha3.png').resize((40, 40), Image.BILINEAR)
        image.paste(alpha_badge, (offset_badge, image_height - 40 * 2 - 28), alpha_badge.convert("RGBA"))
        offset_badge += 45
        
    if user_data['alpha_tester_2_badge_active'] == True and user_data['alpha_tester_2_badge'] == True:
        # alpha tester 2 badge
        alpha_badge = Image.open('badges/alpha2.png').resize((40, 40), Image.BILINEAR)
        image.paste(alpha_badge, (offset_badge, image_height - 40 * 2 - 28), alpha_badge.convert("RGBA"))
        offset_badge += 45
        
    if user_data['alpha_tester_1_badge_active'] == True and user_data['alpha_tester_1_badge'] == True:
        # alpha tester 1 badge
        alpha_badge = Image.open('badges/alpha1.png').resize((40, 40), Image.BILINEAR)
        image.paste(alpha_badge, (offset_badge, image_height - 40 * 2 - 28), alpha_badge.convert("RGBA"))
        offset_badge += 45
   
    draw.text((174, image_height - 61), "ExoCheckBot.gg", font=ImageFont.truetype(font_path, 40), fill=(0, 0, 0)) # shadow     
    draw.text((170, image_height - 65), "ExoCheckBot.gg", font=ImageFont.truetype(font_path, 40), fill=(255, 255, 255))
    image.save(nametosave)
    
def render_kayy_style(header:str, user_data: json, arr: list[str], nametosave:str) -> None:
    # calculating cosmetics per row
    cosmetic_per_row = 6
    total_cosmetics = len(arr)
    num_rows = math.ceil(total_cosmetics / cosmetic_per_row)
    if total_cosmetics > 30:
        num_rows = int(math.sqrt(total_cosmetics))
        cosmetic_per_row = math.ceil(total_cosmetics / num_rows)
        
        while cosmetic_per_row * num_rows < total_cosmetics:
            num_rows += 1
            cosmetic_per_row = math.ceil(total_cosmetics / num_rows)

    # setup for our image, thumbnails
    padding = 30
    thumbnail_width = 128
    thumbnail_height = 128
    image_width = int(cosmetic_per_row * thumbnail_width)
    image_height = int(thumbnail_width * num_rows + 180)
    font_path = 'styles/kayy/font.ttf'
    font_size = 16
    font = ImageFont.truetype(font_path, font_size)
    image = Image.new('RGB', (image_width, image_height), (0, 0, 0))
    
    # custom background
    custom_background_path = f"users/backgrounds/{user_data['ID']}.png"
    if os.path.isfile(custom_background_path):
        custom_background = Image.open(custom_background_path).resize((image_width, image_height), Image.Resampling.BILINEAR)
        image.paste(custom_background, (0, 0))
        
    current_row = 0
    current_column = 0
    sortarray = ['mythic', 'legendary', 'dark', 'slurp', 'starwars', 'marvel', 'lava', 'frozen', 'gaminglegends', 'shadow', 'icon', 'dc', 'epic', 'rare', 'uncommon', 'common']
    arr.sort(key=lambda x: sortarray.index(x.rarity_value))

    # had some issues with exclusives rendering in wrong order, so i'm sorting them
    try:
        with open('exclusive.txt', 'r', encoding='utf-8') as f:
            exclusive_cosmetics = [i.strip() for i in f.readlines()]
        
        with open('most_wanted.txt', 'r', encoding='utf-8') as f:
            popular_cosmetics = [i.strip() for i in f.readlines()]
    except FileNotFoundError:
        print("Error: 'exclusive.txt' or 'most_wanted.txt' not found.")
        exclusive_cosmetics = []
        popular_cosmetics = []

    mythic_items = [item for item in arr if item.rarity_value == 'mythic']
    other_items = [item for item in arr if item.rarity_value != 'mythic']
    mythic_items.sort(
        key=lambda x: exclusive_cosmetics.index(x.cosmetic_id) 
        if x.cosmetic_id in exclusive_cosmetics else float('inf')
    )
        
    if header == "Popular":
        other_items.sort(
            key=lambda x: popular_cosmetics.index(x.cosmetic_id) 
            if x.cosmetic_id in popular_cosmetics else float('inf')
        )
        
    arr = mythic_items + other_items
    draw = ImageDraw.Draw(image)

    special_items = {
        "CID_029_Athena_Commando_F_Halloween": "cache/pink_ghoul.png",
        "CID_030_Athena_Commando_M_Halloween": "cache/purple_skull_old.png",
        "CID_116_Athena_Commando_M_CarbideBlack": "cache/omega_max.png",
        "CID_694_Athena_Commando_M_CatBurglar": "cache/gold_midas.png",
        "CID_693_Athena_Commando_M_BuffCat": "cache/gold_cat.png",
        "CID_691_Athena_Commando_F_TNTina": "cache/gold_tntina.png",
        "CID_690_Athena_Commando_F_Photographer": "cache/gold_skye.png",
        "CID_701_Athena_Commando_M_BananaAgent": "cache/gold_peely.png",
        "CID_315_Athena_Commando_M_TeriyakiFish": "cache/worldcup_fish.png",
        "CID_971_Athena_Commando_M_Jupiter_S0Z6M": "cache/black_masterchief.png",
        "CID_028_Athena_Commando_F": "cache/og_rene.png",
        "CID_017_Athena_Commando_M": "cache/og_aat.png"
    }
        
    for cosmetic in arr:
        special_icon = False
        is_banner = cosmetic.is_banner
        photo = None
        if cosmetic.rarity_value.lower() == "mythic" and cosmetic.cosmetic_id in special_items:
            special_icon = True
            icon_path = special_items[cosmetic.cosmetic_id]
            if os.path.exists(icon_path):
                try:
                    photo = Image.open(icon_path)
                except Exception as e:
                    special_icon = False
            else:
                special_icon = False
        else:
            photo = fortnite_cache.get_cosmetic_icon_from_cache(cosmetic.small_icon, cosmetic.cosmetic_id)
            
        if is_banner:
            scaled_width = int(photo.width * 1.5)
            scaled_height = int(photo.height * 1.5)
            photo = photo.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
            x_offset = 32
            y_offset = 10
                
            new_img = Image.open(f'styles/kayy/rarity/{cosmetic.rarity_value.lower()}.png').convert('RGBA')
            new_img.paste(photo, (x_offset, y_offset), mask=photo)
            photo = new_img
            photo.thumbnail((thumbnail_width, thumbnail_height))
        else:
            new_img = Image.open(f'styles/kayy/rarity/{cosmetic.rarity_value.lower()}.png').convert('RGBA').resize(photo.size)    
            new_img.paste(photo, mask=photo)
            photo = new_img
            photo.thumbnail((thumbnail_width, thumbnail_height))

        # black box for cosmetic name
        box = Image.new('RGBA', (128, 28), (0, 0, 0, 100))
        photo.paste(box, (0, new_img.size[1] - 28), mask=box)
            
        if header != "Exclusives" and cosmetic.cosmetic_id in popular_cosmetics:
            star_image = Image.open('cosmetic_icons/WantedStar.png').resize((128, 128), Image.BILINEAR)
            photo.paste(star_image, (0, 0), star_image.convert("RGBA"))

        x = thumbnail_width * current_column
        y = thumbnail_height * current_row
        image.paste(photo, (x, y))

        name = cosmetic.name.upper()
        max_text_width = thumbnail_width - 10
        max_text_height = 20
            
        # fixed font size
        font_size = 16
        offset = 9
        while True:
            font = ImageFont.truetype(font_path, font_size)
            bbox = draw.textbbox((0, 0), name, font=font)
            name_width = bbox[2] - bbox[0]
            name_height = bbox[3] - bbox[1]

            if name_width > max_text_width or name_height > max_text_height:
                font_size -= 1
                offset += 0.5
            else:
                break

        # cosmetic name
        bbox = draw.textbbox((0, 0), name, font=font)
        name_width = bbox[2] - bbox[0]
        draw.text((x + (thumbnail_width - name_width) // 2, y + (thumbnail_height - padding + offset)), name, font=font, fill=(255, 255, 255))
            
        # make the cosmetics show ordered in rows(cosmetic_per_row is hardcoded)
        current_column += 1
        if current_column >= cosmetic_per_row:
            current_row += 1
            current_column = 0

    # footer
    current_date = datetime.now().strftime('%d/%m/%Y')
    
    # custom logo
    custom_logo_path = f"users/logos/{user_data['ID']}.png"
    if os.path.isfile(custom_logo_path):
        custom_logo = Image.open(custom_logo_path).resize((150, 150), Image.Resampling.BILINEAR)
        image.paste(custom_logo, (10, image_height - 165), mask=custom_logo)
    else:
        # original logo if not found
        logo = Image.open('img/logo.png').resize((150, 150), Image.Resampling.BILINEAR)     
        image.paste(logo, (10, image_height - 165), mask=logo)

    draw.text((174, image_height - 40 * 3 - 24), 'Objects Total: {}'.format(len(arr)), font=ImageFont.truetype(font_path, 40), fill=(255, 255, 255)) # shadow
    draw.text((170, image_height - 40 * 3 - 28), 'Objects Total: {}'.format(len(arr)), font=ImageFont.truetype(font_path, 40), fill=(255, 255, 255))
    draw.text((174, image_height - 40 * 2 - 24), '@{}'.format(user_data['username']), font=ImageFont.truetype(font_path, 40), fill=(255, 255, 255)) # shadow
    draw_gradient_text(user_data['gradient_type'], draw, (170, image_height - 40 * 2 - 28), '@{}'.format(user_data['username']), font=ImageFont.truetype(font_path, 40))
        
    # badges
    font_size = 40
    font = ImageFont.truetype(font_path, font_size)
    username_width = font.getbbox(f"@{user_data['username']}")[2]
    offset_badge = 170 + username_width + 8

    if user_data['epic_badge_active'] == True and user_data['epic_badge'] == True:
        # epic games badge(special people only)
        alpha_badge = Image.open('badges/epic.png').resize((40, 40), Image.BILINEAR)
        image.paste(alpha_badge, (offset_badge, image_height - 40 * 2 - 28), alpha_badge.convert("RGBA"))
        offset_badge += 45

    if user_data['alpha_tester_3_badge_active'] == True and user_data['alpha_tester_3_badge'] == True:
        # alpha tester 3 badge
        alpha_badge = Image.open('badges/alpha3.png').resize((40, 40), Image.BILINEAR)
        image.paste(alpha_badge, (offset_badge, image_height - 40 * 2 - 28), alpha_badge.convert("RGBA"))
        offset_badge += 45
        
    if user_data['alpha_tester_2_badge_active'] == True and user_data['alpha_tester_2_badge'] == True:
        # alpha tester 2 badge
        alpha_badge = Image.open('badges/alpha2.png').resize((40, 40), Image.BILINEAR)
        image.paste(alpha_badge, (offset_badge, image_height - 40 * 2 - 28), alpha_badge.convert("RGBA"))
        offset_badge += 45
        
    if user_data['alpha_tester_1_badge_active'] == True and user_data['alpha_tester_1_badge'] == True:
        # alpha tester 1 badge
        alpha_badge = Image.open('badges/alpha1.png').resize((40, 40), Image.BILINEAR)
        image.paste(alpha_badge, (offset_badge, image_height - 40 * 2 - 28), alpha_badge.convert("RGBA"))
        offset_badge += 45
     
    draw.text((offset_badge + 10, image_height - 40 * 2 - 26), '| {}'.format(current_date), font=ImageFont.truetype(font_path, 40), fill=(0, 0, 0)) # shadow   
    draw.text((offset_badge + 8, image_height - 40 * 2 - 28), '| {}'.format(current_date), font=ImageFont.truetype(font_path, 40), fill=(255, 255, 255))
    draw.text((174, image_height - 61), "ExoCheckBot.gg", font=ImageFont.truetype(font_path, 40), fill=(0, 0, 0)) # shadow
    draw.text((170, image_height - 65), "ExoCheckBot.gg", font=ImageFont.truetype(font_path, 40), fill=(255, 255, 255))
    image.save(nametosave)   
    
def render_storm_style(header:str, user_data: json, arr: list[str], nametosave:str) -> None:
    # calculating cosmetics per row
    cosmetic_per_row = 6
    total_cosmetics = len(arr)
    num_rows = math.ceil(total_cosmetics / cosmetic_per_row)
    if total_cosmetics > 30:
        num_rows = int(math.sqrt(total_cosmetics))
        cosmetic_per_row = math.ceil(total_cosmetics / num_rows)
        
        while cosmetic_per_row * num_rows < total_cosmetics:
            num_rows += 1
            cosmetic_per_row = math.ceil(total_cosmetics / num_rows)

    # setup for our image, thumbnails
    padding = 30
    thumbnail_width = 128
    thumbnail_height = 128
    image_width = int(cosmetic_per_row * thumbnail_width)
    image_height = int(thumbnail_width * num_rows + 180)
    font_path = 'styles/storm/font.ttf'
    font_size = 16
    font = ImageFont.truetype(font_path, font_size)
    image = Image.new('RGB', (image_width, image_height), (0, 0, 0))
    
    # custom background
    custom_background_path = f"users/backgrounds/{user_data['ID']}.png"
    if os.path.isfile(custom_background_path):
        custom_background = Image.open(custom_background_path).resize((image_width, image_height), Image.Resampling.BILINEAR)
        image.paste(custom_background, (0, 0))
        
    current_row = 0
    current_column = 0
    sortarray = ['mythic', 'legendary', 'dark', 'slurp', 'starwars', 'marvel', 'lava', 'frozen', 'gaminglegends', 'shadow', 'icon', 'dc', 'epic', 'rare', 'uncommon', 'common']
    arr.sort(key=lambda x: sortarray.index(x.rarity_value))

    # had some issues with exclusives rendering in wrong order, so i'm sorting them
    try:
        with open('exclusive.txt', 'r', encoding='utf-8') as f:
            exclusive_cosmetics = [i.strip() for i in f.readlines()]
        
        with open('most_wanted.txt', 'r', encoding='utf-8') as f:
            popular_cosmetics = [i.strip() for i in f.readlines()]
    except FileNotFoundError:
        print("Error: 'exclusive.txt' or 'most_wanted.txt' not found.")
        exclusive_cosmetics = []
        popular_cosmetics = []

    mythic_items = [item for item in arr if item.rarity_value == 'mythic']
    other_items = [item for item in arr if item.rarity_value != 'mythic']
    mythic_items.sort(
        key=lambda x: exclusive_cosmetics.index(x.cosmetic_id) 
        if x.cosmetic_id in exclusive_cosmetics else float('inf')
    )
        
    if header == "Popular":
        other_items.sort(
            key=lambda x: popular_cosmetics.index(x.cosmetic_id) 
            if x.cosmetic_id in popular_cosmetics else float('inf')
        )
        
    arr = mythic_items + other_items
    draw = ImageDraw.Draw(image)

    special_items = {
        "CID_029_Athena_Commando_F_Halloween": "cache/pink_ghoul.png",
        "CID_030_Athena_Commando_M_Halloween": "cache/purple_skull_old.png",
        "CID_116_Athena_Commando_M_CarbideBlack": "cache/omega_max.png",
        "CID_694_Athena_Commando_M_CatBurglar": "cache/gold_midas.png",
        "CID_693_Athena_Commando_M_BuffCat": "cache/gold_cat.png",
        "CID_691_Athena_Commando_F_TNTina": "cache/gold_tntina.png",
        "CID_690_Athena_Commando_F_Photographer": "cache/gold_skye.png",
        "CID_701_Athena_Commando_M_BananaAgent": "cache/gold_peely.png",
        "CID_315_Athena_Commando_M_TeriyakiFish": "cache/worldcup_fish.png",
        "CID_971_Athena_Commando_M_Jupiter_S0Z6M": "cache/black_masterchief.png",
        "CID_028_Athena_Commando_F": "cache/og_rene.png",
        "CID_017_Athena_Commando_M": "cache/og_aat.png"
    }
        
    for cosmetic in arr:
        special_icon = False
        is_banner = cosmetic.is_banner
        photo = None
        if cosmetic.rarity_value.lower() == "mythic" and cosmetic.cosmetic_id in special_items:
            special_icon = True
            icon_path = special_items[cosmetic.cosmetic_id]
            if os.path.exists(icon_path):
                try:
                    photo = Image.open(icon_path)
                except Exception as e:
                    special_icon = False
            else:
                special_icon = False
        else:
            photo = fortnite_cache.get_cosmetic_icon_from_cache(cosmetic.small_icon, cosmetic.cosmetic_id)
            
        if is_banner:
            scaled_width = int(photo.width * 1.5)
            scaled_height = int(photo.height * 1.5)
            photo = photo.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
            x_offset = 32
            y_offset = 10
                
            new_img = Image.open(f'styles/storm/rarity/{cosmetic.rarity_value.lower()}.png').convert('RGBA')
            new_img.paste(photo, (x_offset, y_offset), mask=photo)
            photo = new_img
            photo.thumbnail((thumbnail_width, thumbnail_height))
        else:
            new_img = Image.open(f'styles/storm/rarity/{cosmetic.rarity_value.lower()}.png').convert('RGBA').resize(photo.size)    
            new_img.paste(photo, mask=photo)
            photo = new_img
            photo.thumbnail((thumbnail_width, thumbnail_height))

        # black box for cosmetic name
        box = Image.new('RGBA', (128, 28), (0, 0, 0, 100))
        photo.paste(box, (0, new_img.size[1] - 28), mask=box)
            
        if header != "Exclusives" and cosmetic.cosmetic_id in popular_cosmetics:
            star_image = Image.open('cosmetic_icons/WantedStar.png').resize((128, 128), Image.BILINEAR)
            photo.paste(star_image, (0, 0), star_image.convert("RGBA"))

        x = thumbnail_width * current_column
        y = thumbnail_height * current_row
        image.paste(photo, (x, y))

        name = cosmetic.name.upper()
        max_text_width = thumbnail_width - 10
        max_text_height = 20
            
        # fixed font size
        font_size = 16
        offset = 9
        while True:
            font = ImageFont.truetype(font_path, font_size)
            bbox = draw.textbbox((0, 0), name, font=font)
            name_width = bbox[2] - bbox[0]
            name_height = bbox[3] - bbox[1]

            if name_width > max_text_width or name_height > max_text_height:
                font_size -= 1
                offset += 0.5
            else:
                break

        # cosmetic name
        bbox = draw.textbbox((0, 0), name, font=font)
        name_width = bbox[2] - bbox[0]
        draw.text((x + (thumbnail_width - name_width) // 2, y + (thumbnail_height - padding + offset)), name, font=font, fill=(255, 255, 255))
            
        # make the cosmetics show ordered in rows(cosmetic_per_row is hardcoded)
        current_column += 1
        if current_column >= cosmetic_per_row:
            current_row += 1
            current_column = 0

    # footer
    current_date = datetime.now().strftime('%d %B %Y')
    
    # custom logo
    custom_logo_path = f"users/logos/{user_data['ID']}.png"
    if os.path.isfile(custom_logo_path):
        custom_logo = Image.open(custom_logo_path).resize((150, 150), Image.Resampling.BILINEAR)
        image.paste(custom_logo, (10, image_height - 165), mask=custom_logo)
    else:
        # original logo if not found
        logo = Image.open('img/logo.png').resize((150, 150), Image.Resampling.BILINEAR)     
        image.paste(logo, (10, image_height - 165), mask=logo)

    draw.text((174, image_height - 40 * 3 - 24), '{}'.format(current_date), font=ImageFont.truetype(font_path, 40), fill=(0, 0, 0)) # shadow
    draw.text((170, image_height - 40 * 3 - 28), '{}'.format(current_date), font=ImageFont.truetype(font_path, 40), fill=(255, 255, 255))
    draw.text((174, image_height - 40 * 2 - 24), 'Submitted by ', font=ImageFont.truetype(font_path, 40), fill=(0, 0, 0)) # shadow
    draw_gradient_text(0, draw, (170, image_height - 40 * 2 - 28), 'Submitted by ', font=ImageFont.truetype(font_path, 40))
        
    # badges
    font_size = 40
    font = ImageFont.truetype(font_path, font_size)
    submit_width = font.getbbox(f"Submitted by")[2]
    offset_submit = 170 + submit_width + 8
    username_width = font.getbbox(f"Submitted by @{user_data['username']}")[2]
    offset_badge = 170 + username_width + 8

    if user_data['epic_badge_active'] == True and user_data['epic_badge'] == True:
        # epic games badge(special people only)
        alpha_badge = Image.open('badges/epic.png').resize((40, 40), Image.BILINEAR)
        image.paste(alpha_badge, (offset_badge, image_height - 40 * 2 - 28), alpha_badge.convert("RGBA"))
        offset_badge += 45

    if user_data['alpha_tester_3_badge_active'] == True and user_data['alpha_tester_3_badge'] == True:
        # alpha tester 3 badge
        alpha_badge = Image.open('badges/alpha3.png').resize((40, 40), Image.BILINEAR)
        image.paste(alpha_badge, (offset_badge, image_height - 40 * 2 - 28), alpha_badge.convert("RGBA"))
        offset_badge += 45
        
    if user_data['alpha_tester_2_badge_active'] == True and user_data['alpha_tester_2_badge'] == True:
        # alpha tester 2 badge
        alpha_badge = Image.open('badges/alpha2.png').resize((40, 40), Image.BILINEAR)
        image.paste(alpha_badge, (offset_badge, image_height - 40 * 2 - 28), alpha_badge.convert("RGBA"))
        offset_badge += 45
        
    if user_data['alpha_tester_1_badge_active'] == True and user_data['alpha_tester_1_badge'] == True:
        # alpha tester 1 badge
        alpha_badge = Image.open('badges/alpha1.png').resize((40, 40), Image.BILINEAR)
        image.paste(alpha_badge, (offset_badge, image_height - 40 * 2 - 28), alpha_badge.convert("RGBA"))
        offset_badge += 45
      
    draw.text((offset_submit + 2, image_height - 40 * 2 - 26), '@{}'.format(user_data['username']), font=ImageFont.truetype(font_path, 40), fill=(0, 0, 0)) # shadow  
    draw_gradient_text(user_data['gradient_type'], draw, (offset_submit, image_height - 40 * 2 - 28), '@{}'.format(user_data['username']), font=ImageFont.truetype(font_path, 40))
    draw.text((174, image_height - 61), "ExoCheckBot.gg", font=ImageFont.truetype(font_path, 40), fill=(0, 0, 0)) # shadow
    draw.text((170, image_height - 65), "ExoCheckBot.gg", font=ImageFont.truetype(font_path, 40), fill=(255, 255, 255))
    image.save(nametosave)
    
def render_aqua_style(header:str, user_data: json, arr: list[str], nametosave:str) -> None:
    # calculating cosmetics per row
    cosmetic_per_row = 6
    total_cosmetics = len(arr)
    num_rows = math.ceil(total_cosmetics / cosmetic_per_row)
    if total_cosmetics > 30:
        num_rows = int(math.sqrt(total_cosmetics))
        cosmetic_per_row = math.ceil(total_cosmetics / num_rows)
        
        while cosmetic_per_row * num_rows < total_cosmetics:
            num_rows += 1
            cosmetic_per_row = math.ceil(total_cosmetics / num_rows)

    # setup for our image, thumbnails
    padding = 30
    padding_height = 2
    thumbnail_width = 128
    thumbnail_height = 128
    image_width = int(cosmetic_per_row * thumbnail_width)
    image_height = int(thumbnail_height + 5 + (num_rows * (padding_height + thumbnail_height)) + 140)
    font_path = 'styles/aqua/font.ttf'
    font_size = 16
    font = ImageFont.truetype(font_path, font_size)
    image = Image.new('RGB', (image_width, image_height), (0, 0, 0))
        
    current_row = 0
    current_column = 0
    sortarray = ['mythic', 'legendary', 'dark', 'slurp', 'starwars', 'marvel', 'lava', 'frozen', 'gaminglegends', 'shadow', 'icon', 'dc', 'epic', 'rare', 'uncommon', 'common']
    arr.sort(key=lambda x: sortarray.index(x.rarity_value))

    # had some issues with exclusives rendering in wrong order, so i'm sorting them
    try:
        with open('exclusive.txt', 'r', encoding='utf-8') as f:
            exclusive_cosmetics = [i.strip() for i in f.readlines()]
        
        with open('most_wanted.txt', 'r', encoding='utf-8') as f:
            popular_cosmetics = [i.strip() for i in f.readlines()]
    except FileNotFoundError:
        print("Error: 'exclusive.txt' or 'most_wanted.txt' not found.")
        exclusive_cosmetics = []
        popular_cosmetics = []

    mythic_items = [item for item in arr if item.rarity_value == 'mythic']
    other_items = [item for item in arr if item.rarity_value != 'mythic']
    mythic_items.sort(
        key=lambda x: exclusive_cosmetics.index(x.cosmetic_id) 
        if x.cosmetic_id in exclusive_cosmetics else float('inf')
    )
        
    if header == "Popular":
        other_items.sort(
            key=lambda x: popular_cosmetics.index(x.cosmetic_id) 
            if x.cosmetic_id in popular_cosmetics else float('inf')
        )
        
    arr = mythic_items + other_items
    draw = ImageDraw.Draw(image)

    # top
    icon_logo = Image.open(f'cosmetic_icons/{header}.png').resize((128, 128), Image.Resampling.BILINEAR)
    icon_logo.thumbnail((thumbnail_width, thumbnail_height)) 
    image.paste(icon_logo, (10, 5), mask=icon_logo)
    draw.text((162, 30), '{}'.format(len(arr)), font=ImageFont.truetype(font_path, 70), fill=(0, 0, 0)) # shadow
    draw.text((166, 87), '{}'.format(header), font=ImageFont.truetype(font_path, 40), fill=(0, 0, 0)) # shadow
    draw.text((162, 26), '{}'.format(len(arr)), font=ImageFont.truetype(font_path, 70), fill=(255, 255, 255))
    draw.text((166, 83), '{}'.format(header), font=ImageFont.truetype(font_path, 40), fill=(167, 167, 167))
        
    special_items = {
        "CID_029_Athena_Commando_F_Halloween": "cache/pink_ghoul.png",
        "CID_030_Athena_Commando_M_Halloween": "cache/purple_skull_old.png",
        "CID_116_Athena_Commando_M_CarbideBlack": "cache/omega_max.png",
        "CID_694_Athena_Commando_M_CatBurglar": "cache/gold_midas.png",
        "CID_693_Athena_Commando_M_BuffCat": "cache/gold_cat.png",
        "CID_691_Athena_Commando_F_TNTina": "cache/gold_tntina.png",
        "CID_690_Athena_Commando_F_Photographer": "cache/gold_skye.png",
        "CID_701_Athena_Commando_M_BananaAgent": "cache/gold_peely.png",
        "CID_315_Athena_Commando_M_TeriyakiFish": "cache/worldcup_fish.png",
        "CID_971_Athena_Commando_M_Jupiter_S0Z6M": "cache/black_masterchief.png",
        "CID_028_Athena_Commando_F": "cache/og_rene.png",
        "CID_017_Athena_Commando_M": "cache/og_aat.png"
    }
        
    for cosmetic in arr:
        special_icon = False
        is_banner = cosmetic.is_banner
        photo = None
        if cosmetic.rarity_value.lower() == "mythic" and cosmetic.cosmetic_id in special_items:
            special_icon = True
            icon_path = special_items[cosmetic.cosmetic_id]
            if os.path.exists(icon_path):
                try:
                    photo = Image.open(icon_path)
                except Exception as e:
                    special_icon = False
            else:
                special_icon = False
        else:
            photo = fortnite_cache.get_cosmetic_icon_from_cache(cosmetic.small_icon, cosmetic.cosmetic_id)
            
        if is_banner:
            scaled_width = int(photo.width * 1.5)
            scaled_height = int(photo.height * 1.5)
            photo = photo.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
            x_offset = 32
            y_offset = 10
                
            new_img = Image.open(f'styles/aqua/rarity/{cosmetic.rarity_value.lower()}.png').convert('RGBA')
            new_img.paste(photo, (x_offset, y_offset), mask=photo)
            photo = new_img
            photo.thumbnail((thumbnail_width, thumbnail_height))
        else:
            new_img = Image.open(f'styles/aqua/rarity/{cosmetic.rarity_value.lower()}.png').convert('RGBA').resize(photo.size)    
            new_img.paste(photo, mask=photo)
            photo = new_img
            photo.thumbnail((thumbnail_width, thumbnail_height))

        # black box for cosmetic name
        box = Image.new('RGBA', (128, 27), (0, 0, 0, 100))
        photo.paste(box, (0, new_img.size[1] - 27), mask=box)
            
        if header != "Exclusives" and cosmetic.cosmetic_id in popular_cosmetics:
            star_image = Image.open('cosmetic_icons/WantedStar.png').resize((128, 128), Image.BILINEAR)
            photo.paste(star_image, (0, 0), star_image.convert("RGBA"))

        x = thumbnail_width * current_column
        y = thumbnail_width + (thumbnail_height + padding_height) * current_row
        image.paste(photo, (x, y))

        name = cosmetic.name.upper()
        max_text_width = thumbnail_width - 10
        max_text_height = 20
            
        # fixed font size
        font_size = 16
        offset = 6
        while True:
            font = ImageFont.truetype(font_path, font_size)
            bbox = draw.textbbox((0, 0), name, font=font)
            name_width = bbox[2] - bbox[0]
            name_height = bbox[3] - bbox[1]

            if name_width > max_text_width or name_height > max_text_height:
                font_size -= 1
                offset += 0.5
            else:
                break

        # cosmetic name
        bbox = draw.textbbox((0, 0), name, font=font)
        name_width = bbox[2] - bbox[0]
        draw.text((x + (thumbnail_width - name_width) // 2, y + (thumbnail_height - padding + offset)), name, font=font, fill=(255, 255, 255))
            
        # make the cosmetics show ordered in rows(cosmetic_per_row is hardcoded)
        current_column += 1
        if current_column >= cosmetic_per_row:
            current_row += 1
            current_column = 0

    # footer
    current_date = datetime.now().strftime('%d %B %Y')
    
    # custom logo
    custom_logo_path = f"users/logos/{user_data['ID']}.png"
    if os.path.isfile(custom_logo_path):
        custom_logo = Image.open(custom_logo_path).resize((125, 125), Image.Resampling.BILINEAR)
        image.paste(custom_logo, (25, image_height - 140), mask=custom_logo)
    else:
        # original logo if not found
        logo = Image.open('img/logo.png').resize((125, 125), Image.Resampling.BILINEAR)     
        image.paste(logo, (25, image_height - 140), mask=logo)

    draw.text((179, image_height - 114), '{}'.format(current_date), font=ImageFont.truetype(font_path, 30), fill=(0, 0, 0)) # shadow
    draw.text((175, image_height - 118), '{}'.format(current_date), font=ImageFont.truetype(font_path, 30), fill=(255, 255, 255))  
    draw.text((179, image_height - 84), 'Submitted By: @{}'.format(user_data['username']), font=ImageFont.truetype(font_path, 30), fill=(0, 0, 0)) # shadow 
    draw.text((175, image_height - 88), 'Submitted By: @{}'.format(user_data['username']), font=ImageFont.truetype(font_path, 30), fill=(255, 255, 255))
    draw.text((179, image_height - 31), "ExoCheckBot.gg", font=ImageFont.truetype(font_path, 20), fill=(0, 0, 0)) # shadow     
    draw.text((175, image_height - 55), "ExoCheckBot.gg", font=ImageFont.truetype(font_path, 20), fill=(255, 255, 255))
    image.save(nametosave)

class FortniteRenderer:
    """Main renderer class for Fortnite cosmetic images"""
    
    def __init__(self):
        self.cache = fortnite_cache
        self.available_styles = [
            {"ID": 0, "name": "Exo", "render_func": "render_exo_style"},
            {"ID": 1, "name": "Easy", "render_func": "render_easy_style"},
            {"ID": 2, "name": "Raika", "render_func": "render_raika_style"},
            {"ID": 3, "name": "Kayy", "render_func": "render_kayy_style"},
            {"ID": 4, "name": "Storm", "render_func": "render_storm_style"},
            {"ID": 5, "name": "Aqua", "render_func": "render_aqua_style"}
        ]
    
    def get_style_by_id(self, style_id: int):
        """Get style information by ID"""
        for style in self.available_styles:
            if style["ID"] == style_id:
                return style
        return None
    
    def render_cosmetics(self, style_id: int, header: str, user_data: dict, cosmetics: list, output_path: str):
        """Render cosmetics using the specified style"""
        style = self.get_style_by_id(style_id)
        if not style:
            raise ValueError(f"Unknown style ID: {style_id}")
        
        # Get the render function from this module
        render_func = globals()[style["render_func"]]
        
        # Call the render function
        render_func(header, user_data, cosmetics, output_path)

# Global renderer instance
renderer = FortniteRenderer()
