from django.contrib import admin

from housing.models import (
    Community,
    CrawlTask,
    Listing,
    ListingSnapshot,
    PredictionResult,
    PriceIndex,
)


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ("name", "district", "subdistrict", "average_unit_price", "build_year", "on_sale_count")
    search_fields = ("name", "district", "subdistrict")
    list_filter = ("district",)


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "district", "community", "total_price", "unit_price", "area", "source_platform")
    search_fields = ("title", "community__name", "district", "subdistrict")
    list_filter = ("district", "source_platform")


@admin.register(ListingSnapshot)
class ListingSnapshotAdmin(admin.ModelAdmin):
    list_display = ("listing", "snapshot_date", "total_price", "unit_price")
    list_filter = ("snapshot_date",)


@admin.register(PriceIndex)
class PriceIndexAdmin(admin.ModelAdmin):
    list_display = ("stat_month", "city", "size_segment", "mom_index", "yoy_index")
    list_filter = ("stat_month", "size_segment")


@admin.register(CrawlTask)
class CrawlTaskAdmin(admin.ModelAdmin):
    list_display = ("source_name", "task_type", "status", "record_count", "started_at", "finished_at")
    list_filter = ("status", "source_name", "task_type")


@admin.register(PredictionResult)
class PredictionResultAdmin(admin.ModelAdmin):
    list_display = ("target_level", "target_name", "model_name", "predicted_unit_price", "generated_at")
    list_filter = ("target_level", "model_name")
