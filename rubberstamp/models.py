from django.db import models
from django.contrib.contenttypes.models import ContentType


class AppPermission(models.Model):
    """
    Permission model which allows apps to add permissions for models in other
    apps, keeping track of the permissions added by each app.
    """
    
    app_label = models.CharField(max_length=100)
    content_type = models.ForeignKey(ContentType)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        return '%s | %s.%s | %s' % (self.app_label,
            self.content_type.app_label, self.content_type.model, self.name)
    