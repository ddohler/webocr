# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'OCRJob'
        db.delete_table('interface_ocrjob')

        # Adding model 'DocumentPage'
        db.create_table('interface_documentpage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['interface.Document'])),
            ('page_file', self.gf('django.db.models.fields.files.FileField')(max_length=255)),
            ('page_number', self.gf('django.db.models.fields.IntegerField')()),
            ('start_process_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('finish_process_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('is_convert_done', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('convert_time', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('is_binarize_done', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('binarize_time', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('is_recognize_done', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('recognize_time', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('status', self.gf('django.db.models.fields.CharField')(default='w', max_length=1)),
            ('error_text', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('interface', ['DocumentPage'])

        # Deleting field 'Document.finish_ocr_date'
        db.delete_column('interface_document', 'finish_ocr_date')

        # Deleting field 'Document.start_ocr_date'
        db.delete_column('interface_document', 'start_ocr_date')


    def backwards(self, orm):
        
        # Adding model 'OCRJob'
        db.create_table('interface_ocrjob', (
            ('ocr_cost', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('bw_cost', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['interface.Document'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('error_text', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('conv_cost', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('interface', ['OCRJob'])

        # Deleting model 'DocumentPage'
        db.delete_table('interface_documentpage')

        # Adding field 'Document.finish_ocr_date'
        db.add_column('interface_document', 'finish_ocr_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True), keep_default=False)

        # Adding field 'Document.start_ocr_date'
        db.add_column('interface_document', 'start_ocr_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True), keep_default=False)


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '220'}),
            'num_pages': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'upload_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'upload_name': ('django.db.models.fields.CharField', [], {'max_length': '220'})
        },
        'interface.documentpage': {
            'Meta': {'object_name': 'DocumentPage'},
            'binarize_time': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'convert_time': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['interface.Document']"}),
            'error_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'finish_process_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_binarize_done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_convert_done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_recognize_done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'page_file': ('django.db.models.fields.files.FileField', [], {'max_length': '255'}),
            'page_number': ('django.db.models.fields.IntegerField', [], {}),
            'recognize_time': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'start_process_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'w'", 'max_length': '1'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['interface']
