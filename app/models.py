from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Movie(models.Model):
    m_id= models.CharField(primary_key=True,max_length=32)
    name= models.CharField(max_length=64)
    director= models.CharField(max_length=64,null=True, blank=True)
    year= models.CharField(max_length=4,null=True, blank=True)
    rating= models.CharField(max_length=4,null=True, blank=True)
    duration= models.CharField(max_length=4,null=True, blank=True)
    trailer= models.CharField(max_length=128,null=True, blank=True)
    review= models.CharField(max_length=128,null=True, blank=True)
    cover= models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name 

class Group(models.Model):
    name= models.CharField(max_length=64, unique=True)
    c_time= models.DateTimeField(auto_now_add= True)
    movies= models.ManyToManyField(Movie)

    def __str__(self):
        return self.name 
    class Meta:
        ordering= ["-c_time"]
        verbose_name= "Group"
        verbose_name_plural= "Group"

class User(models.Model):
    name= models.CharField(max_length=64,unique=True)
    password= models.CharField(max_length=64)
    email= models.EmailField(unique=True)
    c_time= models.DateTimeField(auto_now_add= True)

    members= models.ManyToManyField(Group, through='Membership')

    def __str__(self):
        return self.name
    class Meta:
        ordering= ["-c_time"]
        verbose_name= "User"
        verbose_name_plural= "User"

class Membership(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add= True)
    title = models.CharField(choices=(('Moderator','Moderator'),('Member','Member')),default='Member',max_length=10)

    class Meta:
        unique_together=("member","group")

class Event(models.Model):
    name= models.CharField(max_length=64)
    group= models.ForeignKey(Group, on_delete=models.CASCADE)
    start= models.DateTimeField()
    end= models.DateTimeField()
    movie= models.ForeignKey(Movie, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

class Voting(models.Model):
    event= models.ForeignKey(Event, on_delete=models.CASCADE, unique=True)
    group= models.ForeignKey(Group, on_delete=models.CASCADE)
    movies= models.ManyToManyField(Movie, through='Votes')

    def __str__(self):
        return self.event.name

class Votes(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    voting = models.ForeignKey(Voting, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)

    class Meta:
        ordering= ["count"]

class HasVoted(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    voting = models.ForeignKey(Voting, on_delete=models.CASCADE)


