import csv
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db.models import Avg, Count

from housing.models import Community, Listing, PredictionResult, PriceIndex


class Command(BaseCommand):
    help = "Import scraped sample CSV data into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--listings",
            default="data_pipeline/outputs/cleaned_lianjia_listings.csv",
            help="Path to cleaned listings CSV",
        )
        parser.add_argument(
            "--price-indices",
            default="data_pipeline/outputs/official_price_indices.csv",
            help="Path to official price indices CSV",
        )

    def handle(self, *args, **options):
        listings_path = Path(options["listings"])
        indices_path = Path(options["price_indices"])

        if listings_path.exists():
            self.import_listings(listings_path)
        if indices_path.exists():
            self.import_price_indices(indices_path)
        self.generate_predictions()
        self.stdout.write(self.style.SUCCESS("Sample data import complete."))

    def import_listings(self, path: Path) -> None:
        with path.open("r", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                community, _ = Community.objects.get_or_create(
                    name=row["community_name"] or "Unknown community",
                    defaults={
                        "district": row["district"] or "Unknown",
                        "subdistrict": row["subdistrict"] or "",
                        "average_unit_price": Decimal(row["unit_price"] or "0"),
                        "build_year": int(row["build_year"]) if row["build_year"] else None,
                    },
                )
                Listing.objects.update_or_create(
                    source_platform=row["source_platform"],
                    external_id=row["external_id"],
                    defaults={
                        "title": row["title"],
                        "listing_url": row["listing_url"],
                        "community": community,
                        "district": row["district"] or "Unknown",
                        "subdistrict": row["subdistrict"] or "",
                        "total_price": Decimal(row["total_price"] or "0"),
                        "unit_price": Decimal(row["unit_price"] or "0"),
                        "area": Decimal(row["area"] or "0"),
                        "layout": row["layout"] or "",
                        "floor_info": row["floor_info"] or "",
                        "orientation": row["orientation"] or "",
                        "decoration": row["decoration"] or "",
                        "build_year": int(row["build_year"]) if row["build_year"] else None,
                        "follow_count": int(row["follow_count"] or "0"),
                        "tags": row["tags"].split("|") if row["tags"] else [],
                    },
                )

    def import_price_indices(self, path: Path) -> None:
        with path.open("r", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                PriceIndex.objects.update_or_create(
                    stat_month=row["stat_month"],
                    city=row["city"],
                    house_type=row["house_type"],
                    size_segment=row["size_segment"],
                    defaults={
                        "mom_index": Decimal(row["mom_index"] or "0"),
                        "yoy_index": Decimal(row["yoy_index"] or "0"),
                    },
                )

    def generate_predictions(self) -> None:
        for row in (
            Listing.objects.values("district")
            .annotate(avg_unit_price=Avg("unit_price"), listing_count=Count("id"))
            .order_by("district")
        ):
            average = Decimal(row["avg_unit_price"] or "0")
            PredictionResult.objects.update_or_create(
                target_level="district",
                target_name=row["district"],
                model_name="baseline_average",
                defaults={
                    "predicted_unit_price": average,
                    "confidence_lower": average * Decimal("0.97"),
                    "confidence_upper": average * Decimal("1.03"),
                    "features_snapshot": {
                        "district": row["district"],
                        "listing_count": row["listing_count"],
                    },
                },
            )
