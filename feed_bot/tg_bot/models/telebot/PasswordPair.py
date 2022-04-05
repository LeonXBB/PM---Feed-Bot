from django.db import models

class PasswordPair(models.Model):
    
    password_sha256 = models.CharField(max_length=5096)
    user_id = models.IntegerField(default=-1)

    #def generate(self, string): #TODO connect (via superadmin commands?)
    #   self.password_sha256 = hashlib.sha256(string.encode('utf8')).hexdigest()
    #   self.save()
    
    def assign_to_user(self, user_id):
        
        from .BotUser import BotUser

        self.user_id = user_id

        users = BotUser.objects.all()
        for user in users:
            if user.id == user_id:
                user.password_id = self.id
                user.save()
        
        self.save()