import csv
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.test import TestCase

from housing.models import Community, Listing, PredictionResult, PriceIndex


class ImportSampleDataCommandTests(TestCase):
    def test_import_sample_data_command_loads_csv_files(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            listings_path = temp_path / "listings.csv"
            indices_path = temp_path / "indices.csv"

            with listings_path.open("w", newline="", encoding="utf-8-sig") as fh:
                writer = csv.DictWriter(
                    fh,
                    fieldnames=[
                        "source_platform",
                        "external_id",
                        "title",
                        "listing_url",
                        "district",
                        "subdistrict",
                        "community_name",
                        "total_price",
                        "unit_price",
                        "area",
                        "layout",
                        "floor_info",
                        "orientation",
                        "decoration",
                        "build_year",
                        "follow_info",
                        "follow_count",
                        "tags",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "source_platform": "lianjia",
                        "external_id": "LJ-9001",
                        "title": "Sample listing",
                        "listing_url": "https://example.com/1",
                        "district": "Pudong",
                        "subdistrict": "Huamu",
                        "community_name": "Century Garden",
                        "total_price": "620",
                        "unit_price": "78481",
                        "area": "79",
                        "layout": "2B1L",
                        "floor_info": "high floor",
                        "orientation": "south",
                        "decoration": "fine",
                        "build_year": "2008",
                        "follow_info": "10 people follow",
                        "follow_count": "10",
                        "tags": "near subway|vr",
                    }
                )

            with indices_path.open("w", newline="", encoding="utf-8-sig") as fh:
                writer = csv.DictWriter(
                    fh,
                    fieldnames=[
                        "stat_month",
                        "city",
                        "house_type",
                        "size_segment",
                        "mom_index",
                        "yoy_index",
                        "average_index",
                        "source_url",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "stat_month": "2026-02",
                        "city": "Shanghai",
                        "house_type": "second_hand",
                        "size_segment": "overall",
                        "mom_index": "100.2",
                        "yoy_index": "93.8",
                        "average_index": "93.5",
                        "source_url": "https://example.com/idx",
                    }
                )

            call_command(
                "import_sample_data",
                listings=str(listings_path),
                price_indices=str(indices_path),
            )

        self.assertEqual(Community.objects.count(), 1)
        self.assertEqual(Listing.objects.count(), 1)
        self.assertEqual(PriceIndex.objects.count(), 1)
        self.assertEqual(PredictionResult.objects.count(), 1)
