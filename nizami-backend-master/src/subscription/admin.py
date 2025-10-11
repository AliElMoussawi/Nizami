from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import render
from django.urls import path

from src.subscription.models import UserSubscription, UserSubscription


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    change_list_template = "admin/subscription/usersubscription/change_list.html"
    raw_id_fields = ("user", "plan")
    list_display = (
        'uuid',
        'user',
        'plan',
        'is_active',
        'expiry_date',
        'last_renewed',
        'deactivated_at',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'is_active',
        'user',
        'plan',
        'expiry_date'
    )
    search_fields = (
        'uuid',
        'plan__name',
        'plan__uuid',
        'user__username',
        'user__email',
    )
    actions = None
    ordering = ("-created_at",)

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        return []

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'report/more-than-1-active/',
                self.admin_site.admin_view(self.report_more_than_one_active),
                name='subscription_users_more_than_one_active',
            ),
            path(
                'report/zero/',
                self.admin_site.admin_view(self.report_zero_subscriptions),
                name='subscription_users_zero',
            ),
        ]
        return custom_urls + urls

    def report_more_than_one_active(self, request):
        User = get_user_model()
        users = User.objects.annotate(
            subs_count=Count('usersubscription', filter=Q(usersubscription__is_active=True))
        ).filter(subs_count__gt=1)
        context = dict(
            self.admin_site.each_context(request),
            title='Users with more than 1 active subscription',
            users=users,
        )
        return render(request, 'admin/subscription/usersubscription/report.html', context)

    def report_zero_subscriptions(self, request):
        User = get_user_model()
        users = User.objects.annotate(
            subs_count=Count('usersubscription')
        ).filter(subs_count=0)
        context = dict(
            self.admin_site.each_context(request),
            title='Users with zero subscriptions',
            users=users,
        )
        return render(request, 'admin/subscription/usersubscription/report.html', context)


class SubscriptionCountFilter(admin.SimpleListFilter):
    title = 'subscription count'
    parameter_name = 'subscription_count'

    def lookups(self, request, model_admin):
        return (
            ('gt1_active', 'More than 1 active subscription'),
            ('eq0', 'Zero subscriptions'),
        )

    def queryset(self, request, queryset):
        from django.db.models import Count, Q
        if self.value() == 'gt1_active':
            return queryset.annotate(subs_count=Count('usersubscription', filter=Q(usersubscription__is_active=True))).filter(subs_count__gt=1)
        if self.value() == 'eq0':
            return queryset.annotate(subs_count=Count('usersubscription')).filter(subs_count=0)
        return queryset


