# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Project'
        db.create_table('pengine_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('color', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('pengine', ['Project'])

        # Adding model 'Item'
        db.create_table('pengine_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pengine.Project'], null=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_mod', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('IS_import_ID', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_gootask_display', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('HTMLnoteBody', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('gtask_id', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('follows', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('parent', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('indentLevel', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('pengine', ['Item'])


    def backwards(self, orm):
        
        # Deleting model 'Project'
        db.delete_table('pengine_project')

        # Deleting model 'Item'
        db.delete_table('pengine_item')


    models = {
        'pengine.item': {
            'HTMLnoteBody': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'IS_import_ID': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'Meta': {'object_name': 'Item'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_gootask_display': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'follows': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'gtask_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indentLevel': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pengine.Project']", 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'pengine.project': {
            'Meta': {'object_name': 'Project'},
            'color': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        }
    }

    complete_apps = ['pengine']
