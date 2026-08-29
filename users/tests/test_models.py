"""Tests for khatma app models."""
from django.test import TestCase
from django.contrib.auth import get_user_model

from khatma.models import Khatma, KhatmaPart, Participant, Deceased, QuranReading

User = get_user_model()


class KhatmaModelTests(TestCase):
    """Test Khatma model."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='model@example.com',
            password='testpass123!'
        )
        self.khatma = Khatma.objects.create(
            title='Model Test Khatma',
            creator=self.user,
            khatma_type='regular',
            frequency='once',
            is_public=True,
            visibility='public',
        )

    def test_khatma_str(self):
        """Test Khatma string representation."""
        self.assertIn('Model Test Khatma', str(self.khatma))

    def test_khatma_progress_percentage(self):
        """Test progress percentage calculation."""
        self.assertEqual(self.khatma.get_progress_percentage(), 0.0)
        KhatmaPart.objects.filter(khatma=self.khatma, part_number=1).update(is_completed=True)
        self.assertAlmostEqual(self.khatma.get_progress_percentage(), 100.0 / 30, places=1)

    def test_khatma_parts_created(self):
        """Test that 30 parts are created for a khatma."""
        self.assertEqual(KhatmaPart.objects.filter(khatma=self.khatma).count(), 30)


class ParticipantModelTests(TestCase):
    """Test Participant model."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='participant@example.com',
            password='testpass123!'
        )
        self.khatma = Khatma.objects.create(
            title='Participant Test',
            creator=self.user,
            khatma_type='regular',
            frequency='once',
            is_public=True,
            visibility='public',
        )

    def test_participant_creation(self):
        """Test participant creation."""
        participant = Participant.objects.create(user=self.user, khatma=self.khatma)
        self.assertEqual(participant.user, self.user)
        self.assertEqual(participant.khatma, self.khatma)
