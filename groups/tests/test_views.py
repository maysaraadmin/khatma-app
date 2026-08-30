"""View tests for groups app."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from groups.models import ReadingGroup, GroupMembership
from notifications.models import Notification

User = get_user_model()


class GroupTests(TestCase):
    """Test group functionality."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='group@example.com',
            password='testpass123!'
        )
        self.client.login(email='group@example.com', password='testpass123!')

    def test_group_list_view(self):
        """Test that group list page loads."""
        response = self.client.get(reverse('groups:group_list'))
        self.assertEqual(response.status_code, 200)

    def test_create_group_view_get(self):
        """Test that create group page loads."""
        response = self.client.get(reverse('groups:create_group'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'إنشاء مجموعة')

    def test_create_group_view_post(self):
        """Test creating a new group."""
        response = self.client.post(reverse('groups:create_group'), {
            'name': 'Test Group',
            'description': 'A test group',
            'is_public': True,
            'allow_join_requests': True,
            'max_members': 0,
            'enable_chat': True,
            'enable_khatma_creation': True,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ReadingGroup.objects.filter(name='Test Group').exists())
        self.assertTrue(GroupMembership.objects.filter(
            user=self.user,
            group__name='Test Group',
            role='admin'
        ).exists())
