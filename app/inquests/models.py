from django.db import models


class Inquest(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=255, blank=True)
    overview = models.CharField(max_length=255)
    summary = models.CharField(max_length=5000)
    key_case_reason = models.CharField(max_length=255, blank=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # TODO: once imports are completed, remove.
    import_metadata = models.CharField(null=True, blank=True)

    presiding_officer = models.ForeignKey(
        'PresidingOfficer',
        related_name='inquests',
        on_delete=models.PROTECT,
    )

    jurisdiction = models.ForeignKey(
        'common.Jurisdiction',
        related_name='inquests',
        on_delete=models.PROTECT,
    )

    keywords = models.ManyToManyField(
        'InquestKeyword',
        related_name='inquests',
        blank=True,
    )

    def __str__(self):
        string = ""
        if self.start_date is not None:
            string += f"[{self.jurisdiction.code}-{self.start_date.year}]"
        else:
            string += f"[{self.jurisdiction.code}]"

        deceased = self.deceased.first()
        if deceased is not None:
            string += f" {deceased}"

        if self.name:
            string += f" - {self.name}"

        return string


class InquestDocument(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=255)
    date = models.DateField()
    source = models.CharField(max_length=255)
    link = models.CharField(max_length=255)

    inquest = models.ForeignKey(
        'Inquest',
        related_name='documents',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'document'
        verbose_name_plural = 'documents'


class Deceased(models.Model):
    id = models.AutoField(primary_key=True)

    class Sex(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    class MannerOfDeath(models.TextChoices):
        ACCIDENT = 'ACCIDENT', 'Accident'
        NATURAL = 'NATURAL', 'Natural'
        SUICIDE = 'SUICIDE', 'Suicide'
        HOMICIDE = 'HOMICIDE', 'Homicide'
        UNDETERMINED = 'UNDETERMINED', 'Undetermined'
        PENDING = 'PENDING', 'Pending'
        OTHER = 'OTHER', 'Other'

    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=50, choices=Sex.choices)
    manner = models.CharField(max_length=50, choices=MannerOfDeath.choices)

    cause = models.ForeignKey(
        'CauseOfDeath',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    inquest = models.ForeignKey(
        'Inquest',
        on_delete=models.CASCADE,
        related_name='deceased'
    )

    class Meta:
        verbose_name_plural = 'deceased'

    def __str__(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"


class CauseOfDeath(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'causes of death'

    def __str__(self):
        return self.name


class RecommendationRecipient(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=255)

    inquests = models.ManyToManyField('Inquest', blank=True)


class InquestKeyword(models.Model):
    id = models.AutoField(primary_key=True)

    class Category(models.TextChoices):
        EQUITY = 'EQUITY', 'Equity'
        FACTOR = 'FACTOR', 'Factor'
        HEALTH = 'HEALTH', 'Health'
        INMATE = 'INMATE', 'Inmate'
        POLICE = 'POLICE', 'Police'
        WORKPLACE = 'WORKPLACE', 'Workplace'

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255, choices=Category.choices)
    description = models.CharField(max_length=255, blank=True)
    synonyms = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'keyword'
        verbose_name_plural = 'keywords'


class PresidingOfficer(models.Model):
    id = models.AutoField(primary_key=True)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
