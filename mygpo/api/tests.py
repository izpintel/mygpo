from django.test import TestCase
from django.contrib.auth.models import User
from mygpo.api.models import Device, Podcast, SubscriptionAction

class SyncTest(TestCase):
    def test_sync_actions(self):
        # this test does not yet complete when run as a unit test
        # because django does not set up the views
        u  = User.objects.create(username='u')
        d1 = Device.objects.create(name='d1', type='other', user=u)
        d2 = Device.objects.create(name='d2', type='other', user=u)
        p1 = Podcast.objects.create(title='p1', url='http://p1.com/')
        p2 = Podcast.objects.create(title='p2', url='http://p2.com/')
        p3 = Podcast.objects.create(title='p3', url='http://p3.com/')
        p4 = Podcast.objects.create(title='p4', url='http://p4.com/')

        s1 = SubscriptionAction.objects.create(device=d1, podcast=p1, action='subscribe')
        s2 = SubscriptionAction.objects.create(device=d2, podcast=p2, action='subscribe')
        u2 = SubscriptionAction.objects.create(device=d2, podcast=p2, action='unsubscribe')
        s3 = SubscriptionAction.objects.create(device=d1, podcast=p3, action='subscribe')
        s3_= SubscriptionAction.objects.create(device=d2, podcast=p3, action='subscribe')
        s4 = SubscriptionAction.objects.create(device=d2, podcast=p4, action='subscribe')
        u3 = SubscriptionAction.objects.create(device=d2, podcast=p3, action='unsubscribe')

        d1.sync_with(d2)

        #d1: p1, p3
        #d2: p4

        sa1 = d1.get_sync_actions()
        sa2 = d2.get_sync_actions()

        self.assertEqual( len(sa1), 2)
        self.assertEqual( len(sa2), 1)

        self.assertEqual( sa1[0].device, d2)
        self.assertEqual( sa1[0].podcast, p4)
        self.assertEqual( sa1[0].action, 'subscribe')

        self.assertEqual( sa1[1].device, d2)
        self.assertEqual( sa1[1].podcast, p3)
        self.assertEqual( sa1[1].action, 'unsubscribe')

        self.assertEqual( sa2[0].device, d1)
        self.assertEqual( sa2[0].podcast, p1)
        self.assertEqual( sa2[0].action, 'subscribe')


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

