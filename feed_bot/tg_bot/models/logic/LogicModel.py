from django.db import models


class LogicModel(models.Model):
    
    @classmethod
    def _get_(cls, params):

        k, v = list(params.items())[0]

        rv = cls.objects.filter(**{k: v})

        if len(list(params.items())) > 1:
            for k, v in list(params.items())[1:]:
                rv = rv.filter(**{k: v}) 
        
        return [*rv,]

    created = models.CharField(max_length=5096, default=f"{{}}") # "by": user_id, "at": timestamp
    status = models.IntegerField(default=0)

    class Meta:
        abstract = True

    def _cancel_(self):
        self.status = 5