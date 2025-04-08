from django.contrib import admin
from .models import Post, PostImage, Dorm, Room


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1


class RoomInline(admin.TabularInline):
    model = Room
    extra = 1


class PostAdmin(admin.ModelAdmin):
    inlines = [PostImageInline]
    list_display = ('title', 'author', 'date_posted', 'room', 'liked')
    list_filter = ('room__dorm', 'room', 'liked')
    search_fields = ('title', 'content', 'author__username', 'room__room_number')


class DormAdmin(admin.ModelAdmin):
    inlines = [RoomInline]
    list_display = ('name', 'get_rooms_count')
    search_fields = ('name', 'description')

    def get_rooms_count(self, obj):
        return obj.rooms.count()

    get_rooms_count.short_description = 'Number of Rooms'


class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'dorm', 'floor', 'get_reviews_count')
    list_filter = ('dorm', 'floor')
    search_fields = ('room_number', 'description', 'dorm__name')

    def get_reviews_count(self, obj):
        return obj.reviews.count()

    get_reviews_count.short_description = 'Number of Reviews'


admin.site.register(Dorm, DormAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PostImage)