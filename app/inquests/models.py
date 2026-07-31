from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower


class Inquest(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=250, blank=True)
    overview = models.CharField(max_length=250)
    summary = models.CharField(max_length=15000)
    key_case_reason = models.CharField(max_length=250, blank=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    recommendation_count = models.PositiveSmallIntegerField(null=True, blank=True)
    response_to_recommendations = models.CharField(max_length=5000, blank=True)
    sitting_days = models.PositiveSmallIntegerField(null=True, blank=True)

    # TODO: once imports are completed, remove.
    import_metadata = models.CharField(null=True, blank=True)

    # TODO: make field required.
    presiding_officer = models.ForeignKey(
        'Participant',
        related_name='presiding_officer_inquests',
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True
    )

    jurisdiction = models.ForeignKey(
        'common.Jurisdiction',
        related_name='inquests',
        on_delete=models.PROTECT,
    )

    groups = models.ManyToManyField(
        'InquestGroup',
        related_name='inquests',
        blank=True,
    )

    keywords = models.ManyToManyField(
        'InquestKeyword',
        related_name='inquests',
        blank=True,
    )

    recommendation_recipients = models.ManyToManyField(
        'Party',
        related_name='inquests',
        blank=True,
    )

    participants = models.ManyToManyField(
        'Participant',
        related_name='participant_inquests',
        blank=True
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

    def clean(self):
        super().clean()
        if self.presiding_officer_id and not self.presiding_officer.roles.filter(category=Role.Category.POI).exists():
            raise ValidationError({
                'presiding_officer': 'Participant must have the presiding officer (POI) role.',
            })


class InquestDocument(models.Model):
    id = models.AutoField(primary_key=True)

    class DocumentType(models.TextChoices):
        VERDICT_AND_EXPLANATION = 'VERDICT_AND_EXPLANATION', 'Verdict & Explanation'
        RESPONSE_TO_RECOMMENDATIONS = 'RESPONSE_TO_RECOMMENDATIONS', 'Response to Recommendations'
        STANDING_RULING = 'STANDING_RULING', 'Standing Ruling'
        SCOPE = 'SCOPE', 'Scope'
        MEDIA = 'MEDIA', 'Media'

    name = models.CharField(max_length=250)
    document_type = models.CharField(max_length=50, choices=DocumentType.choices)
    date = models.DateField(null=True, blank=True)  # TODO: make field required.
    source = models.CharField(max_length=250)
    link = models.CharField(max_length=500)

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
        UNSPECIFIED = 'U', 'Unspecified/Undetermined'

    class MannerOfDeath(models.TextChoices):
        ACCIDENT = 'ACCIDENT', 'Accident'
        NATURAL = 'NATURAL', 'Natural'
        SUICIDE = 'SUICIDE', 'Suicide'
        HOMICIDE = 'HOMICIDE', 'Homicide'
        UNDETERMINED = 'UNDETERMINED', 'Undetermined'
        PENDING = 'PENDING', 'Pending'
        OTHER = 'OTHER', 'Other'

    class ReasonForInquest(models.TextChoices):
        PSYCHIATRIC_RESTRAINT = 'PSYCHIATRIC_RESTRAINT', 'Psychiatric Restraint'
        CUSTODY_INMATE = 'CUSTODY_INMATE', 'Custody-Inmate'
        CUSTODY_POLICE = 'CUSTODY_POLICE', 'Custody-Police'
        CONSTRUCTION = 'CONSTRUCTION', 'Construction'
        MINING = 'MINING', 'Mining'
        CHILD_CYFSA = 'CHILD_CYFSA', 'Child (CYFSA)'
        DISCRETIONARY = 'DISCRETIONARY', 'Discretionary inquest'
        PENDING = 'PENDING', 'Pending inquest'

    class InmateType(models.TextChoices):
        FEDERAL = 'FEDERAL', 'Federal'
        PROVINCIAL_REMAND = 'PROVINCIAL_REMAND', 'Provincial - On Remand'
        PROVINCIAL_SENTENCED = 'PROVINCIAL_SENTENCED', 'Provincial - Serving Sentence'
        PROVINCIAL_IMMIGRATION = 'PROVINCIAL_IMMIGRATION', 'Provincial - Immigration Detention'

    first_name = models.CharField(max_length=250)
    middle_name = models.CharField(max_length=250, blank=True)
    last_name = models.CharField(max_length=250)
    age = models.PositiveSmallIntegerField(null=True, blank=True)  # TODO: ensure consistency with DoB.
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=50, choices=Sex.choices)
    manner = models.CharField(max_length=50, choices=MannerOfDeath.choices)
    reason_for_inquest = models.CharField(  # TODO: make field required.
        max_length=50,
        choices=ReasonForInquest.choices,
        null=True,
        blank=True
    )
    cause_description = models.CharField(max_length=500, blank=True)
    # TODO: not currently populated by the importer.
    inmate_type = models.CharField(
        max_length=50,
        choices=InmateType.choices,
        null=True,
        blank=True,
    )

    cause = models.ForeignKey(
        'CauseOfDeath',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    # If field is null, inquest for deceased is pending.
    inquest = models.ForeignKey(
        'Inquest',
        related_name='deceased',
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = 'deceased'

    def __str__(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"


class CauseOfDeath(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=250)

    class Meta:
        verbose_name_plural = 'causes of death'

    def __str__(self):
        return self.name


class PartyType(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=250, unique=True)
    description = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.name


class Party(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=250, blank=True)
    also_known_as = models.CharField(max_length=250, blank=True)
    notes = models.CharField(max_length=1000, blank=True)

    party_type = models.ForeignKey(
        'PartyType',
        related_name='party',
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name_plural = 'parties'

        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                "party_type",
                name="party_unique_lower_name_party_type"),
        ]

    def __str__(self):
        if not self.name:
            return str(self.party_type)
        return f"{self.party_type}-{self.name}"


class InquestKeyword(models.Model):
    id = models.AutoField(primary_key=True)

    class Category(models.TextChoices):
        EQUITY = 'EQUITY', 'Equity'
        FACTOR = 'FACTOR', 'Factor'
        HEALTH = 'HEALTH', 'Health'
        INMATE = 'INMATE', 'Inmate'
        POLICE = 'POLICE', 'Police'
        WORKPLACE = 'WORKPLACE', 'Workplace'

    name = models.CharField(max_length=250, blank=True)
    category = models.CharField(max_length=250, choices=Category.choices)
    description = models.CharField(max_length=500, blank=True)
    synonyms = models.CharField(max_length=250, blank=True)

    class Meta:
        verbose_name = 'keyword'
        verbose_name_plural = 'keywords'

        constraints = [
            models.UniqueConstraint(Lower("name"), "category", name="inquest_keyword_unique_lower_name_category"),
        ]

    def __str__(self):
        category = InquestKeyword.Category(self.category).label
        if not self.name:
            return category
        return f"{category}-{self.name}"


class Role(models.Model):
    id = models.AutoField(primary_key=True)

    class Category(models.TextChoices):
        POI = 'POI', 'Presiding Officer'
        INQUEST_COUNSEL = 'INQUEST_COUNSEL', 'Inquest Counsel'
        PARTY_COUNSEL = 'PARTY_COUNSEL', 'Party Counsel'
        POLICE = 'POLICE', 'Police'
        PROGRAM_ADMINISTRATOR = 'PROGRAM_ADMINISTRATOR', 'Program Administrator'
        SUPPORT = 'SUPPORT', 'Support'
        OTHER = 'OTHER', 'Other'

    name = models.CharField(max_length=250, blank=True)
    category = models.CharField(max_length=50, choices=Category.choices)

    class Meta:
        verbose_name = 'role'
        verbose_name_plural = 'roles'

        constraints = [
            models.UniqueConstraint(Lower("name"), "category", name="role_unique_lower_name_category"),
        ]

    def __str__(self):
        category = Role.Category(self.category).label
        if not self.name:
            return category
        return f"{category}-{self.name}"


class Participant(models.Model):
    id = models.AutoField(primary_key=True)

    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)

    roles = models.ManyToManyField(
        'Role',
        related_name='participants',
        blank=True,
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class InquestGroup(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=250)
    notes = models.CharField(max_length=5000)

    class Meta:
        verbose_name = 'group'
        verbose_name_plural = 'groups'

        constraints = [
            models.UniqueConstraint(Lower("name"), name="inquest_group_unique_lower_name"),
        ]

    def __str__(self):
        return self.name
