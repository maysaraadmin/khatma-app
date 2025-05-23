def group_list(request):
    """View to display list of reading groups"""
    from groups.models import ReadingGroup, GroupMembership

    # Get all public groups
    public_groups = ReadingGroup.objects.filter(is_public=True).order_by('-created_at')

    # If user is authenticated, also get their private groups
    user_groups = []
    if request.user.is_authenticated:
        # Get groups where the user is a member through GroupMembership
        user_memberships = GroupMembership.objects.filter(
            user=request.user,
            is_active=True
        ).values_list('group_id', flat=True)
        
        user_groups = ReadingGroup.objects.filter(
            id__in=user_memberships
        ).exclude(
            is_public=True
        ).order_by('-created_at')

    context = {
        'public_groups': public_groups,
        'user_groups': user_groups
    }

    return render(request, 'core/group_list.html', context)
