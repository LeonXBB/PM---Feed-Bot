from django.db import models


class TextString(models.Model): #TODO make connection with outside dictionary

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

    screen_id = models.CharField(max_length=5096, default="")
    position_index = models.IntegerField(default=-1)

    language_1 = models.CharField(max_length=5096, blank=True)
    language_2 = models.CharField(max_length=5096, blank=True)
    language_3 = models.CharField(max_length=5096, blank=True)
    language_4 = models.CharField(max_length=5096, blank=True)
    language_5 = models.CharField(max_length=5096, blank=True)
