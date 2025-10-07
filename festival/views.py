from django.shortcuts import render
from festival.models import FestivalSale
from django.utils import timezone

now = timezone.now()
FestivalSale.objects.filter(start_date__lte=now, end_date__gte=now, is_active=True)

