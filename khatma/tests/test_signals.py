"""Tests for Khatma signals and core services."""
from django.test import TestCase
from django.contrib.auth import get_user_model

from quran.models import QuranPart
from khatma.models import Khatma, KhatmaPart, Participant
from khatma.services import distribute_parts_to_participants, get_khatma_progress

User = get_user_model()


class KhatmaPartsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='creator@example.com', password='pass')
        for i in range(1, 31):
            QuranPart.objects.create(part_number=i)

    def test_parts_created_on_khatma_save(self):
        khatma = Khatma.objects.create(title='Test Khatma', creator=self.user)
        self.assertEqual(khatma.parts.count(), 30)

    def test_khatma_marked_completed_when_all_parts_done(self):
        khatma = Khatma.objects.create(title='Test Khatma', creator=self.user)
        for part in khatma.parts.all():
            part.is_completed = True
            part.save()
        khatma.refresh_from_db()
        self.assertTrue(khatma.is_completed)
        self.assertIsNotNone(khatma.completed_at)

    def test_get_khatma_progress(self):
        khatma = Khatma.objects.create(title='Test Khatma', creator=self.user)
        # Complete half the parts via individual saves (triggers signals).
        parts = list(khatma.parts.all())
        for part in parts[:15]:
            part.is_completed = True
            part.save()
        progress = get_khatma_progress(khatma)
        self.assertEqual(progress['total_parts'], 30)
        self.assertEqual(progress['completed_parts'], 15)
        self.assertEqual(progress['progress_percentage'], 50.0)


class DistributePartsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='creator@example.com', password='pass')
        self.other = User.objects.create_user(email='other@example.com', password='pass')
        for i in range(1, 31):
            QuranPart.objects.create(part_number=i)
        self.khatma = Khatma.objects.create(title='Test Khatma', creator=self.user)
        Participant.objects.create(user=self.user, khatma=self.khatma)
        Participant.objects.create(user=self.other, khatma=self.khatma)

    def test_distribute_assigns_all_unassigned_parts(self):
        assigned = distribute_parts_to_participants(self.khatma)
        self.assertEqual(assigned, 30)
        self.assertEqual(
            KhatmaPart.objects.filter(assigned_to__isnull=False).count(), 30
        )

    def test_distribute_is_idempotent(self):
        distribute_parts_to_participants(self.khatma)
        # Running again should not create duplicates or reassign.
        assigned = distribute_parts_to_participants(self.khatma)
        self.assertEqual(assigned, 0)
        self.assertEqual(
            KhatmaPart.objects.filter(assigned_to__isnull=False).count(), 30
        )
