from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging
import traceback

# Import models from other apps
from users.models import Profile, UserAchievement
from khatma.models import Khatma, Deceased, PartAssignment, Participant, QuranReading
from quran.models import QuranPart, Surah, Ayah
from groups.models import ReadingGroup, GroupMembership
from notifications.models import Notification

logger = logging.getLogger(__name__)

def index(request):
    """Main homepage view"""
    # Get featured content
    featured_khatmas = []
    featured_groups = []

    # Get user-specific content if logged in
    if request.user.is_authenticated:
        from khatma.models import Khatma, Participant
        from groups.models import ReadingGroup, GroupMembership

        # Get user's active khatmas
        user_khatmas = Khatma.objects.filter(
            Q(creator=request.user) | Q(participant__user=request.user)
        ).distinct().order_by('-created_at')[:5]

        # Get user's groups
        user_groups = ReadingGroup.objects.filter(
            members=request.user
        ).order_by('-created_at')[:5]

        context = {
            'user_khatmas': user_khatmas,
            'user_groups': user_groups,
            'featured_khatmas': featured_khatmas,
            'featured_groups': featured_groups
        }
    else:
        # For anonymous users, show only featured content
        context = {
            'featured_khatmas': featured_khatmas,
            'featured_groups': featured_groups
        }

    return render(request, 'core/index.html', context)

def about_page(request):
    """About page view"""
    return render(request, 'core/about.html')


def help_page(request):
    """Help page view"""
    return render(request, 'core/help.html')


def contact_us(request):
    """Contact page view"""
    if request.method == 'POST':
        # Process contact form
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Simple validation
        if not all([name, email, message]):
            messages.error(request, 'يرجى ملء جميع الحقول المطلوبة')
            return redirect('core:contact_us')

        # Here you would typically send an email or save to database
        # For now, just show a success message
        messages.success(request, 'تم إرسال رسالتك بنجاح. سنتواصل معك قريباً.')
        return redirect('core:contact_us')

    return render(request, 'core/contact.html')

def global_search(request):
    """Global search view"""
    query = request.GET.get('q', '')
    results = {}

    if query:
        # Import models only when needed
        from khatma.models import Khatma
        from groups.models import ReadingGroup
        from quran.models import Surah
        from django.contrib.auth.models import User

        # Search khatmas
        khatmas = Khatma.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            is_public=True
        )[:10]

        # Search groups
        groups = ReadingGroup.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_public=True
        )[:10]

        # Search surahs
        surahs = Surah.objects.filter(
            Q(name_arabic__icontains=query) | Q(name_english__icontains=query)
        )[:10]

        # Search users (if authenticated)
        users = []
        if request.user.is_authenticated:
            users = User.objects.filter(
                Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
            )[:10]

        results = {
            'khatmas': khatmas,
            'groups': groups,
            'surahs': surahs,
            'users': users,
            'query': query
        }

    return render(request, 'core/search_results.html', results)
def set_language(request):
    """View for setting user language preference"""
    if request.method == 'POST':
        language = request.POST.get('language')
        next_url = request.POST.get('next', '/')

        # Set language in session
        request.session['django_language'] = language

        # If user is authenticated, update their profile
        if request.user.is_authenticated:
            from users.models import Profile
            profile, _ = Profile.objects.get_or_create(user=request.user)
            profile.preferred_language = language
            profile.save()

        return redirect(next_url)

    # If not POST, redirect to homepage
    return redirect('core:index')


def community(request):
    """Community hub view"""
    # Import models only when needed
    from khatma.models import Khatma, PublicKhatma
    from groups.models import ReadingGroup

    # Get public khatmas
    public_khatmas = Khatma.objects.filter(is_public=True).order_by('-created_at')[:10]

    # Get public groups
    public_groups = ReadingGroup.objects.filter(is_public=True).order_by('-created_at')[:10]

    # Get memorial khatmas
    memorial_khatmas = Khatma.objects.filter(
        khatma_type='memorial',
        is_public=True
    ).order_by('-created_at')[:10]

    context = {
        'public_khatmas': public_khatmas,
        'public_groups': public_groups,
        'memorial_khatmas': memorial_khatmas
    }

    return render(request, 'core/community.html', context)


@login_required
def logout_view(request):
    """View for logging out a user"""
    from django.contrib.auth import logout

    if request.method == 'POST':
        logout(request)
        messages.success(request, 'تم تسجيل الخروج بنجاح')
        return redirect('core:index')
    else:
        # For GET requests, show the logout confirmation page
        return render(request, 'registration/logout.html')

@login_required
def profile(request):
    """User profile view"""
    # Get user's khatmas
    from khatma.models import Khatma
    from users.models import UserAchievement

    user_khatmas = Khatma.objects.filter(participants__user=request.user).distinct()

    # Get user's achievements
    user_achievements = UserAchievement.objects.filter(user=request.user)

    context = {
        'user_khatmas': user_khatmas,
        'user_achievements': user_achievements
    }

    return render(request, 'core/profile.html', context)

@login_required
def logout_view(request):
    """View for logging out a user"""
    from django.contrib.auth import logout

    if request.method == 'POST':
        logout(request)
        messages.success(request, 'تم تسجيل الخروج بنجاح')
        return redirect('core:index')
    else:
        # For GET requests, show the logout confirmation page
        return render(request, 'registration/logout.html')



@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'تم تسجيل الخروج بنجاح')
        return redirect('core:index')
    else:
        # For GET requests, show the logout confirmation page
        return render(request, 'registration/logout.html')

@login_required
def profile(request):
    # Get user's khatmas
    user_khatmas = Khatma.objects.filter(participants__user=request.user).distinct()

    # Get user's achievements
    user_achievements = UserAchievement.objects.filter(user=request.user)

    context = {
        'user_khatmas': user_khatmas,
        'user_achievements': user_achievements
    }

    return render(request, 'core/profile.html', context)

@login_required
def settings(request):
    if request.method == 'POST':
        # Handle settings update form
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم حفظ الإعدادات بنجاح')
            return redirect('core:settings')
    else:
        form = UserProfileForm(instance=request.user)

    context = {
        'form': form
    }

    return render(request, 'core/settings.html', context)

@login_required
def edit_profile(request):
    user_profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح')
            return redirect('core:profile')
    else:
        form = UserProfileEditForm(instance=user_profile)

    context = {
        'form': form,
        'profile': user_profile
    }

    return render(request, 'core/edit_profile.html', context)

@login_required
def community_khatmas(request):
    public_khatmas = PublicKhatma.objects.filter(is_completed=True).order_by('-created_at')
    paginator = Paginator(public_khatmas, 10)  # 10 khatmas per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/community_khatmas.html', {
        'page_obj': page_obj,
    })

@login_required
def group_list(request):
    """View for listing all reading groups"""
    # Get groups where the user is a member
    user_groups = ReadingGroup.objects.filter(members=request.user, is_active=True).order_by('-created_at')

    # Get public groups that the user is not a member of
    public_groups = ReadingGroup.objects.filter(
        privacy='public',
        is_active=True
    ).exclude(
        members=request.user
    ).order_by('-created_at')

    # Get groups created by the user
    created_groups = ReadingGroup.objects.filter(creator=request.user).order_by('-created_at')

    context = {
        'user_groups': user_groups,
        'public_groups': public_groups,
        'created_groups': created_groups
    }

    return render(request, 'core/group_list.html', context)

@login_required
def create_group(request):
    """View for creating a new reading group"""
    if request.method == 'POST':
        form = ReadingGroupForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(user=request.user)
            messages.success(request, 'تم إنشاء المجموعة بنجاح')
            return redirect('core:group_detail', group_id=group.id)
    else:
        form = ReadingGroupForm()

    return render(request, 'core/create_group.html', {'form': form})

@login_required
def group_detail(request, group_id):
    """View for displaying group details"""
    group = get_object_or_404(ReadingGroup, id=group_id)

    # Check if user is a member of this group
    is_member = GroupMembership.objects.filter(user=request.user, group=group, is_active=True).exists()

    # Get user's role in the group
    user_role = None
    if is_member:
        membership = GroupMembership.objects.get(user=request.user, group=group)
        user_role = membership.role

    # Get active members
    active_members = group.members.filter(groupmembership__is_active=True)

    # Get group khatmas
    active_khatmas = Khatma.objects.filter(group=group, is_completed=False).order_by('-created_at')
    completed_khatmas = Khatma.objects.filter(group=group, is_completed=True).order_by('-completed_at')

    context = {
        'group': group,
        'is_member': is_member,
        'user_role': user_role,
        'active_members': active_members,
        'active_khatmas': active_khatmas,
        'completed_khatmas': completed_khatmas,
        'is_admin': user_role == 'admin',
        'is_moderator': user_role in ['admin', 'moderator']
    }

    return render(request, 'core/group_detail.html', context)

