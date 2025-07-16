"""Custom validators for the Khatma app."""
import os
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible

@deconstructible
class FileValidator:
    """
    Validator for files, checking the file size and extension.
    
    Args:
        max_size (int): Maximum file size in bytes
        allowed_extensions (list): List of allowed file extensions
    """
    def __init__(self, max_size=2*1024*1024, allowed_extensions=None):
        self.max_size = max_size
        self.allowed_extensions = allowed_extensions or ['.jpg', '.jpeg', '.png', '.gif']
    
    def __call__(self, value):
        """
        Validate the file.
        
        Args:
            value: The file to validate
            
        Raises:
            ValidationError: If the file is invalid
        """
        # Check file size
        if value.size > self.max_size:
            raise ValidationError(
                f'File size must be no more than {filesizeformat(self.max_size)}. Current file size is {filesizeformat(value.size)}.'
            )
        
        # Check file extension
        ext = os.path.splitext(value.name)[1].lower()
        if self.allowed_extensions and ext not in self.allowed_extensions:
            raise ValidationError(
                f'Unsupported file extension. Allowed extensions are: { ", ".join(self.allowed_extensions) }'
            )

    def __eq__(self, other):
        return (
            isinstance(other, FileValidator) and
            self.max_size == other.max_size and
            self.allowed_extensions == other.allowed_extensions
        )

def validate_image_file_extension(value):
    """
    Validate that the uploaded file is an image.
    
    Args:
        value: The file to validate
        
    Raises:
        ValidationError: If the file is not an image
    """
    validator = FileValidator(
        max_size=2*1024*1024,  # 2MB
        allowed_extensions=['.jpg', '.jpeg', '.png', '.gif']
    )
    return validator(value)

def validate_pdf_file_extension(value):
    """
    Validate that the uploaded file is a PDF.
    
    Args:
        value: The file to validate
        
    Raises:
        ValidationError: If the file is not a PDF
    """
    validator = FileValidator(
        max_size=5*1024*1024,  # 5MB
        allowed_extensions=['.pdf']
    )
    return validator(value)

def validate_audio_file_extension(value):
    """
    Validate that the uploaded file is an audio file.
    
    Args:
        value: The file to validate
        
    Raises:
        ValidationError: If the file is not an audio file
    """
    validator = FileValidator(
        max_size=10*1024*1024,  # 10MB
        allowed_extensions=['.mp3', '.wav', '.ogg', '.m4a']
    )
    return validator(value)

def validate_video_file_extension(value):
    """
    Validate that the uploaded file is a video file.
    
    Args:
        value: The file to validate
        
    Raises:
        ValidationError: If the file is not a video file
    """
    validator = FileValidator(
        max_size=50*1024*1024,  # 50MB
        allowed_extensions=['.mp4', '.webm', '.mov', '.avi']
    )
    return validator(value)
