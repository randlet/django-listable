"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from .. import models

from django.contrib.auth.models import User
from django.test.client import Client


class TestDepartment(TestCase):

    def setUp(self):
        self.dpt = models.Department(title="title",slug="slug")

    def test_unicode(self):
        self.assertEqual(str(self.dpt),"title")


class TestPosition(TestCase):

    def setUp(self):
        self.pos = models.Department(title="title",slug="slug")

    def test_unicode(self):
        self.assertEqual(str(self.pos),"title")


class TestStaff(TestCase):

    def setUp(self):

        password = 'password'

        admin = User.objects.create_superuser('admin', 'myemail@test.com', password)
        c = Client()
        c.login(username=admin.username, password=password)

        p = models.Position(title="title", slug="slug")
        p.save()
        sp = models.Position(title="super_title", slug="super_slug")
        sp.save()
        dpt =  models.Department(title="title",slug="slug")
        dpt.save()


        self.super = models.Staff(
            first_name="super",
            last_name="visor",
            position=sp,
            department=dpt,
            is_supervisor=False,
            profile=admin
        )
        self.super.save()

        self.staff = models.Staff(
            first_name="first",
            last_name="last",
            position=p,
            position_no="1234",
            reports_to=self.super,
        )
        self.staff.save()

    def test_name(self):
        self.assertEqual(self.staff.name(),"last, first")

    def test_name_alt(self):
        self.assertEqual(self.staff.name_alt(),"first last")

    def test_toggle_status(self):
        from surveys.models import InactiveQuarter, RoundingQuarter
        cur = RoundingQuarter.objects.current_quarter()

        self.staff.toggle_status()

        #should now be an inactive object
        iq = InactiveQuarter.objects.get(staff=self.staff, quarter=cur)

        self.staff.toggle_status()
        with self.assertRaises(InactiveQuarter.DoesNotExist):
            InactiveQuarter.objects.get(staff=self.staff, quarter=cur)

    def test_inactive_status(self):
        from surveys.models import InactiveQuarter, RoundingQuarter
        cur = RoundingQuarter.objects.current_quarter()

        InactiveQuarter.objects.create( staff=self.staff, quarter=cur)
        expected = models.FYQTR_ACTIVE_CHOICES_DISPLAY[models.FYQTR_INACTIVE]
        self.assertEqual(self.staff.status(),expected)

    def test_active_status(self):
        from surveys.models import InactiveQuarter, RoundingQuarter
        expected = models.FYQTR_ACTIVE_CHOICES_DISPLAY[models.FYQTR_ACTIVE]
        self.assertEqual(self.staff.status(),expected)

    def test_supervisor(self):
        self.assertEqual(self.staff.supervisor(),self.super.name())

    def test_no_supervisor(self):
        self.assertEqual(self.super.supervisor(),"")