@login_required
def join_group(request, group_id):
    """View for joining a group"""
    group = get_object_or_404(ReadingGroup, id=group_id)

    # Check if user is already a member
    if GroupMembership.objects.filter(user=request.user, group=group).exists():
        membership = GroupMembership.objects.get(user=request.user, group=group)
        if membership.is_active:
            messages.info(request, 'أنت عضو بالفعل في هذه المجموعة')
        else:
            # Reactivate membership
            membership.is_active = True
            membership.status = 'joined'
            membership.save()
            messages.success(request, 'تم إعادة الانضمام إلى المجموعة بنجاح')
    else:
        # Check group privacy
        if group.privacy == 'closed':
            messages.error(request, 'هذه المجموعة مغلقة ولا يمكن الانضمام إليها')
            return redirect('core:group_list')
        elif group.privacy == 'private':
            # Create membership with invited status
            GroupMembership.objects.create(
                user=request.user,
                group=group,
                role='member',
                status='invited',
                is_active=False
            )
            messages.info(request, 'تم إرسال طلب الانضمام إلى مدير المجموعة')
        else:  # public group
            # Create active membership
            GroupMembership.objects.create(
                user=request.user,
                group=group,
                role='member',
                status='joined',
                is_active=True
            )
            messages.success(request, 'تم الانضمام إلى المجموعة بنجاح')

    return redirect('core:group_detail', group_id=group.id)

@login_required
def leave_group(request, group_id):
    """View for leaving a group"""
    group = get_object_or_404(ReadingGroup, id=group_id)

    # Check if user is a member
    try:
        membership = GroupMembership.objects.get(user=request.user, group=group, is_active=True)

        # Check if user is the creator/admin
        if membership.role == 'admin' and group.creator == request.user:
            # Check if there are other admins
            other_admins = GroupMembership.objects.filter(
                group=group,
                role='admin',
                is_active=True
            ).exclude(user=request.user)

            if not other_admins.exists():
                messages.error(request, 'لا يمكنك مغادرة المجموعة لأنك المدير الوحيد. قم بتعيين مدير آخر أولاً')
                return redirect('core:group_detail', group_id=group.id)

        # Deactivate membership
        membership.is_active = False
        membership.status = 'left'
        membership.save()

        messages.success(request, 'تم مغادرة المجموعة بنجاح')
    except GroupMembership.DoesNotExist:
        messages.error(request, 'أنت لست عضواً في هذه المجموعة')

    return redirect('core:group_list')

@login_required
def add_group_member(request, group_id):
    """View for adding a member to a group"""
    group = get_object_or_404(ReadingGroup, id=group_id)

    # Check if user is admin or moderator
    try:
        membership = GroupMembership.objects.get(user=request.user, group=group, is_active=True)
        if membership.role not in ['admin', 'moderator']:
            messages.error(request, 'ليس لديك صلاحية إضافة أعضاء')
            return redirect('core:group_detail', group_id=group.id)
    except GroupMembership.DoesNotExist:
        messages.error(request, 'ليس لديك صلاحية إضافة أعضاء')
        return redirect('core:group_list')

    if request.method == 'POST':
        form = GroupMembershipForm(request.POST)
        if form.is_valid():
            # Ensure the group is the current group
            form.instance.group = group
            form.save()
            messages.success(request, 'تمت إضافة العضو بنجاح')
            return redirect('core:group_detail', group_id=group.id)
    else:
        # Pre-select the current group
        form = GroupMembershipForm(initial={'group': group})

    return render(request, 'core/add_group_member.html', {
        'form': form,
        'group': group
    })

@login_required
def remove_group_member(request, group_id, user_id):
    """View for removing a member from a group"""
    group = get_object_or_404(ReadingGroup, id=group_id)
    user_to_remove = get_object_or_404(User, id=user_id)

    # Check if current user is admin or moderator
    try:
        membership = GroupMembership.objects.get(user=request.user, group=group, is_active=True)
        if membership.role not in ['admin', 'moderator']:
            messages.error(request, 'ليس لديك صلاحية إزالة أعضاء')
            return redirect('core:group_detail', group_id=group.id)
    except GroupMembership.DoesNotExist:
        messages.error(request, 'ليس لديك صلاحية إزالة أعضاء')
        return redirect('core:group_list')

    # Check if user to remove is a member
    try:
        member_membership = GroupMembership.objects.get(user=user_to_remove, group=group, is_active=True)

        # Admin can remove anyone, moderator can't remove admin
        if membership.role == 'moderator' and member_membership.role == 'admin':
            messages.error(request, 'لا يمكن للمشرف إزالة المدير')
            return redirect('core:group_detail', group_id=group.id)

        # Deactivate membership
        member_membership.is_active = False
        member_membership.status = 'removed'
        member_membership.save()

        messages.success(request, 'تمت إزالة العضو بنجاح')
    except GroupMembership.DoesNotExist:
        messages.error(request, 'هذا المستخدم ليس عضواً في المجموعة')

    return redirect('core:group_detail', group_id=group.id)

@login_required
def create_group_khatma(request, group_id):
    """View for creating a new group Khatma"""
    print(f"Creating group khatma for group ID: {group_id}")
    group = get_object_or_404(ReadingGroup, id=group_id)
    print(f"Found group: {group.name}")

    # Check if user is a member
    try:
        membership = GroupMembership.objects.get(user=request.user, group=group, is_active=True)
        print(f"User {request.user.username} is a member with role: {membership.role}")
    except GroupMembership.DoesNotExist:
        messages.error(request, 'يجب أن تكون عضواً في المجموعة لإنشاء ختمة')
        return redirect('core:group_detail', group_id=group.id)

    if request.method == 'POST':
        print(f"POST data: {request.POST}")

        # Create a copy of POST data to modify
        post_data = request.POST.copy()
        # Add the group ID to the POST data
        post_data['group'] = group.id
        print(f"Modified POST data: {post_data}")

        form = GroupKhatmaForm(post_data)
        if form.is_valid():
            print("Form is valid")
            # Create the khatma
            try:
                khatma = form.save(user=request.user)
                print(f"Created khatma: {khatma.id} - {khatma.title}")

                # Add all active group members as participants
                active_members = User.objects.filter(groupmembership__group=group, groupmembership__is_active=True)
                print(f"Adding {active_members.count()} members as participants")

                for member in active_members:
                    participant, created = Participant.objects.get_or_create(user=member, khatma=khatma)
                    print(f"Added participant: {member.username} (created: {created})")

                # Distribute parts if auto-distribute is enabled
                if khatma.auto_distribute_parts:
                    print("Auto-distributing parts")
                    success = khatma.distribute_parts_to_group_members()
                    print(f"Parts distribution success: {success}")

                messages.success(request, 'تم إنشاء الختمة الجماعية بنجاح')
                return redirect('core:khatma_detail', khatma_id=khatma.id)
            except Exception as e:
                print(f"Error creating khatma: {str(e)}")
                import traceback
                print(traceback.format_exc())
                messages.error(request, f'حدث خطأ أثناء إنشاء الختمة: {str(e)}')
        else:
            # Print form errors for debugging
            print(f"Form errors: {form.errors}")
    else:
        # Pre-select the current group and set default dates
        today = timezone.now().date()
        end_date = today + timezone.timedelta(days=30)  # Default to 30 days
        form = GroupKhatmaForm(initial={
            'group': group,
            'start_date': today,
            'end_date': end_date
        })
        print(f"Created form with initial data: group={group.id}, start_date={today}, end_date={end_date}")

    return render(request, 'core/create_group_khatma.html', {
        'form': form,
        'group': group
    })

@login_required
def khatma_detail(request, pk):
    khatma = get_object_or_404(PublicKhatma, pk=pk)
    comments = khatma.comments.order_by('-created_at')
    interactions = khatma.interactions.values('interaction_type').annotate(count=Count('interaction_type'))

    context = {
        'khatma': khatma,
        'comments': comments,
        'interactions': interactions,
    }

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'comment':
            text = request.POST.get('text')
            dua = request.POST.get('dua', '')
            KhatmaComment.objects.create(
                public_khatma=khatma,
                user=request.user,
                text=text,
                dua=dua
            )
            messages.success(request, 'تم إضافة التعليق بنجاح')
        elif action == 'interact':
            interaction_type = request.POST.get('interaction_type')
            KhatmaInteraction.objects.get_or_create(
                public_khatma=khatma,
                user=request.user,
                interaction_type=interaction_type
            )
            messages.success(request, 'تم التفاعل بنجاح')

        return redirect('khatma_detail', pk=pk)

    return render(request, 'core/khatma_detail.html', context)

@login_required
def create_public_khatma(request):
    if request.method == 'POST':
        description = request.POST.get('description')
        is_memorial = request.POST.get('is_memorial', False)
        deceased_id = request.POST.get('deceased_id')

        deceased = None
        if is_memorial and deceased_id:
            deceased = get_object_or_404(Deceased, pk=deceased_id)

        public_khatma = PublicKhatma.objects.create(
            user=request.user,
            description=description,
            is_memorial=is_memorial,
            deceased_person=deceased,
        )

        messages.success(request, 'تم إنشاء الختمة العامة بنجاح')
        return redirect('khatma_detail', pk=public_khatma.pk)

    deceased_list = Deceased.objects.filter(added_by=request.user)
    return render(request, 'core/create_public_khatma.html', {
        'deceased_list': deceased_list,
    })

