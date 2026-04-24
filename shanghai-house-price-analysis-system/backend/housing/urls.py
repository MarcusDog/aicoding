from django.urls import path

from housing.views import (
    CommunityListAPIView,
    DistrictStatsAPIView,
    ListingListAPIView,
    OverviewAPIView,
    PredictionListAPIView,
    PriceIndexListAPIView,
)

urlpatterns = [
    path("overview/", OverviewAPIView.as_view(), name="overview"),
    path("listings/", ListingListAPIView.as_view(), name="listings"),
    path("communities/", CommunityListAPIView.as_view(), name="communities"),
    path("district-stats/", DistrictStatsAPIView.as_view(), name="district-stats"),
    path("price-indices/", PriceIndexListAPIView.as_view(), name="price-indices"),
    path("predictions/", PredictionListAPIView.as_view(), name="predictions"),
]
