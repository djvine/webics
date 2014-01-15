from django.contrib import admin
from scans.models import Scan, ScanData

class ScanAdmin(admin.ModelAdmin):
	 list_display = ('pvname', 'ts', 'is_recent_scan')
	 list_filter = ['ts']

admin.site.register(Scan, ScanAdmin)
admin.site.register(ScanData)
