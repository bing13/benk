from pim1.pengine.models import Item, Project
Item.objects.filter(project=px).exclude(id = ex).delete()
