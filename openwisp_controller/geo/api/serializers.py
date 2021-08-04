from django.urls import reverse
from rest_framework import serializers
from rest_framework.serializers import IntegerField, SerializerMethodField
from rest_framework_gis import serializers as gis_serializers
from swapper import load_model

from openwisp_users.api.mixins import FilterSerializerByOrgManaged
from openwisp_utils.api.serializers import ValidatedModelSerializer

Device = load_model('config', 'Device')
Location = load_model('geo', 'Location')
DeviceLocation = load_model('geo', 'DeviceLocation')
FloorPlan = load_model('geo', 'FloorPlan')


class LocationDeviceSerializer(ValidatedModelSerializer):
    admin_edit_url = SerializerMethodField('get_admin_edit_url')

    def get_admin_edit_url(self, obj):
        return self.context['request'].build_absolute_uri(
            reverse(f'admin:{obj._meta.app_label}_device_change', args=(obj.id,))
        )

    class Meta:
        model = Device
        fields = '__all__'


class GeoJsonLocationSerializer(gis_serializers.GeoFeatureModelSerializer):
    device_count = IntegerField()

    class Meta:
        model = Location
        geo_field = 'geometry'
        fields = '__all__'


class BaseSerializer(FilterSerializerByOrgManaged, ValidatedModelSerializer):
    pass


class FloorPlanSerializer(BaseSerializer):
    class Meta:
        model = FloorPlan
        fields = (
            'id',
            'floor',
            'image',
            'location',
            'created',
            'modified',
        )
        read_only_fields = ('created', 'modified')

    def validate(self, data):
        if data.get('location'):
            data['organization'] = data.get('location').organization
        instance = self.instance or self.Meta.model(**data)
        instance.full_clean()
        return data


class LocationModelSerializer(BaseSerializer):
    class Meta:
        model = Location
        fields = (
            'id',
            'organization',
            'name',
            'type',
            'is_mobile',
            'address',
            'geometry',
            'created',
            'modified',
        )
        read_only_fields = ('created', 'modified')


class NestedtLocationSerializer(gis_serializers.GeoFeatureModelSerializer):
    class Meta:
        model = Location
        geo_field = 'geometry'
        fields = (
            'type',
            'is_mobile',
            'name',
            'address',
            'geometry',
        )


class NestedFloorplanSerializer(serializers.ModelSerializer):
    class Meta:
        model = FloorPlan
        fields = (
            'floor',
            'image',
        )


class DeviceLocationSerializer(serializers.ModelSerializer):
    location = NestedtLocationSerializer()
    floorplan = NestedFloorplanSerializer()

    class Meta:
        model = DeviceLocation
        fields = (
            'location',
            'floorplan',
            'indoor',
        )

    def update(self, instance, validated_data):
        if 'location' in validated_data:
            location_data = validated_data.pop('location')
            location = instance.location
            if location.type == 'indoor' and location_data.get('type') == 'outdoor':
                instance.floorplan = None
                validated_data['indoor'] = ""
                location.type = location_data.get('type', location.type)
            location.is_mobile = location_data.get('is_mobile', location.is_mobile)
            location.name = location_data.get('name', location.name)
            location.address = location_data.get('address', location.address)
            location.geometry = location_data.get('geometry', location.geometry)
            location.save()

        if 'floorplan' in validated_data:
            floorplan_data = validated_data.pop('floorplan')
            if instance.location.type == 'indoor':
                if instance.floorplan:
                    floorplan = instance.floorplan
                    floorplan.floor = floorplan_data.get('floor', floorplan.floor)
                    floorplan.image = floorplan_data.get('image', floorplan.image)
                    floorplan.full_clean()
                    floorplan.save()
            if (
                instance.location.type == 'outdoor'
                and location_data['type'] == 'indoor'
            ):
                fl = FloorPlan.objects.create(
                    floor=floorplan_data['floor'],
                    organization=instance.content_object.organization,
                    image=floorplan_data['image'],
                    location=instance.location,
                )
                instance.location.type = 'indoor'
                instance.location.full_clean()
                instance.location.save()
                instance.floorplan = fl

        return super().update(instance, validated_data)
