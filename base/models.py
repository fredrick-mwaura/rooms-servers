from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


class User(AbstractUser):
  name = models.CharField(max_length=200, null=True)
  email = models.EmailField(max_length=255, unique=True, null=True)
  bio = models.TextField(null=True)
  avatar = models.ImageField(null=True, default="avatar.svg")
  
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = []

class Topic(models.Model):
  name = models.CharField(max_length=200)
  slug = models.SlugField(unique=True, blank=True)

  def __str__(self):
    return self.name
  
  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.name)
      original_slug = self.slug
      counter = 1
      while Topic.objects.filter(slug=self.slug).exists():
        self.slug = f"{original_slug}-{counter}"
        counter += 1
    super().save(*args, **kwargs)    

class Room(models.Model):
  host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
  name = models.CharField(max_length=200)
  description = models.TextField(null=True, blank=True)
  participants = models.ManyToManyField(User, related_name='parcipants', blank=True) 
  updated = models.DateTimeField(auto_now=True)
  created = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-updated', '-created']

  def __str__(self):
    return self.name
  
class Message(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  room = models.ForeignKey(Room, on_delete=models.CASCADE)
  body = models.TextField()
  updated = models.DateTimeField(auto_now=True)
  created = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-updated', '-created']

  def __str__(self):
    return self.body[0:47] + '...' if len(self.body) > 50 else self.body