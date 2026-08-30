"""Tests for core forms."""
import os
import sys
from django.test import TestCase, TransactionTestCase, override_settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.db.models.signals import post_save

# Import models from their respective apps
from users.models import Profile
from users import signals  # Import signals to access the signal handlers
from khatma.models import Deceased, Khatma, Participant, PartAssignment
from quran.models import QuranPart

# Import forms
from core.forms import KhatmaCreationForm, PartAssignmentForm, UserProfileForm, UserProfileEditForm
from khatma.forms import DeceasedForm

User = get_user_model()

class BaseTestCase(TransactionTestCase):
    """Base test case with common setup."""
    reset_sequences = True
    
    @classmethod
    def setUpClass(cls):
        """Set up test class."""
        super().setUpClass()
        # Disconnect the signal to prevent automatic profile creation
        post_save.disconnect(signals.create_user_profile, sender=User)
        post_save.disconnect(signals.save_user_profile, sender=User)
    
    @classmethod
    def tearDownClass(cls):
        """Tear down test class."""
        # Reconnect the signals
        post_save.connect(signals.create_user_profile, sender=User)
        post_save.connect(signals.save_user_profile, sender=User)
        super().tearDownClass()
    
    def setUp(self):
        """Set up test data."""
        # Create a counter to ensure unique usernames and emails
        if not hasattr(self.__class__, '_user_counter'):
            self.__class__._user_counter = 0
        self.__class__._user_counter += 1
        
        # Create a unique username and email for this test
        self.test_username = f'testuser_{self._user_counter}'
        self.test_email = f'test_{self._user_counter}@example.com'

class DeceasedFormTest(BaseTestCase):
    """Tests for the DeceasedForm"""

    def setUp(self):
        """Set up test data"""
        from PIL import Image
        from io import BytesIO
        
        self.user = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.valid_data = {
            'name': 'Test Deceased',
            'death_date': timezone.now().date(),
            'birth_date': timezone.now().date(),
            'biography': 'Test biography',
            'relation': 'Parent',
            'cause_of_death': 'Natural causes',
            'burial_place': 'Test Cemetery'
        }
        
        # Create a valid image file in memory
        image = Image.new('RGB', (100, 100), color='red')
        image_io = BytesIO()
        image.save(image_io, format='JPEG', quality=90)
        image_io.seek(0)
        
        self.image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=image_io.read(),
            content_type='image/jpeg'
        )

    def test_deceased_form_valid(self):
        """Test that the form is valid with valid data"""
        form = DeceasedForm(data=self.valid_data, initial={'user': self.user})
        # Set the user as an attribute after instantiation
        form.user = self.user
        self.assertTrue(form.is_valid())

    def test_deceased_form_invalid(self):
        """Test that the form is invalid with invalid data"""
        invalid_data = self.valid_data.copy()
        invalid_data.pop('name')
        form = DeceasedForm(data=invalid_data, initial={'user': self.user})
        # Set the user as an attribute after instantiation
        form.user = self.user
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_deceased_form_with_image(self):
        """Test that the form accepts an image file"""
        form_data = self.valid_data.copy()
        form = DeceasedForm(
            data=form_data,
            files={'photo': self.image_file},
            initial={'user': self.user}
        )
        # Set the user as an attribute after instantiation
        form.user = self.user
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertIn('photo', form.cleaned_data, "Photo was not included in cleaned_data")

