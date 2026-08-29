"""Tests for khatma app."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from khatma.models import Khatma, KhatmaPart, Participant, Deceased

User = get_user_model()


class KhatmaCreationTests(TestCase):
    """Test khatma creation flow."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='khatma@example.com',
            password='testpass123!'
        )
        self.client.login(email='khatma@example.com', password='testpass123!')

    def test_create_khatma_view_get(self):
        """Test that the create khatma page loads."""
        response = self.client.get(reverse('khatma:create_khatma'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ختمة جديدة')

    def test_create_khatma_view_post(self):
        """Test creating a new khatma."""
        response = self.client.post(reverse('khatma:create_khatma'), {
            'title': 'Test Khatma',
            'description': 'A test khatma',
            'khatma_type': 'regular',
            'frequency': 'once',
            'is_public': True,
            'visibility': 'public',
            'allow_comments': True,
            'send_reminders': True,
            'reminder_frequency': 'weekly',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Khatma.objects.filter(title='Test Khatma').exists())
        self.assertEqual(KhatmaPart.objects.filter(khatma__title='Test Khatma').count(), 30)


class KhatmaDetailTests(TestCase):
    """Test khatma detail view."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='detail@example.com',
            password='testpass123!'
        )
        self.khatma = Khatma.objects.create(
            title='Detail Test Khatma',
            creator=self.user,
            khatma_type='regular',
            frequency='once',
            is_public=True,
            visibility='public',
        )

    def test_khatma_detail_view(self):
        """Test that khatma detail page loads."""
        response = self.client.get(reverse('khatma:khatma_detail', kwargs={'khatma_id': self.khatma.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Detail Test Khatma')

    def test_join_khatma(self):
        """Test joining a khatma."""
        new_user = User.objects.create_user(
            email='joiner@example.com',
            password='testpass123!'
        )
        self.client.login(email='joiner@example.com', password='testpass123!')
        response = self.client.get(reverse('khatma:join_khatma', kwargs={'khatma_id': self.khatma.id}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Participant.objects.filter(user=new_user, khatma=self.khatma).exists())


class DeceasedTests(TestCase):
    """Test deceased management."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='deceased@example.com',
            password='testpass123!'
        )
        self.client.login(email='deceased@example.com', password='testpass123!')

    def test_create_deceased_view_get(self):
        """Test that the create deceased page loads."""
        response = self.client.get(reverse('khatma:create_deceased'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'إضافة متوفى')

    def test_create_deceased_view_post(self):
        """Test creating a deceased record."""
        response = self.client.post(reverse('khatma:create_deceased'), {
            'name': 'Test Deceased',
            'death_date': '2020-01-01',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Deceased.objects.filter(name='Test Deceased').exists())
