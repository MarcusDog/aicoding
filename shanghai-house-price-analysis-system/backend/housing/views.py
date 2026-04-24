from rest_framework.response import Response
from rest_framework.views import APIView

from housing.models import Community, Listing, PredictionResult, PriceIndex
from housing.serializers import (
    CommunitySerializer,
    ListingSerializer,
    PredictionResultSerializer,
    PriceIndexSerializer,
)
from housing.services import build_overview_payload, get_district_stats


class OverviewAPIView(APIView):
    def get(self, request):
        return Response(build_overview_payload())


class ListingListAPIView(APIView):
    def get(self, request):
        queryset = Listing.objects.select_related("community").all()
        keyword = request.query_params.get("keyword")
        district = request.query_params.get("district")
        if keyword:
            queryset = queryset.filter(title__icontains=keyword)
        if district:
            queryset = queryset.filter(district=district)
        serializer = ListingSerializer(queryset, many=True)
        return Response({"count": queryset.count(), "results": serializer.data})


class CommunityListAPIView(APIView):
    def get(self, request):
        queryset = Community.objects.all()
        serializer = CommunitySerializer(queryset, many=True)
        return Response({"count": queryset.count(), "results": serializer.data})


class DistrictStatsAPIView(APIView):
    def get(self, request):
        return Response({"results": get_district_stats()})


class PriceIndexListAPIView(APIView):
    def get(self, request):
        queryset = PriceIndex.objects.all()
        serializer = PriceIndexSerializer(queryset, many=True)
        return Response({"count": queryset.count(), "results": serializer.data})


class PredictionListAPIView(APIView):
    def get(self, request):
        queryset = PredictionResult.objects.all()
        serializer = PredictionResultSerializer(queryset, many=True)
        return Response({"count": queryset.count(), "results": serializer.data})
