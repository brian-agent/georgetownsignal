from rest_framework import serializers
from .models import NewsPost
class NewsPostSerializer(serializers.ModelSerializer):
    content_html       = serializers.CharField(read_only=True)
    is_service_article = serializers.BooleanField(read_only=True)
    shows_request_ui   = serializers.BooleanField(read_only=True)
    class Meta:
        model  = NewsPost
        fields = ['id','title','slug','excerpt','content_html','category',
                  'article_type','service_category_slug','is_service_article',
                  'shows_request_ui','tags','read_time_minutes','demand_snapshot','published_at']
