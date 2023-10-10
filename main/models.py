from django.db import models
from django.contrib.auth.models import User

class Record(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	subname = models.CharField(max_length=50)
	topic = models.CharField(max_length=50)
	time_taken = models.DurationField(blank=True, null=True)
	start_at = models.DateTimeField(null=True, blank=True)
	done_at = models.DateTimeField(null=True, blank=True)
	queue_no = models.IntegerField(default=0)
	def __str__(self):
		return(f"{self.subname} {self.topic}")

class UserSettings(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	daily_target_hours = models.DecimalField(max_digits=5, decimal_places=2, default=8.0)
	target_goal = models.TextField(blank=True)
	thestart_date = models.DateField(blank=True, null=True)
	target_date = models.DateField(blank=True, null=True)
	max_queued = models.PositiveIntegerField(default=1)
	def __str__(self):
		return(f"{self.user} {self.daily_target_hours}")
