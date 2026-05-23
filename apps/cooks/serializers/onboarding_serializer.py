from rest_framework import serializers


class CookOnboardingNameSerializer(serializers.Serializer):
    displayName = serializers.CharField(max_length=120)


class CookOnboardingProfileSerializer(serializers.Serializer):
    bio = serializers.CharField(allow_blank=True, required=False)
    avatarUrl = serializers.URLField(required=False, allow_null=True)
    cuisineTypes = serializers.ListField(child=serializers.CharField(max_length=50), allow_empty=True)


class CookOnboardingSpecialtiesSerializer(serializers.Serializer):
    specialties = serializers.ListField(child=serializers.CharField(max_length=50), allow_empty=True)
    capacityPerDay = serializers.IntegerField(min_value=1, required=False, allow_null=True)


class CookOnboardingServiceAreaSerializer(serializers.Serializer):
    areaLabel = serializers.CharField(max_length=120)
    radiusKm = serializers.IntegerField(min_value=1)
    coordinates = serializers.DictField()


class CookOnboardingPayoutSerializer(serializers.Serializer):
    payoutMethod = serializers.CharField(max_length=20)
    payoutNumber = serializers.CharField(max_length=30)
    payoutAccountName = serializers.CharField(max_length=120)
