from django.test import TestCase
from django.contrib.auth.models import User
from wc.models.models import UserProfile

class UserProfileModelTests(TestCase):
    def test_create_user_profile_without_affiliation(self):
        new_user = User.objects.create_user(
                'john', 'lennon@thebeatles.com', 'johnpassword')
        UserProfile.objects.create(user=new_user)
        self.assertQuerysetEqual(
                UserProfile.objects.all(),
                ['<UserProfile: john>'])

    def test_create_user_profile_with_affiliation(self):
        new_user = User.objects.create_user(
                'john', 'lennon@thebeatles.com', 'johnpassword')
        UserProfile.objects.create(user=new_user, affiliation="The UK")
        self.assertQuerysetEqual(
                UserProfile.objects.all(),
                ['<UserProfile: john - The UK>'])


