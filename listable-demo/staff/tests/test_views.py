from django.test import TestCase
from .. import models

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test.client import Client


class TestToggleStatus(TestCase):

    def setUp(self):

        self.password = 'password'

        self.admin = User.objects.create_superuser('admin', 'myemail@test.com', self.password)

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
            profile=self.admin
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

    def test_denies_anon(self):
        url = reverse("toggle-active",kwargs={"pk":self.staff.pk})
        response = self.client.get(url,follow=True)
        self.assertEqual(response.status_code, 403)

    def test_toggle(self):

        from surveys.models import InactiveQuarter, RoundingQuarter
        cur = RoundingQuarter.objects.current_quarter()

        self.client.login(username=self.admin.username, password=self.password)
        url = reverse("toggle-active",kwargs={"pk":self.staff.pk})
        response = self.client.get(url)

        #should now be an inactive object
        iq = InactiveQuarter.objects.get(staff=self.staff, quarter=cur)

    def test_invalid_toggle(self):

        self.client.login(username=self.admin.username, password=self.password)
        url = reverse("toggle-active",kwargs={"pk":99})
        response = self.client.get(url,follow=True)
        self.assertEqual(response.status_code, 404)
