from django.contrib import admin
from .models import Profile, RoomAssignmentLog


class RoomAssignmentLogAdmin(admin.ModelAdmin):
    list_display = (
    'user', 'get_previous_dorm', 'get_previous_room_number', 'get_new_dorm', 'get_new_room_number', 'timestamp')
    list_filter = ('timestamp', 'previous_room__dorm', 'new_room__dorm')
    search_fields = (
    'user__username', 'previous_room__room_number', 'new_room__room_number', 'previous_room__dorm__name',
    'new_room__dorm__name')
    date_hierarchy = 'timestamp'

    def get_previous_dorm(self, obj):
        return obj.previous_room.dorm.name if obj.previous_room else "None"

    get_previous_dorm.short_description = 'Previous Dorm'

    def get_previous_room_number(self, obj):
        return obj.previous_room.room_number if obj.previous_room else "None"

    get_previous_room_number.short_description = 'Previous Room'

    def get_new_dorm(self, obj):
        return obj.new_room.dorm.name if obj.new_room else "None"

    get_new_dorm.short_description = 'New Dorm'

    def get_new_room_number(self, obj):
        return obj.new_room.room_number if obj.new_room else "None"

    get_new_room_number.short_description = 'New Room'


admin.site.register(Profile)
admin.site.register(RoomAssignmentLog, RoomAssignmentLogAdmin)