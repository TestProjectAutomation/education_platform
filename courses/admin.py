from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Course, CourseModule, CourseLesson, Enrollment, Review

class CourseLessonInline(admin.TabularInline):
    model = CourseLesson
    extra = 1
    fields = ('title', 'order', 'duration', 'is_free')

class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 1
    show_change_link = True
    fields = ('title', 'order', 'description')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'level', 'status', 'created_at', 'views')
    list_filter = ('status', 'level', 'is_featured', 'created_at')
    search_fields = ('title', 'description', 'instructor')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views', 'enrollment_count')
    filter_horizontal = ('categories',)
    inlines = [CourseModuleInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'content', 'excerpt', 'featured_image')
        }),
        (_('Course Details'), {
            'fields': ('price', 'discount_price', 'duration', 'level', 'instructor')
        }),
        (_('Advanced'), {
            'fields': ('requirements', 'what_you_will_learn', 'link_display_duration')
        }),
        (_('Categorization'), {
            'fields': ('categories',)
        }),
        (_('Publishing'), {
            'fields': ('author', 'status', 'is_featured')
        }),
        (_('Statistics'), {
            'fields': ('views', 'enrollment_count')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'description')
    inlines = [CourseLessonInline]
    ordering = ('course', 'order')

@admin.register(CourseLesson)
class CourseLessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order', 'duration', 'is_free')
    list_filter = ('is_free', 'module__course')
    search_fields = ('title', 'content')
    ordering = ('module', 'order')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at', 'completed', 'completed_at')
    list_filter = ('completed', 'enrolled_at')
    search_fields = ('user__username', 'course__title')
    readonly_fields = ('enrolled_at',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'course__title', 'comment')
    readonly_fields = ('created_at',)