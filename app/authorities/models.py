from django.db import models
from django.db.models.functions import Lower


class Authority(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=250)
    overview = models.CharField(max_length=500)
    summary = models.CharField(max_length=5000)
    notes = models.CharField(max_length=5000, blank=True)
    quotes = models.CharField(max_length=5000, blank=True)
    key_case_reason = models.CharField(max_length=250, blank=True)
    is_judicial_review = models.BooleanField()

    jurisdiction = models.ForeignKey(
        'common.Jurisdiction',
        related_name='authorities',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    citations = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='cited_by',
        blank=True,
    )

    groups = models.ManyToManyField(
        'AuthorityGroup',
        related_name='authorities',
        blank=True,
    )

    keywords = models.ManyToManyField(
        'AuthorityKeyword',
        related_name='authorities',
        blank=True,
    )

    class Meta:
        verbose_name_plural = 'authorities'

    def __str__(self):
        return self.name

    @property
    def level(self):
        """Authority level, derived from highest-ranked document."""
        document = self.document.filter(level__isnull=False).order_by('-level__rank').first()
        return document.level if document else None


class AuthorityLevel(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=250, unique=True)
    rank = models.SmallIntegerField(unique=True)

    class Meta:
        verbose_name = 'level'
        verbose_name_plural = 'levels'

    def __str__(self):
        return self.name


class AuthorityDocument(models.Model):
    id = models.AutoField(primary_key=True)

    class DocumentType(models.TextChoices):
        CASE_LAW = 'CASE_LAW', 'Case Law'
        REFERENCE = 'REFERENCE', 'Reference'
        COMMISSION_REPORT = 'COMMISSION_REPORT', 'Commission Report'
        STATUTE = 'STATUTE', 'Statute'
        MEDIA = 'MEDIA', 'Media'
        SUMMARY = 'SUMMARY', 'Summary'

    name = models.CharField(max_length=250)
    document_type = models.CharField(max_length=50, choices=DocumentType.choices)
    date = models.DateField(null=True, blank=True)
    source = models.CharField(max_length=250)
    link = models.CharField(max_length=500)
    citation = models.CharField(max_length=500, blank=True)
    is_primary = models.BooleanField(default=False)

    level = models.ForeignKey(
        'AuthorityLevel',
        related_name='documents',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    jurisdiction = models.ForeignKey(
        'common.Jurisdiction',
        related_name='authority_documents',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    authority = models.ForeignKey(
        'Authority',
        related_name='document',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'document'
        verbose_name_plural = 'documents'


class AuthorityKeyword(models.Model):
    id = models.AutoField(primary_key=True)

    class Category(models.TextChoices):
        INQUEST = 'INQUEST', 'Inquest'
        FACTOR = 'FACTOR', 'Factor'
        EVIDENCE = 'EVIDENCE', 'Evidence'

    name = models.CharField(max_length=250, blank=True)
    category = models.CharField(max_length=250, choices=Category.choices)
    description = models.CharField(max_length=500, blank=True)
    synonyms = models.CharField(max_length=250, blank=True)

    class Meta:
        verbose_name = 'keyword'
        verbose_name_plural = 'keywords'

        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                "category",
                name="authority_keyword_unique_lower_name_category"),
        ]

    def __str__(self):
        category = AuthorityKeyword.Category(self.category).label
        if not self.name:
            return category
        return f"{category}-{self.name}"


class AuthorityGroup(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=250)
    notes = models.CharField(max_length=5000)

    class Meta:
        verbose_name = 'group'
        verbose_name_plural = 'groups'

        constraints = [
            models.UniqueConstraint(Lower("name"), name="authority_group_unique_lower_name"),
        ]

    def __str__(self):
        return self.name
