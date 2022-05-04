from django.db import models


class LogicModel(models.Model):
    
    @classmethod
    def _get_(cls, params):

        rv = []

        for k, v in params.items():
            if len(rv) == 0: rv = cls.objects.filter(**{k: v})
            else: rv = rv.filter(**{k: v}) 
        
        return rv
        
        '''
        rv = []

        for obj in cls.objects.all():
            
            true = True
            for k, v in params.items():
                if getattr(obj, k) != v:
                    true = False
            
            if true: rv.append(obj)

        return rv
        '''

    created = models.CharField(max_length=5096, default=f"{{}}") # "by": user_id, "at": timestamp
    status = models.IntegerField(default=0)

    class Meta:
        abstract = True

    def _cancel_(self):
        self.status = 5