@login_required
def khatma_dashboard(request, khatma_id):
    """
    Enhanced dashboard view for a specific Khatma that combines:
    - Khatma detail view
    - Reading plan view
    - Quran chapters view
    """
    try:
        # Get khatma
        khatma = get_object_or_404(Khatma, id=khatma_id)

        # Check if user is a participant
        is_participant = Participant.objects.filter(
            user=request.user, khatma=khatma
        ).exists()

        # Initialize parts if they don't exist
        parts = PartAssignment.objects.filter(khatma=khatma) \
            .select_related('part', 'participant') \
            .order_by('part__part_number')

        # Check if parts exist, if not, initialize them
        if not parts.exists():
            # Create 30 parts for the Khatma
            for part_number in range(1, 31):
                # Get or create the QuranPart
                quran_part, _ = QuranPart.objects.get_or_create(part_number=part_number)
                # Create the PartAssignment
                PartAssignment.objects.create(
                    khatma=khatma,
                    part=quran_part,
                    is_completed=False
                )

            # Refresh the parts queryset
            parts = PartAssignment.objects.filter(khatma=khatma) \
                .select_related('part', 'participant') \
                .order_by('part__part_number')

        # Calculate progress
        total_parts = parts.count()
        completed_parts = parts.filter(is_completed=True).count()
        progress_percentage = int((completed_parts / total_parts * 100) if total_parts > 0 else 0)

        # Generate reading plan
        reading_plan = []

        # Calculate days between start and end date
        if khatma.start_date and khatma.end_date:
            days_total = (khatma.end_date - khatma.start_date).days + 1
            if days_total > 0:
                # Calculate parts per day
                parts_per_day = total_parts / days_total

                # Generate reading plan
                for day in range(1, days_total + 1):
                    current_date = khatma.start_date + timezone.timedelta(days=day-1)

                    # Calculate which parts to read on this day
                    start_part_float = (day - 1) * parts_per_day + 1
                    end_part_float = day * parts_per_day

                    # Convert to integers (ceiling for start, floor for end)
                    start_part_int = int(start_part_float)
                    end_part_int = int(end_part_float)

                    # Ensure we don't exceed the total number of parts
                    if end_part_int > total_parts:
                        end_part_int = total_parts

                    # Add to reading plan
                    reading_plan.append({
                        'day': day,
                        'date': current_date,
                        'start_part_float': start_part_float,
                        'end_part_float': end_part_float,
                        'start_part_int': start_part_int,
                        'end_part_int': end_part_int
                    })

        # Get all surahs for reference
        surahs = Surah.objects.all().order_by('surah_number')

        # Get the mapping of parts to surahs
        part_to_surah_mapping = {}
        for part_num in range(1, 31):
            # Get all ayahs in this part
            ayahs_in_part = Ayah.objects.filter(quran_part_id=part_num).select_related('surah')

            # Get unique surahs in this part
            surahs_in_part = set()
            for ayah in ayahs_in_part:
                surahs_in_part.add((ayah.surah.surah_number, ayah.surah.name_arabic))

            # Sort by surah number
            surahs_in_part = sorted(list(surahs_in_part), key=lambda x: x[0])

            # Store in mapping
            part_to_surah_mapping[part_num] = surahs_in_part

        # Get participants
        participants = Participant.objects.filter(khatma=khatma)

        # Get chat messages
        chat_messages = KhatmaChat.objects.filter(khatma=khatma).order_by('created_at')

        context = {
            'khatma': khatma,
            'is_participant': is_participant,
            'parts': parts,
            'total_parts': total_parts,
            'completed_parts': completed_parts,
            'progress_percentage': progress_percentage,
            'reading_plan': reading_plan,
            'surahs': surahs,
            'part_to_surah_mapping': part_to_surah_mapping,
            'participants': participants,
            'chat_messages': chat_messages
        }

        return render(request, 'core/khatma_dashboard.html', context)

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        print(traceback.format_exc())
        messages.error(request, f'حدث خطأ أثناء عرض لوحة التحكم: {str(e)}')
        return render(request, 'core/error.html', {
            'error_title': 'خطأ في عرض لوحة التحكم',
            'error_message': 'حدث خطأ غير متوقع أثناء محاولة عرض لوحة التحكم. الرجاء المحاولة مرة أخرى لاحقاً.',
            'error_details': str(e),
        })

@login_required
def khatma_share(request, khatma_id):
    """View to share a Khatma on social media"""
    khatma = get_object_or_404(Khatma, pk=khatma_id)

    # Generate social media sharing content
    from .social_media_utils import generate_khatma_social_media_image

    social_media_image = generate_khatma_social_media_image(khatma)

    context = {
        'khatma': khatma,
        'social_media_image': social_media_image
    }

    return render(request, 'core/khatma_share.html', context)

@login_required
def create_khatma_post(request, khatma_id):
    """View to create a post for a specific Khatma"""
    khatma = get_object_or_404(Khatma, pk=khatma_id)

    # Check if user is a participant
    if not Participant.objects.filter(user=request.user, khatma=khatma).exists():
        messages.error(request, 'عليك الانضمام إلى الختمة أولاً')
        return redirect('core:khatma_detail', khatma_id=khatma_id)

    if request.method == 'POST':
        form = KhatmaChatForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.khatma = khatma

            # Check if it's a memorial post
            is_memorial = request.POST.get('is_memorial', False)
            post.is_memorial = is_memorial

            post.save()

            messages.success(request, 'تم إنشاء المنشور بنجاح')
            return redirect('core:khatma_detail', khatma_id=khatma_id)
    else:
        form = KhatmaChatForm()

    context = {
        'khatma': khatma,
        'form': form
    }

    return render(request, 'core/create_khatma_post.html', context)

@login_required
def index(request):
    """Enhanced home page with more personalized content"""
    # Get user's reading groups
    user_groups = ReadingGroup.objects.filter(members=request.user, is_active=True).order_by('-created_at')[:5]

    # Get groups created by the user
    created_groups = ReadingGroup.objects.filter(creator=request.user).order_by('-created_at')[:5]

    # Get public groups that the user is not a member of
    public_groups = ReadingGroup.objects.filter(
        privacy='public',
        is_active=True
    ).exclude(
        members=request.user
    ).order_by('-created_at')[:5]

    context = {
        'user_khatmas': Khatma.objects.filter(creator=request.user).order_by('-id')[:5],
        'participating_khatmas': Khatma.objects.filter(participant__user=request.user).exclude(creator=request.user).order_by('-id')[:5],
        'public_khatmas': Khatma.objects.filter(is_public=True).order_by('-id')[:5],
        'suggested_khatmas': Khatma.objects.filter(
            Q(is_public=True) & ~Q(creator=request.user)
        ).order_by('?')[:5],
        'memorial_khatmas': Khatma.objects.filter(
            khatma_type='memorial'
        ).order_by('-id')[:5],
        'user_achievements': UserAchievement.objects.filter(user=request.user).order_by('-achieved_at')[:3],
        'unread_notifications': Notification.objects.filter(
            user=request.user,
            is_read=False
        ).order_by('-id')[:5],
        'user_groups': user_groups,
        'created_groups': created_groups,
        'public_groups': public_groups
    }

    # Use the modern design template
    return render(request, 'core/index.html', context)

# This function was removed as it was a duplicate of the one below

@login_required
def khatma_detail(request, khatma_id):
    """View for displaying khatma details"""
    try:
        # First try to get a regular Khatma
        khatma = get_object_or_404(Khatma, id=khatma_id)
        print(f"Found regular Khatma: {khatma.id} - {khatma.title}")
        # Redirect to the dashboard view for regular Khatmas
        return redirect('core:khatma_dashboard', khatma_id=khatma_id)
    except:
        try:
            # If not found, try to get a PublicKhatma
            khatma = get_object_or_404(PublicKhatma, id=khatma_id)
            print(f"Found PublicKhatma: {khatma.id}")
            # For PublicKhatma, use the pk parameter
            return redirect('khatma_detail', pk=khatma_id)
        except:
            # If neither is found, show an error
            messages.error(request, 'الختمة غير موجودة')
            return redirect('core:index')

@login_required
def community_khatmas(request):
    """Enhanced community Khatmas view with advanced filtering"""
    # Base queryset for public Khatmas
    community_khatmas = Khatma.objects.filter(
        is_public=True,
        is_completed=False
    ).annotate(
        participants_count=Count('parts__assigned_to', distinct=True)
    ).order_by('-created_at')

    # Filtering options
    khatma_type = request.GET.get('type')
    if khatma_type:
        community_khatmas = community_khatmas.filter(khatma_type=khatma_type)

    # Pagination
    paginator = Paginator(community_khatmas, 10)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'page_obj': page_obj,
        'khatma_types': Khatma.KHATMA_TYPE_CHOICES,
        'selected_type': khatma_type
    }

    return render(request, 'core/community_khatmas.html', context)

