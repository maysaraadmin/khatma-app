from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from core.forms import (
    DeceasedForm, KhatmaCreationForm, PartAssignmentForm,
    UserProfileForm, UserProfileEditForm
)
from core.models import QuranPart, Khatma, PartAssignment

class DeceasedFormTest(TestCase):
    """Tests for the DeceasedForm"""
    
    def setUp(self):
        self.valid_data = {
            'name': 'Test Deceased',
            'death_date': timezone.now().date(),
            'account_type': 'individual',
            'relation': 'Parent',
            'memorial_day': True,
            'memorial_frequency': 'yearly'
        }
        
        # Create a test image file
        self.image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',  # Empty content for testing
            content_type='image/jpeg'
        )
    
    def test_deceased_form_valid(self):
        """Test that the form is valid with valid data"""
        form = DeceasedForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_deceased_form_invalid(self):
        """Test that the form is invalid with invalid data"""
        # Missing required field
        invalid_data = self.valid_data.copy()
        invalid_data.pop('name')
        
        form = DeceasedForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_deceased_form_with_image(self):
        """Test that the form accepts an image file"""
        form_data = self.valid_data.copy()
        form = DeceasedForm(
            data=form_data,
            files={'photo': self.image_file}
        )
        self.assertTrue(form.is_valid())


class KhatmaCreationFormTest(TestCase):
    """Tests for the KhatmaCreationForm"""
    
    def setUp(self):
        self.valid_data = {
            'title': 'Test Khatma',
            'khatma_type': 'regular',
            'description': 'Test description',
            'is_public': True,
            'frequency': 'once',
            'visibility': 'public',
            'send_reminders': True,
            'reminder_frequency': 'weekly'
        }
    
    def test_khatma_creation_form_valid(self):
        """Test that the form is valid with valid data"""
        form = KhatmaCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_khatma_creation_form_invalid(self):
        """Test that the form is invalid with invalid data"""
        # Missing required field
        invalid_data = self.valid_data.copy()
        invalid_data.pop('title')
        
        form = KhatmaCreationForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_khatma_creation_form_invalid_type(self):
        """Test that the form is invalid with an invalid khatma type"""
        invalid_data = self.valid_data.copy()
        invalid_data['khatma_type'] = 'invalid_type'
        
        form = KhatmaCreationForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('khatma_type', form.errors)


class PartAssignmentFormTest(TestCase):
    """Tests for the PartAssignmentForm"""
    
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
        # Create khatma
        self.khatma = Khatma.objects.create(
            title='Test Khatma',
            creator=self.user,
            khatma_type='regular'
        )
        
        # Create part
        self.part = QuranPart.objects.create(part_number=1)
        
        # Create part assignment
        self.part_assignment = PartAssignment.objects.create(
            khatma=self.khatma,
            part=self.part
        )
        
        self.valid_data = {
            'notes': 'Test notes',
            'dua': 'Test dua'
        }
    
    def test_part_assignment_form_valid(self):
        """Test that the form is valid with valid data"""
        form = PartAssignmentForm(
            data=self.valid_data,
            instance=self.part_assignment
        )
        self.assertTrue(form.is_valid())
    
    def test_part_assignment_form_save(self):
        """Test that the form saves correctly"""
        form = PartAssignmentForm(
            data=self.valid_data,
            instance=self.part_assignment
        )
        self.assertTrue(form.is_valid())
        
        # Save the form
        assignment = form.save()
        
        # Check that the data was saved
        self.assertEqual(assignment.notes, 'Test notes')
        self.assertEqual(assignment.dua, 'Test dua')


class UserProfileFormTest(TestCase):
    """Tests for the UserProfileForm"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        self.valid_data = {
            'username': 'testuser2',
            'email': 'test2@example.com',
            'first_name': 'Test2',
            'last_name': 'User2'
        }
    
    def test_user_profile_form_valid(self):
        """Test that the form is valid with valid data"""
        form = UserProfileForm(
            data=self.valid_data,
            instance=self.user
        )
        self.assertTrue(form.is_valid())
    
    def test_user_profile_form_save(self):
        """Test that the form saves correctly"""
        form = UserProfileForm(
            data=self.valid_data,
            instance=self.user
        )
        self.assertTrue(form.is_valid())
        
        # Save the form
        user = form.save()
        
        # Check that the data was saved
        self.assertEqual(user.username, 'testuser2')
        self.assertEqual(user.email, 'test2@example.com')
        self.assertEqual(user.first_name, 'Test2')
        self.assertEqual(user.last_name, 'User2')
