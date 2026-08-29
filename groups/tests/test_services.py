"""Service tests for groups app."""
from django.test import TestCase
from django.contrib.auth import get_user_model

from groups.models import ReadingGroup, GroupMembership

User = get_user_model()


class GroupServicesTests(TestCase):
    """Test group services."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='groupservice@example.com',
            password='testpass123!'
        )
        self.group = ReadingGroup.objects.create(
            name='Service Test Group',
            creator=self.user,
            is_public=True,
            allow_join_requests=True,
        )

    def test_group_membership_creation(self):
        """Test creating a group membership."""
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123!'
        )
        membership = GroupMembership.objects.create(
            user=other_user,
            group=self.group,
            role='member'
        )
        self.assertEqual(membership.user, other_user)
        self.assertEqual(membership.group, self.group)
        self.assertEqual(membership.role, 'member')
