from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
import os

def generate_khatma_social_media_image(khatma):
    """
    Generate a more sophisticated social media sharing image for a Khatma.
    
    Args:
        khatma (Khatma): The Khatma instance
    
    Returns:
        SimpleUploadedFile: Generated image file
    """
    # Create a base image
    width, height = 1200, 630  # Optimal size for most social media platforms
    background_color = (240, 248, 255)  # Light blue background
    
    # Create image
    image = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(image)
    
    # Load fonts
    try:
        # Try to use custom Arabic and English fonts
        title_font = ImageFont.truetype("path/to/arabic_bold_font.ttf", 60)
        subtitle_font = ImageFont.truetype("path/to/arabic_regular_font.ttf", 40)
    except IOError:
        # Fallback to default font
        title_font = ImageFont.truetype(ImageFont.load_default(), 60)
        subtitle_font = ImageFont.truetype(ImageFont.load_default(), 40)
    
    # Title
    title = khatma.title or "ختمة قرآن"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_position = ((width - title_bbox[2]) // 2, 100)
    draw.text(title_position, title, font=title_font, fill=(0, 0, 139))  # Dark blue
    
    # Khatma Type
    khatma_type = khatma.get_khatma_type_display()
    type_bbox = draw.textbbox((0, 0), khatma_type, font=subtitle_font)
    type_position = ((width - type_bbox[2]) // 2, 200)
    draw.text(type_position, khatma_type, font=subtitle_font, fill=(70, 130, 180))
    
    # Progress
    progress = f"التقدم: {khatma.get_progress_percentage()}%"
    progress_bbox = draw.textbbox((0, 0), progress, font=subtitle_font)
    progress_position = ((width - progress_bbox[2]) // 2, 300)
    draw.text(progress_position, progress, font=subtitle_font, fill=(34, 139, 34))  # Green
    
    # Deceased Information (if applicable)
    if khatma.khatma_type == 'memorial' and khatma.deceased:
        memorial_text = f"إهداء إلى روح المرحوم: {khatma.deceased.name}"
        memorial_bbox = draw.textbbox((0, 0), memorial_text, font=subtitle_font)
        memorial_position = ((width - memorial_bbox[2]) // 2, 400)
        draw.text(memorial_position, memorial_text, font=subtitle_font, fill=(139, 0, 0))  # Dark red
    
    # Hashtags
    hashtags = "#ختمة_قرآن #ختمة_رحمة"
    hashtags_bbox = draw.textbbox((0, 0), hashtags, font=subtitle_font)
    hashtags_position = ((width - hashtags_bbox[2]) // 2, 500)
    draw.text(hashtags_position, hashtags, font=subtitle_font, fill=(0, 123, 255))
    
    # Save image to a BytesIO object
    image_io = BytesIO()
    image.save(image_io, format='PNG')
    image_io.seek(0)
    
    # Create a SimpleUploadedFile
    return SimpleUploadedFile(
        f"khatma_{khatma.id}_social_media.png", 
        image_io.getvalue(), 
        content_type='image/png'
    )

def generate_khatma_share_link(khatma):
    """
    Generate a unique shareable link for a Khatma.
    
    Args:
        khatma (Khatma): The Khatma instance
    
    Returns:
        str: Unique sharing link
    """
    import uuid
    
    # Generate a unique UUID if not already exists
    if not khatma.sharing_link:
        khatma.sharing_link = uuid.uuid4()
        khatma.save()
    
    return str(khatma.sharing_link)

def generate_khatma_hashtags(khatma):
    """
    Generate appropriate hashtags for a Khatma.
    
    Args:
        khatma (Khatma): The Khatma instance
    
    Returns:
        str: Generated hashtags
    """
    base_hashtags = ["#ختمة_قرآن", "#ختمة_رحمة"]
    
    type_hashtags = {
        'memorial': ["#ختمة_للمتوفى"],
        'ramadan': ["#ختمة_رمضان"],
        'charity': ["#ختمة_خيرية"],
        'birth': ["#ختمة_مولد"],
        'graduation': ["#ختمة_تخرج"],
        'wedding': ["#ختمة_زفاف"]
    }
    
    # Add type-specific hashtags
    if khatma.khatma_type in type_hashtags:
        base_hashtags.extend(type_hashtags[khatma.khatma_type])
    
    # Add deceased name if memorial
    if khatma.khatma_type == 'memorial' and khatma.deceased:
        base_hashtags.append(f"#ختمة_{khatma.deceased.name.replace(' ', '_')}")
    
    return " ".join(base_hashtags)
