from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class FileSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        max_upload_size = settings.MAX_UPLOAD_SIZE
        if value.size > max_upload_size:
            raise serializers.ValidationError(
                self.default_error_messages['file_size'] % {
                    'max_size': filesizeformat(max_upload_size),
                    'size': filesizeformat(value.size)})
        return value

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.default_error_messages['file_size'] = _(
            'Select a file size less than or equal to %(max_size)s. The selected file size is %(size)s.')


class SupportSerializer(FileSerializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField()
