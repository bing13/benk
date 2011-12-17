from django.db import models

class Project(models.Model):
#    item = models.ManyToManyField(Item)
    name = models.CharField(max_length=120)
    color = models.IntegerField()
    def __unicode__(self):
        return self.name

class Item(models.Model):
    project = models.ForeignKey(Project, null=True)
    date_created = models.DateTimeField('date created',auto_now_add=True)
    date_mod = models.DateTimeField('date last modified',auto_now=True)

    # these are used during Info Select import operation. 
    # They are not unique across import files
    IS_import_ID = models.IntegerField(null=True, blank=True)

    date_gootask_display = models.DateTimeField('date to display as goo Task',null=True, blank=True)
    #date_gootask_display.blank=True
    ##? date_gootask_display.blank=True
    # for now we'll assume we don't need a key field
    HTMLnoteBody = models.TextField(blank=True)
    #HTMLnoteBody.blank=True

    title = models.CharField(max_length=200)
    ## example gtask ID: u'MDA5MTI3NjgzODg0MDUzMjk1MTI6MTk1Mjg0MjA0MzoxMzQ3MDQ3NjYy'
    gtask_id = models.CharField(max_length=100)

    follows = models.IntegerField(null=True, blank=True)
    parent = models.IntegerField(null=True, blank=True)

    PRIORITY_CHOICES = (
        ('1', 'Urgent'),
        ('2', 'Important'),
        ('3', 'Normal'),
        ('4', 'Low'),
        ('0', '')
    )
    STATUS_CHOICES = (
        ('1', 'WIP'),
        ('2', 'Next'),
        ('3', 'Cold'),
        ('5', 'Hold'),
        ('6', 'Cancelled'),
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
