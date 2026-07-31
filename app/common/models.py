from django.db import models


class Jurisdiction(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=250)
    code = models.CharField(max_length=10, unique=True)

    does_conduct_inquests = models.BooleanField(default=False)
    name_for_inquest = models.CharField(max_length=250, blank=True)

    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.name
