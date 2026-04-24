from decimal import Decimal

from django.test import TestCase

from housing.models import Community, Listing, PredictionResult


class HousingApiTests(TestCase):
    def setUp(self) -> None:
        community = Community.objects.create(
            name="Century Garden",
            district="Pudong",
            subdistrict="Huamu",
            average_unit_price=Decimal("78000.00"),
            build_year=2008,
            on_sale_count=12,
        )
        Listing.objects.create(
            source_platform="lianjia",
            external_id="LJ-1001",
            title="Century Garden bright two-bedroom",
            community=community,
            district="Pudong",
            subdistrict="Huamu",
            total_price=Decimal("620.00"),
            unit_price=Decimal("78481.00"),
            area=Decimal("79.00"),
            layout="2B1L",
            floor_info="high floor",
            orientation="south-north",
            build_year=2008,
        )
        Listing.objects.create(
            source_platform="lianjia",
            external_id="LJ-1002",
            title="Century Garden renovated three-bedroom",
            community=community,
            district="Pudong",
            subdistrict="Huamu",
            total_price=Decimal("930.00"),
            unit_price=Decimal("80172.00"),
            area=Decimal("116.00"),
            layout="3B1L",
            floor_info="middle floor",
            orientation="south",
            build_year=2008,
        )
        PredictionResult.objects.create(
            target_level="district",
            target_name="Pudong",
            model_name="random_forest",
            predicted_unit_price=Decimal("79888.00"),
            confidence_lower=Decimal("78000.00"),
            confidence_upper=Decimal("81500.00"),
            features_snapshot={"district": "Pudong", "listing_count": 2},
        )

    def test_overview_endpoint_returns_metrics(self) -> None:
        response = self.client.get("/api/overview/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["metrics"]["listing_count"], 2)
        self.assertEqual(payload["metrics"]["community_count"], 1)
        self.assertIn("district_distribution", payload["charts"])

    def test_listings_endpoint_returns_items(self) -> None:
        response = self.client.get("/api/listings/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 2)
        self.assertEqual(len(payload["results"]), 2)
        self.assertEqual(payload["results"][0]["community_name"], "Century Garden")

    def test_district_stats_endpoint_returns_aggregations(self) -> None:
        response = self.client.get("/api/district-stats/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["results"][0]["district"], "Pudong")
        self.assertEqual(payload["results"][0]["listing_count"], 2)
