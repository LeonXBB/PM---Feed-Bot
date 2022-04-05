from django.db import models


class ScheduledMessage(models.Model):

    @classmethod
    def _get_(cls, params):

        rv = []

        for obj in cls.objects.all():
            
            true = True
            for k, v in params.items():
                if getattr(obj, k) != v:
                    true = False
            
            if true: rv.append(obj)

        return rv

    user_id = models.IntegerField(default=-1)
    messages_ids = models.CharField(max_length=5096, default=";")

    epoch = models.CharField(max_length=5096, default="")
    pause_epoch = models.CharField(max_length=5096, default="")

    content_type = models.CharField(max_length=5096, default="remainder")
    content_id = models.IntegerField(default=-1)
    content_formatters = models.CharField(max_length=5096, default="")
    content_callback = models.CharField(max_length=5096, default="")

    is_sent = models.IntegerField(default=0)
    is_active = models.IntegerField(default=1)

    group_name = models.CharField(max_length=5096, default="")