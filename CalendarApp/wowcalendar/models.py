import datetime
import os
from django.db import models
from django.conf import settings

class Profile(models.Model):
  user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=False,  null=False)
  email = models.EmailField(max_length=254, blank=False, null=False, default='tempEmail@domain.com')
  profile_username = models.CharField(max_length=50, blank=False, null=False, default='temp_username')
  role = models.CharField(max_length=50, blank=True, default='User')
  description = models.CharField(max_length=150, blank=True, null=True)
  created_on = models.DateTimeField(auto_now=False, default=datetime.datetime.now)

class Character(models.Model):
  profile_id = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=False, null=False)
  name = models.CharField(max_length=100, blank=False, null=False, unique=True)
  class_id = models.IntegerField(default=0)
  class_name = models.CharField(max_length=100, blank=False, null=False, default="Warrior")
  spec = models.CharField(max_length=100, blank=True, null=True)
  role = models.CharField(max_length=100, blank=True, null=True)
  
  def __str__(self):
    return self.name
  
class Class(models.Model):
  name = models.CharField(max_length=100, blank=False, null=False, unique=True)
  color = models.CharField(max_length=100, blank=False, null=False)
  
  def __str__(self):
    return self.name

class Spec(models.Model):
  class_id = models.ForeignKey(Class, on_delete=models.CASCADE, blank=False, null=False)
  name = models.CharField(max_length=100, blank=False, null=False)
  
class Event(models.Model):
  name = models.CharField(max_length=100, blank=False, null=False, default='Vault of Incarnates')
  start_date = models.CharField(max_length=20, blank=False, null=False, default='1.1.2023')
  end_date = models.CharField(max_length=20, blank=False, null=False, default='1.1.2023')
  start_time = models.CharField(max_length=100, blank=False, null=False, default='21:00')
  end_time = models.CharField(max_length=100, blank=False, null=False, default='24:00')
  deadline = models.CharField(max_length=100, blank=False, null=False, default='16:30')
  description = models.CharField(max_length=100, blank=True, null=True, default='Пред инстанцията в 20:45')

#status:
# - unknown     - 0
# - signed up   - 1
# - signed off  - 2
# - backup      - 3
# - guest       - 4
# - confirmed   - 5
class Participant(models.Model):
  event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=False, null=False)
  profile_id = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=False, null=False)
  character = models.ForeignKey(Character, on_delete=models.CASCADE, blank=False, null=False)
  status = models.IntegerField(default=0)