class KhatmaCreationFormTest(BaseTestCase):
    """Tests for the KhatmaCreationForm"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        from datetime import date, timedelta
        today = date.today()
        
        self.valid_data = {
            'title': 'Test Khatma',
            'khatma_type': 'regular',
            'description': 'Test description',
            'is_public': True,
            'frequency': 'once',
            'visibility': 'public',
            'allow_comments': True,
            'send_reminders': True,
            'reminder_frequency': 'weekly',
            'target_completion_date': (today + timedelta(days=30)).isoformat(),
            'start_date': today.isoformat(),
            'end_date': (today + timedelta(days=30)).isoformat(),
            'auto_distribute_parts': True
        }

    def test_khatma_creation_form_valid(self):
        """Test that the form is valid with valid data"""
        form = KhatmaCreationForm(
            data=self.valid_data,
            initial={'user': self.user}
        )
        # Set the user as an attribute after instantiation
        form.user = self.user
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_khatma_creation_form_invalid(self):
        """Test that the form is invalid with invalid data"""
        invalid_data = self.valid_data.copy()
        invalid_data.pop('title')
        form = KhatmaCreationForm(data=invalid_data, initial={'user': self.user})
        # Set the user as an attribute after instantiation
        form.user = self.user
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_khatma_creation_form_invalid_type(self):
        """Test that the form is invalid with an invalid khatma type"""
        invalid_data = self.valid_data.copy()
        invalid_data['khatma_type'] = 'invalid_type'
        form = KhatmaCreationForm(data=invalid_data, initial={'user': self.user})
        # Set the user as an attribute after instantiation
        form.user = self.user
        self.assertFalse(form.is_valid())
        self.assertIn('khatma_type', form.errors)

class PartAssignmentFormTest(BaseTestCase):
    """Tests for the PartAssignmentForm"""

    def setUp(self):
        """Set up test data"""
        self.creator = User.objects.create_user(
            username='testcreator',
            email='creator@example.com',
            password='testpass123'
        )
        self.participant = User.objects.create_user(
            username='testparticipant',
            email='participant@example.com',
            password='testpass123'
        )
        
        # Create a Quran part - only part_number is required
        self.part = QuranPart.objects.create(
            part_number=1
        )
        
        # Create a khatma
        self.khatma = Khatma.objects.create(
            title='Test Khatma',
            creator=self.creator,
            khatma_type='regular',
            is_public=True
        )
        
        # Add participant to the khatma
        from khatma.models import Participant
        Participant.objects.create(
            khatma=self.khatma,
            user=self.participant,
            joined_at=timezone.now()
        )
        
        # Create a part assignment
        self.part_assignment = PartAssignment.objects.create(
            khatma=self.khatma,
            part=self.part,
            participant=self.participant,
            is_completed=False
        )
        
        self.valid_data = {
            'notes': 'Test notes',
            'dua': 'Test dua',
            'is_completed': True,
            'participant': self.participant.id
        }

    def test_part_assignment_form_valid(self):
        """Test that the form is valid with valid data"""
        form = PartAssignmentForm(
            data=self.valid_data,
            instance=self.part_assignment,
            initial={'user': self.participant, 'khatma': self.khatma}
        )
        # Set the user and khatma as attributes after instantiation
        form.user = self.participant
        form.khatma = self.khatma
        self.assertTrue(form.is_valid())

    def test_part_assignment_form_save(self):
        """Test that the form saves correctly"""
        # Include the participant in the form data
        form_data = self.valid_data.copy()
        form_data['participant'] = self.participant.id
        
        print(f"[TEST] Form data: {form_data}")
        
        form = PartAssignmentForm(
            data=form_data,
            instance=self.part_assignment,
            initial={'user': self.participant, 'khatma': self.khatma}
        )
        # Set the user and khatma as attributes after instantiation
        form.user = self.participant
        form.khatma = self.khatma
        
        is_valid = form.is_valid()
        print("[TEST] Form is valid:", is_valid)
        if not is_valid:
            print("[TEST] Form errors:")
            for field, errors in form.errors.items():
                # Convert errors to ASCII to avoid encoding issues
                error_msgs = [str(e).encode('ascii', 'replace').decode('ascii') for e in errors]
                print(f"  {field}: {', '.join(error_msgs)}")
            
            # Print form data for debugging
            print("[TEST] Form data:", form.data)
            print("[TEST] Form fields:", list(form.fields.keys()))
        
        self.assertTrue(is_valid, "Form should be valid. Check the test output for error details.")
        
        # Print cleaned data for debugging
        print("[TEST] Form cleaned_data:")
        if hasattr(form, 'cleaned_data'):
            for field, value in form.cleaned_data.items():
                print(f"  {field}: {value}")
        else:
            print("  No cleaned_data available")
        
        assignment = form.save()
        
        # Refresh the instance from the database
        assignment.refresh_from_db()
        
        # Print the saved instance for debugging
        print(f"[TEST] Saved assignment - is_completed: {assignment.is_completed}")
        print(f"[TEST] Saved assignment - completed_at: {assignment.completed_at}")
        
        self.assertEqual(assignment.notes, 'Test notes')
        self.assertEqual(assignment.dua, 'Test dua')
        self.assertTrue(assignment.is_completed, f"Assignment should be marked as completed. Current value: {assignment.is_completed}")
        
        # Test that completed_at is set when marking as completed
        self.assertIsNotNone(assignment.completed_at, f"completed_at should be set when marking as completed. Current value: {assignment.completed_at}")

class UserProfileFormTest(BaseTestCase):
    """Tests for the UserProfileForm"""
    reset_sequences = True

    def setUp(self):
        """Set up test data"""
        super().setUp()
        
        # Create a user with a unique username and email
        self.user = User.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create the profile manually since we disabled the signal
        self.profile, created = Profile.objects.get_or_create(
            user=self.user,
            defaults={
                'bio': 'Test bio',
                'account_type': 'reader',
                'last_activity_date': timezone.now().date(),  # Add required field
                'consecutive_days': 0,  # Add default value for consecutive_days
                'level': 1,  # Add default value for level
                'total_points': 0,  # Add default value for total_points
            }
        )
        
        # Update the user's profile with any additional fields
        if not created:
            self.profile.bio = 'Test bio'
            self.profile.last_activity_date = timezone.now().date()
            self.profile.save()
        
        self.valid_data = {
            'username': 'testuser_profile_updated',
            'email': 'testprofileupdated@example.com',
            'first_name': 'Test_Updated',
            'last_name': 'User_Updated'
        }

    def test_user_profile_form_valid(self):
        """Test that the form is valid with valid data"""
        form = UserProfileForm(data=self.valid_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_user_profile_form_save(self):
        """Test that the form saves correctly"""
        form = UserProfileForm(data=self.valid_data, instance=self.user)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.email, 'testprofileupdated@example.com')
        self.assertEqual(user.first_name, 'Test_Updated')
        self.assertEqual(user.last_name, 'User_Updated')