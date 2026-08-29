"""Tests for khatma app services."""
from django.test import TestCase
from django.contrib.auth import get_user_model

from khatma.models import Khatma, KhatmaPart, Participant
from khatma.services import get_khatma_progress, get_user_khatma_stats, distribute_parts_to_participants

User = get_user_model()


class KhatmaServicesTests(TestCase):
    """Test khatma services."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='service@example.com',
            password='testpass123!'
        )
        self.khatma = Khatma.objects.create(
            title='Service Test Khatma',
            creator=self.user,
            khatma_type='regular',
            frequency='once',
            is_public=True,
            visibility='public',
        )

    def test_get_khatma_progress(self):
        """Test getting khatma progress."""
        progress = get_khatma_progress(self.khatma)
        self.assertEqual(progress['total_parts'], 30)
        self.assertEqual(progress['completed_parts'], 0)
        self.assertEqual(progress['progress_percentage'], 0.0)

    def test_get_khatma_progress_with_completed(self):
        """Test progress calculation with completed parts."""
        KhatmaPart.objects.filter(khatma=self.khatma, part_number=1).update(is_completed=True)
        progress = get_khatma_progress(self.khatma)
        self.assertEqual(progress['completed_parts'], 1)
        self.assertAlmostEqual(progress['progress_percentage'], 100.0 / 30, places=1)

    def test_get_user_khatma_stats(self):
        """Test getting user khatma statistics."""
        stats = get_user_khatma_stats(self.user)
        self.assertEqual(stats['created_khatmas'], 1)
        self.assertEqual(stats['participated_khatmas'], 0)
        self.assertEqual(stats['completed_khatmas'], 0)
