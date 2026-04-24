from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Community(TimestampedModel):
    name = models.CharField(max_length=120, unique=True)
    district = models.CharField(max_length=64)
    subdistrict = models.CharField(max_length=64, blank=True)
    average_unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    build_year = models.PositiveIntegerField(null=True, blank=True)
    on_sale_count = models.PositiveIntegerField(default=0)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ["district", "name"]

    def __str__(self) -> str:
        return self.name


class Listing(TimestampedModel):
    source_platform = models.CharField(max_length=32)
    external_id = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    listing_url = models.URLField(blank=True)
    community = models.ForeignKey(
        Community,
        related_name="listings",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    district = models.CharField(max_length=64)
    subdistrict = models.CharField(max_length=64, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    area = models.DecimalField(max_digits=8, decimal_places=2)
    layout = models.CharField(max_length=64, blank=True)
    floor_info = models.CharField(max_length=64, blank=True)
    orientation = models.CharField(max_length=64, blank=True)
    decoration = models.CharField(max_length=64, blank=True)
    build_year = models.PositiveIntegerField(null=True, blank=True)
    elevator = models.CharField(max_length=32, blank=True)
    tags = models.JSONField(default=list, blank=True)
    follow_count = models.PositiveIntegerField(default=0)
    listed_at = models.DateField(null=True, blank=True)
    last_crawled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-unit_price", "-total_price", "id"]
        unique_together = ("source_platform", "external_id")

    def __str__(self) -> str:
        return f"{self.title} ({self.source_platform})"


class ListingSnapshot(TimestampedModel):
    listing = models.ForeignKey(Listing, related_name="snapshots", on_delete=models.CASCADE)
    snapshot_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["-snapshot_date", "-id"]
        unique_together = ("listing", "snapshot_date")

    def __str__(self) -> str:
        return f"{self.listing_id}-{self.snapshot_date}"


class PriceIndex(TimestampedModel):
    stat_month = models.CharField(max_length=7)
    city = models.CharField(max_length=64, default="Shanghai")
    house_type = models.CharField(max_length=32, default="second_hand")
    size_segment = models.CharField(max_length=64)
    mom_index = models.DecimalField(max_digits=8, decimal_places=2)
    yoy_index = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ["stat_month", "size_segment"]
        unique_together = ("stat_month", "city", "house_type", "size_segment")

    def __str__(self) -> str:
        return f"{self.stat_month}-{self.size_segment}"


class CrawlTask(TimestampedModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    source_name = models.CharField(max_length=64)
    task_type = models.CharField(max_length=32)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    record_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.source_name}-{self.task_type}-{self.status}"


class PredictionResult(TimestampedModel):
    target_level = models.CharField(max_length=32)
    target_name = models.CharField(max_length=120)
    model_name = models.CharField(max_length=64)
    predicted_unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    confidence_lower = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    confidence_upper = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    features_snapshot = models.JSONField(default=dict, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-generated_at"]

    def __str__(self) -> str:
        return f"{self.target_level}:{self.target_name}"
