from rest_framework import serializers

from housing.models import Community, Listing, PredictionResult, PriceIndex


class ListingSerializer(serializers.ModelSerializer):
    community_name = serializers.CharField(source="community.name", default="", read_only=True)

    class Meta:
        model = Listing
        fields = [
            "id",
            "source_platform",
            "external_id",
            "title",
            "community_name",
            "district",
            "subdistrict",
            "total_price",
            "unit_price",
            "area",
            "layout",
            "floor_info",
            "orientation",
            "decoration",
            "build_year",
            "follow_count",
            "listing_url",
        ]


class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = [
            "id",
            "name",
            "district",
            "subdistrict",
            "average_unit_price",
            "build_year",
            "on_sale_count",
            "latitude",
            "longitude",
        ]


class PriceIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceIndex
        fields = "__all__"


class PredictionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionResult
        fields = "__all__"
