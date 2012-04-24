# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Project.color'
        db.alter_column('pengine_project', 'color', self.gf('django.db.models.fields.CharField')(max_length=24))

        # Changing field 'ProjectSet.color'
        db.alter_column('pengine_projectset', 'color', self.gf('django.db.models.fields.CharField')(max_length=24))


    def backwards(self, orm):
        
        # Changing field 'Project.color'
        db.alter_column('pengine_project', 'color', self.gf('django.db.models.fields.CharField')(max_length=8))

        # Changing field 'ProjectSet.color'
        db.alter_column('pengine_projectset', 'color', self.gf('django.db.models.fields.CharField')(max_length=8))


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
            'owner': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'parent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pengine.Project']", 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'pengine.project': {
            'Meta': {'object_name': 'Project'},
            'archivePair': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pengine.Project']", 'null': 'True', 'blank': 'True'}),
            'color': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'owner': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'projType': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pengine.ProjectSet']", 'null': 'True'})
        },
        'pengine.projectset': {
            'Meta': {'object_name': 'ProjectSet'},
            'color': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'owner': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['pengine']
