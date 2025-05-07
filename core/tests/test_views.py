from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import (
    Profile, Deceased, QuranPart, Khatma, Participant,
    PartAssignment, Notification, UserAchievement
)
import json

class IndexViewTest(TestCase):
    """Tests for the index view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')
        
        # Create khatmas
        self.khatma1 = Khatma.objects.create(
            title='User Khatma',
            creator=self.user,
            khatma_type='regular',
            is_public=True
        )
        
        # Create another user and khatma
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpassword'
        )
        self.khatma2 = Khatma.objects.create(
            title='Other Khatma',
            creator=self.other_user,
            khatma_type='regular',
            is_public=True
        )
        
        # Add user as participant in other khatma
        Participant.objects.create(
            user=self.user,
            khatma=self.khatma2
        )
    
    def test_index_view_authenticated(self):
        """Test that the index view works for authenticated users"""
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')
        
        # Check that user's khatmas are in the context
        self.assertIn('user_khatmas', response.context)
        self.assertIn(self.khatma1, response.context['user_khatmas'])
        
        # Check that participating khatmas are in the context
        self.assertIn('participating_khatmas', response.context)
        self.assertIn(self.khatma2, response.context['participating_khatmas'])
    
    def test_index_view_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        self.client.logout()
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 302)  # Redirect to login


class CreateKhatmaViewTest(TestCase):
    """Tests for the create_khatma view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')
        
        # Create QuranParts
        for i in range(1, 31):
            QuranPart.objects.create(part_number=i)
        
        # Create a deceased person
        self.deceased = Deceased.objects.create(
            name='Test Deceased',
            death_date=timezone.now().date(),
            added_by=self.user
        )
        
        # Valid form data
        self.form_data = {
            'title': 'Test Khatma',
            'khatma_type': 'regular',
            'description': 'Test description',
            'is_public': True,
            'frequency': 'once',
            'visibility': 'public'
        }
    
    def test_create_khatma_view_get(self):
        """Test that the create_khatma view works for GET requests"""
        response = self.client.get(reverse('core:create_khatma'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/create_khatma.html')
        
        # Check that form is in the context
        self.assertIn('form', response.context)
        
        # Check that deceased list is in the context
        self.assertIn('deceased_list', response.context)
        self.assertIn(self.deceased, response.context['deceased_list'])
    
    def test_create_khatma_view_post_regular(self):
        """Test creating a regular khatma"""
        response = self.client.post(
            reverse('core:create_khatma'),
            data=self.form_data,
            follow=True
        )
        
        # Check that the khatma was created
        self.assertEqual(Khatma.objects.count(), 1)
        khatma = Khatma.objects.first()
        self.assertEqual(khatma.title, 'Test Khatma')
        self.assertEqual(khatma.creator, self.user)
        
        # Check that part assignments were created
        self.assertEqual(PartAssignment.objects.count(), 30)
        
        # Check that KhatmaParts were created
        self.assertEqual(khatma.parts.count(), 30)
        
        # Check that user is a participant
        self.assertTrue(Participant.objects.filter(user=self.user, khatma=khatma).exists())
        
        # Check that achievement was created
        self.assertTrue(UserAchievement.objects.filter(
            user=self.user,
            achievement_type='first_khatma'
        ).exists())
        
        # Check that notification was created
        self.assertTrue(Notification.objects.filter(
            user=self.user,
            notification_type='khatma_progress',
            related_khatma=khatma
        ).exists())
        
        # Check redirect to khatma detail
        self.assertRedirects(response, reverse('core:khatma_detail', args=[khatma.id]))
    
    def test_create_khatma_view_post_memorial(self):
        """Test creating a memorial khatma"""
        # Update form data for memorial khatma
        memorial_data = self.form_data.copy()
        memorial_data.update({
            'khatma_type': 'memorial',
            'deceased': self.deceased.id
        })
        
        response = self.client.post(
            reverse('core:create_khatma'),
            data=memorial_data,
            follow=True
        )
        
        # Check that the khatma was created
        self.assertEqual(Khatma.objects.count(), 1)
        khatma = Khatma.objects.first()
        self.assertEqual(khatma.khatma_type, 'memorial')
        self.assertEqual(khatma.deceased, self.deceased)
        
        # Check redirect to khatma detail
        self.assertRedirects(response, reverse('core:khatma_detail', args=[khatma.id]))
    
    def test_create_khatma_view_post_invalid(self):
        """Test creating a khatma with invalid data"""
        # Remove required field
        invalid_data = self.form_data.copy()
        invalid_data.pop('title')
        
        response = self.client.post(
            reverse('core:create_khatma'),
            data=invalid_data
        )
        
        # Check that the form is invalid
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        
        # Check that no khatma was created
        self.assertEqual(Khatma.objects.count(), 0)


class KhatmaDetailViewTest(TestCase):
    """Tests for the khatma_detail view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')
        
        # Create a khatma
        self.khatma = Khatma.objects.create(
            title='Test Khatma',
            creator=self.user,
            khatma_type='regular',
            is_public=True
        )
        
        # Create QuranParts and PartAssignments
        for i in range(1, 31):
            part = QuranPart.objects.create(part_number=i)
            PartAssignment.objects.create(
                khatma=self.khatma,
                part=part,
                is_completed=(i <= 15)  # Mark first 15 parts as completed
            )
    
    def test_khatma_detail_view(self):
        """Test that the khatma_detail view works"""
        response = self.client.get(
            reverse('core:khatma_detail', args=[self.khatma.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/khatma_detail.html')
        
        # Check that khatma is in the context
        self.assertEqual(response.context['khatma'], self.khatma)
        
        # Check that parts are in the context
        self.assertEqual(len(response.context['parts']), 30)
        
        # Check that progress is calculated correctly
        self.assertEqual(response.context['completed_parts'], 15)
        self.assertEqual(response.context['total_parts'], 30)
        self.assertEqual(response.context['progress_percentage'], 50.0)
    
    def test_khatma_detail_view_nonexistent(self):
        """Test that a 404 is returned for a nonexistent khatma"""
        response = self.client.get(
            reverse('core:khatma_detail', args=[999])
        )
        self.assertEqual(response.status_code, 404)
    
    def test_khatma_detail_view_join(self):
        """Test joining a khatma"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpassword'
        )
        self.client.login(username='otheruser', password='testpassword')
        
        # Join the khatma
        response = self.client.post(
            reverse('core:khatma_detail', args=[self.khatma.id]),
            follow=True
        )
        
        # Check that the user is now a participant
        self.assertTrue(Participant.objects.filter(
            user=other_user,
            khatma=self.khatma
        ).exists())
        
        # Check for success message
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'تم الانضمام إلى الختمة بنجاح')


class QuranPartViewTest(TestCase):
    """Tests for the quran_part_view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')
        
        # Create QuranPart
        self.part = QuranPart.objects.create(part_number=1)
    
    def test_quran_part_view(self):
        """Test that the quran_part_view works"""
        response = self.client.get(
            reverse('core:quran_part', args=[1])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/quran_part.html')
        
        # Check that part is in the context
        self.assertEqual(response.context['part'], self.part)
        
        # Check that next and prev parts are in the context
        self.assertEqual(response.context['next_part'], 2)
        self.assertIsNone(response.context['prev_part'])
    
    def test_quran_part_view_nonexistent(self):
        """Test that a 404 is returned for a nonexistent part"""
        response = self.client.get(
            reverse('core:quran_part', args=[999])
        )
        self.assertEqual(response.status_code, 404)
