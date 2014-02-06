# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Department'
        db.create_table(u'staff_department', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'staff', ['Department'])

        # Adding model 'Position'
        db.create_table(u'staff_position', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255)),
        ))
        db.send_create_signal(u'staff', ['Position'])

        # Adding model 'Staff'
        db.create_table(u'staff_staff', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('position', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['staff.Position'])),
            ('position_no', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('reports_to', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['staff.Staff'], null=True, blank=True)),
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['staff.Department'], null=True, blank=True)),
            ('fyqtr_status', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_supervisor', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'staff', ['Staff'])

        # Adding unique constraint on 'Staff', fields ['first_name', 'last_name']
        db.create_unique(u'staff_staff', ['first_name', 'last_name'])


    def backwards(self, orm):
        # Removing unique constraint on 'Staff', fields ['first_name', 'last_name']
        db.delete_unique(u'staff_staff', ['first_name', 'last_name'])

        # Deleting model 'Department'
        db.delete_table(u'staff_department')

        # Deleting model 'Position'
        db.delete_table(u'staff_position')

        # Deleting model 'Staff'
        db.delete_table(u'staff_staff')


    models = {
        u'staff.department': {
            'Meta': {'object_name': 'Department'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'staff.position': {
            'Meta': {'object_name': 'Position'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'staff.staff': {
            'Meta': {'ordering': "('last_name', 'first_name')", 'unique_together': "(('first_name', 'last_name'),)", 'object_name': 'Staff'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['staff.Department']", 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'fyqtr_status': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_supervisor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'position': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['staff.Position']"}),
            'position_no': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'reports_to': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['staff.Staff']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['staff']