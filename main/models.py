from django.db import models

# Create your models here.


class Teams(models.Model):
    access_token = models.CharField(max_length=1000)
    team_name = models.CharField(max_length=1000)
    team_id = models.CharField(primary_key=True, max_length=1000)
    incoming_webhook_url = models.CharField(max_length=1000)
    incoming_webhook_configuration_url = models.CharField(max_length=1000)
    last_changed = models.DateTimeField(auto_now = True, auto_now_add = False)
    created = models.DateTimeField(auto_now = False, auto_now_add = True, editable=False)

    def __unicode__(self):
        return str(self.unique_uuid)
