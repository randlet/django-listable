from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

import staff.models as models
import csv

def clean_header(header):
    return header.replace(" ","").replace("#","").lower()

REQUIRED_HEADERS = "Department Title,Position No#,Incumbent Name,Position title,Reports to Employee,FYQTR_Status"


def get_dpt(dpt_title):

    slug = slugify(dpt_title)
    try:
        return models.Department.objects.get(slug=slug)
    except models.Department.DoesNotExist:
        return models.Department.objects.create(slug=slug, title=dpt_title)

def get_pos(pos_title):

    slug = slugify(pos_title)
    try:
        return models.Position.objects.get(slug=slug)
    except models.Position.DoesNotExist:
        return models.Position.objects.create(slug=slug, title=pos_title)

def get_super(supervisor):

    last_name, first_name = supervisor.split(',')

    position = get_pos("Supervisor")
    try:
        sv = models.Staff.objects.get(first_name=first_name, last_name=last_name)
    except models.Staff.DoesNotExist:
        sv = models.Staff(
            first_name = first_name,
            last_name = last_name,
            position = position,
            fyqtr_status="active",
            is_supervisor=True
        )

        sv.save()
    return sv


def bulk_load_staff(csvfile):

    reader = csv.reader(csvfile, delimiter=',',quotechar='"')
    header = ",".join(reader.next())
    if clean_header(header) != clean_header(REQUIRED_HEADERS):
        raise ValueError("Incorrect csv file format. Must be:\n%s" %(REQUIRED_HEADERS))

    for line in reader:
        dpt, pos_no, name, position , reports_to, status =  line

        dpt = get_dpt(dpt)
        pos = get_pos(position)
        sv = get_super(reports_to)

        first_name, last_name = name.split(' ',1)

        try:
            sv = models.Staff.objects.get(first_name=first_name, last_name=last_name)
        except models.Staff.DoesNotExist:
            sv = models.Staff(
                first_name = first_name,
                last_name = last_name,
                position_no = pos_no,
                position = pos,
                reports_to=sv,
                department=dpt,
                fyqtr_status=models.FYQTR_ACTIVE,
                is_supervisor=False
            )
            sv.save()

class Command(BaseCommand):
    args = '<filename>'
    help = 'bulk loads staff listings from csv file'

    def handle(self, *args, **options):

        with open(args[0],'r') as f:
            bulk_load_staff(f)

            #self.stdout.write('Successfully closed poll "%s"' % poll_id)

