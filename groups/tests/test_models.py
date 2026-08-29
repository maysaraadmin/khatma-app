"""Model tests for groups app."""
from django.test import TestCase
from django.contrib.auth import get_user_model

from groups.models import ReadingGroup, GroupMembership

User = get_user_model()


class GroupModelTests(TestCase):
    """Test group models."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='groupmodel@example.com',
            password='testpass123!'
        )
        self.group = ReadingGroup.objects.create(
            name='Model Test Group',
            creator=self.user,
            is_public=True,
            allow_join_requests=True,
        )

    def test_group_str(self):
        """Test ReadingGroup string representation."""
        self.assertEqual(str(self.group), 'Model Test Group')

    def test_group_membership_str(self):
        """Test GroupMembership string representation."""
        membership = GroupMembership.objects.get(user=self.user, group=self.group)
        self.assertIn('Model Test Group', str(membership))
        self.assertIn('groupmodel@example.com', str(membership))
