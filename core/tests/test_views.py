'''"""This module contains Module functionality."""'''
import json
'\n'
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
'\n'
from core.models import Profile, Deceased, QuranPart, Khatma, Participant, PartAssignment, Notification, UserAchievement

class IndexViewTest(TestCase):
    """Tests for the index view"""

    def setUp(self):
        '''"""Function to setUp."""'''
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.khatma1 = Khatma.objects.create(title='User Khatma', creator=self.user, khatma_type='regular', is_public=True)
        self.other_user = User.objects.create_user(username='otheruser', password='testpassword')
        self.khatma2 = Khatma.objects.create(title='Other Khatma', creator=self.other_user, khatma_type='regular', is_public=True)
        Participant.objects.create(user=self.user, khatma=self.khatma2)

    def test_index_view_authenticated(self):
        """Test that the index view works for authenticated users"""
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')
        self.assertIn('user_khatmas', response.context)
        self.assertIn(self.khatma1, response.context['user_khatmas'])
        self.assertIn('participating_khatmas', response.context)
        self.assertIn(self.khatma2, response.context['participating_khatmas'])

    def test_index_view_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        self.client.logout()
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 302)

class CreateKhatmaViewTest(TestCase):
    """Tests for the create_khatma view"""

    def setUp(self):
        '''"""Function to setUp."""'''
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        for i in range(1, 31):
            QuranPart.objects.create(part_number=i)
        self.deceased = Deceased.objects.create(name='Test Deceased', death_date=timezone.now().date(), added_by=self.user)
        self.form_data = {'title': 'Test Khatma', 'khatma_type': 'regular', 'description': 'Test description', 'is_public': True, 'frequency': 'once', 'visibility': 'public'}

    def test_create_khatma_view_get(self):
        """Test that the create_khatma view works for GET requests"""
        response = self.client.get(reverse('core:create_khatma'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/create_khatma.html')
        self.assertIn('form', response.context)
        self.assertIn('deceased_list', response.context)
        self.assertIn(self.deceased, response.context['deceased_list'])

    def test_create_khatma_view_post_regular(self):
        """Test creating a regular khatma"""
        response = self.client.post(reverse('core:create_khatma'), data=self.form_data, follow=True)
        self.assertEqual(Khatma.objects.count(), 1)
        khatma = Khatma.objects.first()
        self.assertEqual(khatma.title, 'Test Khatma')
        self.assertEqual(khatma.creator, self.user)
        self.assertEqual(PartAssignment.objects.count(), 30)
        self.assertEqual(khatma.parts.count(), 30)
        self.assertTrue(Participant.objects.filter(user=self.user, khatma=khatma).exists())
        self.assertTrue(UserAchievement.objects.filter(user=self.user, achievement_type='first_khatma').exists())
        self.assertTrue(Notification.objects.filter(user=self.user, notification_type='khatma_progress', related_khatma=khatma).exists())
        self.assertRedirects(response, reverse('core:khatma_detail', args=[khatma.id]))

    def test_create_khatma_view_post_memorial(self):
        """Test creating a memorial khatma"""
        memorial_data = self.form_data.copy()
        memorial_data.update({'khatma_type': 'memorial', 'deceased': self.deceased.id})
        response = self.client.post(reverse('core:create_khatma'), data=memorial_data, follow=True)
        self.assertEqual(Khatma.objects.count(), 1)
        khatma = Khatma.objects.first()
        self.assertEqual(khatma.khatma_type, 'memorial')
        self.assertEqual(khatma.deceased, self.deceased)
        self.assertRedirects(response, reverse('core:khatma_detail', args=[khatma.id]))

    def test_create_khatma_view_post_invalid(self):
        """Test creating a khatma with invalid data"""
        invalid_data = self.form_data.copy()
        invalid_data.pop('title')
        response = self.client.post(reverse('core:create_khatma'), data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(Khatma.objects.count(), 0)

class KhatmaDetailViewTest(TestCase):
    """Tests for the khatma_detail view"""

    def setUp(self):
        '''"""Function to setUp."""'''
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.khatma = Khatma.objects.create(title='Test Khatma', creator=self.user, khatma_type='regular', is_public=True)
        for i in range(1, 31):
            part = QuranPart.objects.create(part_number=i)
            PartAssignment.objects.create(khatma=self.khatma, part=part, is_completed=i <= 15)

    def test_khatma_detail_view(self):
        """Test that the khatma_detail view works"""
        response = self.client.get(reverse('core:khatma_detail', args=[self.khatma.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/khatma_detail.html')
        self.assertEqual(response.context['khatma'], self.khatma)
        self.assertEqual(len(response.context['parts']), 30)
        self.assertEqual(response.context['completed_parts'], 15)
        self.assertEqual(response.context['total_parts'], 30)
        self.assertEqual(response.context['progress_percentage'], 50.0)

    def test_khatma_detail_view_nonexistent(self):
        """Test that a 404 is returned for a nonexistent khatma"""
        response = self.client.get(reverse('core:khatma_detail', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_khatma_detail_view_join(self):
        """Test joining a khatma"""
        other_user = User.objects.create_user(username='otheruser', password='testpassword')
        self.client.login(username='otheruser', password='testpassword')
        response = self.client.post(reverse('core:khatma_detail', args=[self.khatma.id]), follow=True)
        self.assertTrue(Participant.objects.filter(user=other_user, khatma=self.khatma).exists())
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'تم الانضمام إلى الختمة بنجاح')

class QuranPartViewTest(TestCase):
    """Tests for the quran_part_view"""

    def setUp(self):
        '''"""Function to setUp."""'''
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.part = QuranPart.objects.create(part_number=1)

    def test_quran_part_view(self):
        """Test that the quran_part_view works"""
        response = self.client.get(reverse('core:quran_part', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/quran_part.html')
        self.assertEqual(response.context['part'], self.part)
        self.assertEqual(response.context['next_part'], 2)
        self.assertIsNone(response.context['prev_part'])

    def test_quran_part_view_nonexistent(self):
        """Test that a 404 is returned for a nonexistent part"""
        response = self.client.get(reverse('core:quran_part', args=[999]))
        self.assertEqual(response.status_code, 404)