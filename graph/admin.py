from django.contrib import admin
from django.utils.html import format_html
from .models import Node


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "connection_count",
    )
    search_fields = ("name",)
    readonly_fields = ["connection_count"]
    ordering = ("name",)

    fieldsets = (
        ("Basic Information", {"fields": ("name",)}),
        (
            "Connections",
            {
                "fields": ("connections",),
                "description": "Select nodes that this node connects to",
            },
        ),
    )

    def connection_count(self, obj):
        """Display the number of connections for each node"""
        count = obj.connections.count()
        return format_html(
            '<span style="color: {};">{}</span>', "green" if count > 0 else "red", count
        )

    connection_count.short_description = "Connections"

    def get_queryset(self, request):
        """Optimize queryset with prefetch_related"""
        return super().get_queryset(request).prefetch_related("connections")
