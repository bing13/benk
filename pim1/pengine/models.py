###
# help with south for model migration
# http://south.aeracode.org/docs/tutorial/part1.html
#
# ./manage.py schemamigration pengine --auto
# ./manage.py migrate pengine

####

from django.db import models


class ProjectSet(models.Model):
    PROJSET_CHOICES = (
        ('1', 'work'),
        ('2', 'personal'),
        ('3', 'testing'),
        ('4', 'retired'),
    )
    
    name = models.CharField(max_length=120, choices=PROJSET_CHOICES)
    color = models.CharField(max_length=8)
    def __unicode__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=120)
    color = models.CharField(max_length=8)
    archivePair = models.ForeignKey('self', null=True, blank=True)
    set = models.ForeignKey(ProjectSet, null=True)

    ### archive is for done items, etc
    ### retired project is for mothballing the entire main project

    PROJTYPE_CHOICES = (
        ('1', 'normal'),
        ('2', 'retired project'),
        ('3', 'archive'),
    )
         
    projType = models.CharField(max_length=20, choices=PROJTYPE_CHOICES )    

    def __unicode__(self):
        return self.name
    
    projectTypeLookup = {}
    for pt in PROJTYPE_CHOICES:
        projectTypeLookup[pt[0]]=pt[1]

    def projectTypeText(self):
        return(self.projectTypeLookup[self.projtype])



class Item(models.Model):
    project = models.ForeignKey(Project, null=True)
    date_created = models.DateTimeField('date created',auto_now_add=True)
    date_mod = models.DateTimeField('date last modified',auto_now=True)

    # these are used during Info Select import operation. 
    # They are not unique across import files
    IS_import_ID = models.IntegerField(null=True, blank=True)

    date_gootask_display = models.DateTimeField('to do date',null=True, blank=True)
    HTMLnoteBody = models.TextField(blank=True)

    title = models.CharField(max_length=200)
    ## example gtask ID: u'MDA5MTI3NjgzODg0MDUzMjk1MTI6MTk1Mjg0MjA0MzoxMzQ3MDQ3NjYy'
    gtask_id = models.CharField(max_length=100)

    follows = models.IntegerField(null=True, blank=True)
    parent = models.IntegerField(null=True, blank=True)

    indentLevel = models.IntegerField(null=True, blank=True)

    PRIORITY_CHOICES = (
        ('1', 'TODAY'),
        ('2', 'Urgent'),        
        ('3', 'Important'),
        ('4', 'Normal'),
        ('5', 'Low'),
        ('0', '')
    )
    STATUS_CHOICES = (
        ('1', 'WIP'),
        ('2', 'Next'),
        ('3', 'Cold'),
        ('5', 'Hold'),
        ('6', 'Cancelled'),
        ('8', 'Ref'),        
        ('9', 'Done'),
        ('0', '')
    )
         

    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)


    statusChoiceLookup = {}
    priorityChoiceLookup = {}
    #exampleItem=Item.objects.filter(pk=1)[0]  #filter returns a result set

    for sc in STATUS_CHOICES:
        statusChoiceLookup[sc[0]]=sc[1]

    for pc in PRIORITY_CHOICES:
        priorityChoiceLookup[pc[0]]=pc[1]
 
    def __unicode__(self):
        return self.title    

    def priorityText(self):
        return(self.priorityChoiceLookup[self.priority])

    def statusText(self):
        return(self.statusChoiceLookup[self.status])
