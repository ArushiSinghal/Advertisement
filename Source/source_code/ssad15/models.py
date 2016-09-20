from __future__ import unicode_literals

from django.db import models



class zone(models.Model):
    total_bundles=models.IntegerField(default=10)
    bundles_used=models.IntegerField(default=0)
    cost=models.DecimalField(default=0,max_digits=10,decimal_places=2)
    bottom_left_coordinate_x=models.DecimalField(max_digits=9,decimal_places=6,default=0)
    bottom_left_coordinate_y=models.DecimalField(max_digits=9,decimal_places=6,default=0)

class slot(models.Model):
    zone_id = models.ForeignKey(zone, on_delete=models.CASCADE)
    slot_no = models.IntegerField(default=0)

class advertisement(models.Model):
    slot_id = models.ForeignKey(slot, on_delete=models.CASCADE)
    upload = models.FileField(upload_to='uploads/')


#to store  device ids of configured devices
#to be decided if username of device will be alphanumeric or numeric string
class devices(models.Model):
    username=models.CharField(max_length=10,unique=True)