@login_required
def add_khatma_interaction(request, khatma_id):
    """Add social interactions to a Khatma"""
    khatma = get_object_or_404(Khatma, id=khatma_id)

    if request.method == 'POST':
        form = KhatmaInteractionForm(request.POST)
        if form.is_valid():
            interaction = form.save(commit=False)
            interaction.user = request.user
            interaction.khatma = khatma
            interaction.save()

            # Create notification for Khatma creator
            Notification.objects.create(
                user=khatma.creator,
                notification_type='reaction',
                message=f'تفاعل جديد على ختمتك: {interaction.get_interaction_type_display()}',
                related_khatma=khatma,
                related_user=request.user
            )

            messages.success(request, 'تم إضافة التفاعل بنجاح')
            return redirect('core:khatma_detail', khatma_id=khatma.id)
    else:
        form = KhatmaInteractionForm()

    context = {
        'form': form,
        'khatma': khatma
    }

    return render(request, 'core/add_khatma_interaction.html', context)

@login_required
def user_profile(request):
    """Enhanced user profile view"""
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح')
            return redirect('core:user_profile')
    else:
        form = UserProfileForm(instance=profile)

    context = {
        'profile': profile,
        'form': form,
        'user_khatmas': Khatma.objects.filter(creator=request.user).order_by('-created_at'),
        'user_achievements': UserAchievement.objects.filter(user=request.user).order_by('-earned_at'),
        'total_parts_read': profile.total_parts_read
    }

    return render(request, 'core/user_profile.html', context)

@login_required
def create_deceased(request):
    if request.method == 'POST':
        form = DeceasedForm(request.POST, request.FILES)
        if form.is_valid():
            # Create the deceased person
            deceased = form.save(commit=False)
            deceased.added_by = request.user
            deceased.save()

            messages.success(request, f'تم إضافة {deceased.name} بنجاح')
            return redirect('core:deceased_list')
    else:
        form = DeceasedForm()
    return render(request, 'core/create_deceased.html', {'form': form})

@login_required
def deceased_list(request):
    """List of deceased people added by the user."""
    deceased_list = Deceased.objects.filter(added_by=request.user).order_by('-created_at')
    return render(request, 'core/deceased_list.html', {'deceased_list': deceased_list})

@login_required
def deceased_detail(request, deceased_id):
    """View details of a specific deceased person."""
    deceased = get_object_or_404(Deceased, id=deceased_id, added_by=request.user)

    # Get khatmas associated with this deceased person
    memorial_khatmas = Khatma.objects.filter(deceased=deceased).order_by('-created_at')

    context = {
        'deceased': deceased,
        'memorial_khatmas': memorial_khatmas
    }

    return render(request, 'core/deceased_detail.html', context)

@login_required
def create_khatma(request):
    """
    Create a new Khatma with enhanced error handling and validation
    """
    logger = logging.getLogger(__name__)

    try:
        if request.method == 'POST':
            logger.info(f"User {request.user.username} is creating a new khatma")
            logger.debug(f"POST data: {request.POST}")

            form = KhatmaCreationForm(request.POST)
            if form.is_valid():
                # Create a new Khatma
                kh = form.save(commit=False)
                kh.creator = request.user

                # Save start and end dates
                kh.start_date = form.cleaned_data['start_date']
                kh.end_date = form.cleaned_data['end_date']

                # Set target_completion_date to end_date
                kh.target_completion_date = kh.end_date

                # Calculate reading plan
                start_date = kh.start_date
                end_date = kh.end_date

                # Calculate the number of days for the Khatma
                if start_date and end_date:
                    days_duration = (end_date - start_date).days + 1  # Include both start and end days
                    if days_duration <= 0:
                        days_duration = 1  # Minimum 1 day
                else:
                    days_duration = 30  # Default to 30 days if dates not provided

                # Store the duration in session for the reading plan
                request.session['khatma_duration'] = days_duration
                request.session['khatma_start_date'] = start_date.strftime('%Y-%m-%d')
                request.session['khatma_end_date'] = end_date.strftime('%Y-%m-%d')

                logger.info(f"Form is valid. Khatma type: {kh.khatma_type}. Duration: {days_duration} days")

                # Handle deceased person if selected
                if kh.khatma_type == 'memorial':
                    deceased_id = request.POST.get('deceased')
                    logger.info(f"Memorial khatma. Deceased ID: {deceased_id}")

                    if not deceased_id:
                        logger.warning("No deceased person selected for memorial khatma")
                        messages.error(request, 'يجب تحديد المتوفى للختمات التذكارية')
                        return render(request, 'core/create_khatma.html', {
                            'form': form,
                            'deceased_list': Deceased.objects.filter(added_by=request.user).only('id', 'name', 'death_date', 'created_at')
                        })

                    # If 'new' is selected, redirect to create deceased
                    if deceased_id == 'new':
                        logger.info("User selected to create a new deceased person")
                        messages.info(request, 'أضف المتوفى أولاً')
                        return redirect('core:create_deceased')

                    try:
                        # Set the deceased
                        kh.deceased = Deceased.objects.get(id=deceased_id)
                        logger.info(f"Found deceased: {kh.deceased.name}")
                    except Deceased.DoesNotExist:
                        logger.error(f"Deceased with ID {deceased_id} not found")
                        messages.error(request, 'المتوفى غير موجود')
                        return render(request, 'core/create_khatma.html', {
                            'form': form,
                            'deceased_list': Deceased.objects.filter(added_by=request.user).only('id', 'name', 'death_date', 'created_at')
                        })

                # Transaction to ensure all related objects are created or none
                from django.db import transaction

                try:
                    with transaction.atomic():
                        # Save the khatma
                        kh.save()
                        logger.info(f"Khatma saved successfully with ID: {kh.id}")

                        # Create part assignments for all Quran parts
                        quran_parts = QuranPart.objects.all()
                        logger.info(f"Creating {quran_parts.count()} part assignments")

                        # Bulk create part assignments for better performance
                        part_assignments = [
                            PartAssignment(khatma=kh, part=part)
                            for part in quran_parts
                        ]
                        PartAssignment.objects.bulk_create(part_assignments)
                        logger.info("Part assignments created successfully")

                        # Bulk create KhatmaPart objects for better performance
                        logger.info("Creating 30 KhatmaPart objects")
                        khatma_parts = [
                            KhatmaPart(
                                khatma=kh,
                                part_number=part_number,
                                is_completed=False
                            )
                            for part_number in range(1, 31)
                        ]
                        KhatmaPart.objects.bulk_create(khatma_parts)
                        logger.info("KhatmaPart objects created successfully")

                        # Add creator as first participant
                        Participant.objects.create(user=request.user, khatma=kh)
                        logger.info("Added creator as participant")

                        # Check if this is the user's first khatma
                        if not UserAchievement.objects.filter(user=request.user, achievement_type='first_khatma').exists():
                            # Create achievement for creating a khatma
                            UserAchievement.objects.create(
                                user=request.user,
                                achievement_type='first_khatma',
                                points_earned=10
                            )
                            logger.info("Created first khatma achievement")

                        # Create notification
                        Notification.objects.create(
                            user=request.user,
                            notification_type='khatma_progress',
                            message=f'تم إنشاء ختمة جديدة: {kh.title}',
                            related_khatma=kh
                        )
                        logger.info("Created notification")

                        messages.success(request, 'تم إنشاء الختمة بنجاح')

                        # Redirect directly to the new dashboard view
                        return redirect('core:khatma_dashboard', khatma_id=kh.id)

                except Exception as e:
                    logger.error(f"Error in transaction while creating khatma: {str(e)}")
                    logger.error(traceback.format_exc())
                    messages.error(request, 'حدث خطأ أثناء إنشاء الختمة. الرجاء المحاولة مرة أخرى.')
                    # Re-raise to be caught by the outer try-except
                    raise
            else:
                logger.warning(f"Form is invalid. Errors: {form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'خطأ في {field}: {error}')
        else:
            form = KhatmaCreationForm()
            logger.info(f"Displaying empty khatma creation form for user {request.user.username}")

        # Get suggested khatmas for the user - optimized query
        suggested_khatmas = Khatma.objects.filter(
            is_public=True,
            is_completed=False
        ).exclude(creator=request.user).select_related('creator').prefetch_related('parts')[:5]

        # Get deceased list for memorial khatmas - only select fields that exist in the database
        deceased_list = Deceased.objects.filter(added_by=request.user).only('id', 'name', 'death_date', 'created_at')
        logger.info(f"Found {deceased_list.count()} deceased persons for user {request.user.username}")

        context = {
            'form': form,
            'suggested_khatmas': suggested_khatmas,
            'deceased_list': deceased_list
        }
        return render(request, 'core/create_khatma.html', context)

    except Exception as e:
        logger.error(f"Unhandled exception in create_khatma view: {str(e)}")
        logger.error(traceback.format_exc())
        messages.error(request, 'حدث خطأ غير متوقع. الرجاء المحاولة مرة أخرى لاحقاً.')
        return render(request, 'core/error.html', {
            'error_title': 'خطأ في إنشاء الختمة',
            'error_message': 'حدث خطأ غير متوقع أثناء محاولة إنشاء الختمة. الرجاء المحاولة مرة أخرى لاحقاً.',
            'error_details': str(e) if request.user.is_staff else None,
        })

@login_required
def khatma_part_reading(request, khatma_id, part_id):
    khatma = get_object_or_404(Khatma, id=khatma_id)
    part = get_object_or_404(QuranPart, part_number=part_id)
    part_assignment = get_object_or_404(
        PartAssignment,
        khatma=khatma,
        part=part
    )

    if request.method == 'POST':
        form = QuranReadingForm(request.POST)
        if form.is_valid():
            # Update part assignment
            part_assignment.is_completed = form.cleaned_data['is_completed']
            part_assignment.notes = form.cleaned_data['notes']
            part_assignment.dua = form.cleaned_data['dua']
            part_assignment.participant = request.user
            part_assignment.completed_at = timezone.now()
            part_assignment.save()

            # Check if khatma is fully completed
            all_parts_completed = PartAssignment.objects.filter(
                khatma=khatma,
                is_completed=False
            ).count() == 0

            if all_parts_completed:
                khatma.is_completed = True
                khatma.completed_at = timezone.now()
                khatma.save()

                # Create achievement for completing khatma
                UserAchievement.objects.create(
                    user=request.user,
                    achievement_type='full_quran',
                    points_earned=100
                )

            messages.success(request, 'تم تسجيل قراءة الجزء بنجاح')
            return redirect('core:khatma_detail', khatma_id=khatma.id)
    else:
        form = QuranReadingForm()

    # Get ayahs for this part
    ayahs = Ayah.objects.filter(quran_part=part)

    context = {
        'khatma': khatma,
        'part': part,
        'part_assignment': part_assignment,
        'form': form,
        'ayahs': ayahs
    }
    return render(request, 'core/khatma_part_reading.html', context)

@login_required
def khatma_detail(request, khatma_id):
    """
    Simplified Khatma detail view for public Khatmas
    """
    try:
        # Get the khatma
        khatma = get_object_or_404(Khatma, id=khatma_id)

        # Initialize parts if they don't exist
        parts = []
        for part_number in range(1, 31):
            # Get or create the QuranPart
            quran_part, _ = QuranPart.objects.get_or_create(part_number=part_number)

            # Get or create the PartAssignment
            part_assignment, created = PartAssignment.objects.get_or_create(
                khatma=khatma,
                part=quran_part,
                defaults={'is_completed': False}
            )

            parts.append(part_assignment)

        # Calculate completed parts
        completed_parts = sum(1 for part in parts if part.is_completed)
        total_parts = len(parts)

        # Check if user is a participant
        joined = Participant.objects.filter(
            user=request.user, khatma=khatma
        ).exists()

        # Handle join request
        if request.method == 'POST' and not joined:
            Participant.objects.create(user=request.user, khatma=khatma)
            messages.success(request, 'تم الانضمام إلى الختمة بنجاح')
            return redirect('core:khatma_detail', khatma_id=khatma.id)

        # Get participants count
        participants_count = Participant.objects.filter(khatma=khatma).count()

        context = {
            'khatma': khatma,
            'parts': parts,
            'posts': [],  # Empty list for now
            'is_participant': joined,
            'completed_parts': completed_parts,
            'total_parts': total_parts,
            'progress_percentage': (completed_parts / total_parts * 100) if total_parts > 0 else 0,
            'participants_count': participants_count,
        }

        return render(request, 'core/khatma_dashboard.html', context)

    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(traceback.format_exc())
        messages.error(request, f'حدث خطأ أثناء عرض الختمة: {str(e)}')
        return render(request, 'core/error.html', {
            'error_title': 'خطأ في عرض الختمة',
            'error_message': 'حدث خطأ غير متوقع أثناء محاولة عرض الختمة. الرجاء المحاولة مرة أخرى لاحقاً.',
            'error_details': str(e),
        })

@login_required
def community_khatmas(request):
    # Display public Khatmas with social features.
    community_khatmas = Khatma.objects.filter(
        is_public=True,
        is_completed=False
    ).order_by('-created_at')

    # Get khatmas by type
    memorial_khatmas = community_khatmas.filter(khatma_type='memorial')
    regular_khatmas = community_khatmas.filter(khatma_type='regular')

    # Get total number of participants for each khatma
    for khatma in community_khatmas:
        khatma.total_participants = Participant.objects.filter(khatma=khatma).count()

    paginator = Paginator(community_khatmas, 10)  # 10 khatmas per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'community_khatmas': community_khatmas,
        'memorial_khatmas': memorial_khatmas,
        'regular_khatmas': regular_khatmas,
    }

    return render(request, 'core/community_khatmas.html', context)

