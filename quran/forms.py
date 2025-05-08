from django import forms
from .models import QuranBookmark, QuranReadingSettings


class QuranBookmarkForm(forms.ModelForm):
    """Form for creating and editing Quran bookmarks"""
    class Meta:
        model = QuranBookmark
        fields = ['title', 'notes', 'color']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'color': forms.Select(choices=[
                ('blue', 'أزرق'),
                ('green', 'أخضر'),
                ('red', 'أحمر'),
                ('yellow', 'أصفر'),
                ('purple', 'بنفسجي'),
                ('orange', 'برتقالي'),
            ])
        }


class QuranReadingSettingsForm(forms.ModelForm):
    """Form for user's Quran reading settings"""
    class Meta:
        model = QuranReadingSettings
        fields = [
            'font_type', 'font_size', 'theme', 
            'show_translation', 'show_tajweed', 
            'preferred_reciter', 'auto_play_audio'
        ]
        widgets = {
            'font_size': forms.NumberInput(attrs={'min': 12, 'max': 36}),
        }


class QuranSearchForm(forms.Form):
    """Form for searching the Quran"""
    search_text = forms.CharField(
        max_length=100, 
        required=True,
        label='نص البحث',
        widget=forms.TextInput(attrs={'placeholder': 'ادخل نص البحث...'})
    )
    search_type = forms.ChoiceField(
        choices=[
            ('text', 'نص الآية'),
            ('translation', 'الترجمة'),
            ('both', 'النص والترجمة')
        ],
        initial='text',
        label='نوع البحث'
    )
    surah = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=114,
        label='السورة (اختياري)'
    )
    juz = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=30,
        label='الجزء (اختياري)'
    )


class ReciterFilterForm(forms.Form):
    """Form for filtering Quran reciters"""
    name = forms.CharField(
        max_length=100, 
        required=False,
        label='اسم القارئ',
        widget=forms.TextInput(attrs={'placeholder': 'ابحث عن قارئ...'})
    )
    style = forms.ChoiceField(
        choices=[
            ('', 'جميع الأنماط'),
            ('murattal', 'مرتل'),
            ('mujawwad', 'مجود'),
            ('muallim', 'معلم')
        ],
        required=False,
        label='نمط القراءة'
    )
