from django.db import models


class TextLanguage(models.Model):

    self_name = models.CharField(max_length=5096, default="")