@login_required
def add_comment(request, khatma_id):
    """Add a comment to a Khatma."""
    khatma = get_object_or_404(Khatma, id=khatma_id)

    if request.method == 'POST':
        content = request.POST.get('content', '')

        # Create comment
        KhatmaComment.objects.create(
            user=request.user,
            khatma=khatma,
            text=content
        )

        messages.success(request, 'تم إضافة التعليق بنجاح')
        return redirect('core:khatma_detail', khatma_id=khatma_id)

    return redirect('core:khatma_detail', khatma_id=khatma_id)

@login_required
def add_reaction(request, khatma_id, reaction_type):
    """Add a reaction to a Khatma."""
    khatma = get_object_or_404(Khatma, id=khatma_id)

    # Validate reaction type
    valid_reactions = dict(PostReaction.REACTION_TYPES)

    if reaction_type not in valid_reactions:
        messages.error(request, 'نوع رد غير صالح')
        return redirect('core:khatma_detail', khatma_id=khatma_id)

    # Create reaction
    KhatmaInteraction.objects.create(
        user=request.user,
        khatma=khatma,
        interaction_type=reaction_type
    )

    messages.success(request, f'تم إضافة {valid_reactions[reaction_type]}')
    return redirect('core:khatma_detail', khatma_id=khatma_id)

@login_required
def assign_part(request, khatma_id, part_id):
    print(f"Assign part view called with khatma_id={khatma_id}, part_id={part_id}")

    try:
        kh = get_object_or_404(Khatma, id=khatma_id)
        print(f"Found khatma: {kh.id} - {kh.title}")

        part = get_object_or_404(QuranPart, part_number=part_id)
        print(f"Found part: {part.part_number}")

        # Check if PartAssignment exists
        try:
            pa = PartAssignment.objects.get(khatma=kh, part=part)
            print(f"Found part assignment: {pa.id}")
        except PartAssignment.DoesNotExist:
            print(f"PartAssignment does not exist, creating one")
            # Create the part assignment if it doesn't exist
            pa = PartAssignment.objects.create(
                khatma=kh,
                part=part,
                is_completed=False
            )
            print(f"Created part assignment: {pa.id}")

        # Check if user is a participant
        is_participant = Participant.objects.filter(user=request.user, khatma=kh).exists()
        print(f"User is participant: {is_participant}")

        if not is_participant:
            print("User is not a participant, creating participant record")
            # Create participant record
            Participant.objects.create(user=request.user, khatma=kh)
            messages.success(request, 'تم انضمامك إلى الختمة بنجاح')

        if request.method == 'POST':
            print(f"POST data: {request.POST}")

            # Create a simplified form that only includes the fields we need
            form = PartAssignmentForm(request.POST, instance=pa)
            if form.is_valid():
                print("Form is valid")
                a = form.save(commit=False)
                a.participant = request.user
                a.is_completed = True
                a.completed_at = timezone.now()
                a.save()
                print(f"Saved part assignment: {a.id}")
                messages.success(request, 'تم تسجيل الجزء كمقروء بنجاح')
                return redirect('core:khatma_detail', khatma_id=kh.id)
            else:
                print(f"Form errors: {form.errors}")
        else:
            # Create a simplified form for GET request
            form = PartAssignmentForm(instance=pa)
            print("Created form for GET request")

        # Get ayahs for this part
        try:
            ayahs = Ayah.objects.filter(quran_part=part) \
                .select_related('surah') \
                .order_by('surah__surah_number', 'ayah_number_in_surah')
            print(f"Found {ayahs.count()} ayahs for part {part.part_number}")

            # Get the last ayah number for the template
            last_ayah_number = ayahs.last().ayah_number_in_surah if ayahs.exists() else None
            print(f"Last ayah number: {last_ayah_number}")
        except Exception as e:
            print(f"Error getting ayahs: {str(e)}")
            ayahs = []
            last_ayah_number = None

        return render(request, 'core/assign_part.html', {
            'khatma': kh,
            'part': pa,
            'part_number': part.part_number,
            'ayahs': ayahs,
            'last_ayah_number': last_ayah_number,
            'form': form,
        })

    except Exception as e:
        print(f"Error in assign_part view: {str(e)}")
        import traceback
        print(traceback.format_exc())
        messages.error(request, 'حدث خطأ غير متوقع. الرجاء المحاولة مرة أخرى لاحقاً.')
        return render(request, 'core/error.html', {
            'error_title': 'خطأ في تعيين الجزء',
            'error_message': 'حدث خطأ غير متوقع أثناء محاولة تعيين الجزء. الرجاء المحاولة مرة أخرى لاحقاً.',
            'error_details': str(e) if request.user.is_staff else None,
        })

