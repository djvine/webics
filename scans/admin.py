from django.contrib import admin

from scans.models import UserProfile, Experiment, Scan, ScanHistory, ScanDetectors, ScanData, ScanMetadata

class ScanAdmin(admin.ModelAdmin):
	 list_display = ('ts', 'scan_id', 'is_recent_scan')
	 list_filter = ['ts']

admin.site.register(UserProfile)
admin.site.register(Experiment)
admin.site.register(Scan, ScanAdmin)
admin.site.register(ScanHistory)
admin.site.register(ScanDetectors)
admin.site.register(ScanData)
admin.site.register(ScanMetadata)
