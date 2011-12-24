from pim1.pengine.models import Item, Project
Item.objects.filter(project=1).exclude(id = 1).delete()