@login_required
def surah_view(request, surah_id):
    sur = get_object_or_404(Surah, surah_number=surah_id)
    ayahs = Ayah.objects.filter(surah=sur).order_by('ayah_number_in_surah')
    return render(request, 'core/surah.html', {
        'surah': sur,
        'ayahs': ayahs,
    })

@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    # Mark all notifications as read
    user_notifications.update(is_read=True)

    return render(request, 'core/notifications.html', {
        'notifications': user_notifications,
    })

@login_required
@require_POST
def mark_all_notifications_read(request):
    if request.user.is_authenticated:
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return redirect('notifications')
    return redirect('login')

def user_achievements(request):
    """View to display user achievements"""
    if not request.user.is_authenticated:
        return redirect('login')

    # Get all achievements for the current user
    user_achievements = UserAchievement.objects.filter(user=request.user)

    context = {
        'user_achievements': user_achievements
    }

    return render(request, 'core/user_achievements.html', context)

@login_required
@require_POST
def join_khatma(request, khatma_id):
    """View to allow a user to join a Khatma"""
    khatma = get_object_or_404(Khatma, pk=khatma_id)

    # Check if the Khatma is public or user is invited
    if not khatma.is_public and not khatma.participants.filter(user=request.user).exists():
        messages.error(request, 'لا يمكنك الانضمام لهذه الختمة')
        return redirect('community_khatmas')

    # Create a participant record
    Participant.objects.get_or_create(
        khatma=khatma,
        user=request.user
    )

    messages.success(request, f'تم الانضمام إلى ختمة {khatma.title} بنجاح')
    return redirect('khatma_detail', khatma_id=khatma_id)

@login_required
@require_POST
def leave_khatma(request, khatma_id):
    """View to allow a user to leave a Khatma"""
    khatma = get_object_or_404(Khatma, pk=khatma_id)

    # Check if the user is a participant
    participant = get_object_or_404(Participant, khatma=khatma, user=request.user)

    # Check if the user has any ongoing reading assignments
    ongoing_readings = QuranReading.objects.filter(
        khatma=khatma,
        participant=request.user,
        status__in=['not_started', 'in_progress']
    )

    if ongoing_readings.exists():
        messages.error(request, 'لا يمكنك مغادرة الختمة لوجود أجزاء قيد القراءة')
        return redirect('khatma_detail', khatma_id=khatma_id)

    # Remove the participant
    participant.delete()

    messages.success(request, f'تم مغادرة ختمة {khatma.title} بنجاح')
    return redirect('community_khatmas')

@login_required
def achievements_list(request):
    """View to list all available achievements and user's progress"""
    # Get all possible achievement types
    all_achievements = [
        {'type': 'first_khatma', 'name': 'أول ختمة', 'description': 'إكمال أول ختمة'},
        {'type': 'consecutive_khatmas', 'name': 'ختمات متتالية', 'description': 'إكمال ختمات متتالية'},
        {'type': 'community_participation', 'name': 'مشاركة مجتمعية', 'description': 'المشاركة في ختمات المجتمع'},
        {'type': 'memorial_khatma', 'name': 'ختمة ترحم', 'description': 'المشاركة في ختمة ترحم'},
    ]

    # Get user's current achievements
    user_achievements = UserAchievement.objects.filter(user=request.user)
    user_achievement_types = set(ua.achievement_type for ua in user_achievements)

    # Prepare context with achievement status
    achievements_context = []
    for achievement in all_achievements:
        achievements_context.append({
            'type': achievement['type'],
            'name': achievement['name'],
            'description': achievement['description'],
            'achieved': achievement['type'] in user_achievement_types
        })

    context = {
        'achievements': achievements_context
    }

    return render(request, 'core/achievements_list.html', context)

@login_required
def community_leaderboard(request):
    """View to display community leaderboard based on Khatma participation"""
    # Aggregate user participation and achievements
    leaderboard_data = []

    # Get all users who have participated in Khatmas
    participants = Participant.objects.values('user').annotate(
        total_khatmas=Count('khatma', distinct=True),
        total_parts_read=Count('khatma__partassignment', filter=Q(khatma__partassignment__is_completed=True))
    ).order_by('-total_khatmas', '-total_parts_read')

    for participant in participants:
        user = User.objects.get(pk=participant['user'])
        profile = Profile.objects.get(user=user)

        leaderboard_data.append({
            'username': user.username,
            'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
            'total_khatmas': participant['total_khatmas'],
            'total_parts_read': participant['total_parts_read']
        })

    context = {
        'leaderboard': leaderboard_data
    }

    return render(request, 'core/community_leaderboard.html', context)

@login_required
def set_language(request):
    """View to set user's preferred language"""
    if request.method == 'POST':
        language = request.POST.get('language', 'ar')  # Default to Arabic

        # Validate language
        if language not in ['ar', 'en']:
            language = 'ar'

        # Update user's profile
        profile, created = Profile.objects.get_or_create(user=request.user)
        profile.preferred_language = language
        profile.save()

        messages.success(request, 'تم تغيير اللغة بنجاح')

        # Redirect to the previous page or home
        return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required
def global_search(request):
    """View to provide a global search across Khatmas, Deceased, and Participants"""
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'all')

    results = {
        'khatmas': [],
        'deceased': [],
        'participants': []
    }

    if not query:
        return render(request, 'core/global_search.html', {'results': results})

    # Search Khatmas
    if search_type in ['khatmas', 'all']:
        khatmas = Khatma.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
        results['khatmas'] = [{
            'id': k.id,
            'title': k.title,
            'description': k.description,
            'total_parts': k.total_parts,
            'status': k.status
        } for k in khatmas]

    # Search Deceased
    if search_type in ['deceased', 'all']:
        deceased_list = Deceased.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
        results['deceased'] = [{
            'id': d.id,
            'name': d.name,
            'description': d.description,
            'date_of_death': d.date_of_death
        } for d in deceased_list]

    # Search Participants
    if search_type in ['participants', 'all']:
        participants = Participant.objects.filter(
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        )
        results['participants'] = [{
            'id': p.id,
            'username': p.user.username,
            'full_name': f'{p.user.first_name} {p.user.last_name}',
            'khatma': p.khatma.title,
            'joined_date': p.joined_date
        } for p in participants]

    context = {
        'results': results,
        'query': query,
        'search_type': search_type
    }

    return render(request, 'core/global_search.html', context)

def about_page(request):
    """View to display information about the Khatma app"""
    context = {
        'app_name': 'ختمة',
        'app_description': 'تطبيق لتتبع قراءة القرآن الكريم والترحم على الموتى',
        'features': [
            {
                'name': 'إنشاء ختمات',
                'description': 'إنشاء ختمات عامة أو خاصة للترحم على الموتى'
            },
            {
                'name': 'تتبع القراءة',
                'description': 'تتبع تقدم القراءة لكل مشارك في الختمة'
            },
            {
                'name': 'الإنجازات',
                'description': 'نظام إنجازات لتشجيع المشاركين'
            }
        ]
    }
    return render(request, 'core/about_page.html', context)

