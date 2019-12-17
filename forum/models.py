from django.db import models
from Anlz_app.models import User
from django.utils import timezone
# Create your models here.
class Forum(models.Model):

    title = models.CharField(max_length=60)
    created = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    description = models.CharField(max_length=255,blank=True )

    def num_post(self):
        return sum([threads.num_post() for threads in self.thread_set.all()])

    def num_threads(self):
        return self.thread_set.count()

    def last_post(self):
        if self.thread_set.count():
            last = None
            for thread in self.thread_set.all():
                l = thread.last_post()
                if l:
                    if not last:
                        last = l
                    elif l.created > last.created:
                        last = l
            return last

    def __str__(self):
        return self.title

class thread(models.Model):
    title = models.CharField(max_length =60)
    created = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(User,blank=True,null=True,on_delete=models.CASCADE)
    forum = models.ForeignKey(Forum,on_delete=models.CASCADE)
    description = models.CharField(max_length =255 ,blank=True)

    def __str__(self):
        return str(self.creator) + " - "  + self.title

    def num_post(self):
        return self.post_set.count()

    def num_replies(self):
        return self.post_set.count()

    def last_post(self):
        if self.post_set.count():
            return self.post_set.order_by('-created')[0]

class Post(models.Model):
    title = models.CharField(max_length=60)
    created = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(User,blank=True,on_delete=models.CASCADE)
    thread = models.ForeignKey(thread,on_delete=models.CASCADE)
    body = models.TextField(max_length=1000)

    def __str__(self):
        return "{} - {} - {}".format(self.creator,self.thread,self.title)

    def short(self):
        return "{} - {}".format(self.creator,self.title)
    short.allow_tags = True


class Comment(models.Model):
    body = models.TextField(max_length=10000)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.body

class Contact(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    text = models.TextField(max_length=500)
