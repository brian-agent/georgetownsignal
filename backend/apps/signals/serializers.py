from rest_framework import serializers
from .models import Signal
class SignalSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Signal
        fields = ['id','business_name','service','mentions','source','sentiment','timestamp']