def quran_part_view(request, part_number):
    """View for displaying a specific Quran part (juz)"""
    # Add debugging information
    print(f"Quran Part View - Part Number: {part_number}")

    # Check if the part exists
    try:
        part = QuranPart.objects.get(part_number=part_number)
        print(f"Found part: {part}")
    except QuranPart.DoesNotExist:
        print(f"Part {part_number} does not exist")
        # Create the part if it doesn't exist
        part = QuranPart.objects.create(part_number=part_number)
        print(f"Created part: {part}")

    # Get all ayahs in this part
    ayahs = Ayah.objects.filter(quran_part=part).select_related('surah').order_by('surah__surah_number', 'ayah_number_in_surah')
    print(f"Found {ayahs.count()} ayahs in part {part_number}")

    # If no ayahs found, import them from the quran-text.txt file
    if not ayahs.exists():
        print("No ayahs found, importing from quran-text.txt file")

        # Surah names in Arabic
        surah_names = {
            1: "الفاتحة", 2: "البقرة", 3: "آل عمران", 4: "النساء", 5: "المائدة",
            6: "الأنعام", 7: "الأعراف", 8: "الأنفال", 9: "التوبة", 10: "يونس",
            11: "هود", 12: "يوسف", 13: "الرعد", 14: "إبراهيم", 15: "الحجر",
            16: "النحل", 17: "الإسراء", 18: "الكهف", 19: "مريم", 20: "طه",
            21: "الأنبياء", 22: "الحج", 23: "المؤمنون", 24: "النور", 25: "الفرقان",
            26: "الشعراء", 27: "النمل", 28: "القصص", 29: "العنكبوت", 30: "الروم",
            31: "لقمان", 32: "السجدة", 33: "الأحزاب", 34: "سبأ", 35: "فاطر",
            36: "يس", 37: "الصافات", 38: "ص", 39: "الزمر", 40: "غافر",
            41: "فصلت", 42: "الشورى", 43: "الزخرف", 44: "الدخان", 45: "الجاثية",
            46: "الأحقاف", 47: "محمد", 48: "الفتح", 49: "الحجرات", 50: "ق",
            51: "الذاريات", 52: "الطور", 53: "النجم", 54: "القمر", 55: "الرحمن",
            56: "الواقعة", 57: "الحديد", 58: "المجادلة", 59: "الحشر", 60: "الممتحنة",
            61: "الصف", 62: "الجمعة", 63: "المنافقون", 64: "التغابن", 65: "الطلاق",
            66: "التحريم", 67: "الملك", 68: "القلم", 69: "الحاقة", 70: "المعارج",
            71: "نوح", 72: "الجن", 73: "المزمل", 74: "المدثر", 75: "القيامة",
            76: "الإنسان", 77: "المرسلات", 78: "النبأ", 79: "النازعات", 80: "عبس",
            81: "التكوير", 82: "الانفطار", 83: "المطففين", 84: "الانشقاق", 85: "البروج",
            86: "الطارق", 87: "الأعلى", 88: "الغاشية", 89: "الفجر", 90: "البلد",
            91: "الشمس", 92: "الليل", 93: "الضحى", 94: "الشرح", 95: "التين",
            96: "العلق", 97: "القدر", 98: "البينة", 99: "الزلزلة", 100: "العاديات",
            101: "القارعة", 102: "التكاثر", 103: "العصر", 104: "الهمزة", 105: "الفيل",
            106: "قريش", 107: "الماعون", 108: "الكوثر", 109: "الكافرون", 110: "النصر",
            111: "المسد", 112: "الإخلاص", 113: "الفلق", 114: "الناس"
        }

        # Mapping of surahs to their juz (part)
        juz_surah_mapping = {
            1: [1, 2], 2: [2], 3: [2, 3], 4: [3, 4], 5: [4, 5],
            6: [5, 6], 7: [6, 7], 8: [7, 8], 9: [8, 9], 10: [9, 10, 11],
            11: [11, 12, 13, 14], 12: [15, 16], 13: [17, 18], 14: [18, 19, 20], 15: [20, 21, 22],
            16: [18, 19, 20], 17: [21, 22], 18: [23, 24, 25], 19: [25, 26, 27], 20: [27, 28, 29],
            21: [29, 30, 31, 32, 33], 22: [33, 34, 35, 36], 23: [36, 37, 38, 39], 24: [39, 40, 41], 25: [41, 42, 43, 44, 45],
            26: [46, 47, 48, 49, 50, 51], 27: [51, 52, 53, 54, 55, 56, 57], 28: [58, 59, 60, 61, 62, 63, 64, 65, 66],
            29: [67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77], 30: [78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114]
        }

        # Get or create surahs for this part
        surahs_for_this_part = juz_surah_mapping.get(part_number, [])

        # Create surahs if they don't exist
        for surah_number in surahs_for_this_part:
            surah_name = surah_names.get(surah_number, f"Surah {surah_number}")

            # Determine if Meccan or Medinan (simplified)
            revelation_type = "meccan" if surah_number not in [2, 3, 4, 5, 8, 9, 24, 33, 47, 48, 49, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 98, 110] else "medinan"

            Surah.objects.get_or_create(
                surah_number=surah_number,
                defaults={
                    'name_arabic': surah_name,
                    'name_english': f"Chapter {surah_number}",
                    'revelation_type': revelation_type,
                    'verses_count': 0  # Will be updated later
                }
            )

        # Try to import from quran-text.txt
        import os
        quran_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'quran-text.txt')

        if os.path.exists(quran_file_path):
            print(f"Found Quran text file at {quran_file_path}")

            # Dictionary to store verse counts for each surah
            verse_counts = {}

            # First pass: Count verses per surah
            with open(quran_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) != 3:
                        continue

                    surah_number = int(parts[0])
                    verse_number = int(parts[1])

                    if surah_number not in verse_counts:
                        verse_counts[surah_number] = 0

                    verse_counts[surah_number] = max(verse_counts[surah_number], verse_number)

            # Update surah verse counts
            for surah_number, count in verse_counts.items():
                Surah.objects.filter(surah_number=surah_number).update(verses_count=count)

            # Second pass: Create verses for this part
            verses_created = 0
            with open(quran_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) != 3:
                        continue

                    surah_number = int(parts[0])
                    verse_number = int(parts[1])
                    verse_text = parts[2]

                    # Skip if this surah is not in this part
                    if surah_number not in surahs_for_this_part:
                        continue

                    # Get the surah
                    try:
                        surah = Surah.objects.get(surah_number=surah_number)

                        # Create verse
                        Ayah.objects.create(
                            surah=surah,
                            ayah_number_in_surah=verse_number,
                            text_uthmani=verse_text,
                            translation='',  # No translation in this format
                            quran_part=part,
                            page=0  # No page info in this format
                        )
                        verses_created += 1
                    except Surah.DoesNotExist:
                        print(f"Surah {surah_number} does not exist")

            print(f"Created {verses_created} verses for part {part_number}")
        else:
            print(f"Quran text file not found at {quran_file_path}")

            # Create some sample ayahs for testing if file not found
            surahs = Surah.objects.all()
            if not surahs.exists():
                print("No surahs found, creating sample surahs")
                # Create sample surahs
                surah1 = Surah.objects.create(
                    surah_number=1,
                    name_arabic="الفاتحة",
                    name_english="The Opening",
                    revelation_type="meccan",
                    verses_count=7
                )
                surah2 = Surah.objects.create(
                    surah_number=2,
                    name_arabic="البقرة",
                    name_english="The Cow",
                    revelation_type="medinan",
                    verses_count=286
                )
            else:
                surah1 = Surah.objects.get(surah_number=1)
                surah2 = Surah.objects.filter(surah_number=2).first() or Surah.objects.first()

            # Create sample ayahs for testing
            sample_ayahs = [
                {
                    "surah": surah1,
                    "ayah_number_in_surah": 1,
                    "text_uthmani": "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ",
                    "translation": "In the name of Allah, the Entirely Merciful, the Especially Merciful"
                },
                {
                    "surah": surah1,
                    "ayah_number_in_surah": 2,
                    "text_uthmani": "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
                    "translation": "All praise is due to Allah, Lord of the worlds"
                },
                {
                    "surah": surah1,
                    "ayah_number_in_surah": 3,
                    "text_uthmani": "الرَّحْمَنِ الرَّحِيمِ",
                    "translation": "The Entirely Merciful, the Especially Merciful"
                },
                {
                    "surah": surah2,
                    "ayah_number_in_surah": 1,
                    "text_uthmani": "الم",
                    "translation": "Alif, Lam, Meem"
                },
                {
                    "surah": surah2,
                    "ayah_number_in_surah": 2,
                    "text_uthmani": "ذَلِكَ الْكِتَابُ لَا رَيْبَ فِيهِ هُدًى لِلْمُتَّقِينَ",
                    "translation": "This is the Book about which there is no doubt, a guidance for those conscious of Allah"
                }
            ]

            for ayah_data in sample_ayahs:
                Ayah.objects.create(
                    surah=ayah_data["surah"],
                    ayah_number_in_surah=ayah_data["ayah_number_in_surah"],
                    text_uthmani=ayah_data["text_uthmani"],
                    translation=ayah_data["translation"],
                    quran_part=part
                )

        # Refresh the ayahs queryset
        ayahs = Ayah.objects.filter(quran_part=part).select_related('surah').order_by('surah__surah_number', 'ayah_number_in_surah')
        print(f"Found {ayahs.count()} ayahs in part {part_number} after import")

    # Group ayahs by surah for better display
    surahs_in_part = {}
    for ayah in ayahs:
        if ayah.surah.id not in surahs_in_part:
            surahs_in_part[ayah.surah.id] = {
                'surah': ayah.surah,
                'ayahs': []
            }
        surahs_in_part[ayah.surah.id]['ayahs'].append(ayah)

    # Convert to list for template
    surahs_list = list(surahs_in_part.values())
    print(f"Found {len(surahs_list)} surahs in part {part_number}")

    # Get next and previous part numbers for navigation
    next_part = part_number + 1 if part_number < 30 else None
    prev_part = part_number - 1 if part_number > 1 else None

    context = {
        'part': part,
        'surahs': surahs_list,
        'next_part': next_part,
        'prev_part': prev_part,
    }

    return render(request, 'core/quran_part.html', context)

