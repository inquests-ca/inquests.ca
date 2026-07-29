from django.db import models


class Jurisdiction(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)

    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.name
