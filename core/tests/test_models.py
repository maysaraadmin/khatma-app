'''"""This module contains Module functionality."""'''
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
'\n'
from core.models import Profile, Deceased, QuranPart, Khatma, Participant, PartAssignment, Notification, UserAchievement

class ProfileModelTest(TestCase):
    """Tests for the Profile model"""

    def setUp(self):
        '''"""Function to setUp."""'''
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.profile = Profile.objects.create(user=self.user, account_type='individual', total_points=100, level=2)

    def test_profile_creation(self):
        """Test that a profile can be created"""
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.account_type, 'individual')
        self.assertEqual(self.profile.total_points, 100)
        self.assertEqual(self.profile.level, 2)

    def test_profile_str_representation(self):
        """Test the string representation of a profile"""
        self.assertEqual(str(self.profile), "testuser's Profile")

    def test_get_family_members(self):
        """Test the get_family_members method"""
        family_admin = Profile.objects.create(user=User.objects.create_user(username='familyadmin', password='testpassword'), account_type='family', family_admin=True)
        family_member1 = Profile.objects.create(user=User.objects.create_user(username='member1', password='testpassword'), account_type='family', family_admin=False, family_group=family_admin)
        family_member2 = Profile.objects.create(user=User.objects.create_user(username='member2', password='testpassword'), account_type='family', family_admin=False, family_group=family_admin)
        family_members = family_admin.get_family_members()
        self.assertEqual(family_members.count(), 2)
        self.assertIn(family_member1, family_members)
        self.assertIn(family_member2, family_members)
        self.assertEqual(self.profile.get_family_members().count(), 0)

class DeceasedModelTest(TestCase):
    """Tests for the Deceased model"""

    def setUp(self):
        '''"""Function to setUp."""'''
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.deceased = Deceased.objects.create(name='Test Deceased', death_date=timezone.now().date(), birth_date=timezone.now().date().replace(year=1950), added_by=self.user)

    def test_deceased_creation(self):
        """Test that a deceased person can be created"""
        self.assertEqual(self.deceased.name, 'Test Deceased')
        self.assertEqual(self.deceased.added_by, self.user)

    def test_deceased_str_representation(self):
        """Test the string representation of a deceased person"""
        self.assertEqual(str(self.deceased), 'Test Deceased')

    def test_age_at_death(self):
        """Test the age_at_death method"""
        death_year = self.deceased.death_date.year
        birth_year = self.deceased.birth_date.year
        expected_age = death_year - birth_year
        self.assertEqual(self.deceased.age_at_death(), expected_age)

class KhatmaModelTest(TestCase):
    """Tests for the Khatma model"""

    def setUp(self):
        '''"""Function to setUp."""'''
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.deceased = Deceased.objects.create(name='Test Deceased', death_date=timezone.now().date(), added_by=self.user)
        self.khatma = Khatma.objects.create(title='Test Khatma', creator=self.user, khatma_type='memorial', deceased=self.deceased, is_public=True)
        for i in range(1, 31):
            QuranPart.objects.create(part_number=i)

    def test_khatma_creation(self):
        """Test that a khatma can be created"""
        self.assertEqual(self.khatma.title, 'Test Khatma')
        self.assertEqual(self.khatma.creator, self.user)
        self.assertEqual(self.khatma.khatma_type, 'memorial')
        self.assertEqual(self.khatma.deceased, self.deceased)
        self.assertTrue(self.khatma.is_public)

    def test_khatma_str_representation(self):
        """Test the string representation of a khatma"""
        self.assertEqual(str(self.khatma), 'Test Khatma - ختمة للمتوفى')

    def test_get_progress_percentage(self):
        """Test the get_progress_percentage method"""
        for i in range(1, 31):
            part = QuranPart.objects.get(part_number=i)
            part_assignment = PartAssignment.objects.create(khatma=self.khatma, part=part, is_completed=i <= 15)
        self.assertEqual(self.khatma.get_progress_percentage(), 50.0)

class NotificationModelTest(TestCase):
    """Tests for the Notification model"""

    def setUp(self):
        '''"""Function to setUp."""'''
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.khatma = Khatma.objects.create(title='Test Khatma', creator=self.user, khatma_type='regular')
        self.notification = Notification.objects.create(user=self.user, notification_type='khatma_progress', message='Test notification', related_khatma=self.khatma)

    def test_notification_creation(self):
        """Test that a notification can be created"""
        self.assertEqual(self.notification.user, self.user)
        self.assertEqual(self.notification.notification_type, 'khatma_progress')
        self.assertEqual(self.notification.message, 'Test notification')
        self.assertEqual(self.notification.related_khatma, self.khatma)
        self.assertFalse(self.notification.is_read)

    def test_notification_str_representation(self):
        """Test the string representation of a notification"""
        expected_str = 'تقدم ختمة - Test notification - testuser'
        self.assertEqual(str(self.notification), expected_str)

class UserAchievementModelTest(TestCase):
    """Tests for the UserAchievement model"""

    def setUp(self):
        '''"""Function to setUp."""'''
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.achievement = UserAchievement.objects.create(user=self.user, achievement_type='first_khatma', points_earned=10)

    def test_achievement_creation(self):
        """Test that an achievement can be created"""
        self.assertEqual(self.achievement.user, self.user)
        self.assertEqual(self.achievement.achievement_type, 'first_khatma')
        self.assertEqual(self.achievement.points_earned, 10)

    def test_achievement_str_representation(self):
        """Test the string representation of an achievement"""
        expected_str = 'testuser - أول ختمة'
        self.assertEqual(str(self.achievement), expected_str)