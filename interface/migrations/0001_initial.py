# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Document'
        db.create_table('interface_document', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('doc_file', self.gf('django.db.models.fields.files.FileField')(max_length=255)),
            ('upload_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('start_ocr_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('finish_ocr_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('upload_name', self.gf('django.db.models.fields.CharField')(max_length=220)),
            ('internal_name', self.gf('django.db.models.fields.CharField')(max_length=220)),
            ('num_pages', self.gf('django.db.models.fields.IntegerField')()),
            ('file_format', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('color_depth', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('interface', ['Document'])

        # Adding model 'OCRJob'
        db.create_table('interface_ocrjob', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['interface.Document'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('conv_cost', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('bw_cost', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('ocr_cost', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('error_text', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('interface', ['OCRJob'])


    def backwards(self, orm):
        
        # Deleting model 'Document'
        db.delete_table('interface_document')

        # Deleting model 'OCRJob'
        db.delete_table('interface_ocrjob')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'interface.document': {
            'Meta': {'object_name': 'Document'},
            'color_depth': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'doc_file': ('django.db.models.fields.files.FileField', [], {'max_length': '255'}),
            'file_format': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'finish_ocr_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '220'}),
            'num_pages': ('django.db.models.fields.IntegerField', [], {}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'start_ocr_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'upload_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'upload_name': ('django.db.models.fields.CharField', [], {'max_length': '220'})
        },
        'interface.ocrjob': {
            'Meta': {'object_name': 'OCRJob'},
            'bw_cost': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'conv_cost': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['interface.Document']"}),
            'error_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ocr_cost': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['interface']