def help_page(request):
    """View to provide help and support for the Khatma app"""
    context = {
        'faq_sections': [
            {
                'title': 'إنشاء ختمة',
                'questions': [
                    {
                        'question': 'كيف أنشئ ختمة جديدة؟',
                        'answer': 'يمكنك إنشاء ختمة جديدة بالنقر على زر "إنشاء ختمة" في الصفحة الرئيسية. قم بتعبئة التفاصيل مثل العنوان، نوع الختمة، والهدف منها.'
                    },
                    {
                        'question': 'ما هي أنواع الختمات المتاحة؟',
                        'answer': 'يمكنك إنشاء ختمات متنوعة مثل الختمة العادية، الختمة التذكارية، ختمة خيرية، ختمة مولد، وختمة شفاء.'
                    }
                ]
            },
            {
                'title': 'المشاركة في ختمة',
                'questions': [
                    {
                        'question': 'كيف أنضم إلى ختمة؟',
                        'answer': 'يمكنك البحث عن الختمات العامة في صفحة "الختمات المجتمعية" والانضمام إليها بالنقر على زر "انضمام".'
                    },
                    {
                        'question': 'هل يمكنني الانسحاب من ختمة؟',
                        'answer': 'نعم، يمكنك الانسحاب من ختمة في أي وقت من صفحة تفاصيل الختمة.'
                    }
                ]
            },
            {
                'title': 'الإنجازات والنقاط',
                'questions': [
                    {
                        'question': 'كيف أكتسب نقاط وإنجازات؟',
                        'answer': 'تكتسب النقاط والإنجازات عند إكمال أجزاء من القرآن، والمشاركة في ختمات مختلفة، وتحقيق أهداف معينة.'
                    },
                    {
                        'question': 'أين يمكنني رؤية إنجازاتي؟',
                        'answer': 'يمكنك عرض إنجازاتك في صفحة "إنجازاتي" التي تعرض جميع الإنجازات التي حققتها.'
                    }
                ]
            },
            {
                'title': 'الدعم والمساعدة',
                'questions': [
                    {
                        'question': 'كيف يمكنني التواصل مع الدعم؟',
                        'answer': 'يمكنك التواصل معنا من خلال صفحة "اتصل بنا" أو مراسلتنا على البريد الإلكتروني support@khatmaapp.com.'
                    },
                    {
                        'question': 'هل التطبيق مجاني؟',
                        'answer': 'نعم، التطبيق مجاني تمامًا. نهدف إلى نشر ثقافة قراءة القرآن في المجتمع.'
                    }
                ]
            }
        ]
    }
    return render(request, 'core/help_page.html', context)

def contact_us(request):
    """View to display contact information and form"""
    if request.method == 'POST':
        # This would normally process a contact form
        # For now, just show a success message
        messages.success(request, 'تم إرسال رسالتك بنجاح. سنتواصل معك قريباً.')
        return redirect('core:contact_us')

    context = {
        'contact_email': 'support@khatmaapp.com',
        'contact_phone': '+966 50 123 4567',
        'social_media': [
            {
                'name': 'Twitter',
                'icon': 'bi-twitter',
                'url': 'https://twitter.com/khatmaapp'
            },
            {
                'name': 'Facebook',
                'icon': 'bi-facebook',
                'url': 'https://facebook.com/khatmaapp'
            },
            {
                'name': 'Instagram',
                'icon': 'bi-instagram',
                'url': 'https://instagram.com/khatmaapp'
            }
        ]
    }
    return render(request, 'core/contact_us.html', context)

def register(request):
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Create user profile with selected account type
            account_type = request.POST.get('account_type', 'individual')
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={'account_type': account_type}
            )

            if not created:
                profile.account_type = account_type
                profile.save()

            messages.success(
                request,
                'تم إنشاء الحساب بنجاح. يمكنك تسجيل الدخول الآن.'
            )
            return redirect('login')
    else:
        form = ExtendedUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def user_profile(request):
    # Get user's khatmas
    user_khatmas = Khatma.objects.filter(creator=request.user)

    # Get user's achievements
    user_achievements = UserAchievement.objects.filter(user=request.user)

    # Get user's notifications
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]

    # Get user's part assignments
    user_part_assignments = PartAssignment.objects.filter(participant=request.user)

    # Get user's public khatmas
    public_khatmas = PublicKhatma.objects.filter(user=request.user)

    context = {
        'user_profile': request.user.profile,
        'user_khatmas': user_khatmas,
        'user_achievements': user_achievements,
        'user_notifications': user_notifications,
        'user_part_assignments': user_part_assignments,
        'public_khatmas': public_khatmas,
    }

    return render(request, 'core/user_profile.html', context)

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        # Add form validation and profile update logic
        profile.bio = request.POST.get('bio', '')
        profile.location = request.POST.get('location', '')
        profile.birth_date = request.POST.get('birth_date', None)
        profile.account_type = request.POST.get('account_type', 'individual')
        profile.save()

        messages.success(request, 'تم تحديث ملفك الشخصي بنجاح')
        return redirect('user_profile')

    return render(request, 'core/edit_profile.html', {'profile': profile})

@login_required
def khatma_chat(request, khatma_id):
    khatma = get_object_or_404(Khatma, id=khatma_id)

    # Check if user is a participant
    if not Participant.objects.filter(user=request.user, khatma=khatma).exists():
        messages.error(request, 'يجب أن تكون مشاركًا في الختمة للتحدث')
        return redirect('core:khatma_detail', khatma_id=khatma.id)

    if request.method == 'POST':
        message_type = request.POST.get('message_type', 'text')
        message_text = request.POST.get('message', '').strip()
        image = request.FILES.get('image')
        audio = request.FILES.get('audio')

        if not message_text and not image and not audio:
            messages.error(request, 'لا يمكن إرسال رسالة فارغة')
            return redirect('core:khatma_chat', khatma_id=khatma.id)

        # Create chat message
        chat_message = KhatmaChat.objects.create(
            khatma=khatma,
            user=request.user,
            message=message_text,
            message_type=message_type,
            image=image,
            audio=audio
        )

        # Create notification for other participants
        other_participants = Participant.objects.filter(
            khatma=khatma
        ).exclude(user=request.user)

        for participant in other_participants:
            Notification.objects.create(
                user=participant.user,
                notification_type='comment',
                message=f'رسالة جديدة من {request.user.username} في ختمة {khatma.title}',
                related_khatma=khatma,
                related_user=request.user
            )

        messages.success(request, 'تم إرسال الرسالة بنجاح')
        return redirect('core:khatma_chat', khatma_id=khatma.id)

    # Get chat messages
    chat_messages = KhatmaChat.objects.filter(
        khatma=khatma
    ).order_by('created_at')

    # Get total participants count
    participants_count = Participant.objects.filter(khatma=khatma).count()

    context = {
        'khatma': khatma,
        'chat_messages': chat_messages,
        'participants_count': participants_count
    }

    return render(request, 'core/khatma_chat.html', context)

@login_required
def group_chat(request, group_id):
    """View for group chat functionality"""
    group = get_object_or_404(ReadingGroup, id=group_id)

    # Check if user is a member of the group
    if not GroupMembership.objects.filter(user=request.user, group=group, is_active=True).exists():
        messages.error(request, 'يجب أن تكون عضوًا في المجموعة للمشاركة في الدردشة')
        return redirect('core:group_detail', group_id=group.id)

    # Get user's role in the group
    user_membership = GroupMembership.objects.get(user=request.user, group=group)
    user_role = user_membership.role

    if request.method == 'POST':
        message_type = request.POST.get('message_type', 'text')
        message_text = request.POST.get('message', '').strip()
        image = request.FILES.get('image')
        audio = request.FILES.get('audio')

        if not message_text and not image and not audio:
            messages.error(request, 'لا يمكن إرسال رسالة فارغة')
            return redirect('core:group_chat', group_id=group.id)

        # Create chat message
        GroupChat.objects.create(
            group=group,
            user=request.user,
            message=message_text,
            message_type=message_type,
            image=image,
            audio=audio
        )

        # Create notifications for other group members
        other_members = GroupMembership.objects.filter(
            group=group,
            is_active=True
        ).exclude(user=request.user)

        for membership in other_members:
            Notification.objects.create(
                user=membership.user,
                notification_type='group_chat',
                message=f'رسالة جديدة من {request.user.username} في مجموعة {group.name}',
                related_user=request.user
            )

        messages.success(request, 'تم إرسال الرسالة بنجاح')
        return redirect('core:group_chat', group_id=group.id)

    # Get chat messages
    chat_messages = GroupChat.objects.filter(group=group).order_by('created_at')

    # Get active members count
    members_count = group.get_active_members_count()

    # Get pinned messages
    pinned_messages = GroupChat.objects.filter(group=group, is_pinned=True).order_by('-created_at')

    context = {
        'group': group,
        'chat_messages': chat_messages,
        'members_count': members_count,
        'pinned_messages': pinned_messages,
        'user_role': user_role,
        'is_admin': user_role == 'admin',
        'is_moderator': user_role in ['admin', 'moderator']
    }

    return render(request, 'core/group_chat.html', context)


@login_required
def khatma_reading_plan(request):
    """Redirect to the enhanced dashboard view"""
    # Get khatma ID from URL parameter
    khatma_id = request.GET.get('khatma_id')

    # If no khatma_id, show error
    if not khatma_id:
        messages.error(request, 'لم يتم العثور على الختمة')
        return redirect('core:index')

    # Redirect to the dashboard view
    return redirect('core:khatma_dashboard', khatma_id=khatma_id)


@login_required
def khatma_quran_chapters(request):
    """Redirect to the enhanced dashboard view"""
    # Get khatma ID from URL parameter
    khatma_id = request.GET.get('khatma_id')

    # If no khatma_id, show error
    if not khatma_id:
        messages.error(request, 'لم يتم العثور على الختمة')
        return redirect('core:index')

    # Redirect to the dashboard view
    return redirect('core:khatma_dashboard', khatma_id=khatma_id)
