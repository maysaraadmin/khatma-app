from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
import logging

# Import models from other apps as needed
from users.models import Profile
from khatma.models import Khatma, Participant
from quran.models import QuranPart

logger = logging.getLogger(__name__)

def index(request):
    """Home page view"""
    try:
        from khatma.models import Khatma
        import logging

        logger = logging.getLogger(__name__)
        logger.info("Loading homepage")

        # Get user's khatmas
        user_khatmas = []
        participating_khatmas = []

        if request.user.is_authenticated:
            try:
                # Get khatmas created by the user
                user_khatmas = Khatma.objects.filter(creator=request.user).order_by('-created_at')[:5]
                logger.info(f"Found {user_khatmas.count()} khatmas created by user {request.user.username}")

                # Get khatmas where the user is a participant
                from khatma.models import Participant
                participating_khatma_ids = Participant.objects.filter(
                    user=request.user
                ).values_list('khatma_id', flat=True)

                participating_khatmas = Khatma.objects.filter(
                    id__in=participating_khatma_ids
                ).exclude(
                    creator=request.user  # Exclude khatmas created by the user
                ).order_by('-created_at')[:5]

                logger.info(f"Found {participating_khatmas.count()} khatmas where user {request.user.username} is a participant")
            except Exception as e:
                logger.error(f"Error retrieving user khatmas: {str(e)}")

        # Get public khatmas
        try:
            public_khatmas = Khatma.objects.filter(is_public=True).order_by('-created_at')[:5]
            logger.info(f"Found {public_khatmas.count()} public khatmas")
        except Exception as e:
            logger.error(f"Error retrieving public khatmas: {str(e)}")
            public_khatmas = []

        # Get suggested khatmas (for now, just get some recent public khatmas)
        try:
            suggested_khatmas = Khatma.objects.filter(is_public=True).order_by('?')[:5]
            logger.info(f"Found {suggested_khatmas.count()} suggested khatmas")
        except Exception as e:
            logger.error(f"Error retrieving suggested khatmas: {str(e)}")
            suggested_khatmas = []

        context = {
            'user_khatmas': user_khatmas,
            'participating_khatmas': participating_khatmas,
            'public_khatmas': public_khatmas,
            'suggested_khatmas': suggested_khatmas
        }

        return render(request, 'core/index.html', context)
    except Exception as e:
        # Log the error
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error in index view: {str(e)}")
        logger.error(traceback.format_exc())

        # Return a simple error message
        return render(request, 'core/test_index.html', {
            'test_message': 'حدث خطأ أثناء تحميل الصفحة الرئيسية. يرجى المحاولة مرة أخرى لاحقاً.'
        })


def global_search(request):
    """Global search functionality across khatmas, deceased persons, and participants"""
    from khatma.models import Khatma, Deceased
    from django.contrib.auth.models import User
    from django.db.models import Q

    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'all')

    results = {
        'khatmas': [],
        'deceased': [],
        'participants': []
    }

    if query:
        # Search in khatmas
        if search_type in ['all', 'khatmas']:
            khatmas = Khatma.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            ).order_by('-created_at')

            results['khatmas'] = [{
                'id': khatma.id,
                'title': khatma.title,
                'description': khatma.description or '',
                'status': 'مكتملة' if khatma.is_completed else 'جارية',
                'total_parts': 30  # Quran has 30 parts
            } for khatma in khatmas[:10]]

        # Search in deceased persons
        if search_type in ['all', 'deceased']:
            deceased_persons = Deceased.objects.filter(
                Q(name__icontains=query) |
                Q(biography__icontains=query)
            ).order_by('-death_date')

            results['deceased'] = [{
                'id': deceased.id,
                'name': deceased.name,
                'date_of_death': deceased.death_date,
                'description': deceased.biography or ''
            } for deceased in deceased_persons[:10]]

        # Search in participants (users)
        if search_type in ['all', 'participants']:
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).order_by('username')

            results['participants'] = [{
                'username': user.username,
                'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'joined_date': user.date_joined.strftime('%Y-%m-%d'),
                'khatma': user.created_khatmas.first().title if user.created_khatmas.exists() else 'لا يوجد'
            } for user in users[:10]]

    context = {
        'query': query,
        'search_type': search_type,
        'results': results
    }

    return render(request, 'core/global_search.html', context)


def about_page(request):
    """View for the about page"""
    context = {
        'app_name': 'ختمة',
        'app_description': 'تطبيق لتنظيم ختمات القرآن الكريم وإهداء ثوابها للمتوفين',
        'features': [
            {
                'name': 'ختمات القرآن',
                'description': 'إنشاء وإدارة ختمات القرآن الكريم بسهولة'
            },
            {
                'name': 'إهداء الثواب',
                'description': 'إهداء ثواب القراءة للمتوفين'
            },
            {
                'name': 'المشاركة الجماعية',
                'description': 'المشاركة مع الأصدقاء والعائلة في ختمات القرآن'
            },
            {
                'name': 'متابعة التقدم',
                'description': 'متابعة تقدم القراءة وإكمال الختمة'
            },
            {
                'name': 'الإشعارات',
                'description': 'إشعارات للتذكير بالقراءة وإكمال الأجزاء'
            },
            {
                'name': 'المجتمع',
                'description': 'مشاركة الختمات مع المجتمع والمشاركة في ختمات الآخرين'
            }
        ]
    }

    return render(request, 'core/about_page.html', context)


def help_page(request):
    """View for the help page with FAQ sections"""
    context = {
        'faq_sections': [
            {
                'title': 'أسئلة عامة',
                'questions': [
                    {
                        'question': 'ما هو تطبيق ختمة؟',
                        'answer': 'تطبيق ختمة هو منصة لتنظيم ختمات القرآن الكريم وإهداء ثوابها للمتوفين. يمكنك إنشاء ختمات فردية أو جماعية ومشاركتها مع الأصدقاء والعائلة.'
                    },
                    {
                        'question': 'هل التطبيق مجاني؟',
                        'answer': 'نعم، التطبيق مجاني بالكامل ويمكن استخدامه دون أي تكلفة.'
                    },
                    {
                        'question': 'هل يمكنني استخدام التطبيق بدون تسجيل؟',
                        'answer': 'لا، يجب عليك إنشاء حساب للاستفادة من جميع ميزات التطبيق.'
                    }
                ]
            },
            {
                'title': 'الختمات',
                'questions': [
                    {
                        'question': 'كيف يمكنني إنشاء ختمة جديدة؟',
                        'answer': 'يمكنك إنشاء ختمة جديدة من خلال النقر على زر "إنشاء ختمة جديدة" في الصفحة الرئيسية أو من خلال قائمة الختمات.'
                    },
                    {
                        'question': 'هل يمكنني إنشاء ختمة للمتوفين؟',
                        'answer': 'نعم، يمكنك إنشاء ختمة وإهداء ثوابها لشخص متوفى. يمكنك إضافة معلومات المتوفى وصورته وتاريخ وفاته.'
                    },
                    {
                        'question': 'كيف يمكنني دعوة الآخرين للمشاركة في ختمة؟',
                        'answer': 'يمكنك مشاركة رابط الختمة مع الأصدقاء والعائلة عبر وسائل التواصل الاجتماعي أو البريد الإلكتروني.'
                    }
                ]
            },
            {
                'title': 'المجموعات',
                'questions': [
                    {
                        'question': 'ما هي المجموعات؟',
                        'answer': 'المجموعات هي طريقة لتنظيم الأشخاص الذين يشاركون في ختمات متعددة معًا، مثل العائلة أو الأصدقاء أو زملاء العمل.'
                    },
                    {
                        'question': 'كيف يمكنني إنشاء مجموعة جديدة؟',
                        'answer': 'يمكنك إنشاء مجموعة جديدة من خلال النقر على "المجموعات" في القائمة الرئيسية ثم النقر على "إنشاء مجموعة جديدة".'
                    },
                    {
                        'question': 'هل يمكنني إنشاء مجموعة خاصة؟',
                        'answer': 'نعم، يمكنك إنشاء مجموعة خاصة وتحديد من يمكنه الانضمام إليها.'
                    }
                ]
            }
        ]
    }

    return render(request, 'core/help_page.html', context)


def contact_us(request):
    """View for the contact us page"""
    if request.method == 'POST':
        # Get form data but not using it yet since we're just showing a success message
        # In a real application, you would process this data (send email, save to database, etc.)

        messages.success(request, 'تم إرسال رسالتك بنجاح. سنتواصل معك قريبًا.')
        return redirect('core:contact_us')

    context = {
        'contact_email': 'support@khatma-app.com',
        'contact_phone': '+966 123 456 789',
        'social_media': [
            {
                'name': 'Twitter',
                'icon': 'bi-twitter',
                'url': 'https://twitter.com/khatma_app'
            },
            {
                'name': 'Facebook',
                'icon': 'bi-facebook',
                'url': 'https://facebook.com/khatma_app'
            },
            {
                'name': 'Instagram',
                'icon': 'bi-instagram',
                'url': 'https://instagram.com/khatma_app'
            }
        ]
    }

    return render(request, 'core/contact_us.html', context)


def set_language(request):
    """View for setting the language preference"""
    from django.utils.translation import activate
    from django.conf import settings

    next_url = request.POST.get('next', request.GET.get('next', '/'))
    lang_code = request.POST.get('language', request.GET.get('language', settings.LANGUAGE_CODE))

    # Activate the language
    activate(lang_code)

    # Set the language in the session
    request.session[settings.LANGUAGE_SESSION_KEY] = lang_code

    # Redirect to the previous page
    return redirect(next_url)


def group_list(request):
    """View to display list of reading groups"""
    try:
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
    except Exception as e:
        # Log the error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in group_list view: {str(e)}")

        # Return an empty context
        context = {
            'public_groups': [],
            'user_groups': [],
            'error_message': 'حدث خطأ أثناء تحميل المجموعات. يرجى المحاولة مرة أخرى لاحقاً.'
        }

        return render(request, 'core/group_list.html', context)


def group_detail(request, group_id):
    """View for displaying group details"""
    try:
        from groups.models import ReadingGroup, GroupMembership

        group = get_object_or_404(ReadingGroup, id=group_id)

        # Check if group is public or user is a member
        is_member = request.user.is_authenticated and GroupMembership.objects.filter(
            user=request.user,
            group=group,
            is_active=True
        ).exists()

        if not group.is_public and not is_member:
            messages.error(request, 'هذه المجموعة خاصة. يجب أن تكون عضواً للوصول إليها.')
            return redirect('core:group_list')

        # Get member role if user is a member
        member_role = None
        if is_member:
            membership = GroupMembership.objects.get(user=request.user, group=group)
            member_role = membership.role

        # Get active members
        active_members = User.objects.filter(
            groupmembership__group=group,
            groupmembership__is_active=True
        ).select_related('profile')

        # Get active and completed khatmas
        from khatma.models import Khatma
        active_khatmas = Khatma.objects.filter(
            group=group,
            is_completed=False
        ).order_by('-created_at')

        completed_khatmas = Khatma.objects.filter(
            group=group,
            is_completed=True
        ).order_by('-completed_at')[:5]

        context = {
            'group': group,
            'is_member': is_member,
            'member_role': member_role,
            'is_admin': member_role == 'admin',
            'is_moderator': member_role in ['admin', 'moderator'],
            'active_members': active_members,
            'active_khatmas': active_khatmas,
            'completed_khatmas': completed_khatmas
        }

        return render(request, 'core/group_detail.html', context)
    except Exception as e:
        # Log the error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in group_detail view: {str(e)}")

        # Return an error message
        messages.error(request, 'حدث خطأ أثناء تحميل تفاصيل المجموعة. يرجى المحاولة مرة أخرى لاحقاً.')
        return redirect('core:index')


@login_required
def create_deceased(request):
    """View for creating a new deceased person"""
    try:
        from khatma.models import Deceased
        import logging

        logger = logging.getLogger(__name__)
        logger.info("Creating new deceased person")

        if request.method == 'POST':
            try:
                name = request.POST.get('name')
                death_date = request.POST.get('death_date')
                relation = request.POST.get('relation')
                photo = request.FILES.get('photo')

                logger.info(f"Received form data: name={name}, death_date={death_date}, relation={relation}, photo={photo is not None}")

                if name and death_date:
                    try:
                        deceased = Deceased(
                            name=name,
                            death_date=death_date,
                            relation=relation,
                            added_by=request.user
                        )

                        if photo:
                            deceased.photo = photo

                        deceased.save()
                        logger.info(f"Successfully created deceased person: {name}")

                        messages.success(request, 'تم إضافة المتوفى بنجاح')
                        return redirect('core:deceased_list')
                    except Exception as e:
                        logger.error(f"Error saving deceased person: {str(e)}")
                        messages.error(request, f'حدث خطأ أثناء حفظ بيانات المتوفى: {str(e)}')
                else:
                    logger.warning("Missing required fields: name or death_date")
                    messages.error(request, 'يرجى إدخال اسم المتوفى وتاريخ الوفاة')
            except Exception as e:
                logger.error(f"Error processing form data: {str(e)}")
                messages.error(request, 'حدث خطأ أثناء معالجة البيانات. يرجى المحاولة مرة أخرى.')

        return render(request, 'core/create_deceased.html')
    except Exception as e:
        # Log the error
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error in create_deceased view: {str(e)}")
        logger.error(traceback.format_exc())

        # Return an error message
        context = {
            'error_message': 'حدث خطأ أثناء تحميل صفحة إضافة متوفى. يرجى المحاولة مرة أخرى لاحقاً.'
        }

        return render(request, 'core/create_deceased.html', context)


@login_required
def deceased_list(request):
    """View for listing deceased persons"""
    try:
        from khatma.models import Deceased
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Listing deceased persons for user: {request.user.username}")

        try:
            deceased_list = Deceased.objects.filter(added_by=request.user).order_by('-death_date')
            logger.info(f"Found {deceased_list.count()} deceased persons for user {request.user.username}")
        except Exception as e:
            logger.error(f"Error retrieving deceased persons: {str(e)}")
            deceased_list = []
            messages.warning(request, 'تعذر تحميل قائمة المتوفين. يرجى المحاولة مرة أخرى لاحقاً.')

        context = {
            'deceased_list': deceased_list
        }

        return render(request, 'core/deceased_list.html', context)
    except Exception as e:
        # Log the error
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error in deceased_list view: {str(e)}")
        logger.error(traceback.format_exc())

        # Return an error message
        context = {
            'error_message': 'حدث خطأ أثناء تحميل قائمة المتوفين. يرجى المحاولة مرة أخرى لاحقاً.',
            'deceased_list': []
        }

        return render(request, 'core/deceased_list.html', context)


@login_required
def deceased_detail(request, deceased_id):
    """View for displaying deceased person details"""
    try:
        from khatma.models import Deceased, Khatma
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Viewing deceased person details for ID: {deceased_id}")

        try:
            deceased = get_object_or_404(Deceased, id=deceased_id)

            # Check if user is allowed to view this deceased person
            if deceased.added_by != request.user:
                logger.warning(f"Unauthorized access attempt to deceased ID {deceased_id} by user {request.user.username}")
                messages.error(request, 'ليس لديك صلاحية لعرض هذا المتوفى')
                return redirect('core:deceased_list')

            # Get khatmas for this deceased person
            try:
                khatmas = Khatma.objects.filter(deceased=deceased).order_by('-created_at')
                memorial_khatmas = khatmas
                logger.info(f"Found {khatmas.count()} khatmas for deceased ID {deceased_id}")
            except Exception as e:
                logger.error(f"Error retrieving khatmas for deceased ID {deceased_id}: {str(e)}")
                memorial_khatmas = []
                messages.warning(request, 'تعذر تحميل الختمات المرتبطة بهذا المتوفى')

            context = {
                'deceased': deceased,
                'khatmas': khatmas,
                'memorial_khatmas': memorial_khatmas
            }

            return render(request, 'core/deceased_detail.html', context)
        except Exception as e:
            logger.error(f"Error retrieving deceased person with ID {deceased_id}: {str(e)}")
            messages.error(request, 'تعذر العثور على المتوفى المطلوب')
            return redirect('core:deceased_list')
    except Exception as e:
        # Log the error
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error in deceased_detail view: {str(e)}")
        logger.error(traceback.format_exc())

        # Return an error message
        messages.error(request, 'حدث خطأ أثناء عرض تفاصيل المتوفى. يرجى المحاولة مرة أخرى لاحقاً.')
        return redirect('core:deceased_list')


def community(request):
    """View for the community page"""
    from khatma.models import Khatma

    # Get recent public khatmas
    public_khatmas = Khatma.objects.filter(is_public=True).order_by('-created_at')[:10]

    # Get most active users
    from django.contrib.auth.models import User
    from django.db.models import Count
    active_users = User.objects.annotate(
        khatma_count=Count('created_khatmas'),
        participation_count=Count('joined_khatmas')
    ).order_by('-khatma_count', '-participation_count')[:10]

    context = {
        'public_khatmas': public_khatmas,
        'active_users': active_users
    }

    return render(request, 'core/community.html', context)


def community_khatmas(request):
    """View for displaying community khatmas"""
    try:
        from khatma.models import Khatma
        import logging

        logger = logging.getLogger(__name__)
        logger.info("Loading community khatmas")

        # Get all public khatmas
        try:
            public_khatmas = Khatma.objects.filter(is_public=True).order_by('-created_at')

            # Filter by type if specified
            khatma_type = request.GET.get('type')
            if khatma_type:
                public_khatmas = public_khatmas.filter(khatma_type=khatma_type)

            logger.info(f"Found {public_khatmas.count()} public khatmas")
        except Exception as e:
            logger.error(f"Error getting public khatmas: {str(e)}")
            public_khatmas = []
            khatma_type = None

        # Pagination
        try:
            paginator = Paginator(public_khatmas, 12)  # 12 khatmas per page
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
        except Exception as e:
            logger.error(f"Error with pagination: {str(e)}")
            page_obj = None

        context = {
            'page_obj': page_obj,
            'khatma_type': khatma_type
        }

        return render(request, 'core/community_khatmas.html', context)
    except Exception as e:
        # Log the error
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error in community_khatmas view: {str(e)}")
        logger.error(traceback.format_exc())

        # Return an error message
        context = {
            'error_message': 'حدث خطأ أثناء تحميل الختمات المجتمعية. يرجى المحاولة مرة أخرى لاحقاً.'
        }

        return render(request, 'core/community_khatmas.html', context)


def community_leaderboard(request):
    """View for displaying community leaderboard"""
    try:
        from django.contrib.auth.models import User
        from django.db.models import Count, Sum
        import logging

        logger = logging.getLogger(__name__)
        logger.info("Loading community leaderboard")

        # Get top users by number of khatmas created
        try:
            top_creators = User.objects.annotate(
                khatma_count=Count('created_khatmas')
            ).filter(khatma_count__gt=0).order_by('-khatma_count')[:10]
            logger.info(f"Found {top_creators.count()} top creators")
        except Exception as e:
            logger.error(f"Error getting top creators: {str(e)}")
            top_creators = []

        # Get top users by number of khatmas participated in
        try:
            top_participants = User.objects.annotate(
                participation_count=Count('joined_khatmas')
            ).filter(participation_count__gt=0).order_by('-participation_count')[:10]
            logger.info(f"Found {top_participants.count()} top participants")
        except Exception as e:
            logger.error(f"Error getting top participants: {str(e)}")
            top_participants = []

        # Get top users by number of parts read
        try:
            top_readers = User.objects.annotate(
                parts_read=Sum('quran_readings__part_number')
            ).filter(parts_read__gt=0).order_by('-parts_read')[:10]
            logger.info(f"Found {top_readers.count()} top readers")
        except Exception as e:
            logger.error(f"Error getting top readers: {str(e)}")
            top_readers = []

        context = {
            'top_creators': top_creators,
            'top_participants': top_participants,
            'top_readers': top_readers
        }

        return render(request, 'core/community_leaderboard.html', context)
    except Exception as e:
        # Log the error
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error in community_leaderboard view: {str(e)}")
        logger.error(traceback.format_exc())

        # Return an error message
        context = {
            'error_message': 'حدث خطأ أثناء تحميل لوحة الشرف. يرجى المحاولة مرة أخرى لاحقاً.'
        }

        return render(request, 'core/community_leaderboard.html', context)


@login_required
def create_group(request):
    """View for creating a new reading group"""
    from groups.models import ReadingGroup

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_public = request.POST.get('is_public') == 'on'
        image = request.FILES.get('image')

        if name:
            group = ReadingGroup(
                name=name,
                description=description,
                is_public=is_public,
                creator=request.user
            )

            if image:
                group.image = image

            group.save()

            # Add creator as a member with admin role
            from groups.models import GroupMembership
            GroupMembership.objects.create(
                user=request.user,
                group=group,
                role='admin'
            )

            messages.success(request, 'تم إنشاء المجموعة بنجاح')
            return redirect('core:group_detail', group_id=group.id)
        else:
            messages.error(request, 'يرجى إدخال اسم المجموعة')

    return render(request, 'core/create_group.html')


@login_required
def group_chat_redirect(request, group_id):
    """Redirect to the group chat page"""
    return redirect('chat:group_chat', group_id=group_id)


@login_required
def create_khatma(request):
    """View for creating a new Khatma"""
    try:
        from khatma.models import Khatma, KhatmaPart, Deceased, Participant
        from core.forms import KhatmaCreationForm
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Creating new khatma for user: {request.user.username}")

        if request.method == 'POST':
            form = KhatmaCreationForm(request.POST)
            if form.is_valid():
                try:
                    # Get form data
                    title = form.cleaned_data['title']
                    description = form.cleaned_data['description']
                    khatma_type = form.cleaned_data['khatma_type']
                    is_public = form.cleaned_data['is_public']
                    start_date = form.cleaned_data['start_date']
                    end_date = form.cleaned_data['end_date']
                    frequency = form.cleaned_data['frequency']
                    deceased_id = request.POST.get('deceased')

                    logger.info(f"Form data: title={title}, khatma_type={khatma_type}, is_public={is_public}")

                    # Create khatma
                    khatma = Khatma(
                        title=title,
                        description=description,
                        khatma_type=khatma_type,
                        is_public=is_public,
                        creator=request.user,
                        start_date=start_date,
                        end_date=end_date,
                        frequency=frequency
                    )

                    # Set deceased if provided
                    if deceased_id and khatma_type == 'memorial':
                        try:
                            deceased = Deceased.objects.get(id=deceased_id, added_by=request.user)
                            khatma.deceased = deceased
                            logger.info(f"Set deceased: {deceased.name}")
                        except Deceased.DoesNotExist:
                            logger.warning(f"Deceased with ID {deceased_id} not found")

                    khatma.save()
                    logger.info(f"Created khatma with ID: {khatma.id}")

                    # Create parts for the khatma
                    try:
                        # First check if parts already exist
                        existing_parts = KhatmaPart.objects.filter(khatma=khatma).count()
                        if existing_parts == 0:
                            # Create parts only if none exist
                            for i in range(1, 31):  # 30 parts of Quran
                                KhatmaPart.objects.create(
                                    khatma=khatma,
                                    part_number=i
                                )
                            logger.info("Created 30 parts for the khatma")
                        else:
                            logger.info(f"Skipped creating parts - {existing_parts} parts already exist")
                    except Exception as e:
                        logger.error(f"Error creating khatma parts: {str(e)}")
                        # Continue with the process even if parts creation fails
                        # The parts can be created later if needed

                    # Add creator as participant
                    try:
                        # Check if user is already a participant
                        participant, created = Participant.objects.get_or_create(
                            user=request.user,
                            khatma=khatma
                        )
                        if created:
                            logger.info(f"Added user {request.user.username} as participant")
                        else:
                            logger.info(f"User {request.user.username} is already a participant")
                    except Exception as e:
                        logger.error(f"Error adding participant: {str(e)}")
                        # Continue with the process even if participant creation fails

                    messages.success(request, 'تم إنشاء الختمة بنجاح')
                    logger.info(f"Redirecting to khatma dashboard after successful khatma creation")
                    # Redirect to the khatma dashboard
                    return redirect('core:khatma_dashboard')
                except Exception as e:
                    logger.error(f"Error creating khatma: {str(e)}")
                    messages.error(request, f'حدث خطأ أثناء إنشاء الختمة: {str(e)}')
            else:
                logger.warning(f"Form validation errors: {form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
        else:
            form = KhatmaCreationForm()
            logger.info("Displaying empty form")

        # Get user's deceased persons for memorial khatmas
        try:
            deceased_list = Deceased.objects.filter(added_by=request.user).order_by('-death_date')
            logger.info(f"Found {deceased_list.count()} deceased persons for user {request.user.username}")
        except Exception as e:
            logger.error(f"Error retrieving deceased list: {str(e)}")
            deceased_list = []
            messages.warning(request, 'تعذر تحميل قائمة المتوفين. يرجى المحاولة مرة أخرى لاحقاً.')

        context = {
            'form': form,
            'deceased_list': deceased_list
        }

        return render(request, 'core/create_khatma.html', context)
    except Exception as e:
        # Log the error
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error in create_khatma view: {str(e)}")
        logger.error(traceback.format_exc())

        # Return an error message
        context = {
            'error_message': 'حدث خطأ أثناء تحميل صفحة إنشاء ختمة. يرجى المحاولة مرة أخرى لاحقاً.'
        }

        return render(request, 'core/create_khatma.html', context)


def khatma_detail(request, khatma_id):
    """View for displaying khatma details"""
    try:
        from khatma.models import Khatma, KhatmaPart, Participant
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Loading khatma details for ID: {khatma_id}")

        try:
            khatma = get_object_or_404(Khatma, id=khatma_id)
            logger.info(f"Found khatma: {khatma.title}")

            # Check if khatma is public or user is a participant
            is_participant = request.user.is_authenticated and Participant.objects.filter(
                user=request.user,
                khatma=khatma
            ).exists()

            is_creator = request.user.is_authenticated and khatma.creator == request.user

            if not khatma.is_public and not is_participant and not is_creator:
                messages.error(request, 'هذه الختمة خاصة. يجب أن تكون مشاركًا للوصول إليها.')
                return redirect('core:index')

            # Get parts with their assignments
            try:
                parts = KhatmaPart.objects.filter(khatma=khatma).order_by('part_number')
                logger.info(f"Found {parts.count()} parts for khatma ID {khatma_id}")

                # Calculate completed parts
                completed_parts = parts.filter(is_completed=True).count()
                total_parts = parts.count()
                logger.info(f"Completed parts: {completed_parts}/{total_parts}")
            except Exception as e:
                logger.error(f"Error retrieving parts for khatma ID {khatma_id}: {str(e)}")
                parts = []
                completed_parts = 0
                total_parts = 30

            # Get participants
            try:
                participants = Participant.objects.filter(khatma=khatma).select_related('user')
                logger.info(f"Found {participants.count()} participants for khatma ID {khatma_id}")
            except Exception as e:
                logger.error(f"Error retrieving participants for khatma ID {khatma_id}: {str(e)}")
                participants = []

            # Get posts (if any)
            posts = []

            context = {
                'khatma': khatma,
                'parts': parts,
                'participants': participants,
                'is_participant': is_participant,
                'is_creator': is_creator,
                'progress_percentage': khatma.get_progress_percentage() if hasattr(khatma, 'get_progress_percentage') else 0,
                'completed_parts': completed_parts,
                'total_parts': total_parts,
                'posts': posts
            }

            return render(request, 'core/khatma_merged_dashboard.html', context)
        except Exception as e:
            logger.error(f"Error retrieving khatma with ID {khatma_id}: {str(e)}")
            messages.error(request, 'تعذر العثور على الختمة المطلوبة')
            return redirect('core:index')
    except Exception as e:
        # Log the error
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error in khatma_detail view: {str(e)}")
        logger.error(traceback.format_exc())

        # Return an error message
        messages.error(request, 'حدث خطأ غير متوقع. الرجاء المحاولة مرة أخرى لاحقاً.')
        return redirect('core:index')


@login_required
def khatma_chat_redirect(request, khatma_id):
    """Redirect to the khatma chat page"""
    return redirect('chat:khatma_chat', khatma_id=khatma_id)


def quran_part_view(request, part_number):
    """View for displaying a specific part of the Quran"""
    from quran.models import QuranPart, Ayah

    # Get the part
    part = get_object_or_404(QuranPart, part_number=part_number)

    # Get all ayahs in this part
    ayahs = Ayah.objects.filter(part=part).order_by('surah__number', 'number')

    # Group ayahs by surah
    surahs = {}
    for ayah in ayahs:
        if ayah.surah.number not in surahs:
            surahs[ayah.surah.number] = {
                'surah': ayah.surah,
                'ayahs': []
            }
        surahs[ayah.surah.number]['ayahs'].append(ayah)

    context = {
        'part': part,
        'surahs': surahs.values(),
        'prev_part': part_number - 1 if part_number > 1 else None,
        'next_part': part_number + 1 if part_number < 30 else None
    }

    return render(request, 'core/quran_part.html', context)


def quran_reciters(request):
    """View for displaying list of Quran reciters"""
    from quran.models import Reciter

    reciters = Reciter.objects.all().order_by('name')

    context = {
        'reciters': reciters
    }

    return render(request, 'core/quran_reciters.html', context)


def reciter_surahs(request, reciter_name):
    """View for displaying surahs by a specific reciter"""
    from quran.models import Reciter, Surah, ReciterSurah

    reciter = get_object_or_404(Reciter, slug=reciter_name)

    # Get all surahs with audio by this reciter
    reciter_surahs = ReciterSurah.objects.filter(reciter=reciter).select_related('surah')

    context = {
        'reciter': reciter,
        'reciter_surahs': reciter_surahs
    }

    return render(request, 'core/reciter_surahs.html', context)


@login_required
def user_profile(request):
    """View for displaying user profile"""
    try:
        # Get user's khatmas
        from khatma.models import Khatma, Participant
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Loading user profile for user: {request.user.username}")

        try:
            created_khatmas = Khatma.objects.filter(creator=request.user).order_by('-created_at')
            logger.info(f"Found {created_khatmas.count()} created khatmas for user {request.user.username}")
        except Exception as e:
            logger.error(f"Error retrieving created khatmas: {str(e)}")
            created_khatmas = []

        # Get khatmas the user is participating in
        try:
            participating_khatmas = Khatma.objects.filter(
                participants=request.user
            ).exclude(
                creator=request.user
            ).order_by('-created_at')
            logger.info(f"Found {participating_khatmas.count()} participating khatmas for user {request.user.username}")
        except Exception as e:
            logger.error(f"Error retrieving participating khatmas: {str(e)}")
            participating_khatmas = []

        # Get user's groups
        try:
            from groups.models import ReadingGroup, GroupMembership
            user_groups = ReadingGroup.objects.filter(
                groupmembership__user=request.user,
                groupmembership__is_active=True
            ).order_by('-created_at')
            logger.info(f"Found {user_groups.count()} groups for user {request.user.username}")
        except Exception as e:
            logger.error(f"Error retrieving user groups: {str(e)}")
            user_groups = []

        # Get user's achievements
        try:
            from users.models import UserAchievement
            achievements = UserAchievement.objects.filter(user=request.user).order_by('-date_earned')
            logger.info(f"Found {achievements.count()} achievements for user {request.user.username}")
        except Exception as e:
            logger.error(f"Error retrieving user achievements: {str(e)}")
            achievements = []

        context = {
            'created_khatmas': created_khatmas,
            'participating_khatmas': participating_khatmas,
            'user_groups': user_groups,
            'achievements': achievements
        }

        return render(request, 'core/user_profile.html', context)
    except Exception as e:
        # Log the error
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error in user_profile view: {str(e)}")
        logger.error(traceback.format_exc())

        # Return an error message
        context = {
            'error_message': 'حدث خطأ أثناء تحميل الملف الشخصي. يرجى المحاولة مرة أخرى لاحقاً.'
        }

        return render(request, 'core/user_profile.html', context)


@login_required
def user_achievements(request):
    """View for displaying user achievements"""
    try:
        from users.models import UserAchievement
        from .achievements import get_total_points, get_user_level, get_available_achievements
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Loading achievements for user: {request.user.username}")

        try:
            # Get user's achievements
            user_achievements = UserAchievement.objects.filter(user=request.user).order_by('-date_earned')
            logger.info(f"Found {user_achievements.count()} achievements for user {request.user.username}")

            # Calculate total points and level
            total_points = get_total_points(request.user)
            level = get_user_level(request.user)

            # Get available achievements
            available_achievements = get_available_achievements(request.user)

            # Example of all achievements
            all_achievements = [
                {
                    'name': 'قارئ نشط',
                    'description': 'أكمل 5 أجزاء من القرآن',
                    'achieved': True,
                    'points': 50
                },
                {
                    'name': 'مشارك في الختمات',
                    'description': 'شارك في 3 ختمات',
                    'achieved': False,
                    'points': 30
                },
                {
                    'name': 'منشئ ختمات',
                    'description': 'أنشئ 2 ختمات',
                    'achieved': True,
                    'points': 40
                },
                {
                    'name': 'قارئ متميز',
                    'description': 'أكمل 10 أجزاء من القرآن',
                    'achieved': False,
                    'points': 100
                },
                {
                    'name': 'مشارك فعال',
                    'description': 'شارك في 5 ختمات',
                    'achieved': False,
                    'points': 60
                },
                {
                    'name': 'منشئ نشط',
                    'description': 'أنشئ 5 ختمات',
                    'achieved': False,
                    'points': 80
                },
                {
                    'name': 'ختمة كاملة',
                    'description': 'أكمل ختمة كاملة بمفردك',
                    'achieved': False,
                    'points': 200
                },
                {
                    'name': 'مساهم في المجتمع',
                    'description': 'شارك في 10 ختمات',
                    'achieved': False,
                    'points': 120
                }
            ]

            context = {
                'user_achievements': user_achievements,
                'achievements': all_achievements,
                'total_points': total_points,
                'level': level,
                'available_achievements': available_achievements
            }

            return render(request, 'core/user_achievements.html', context)
        except Exception as e:
            logger.error(f"Error retrieving user achievements: {str(e)}")
            context = {
                'error_message': 'حدث خطأ أثناء تحميل الإنجازات. يرجى المحاولة مرة أخرى لاحقاً.',
                'user_achievements': [],
                'achievements': [],
                'total_points': 0,
                'level': 1,
                'available_achievements': []
            }
            return render(request, 'core/user_achievements.html', context)
    except Exception as e:
        # Log the error
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error in user_achievements view: {str(e)}")
        logger.error(traceback.format_exc())

        # Return an error message
        context = {
            'error_message': 'حدث خطأ أثناء تحميل الإنجازات. يرجى المحاولة مرة أخرى لاحقاً.',
            'user_achievements': [],
            'achievements': [],
            'total_points': 0,
            'level': 1,
            'available_achievements': []
        }

        return render(request, 'core/user_achievements.html', context)


@login_required
def user_settings(request):
    """View for user settings"""
    from users.models import Profile

    # Get or create user profile
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update user information
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        # Update profile information
        bio = request.POST.get('bio')
        location = request.POST.get('location')
        avatar = request.FILES.get('avatar')

        # Update notification settings
        email_notifications = request.POST.get('email_notifications') == 'on'
        push_notifications = request.POST.get('push_notifications') == 'on'

        # Update user
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()

        # Update profile
        profile.bio = bio
        profile.location = location
        profile.email_notifications = email_notifications
        profile.push_notifications = push_notifications

        if avatar:
            profile.avatar = avatar

        profile.save()

        messages.success(request, 'تم تحديث الإعدادات بنجاح')
        return redirect('core:profile')

    context = {
        'profile': profile
    }

    return render(request, 'core/user_settings.html', context)


@login_required
def khatma_dashboard(request):
    """View for displaying khatma dashboard"""
    try:
        from khatma.models import Khatma, KhatmaPart, Participant
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Loading khatma dashboard for user: {request.user.username}")

        try:
            # Get khatmas created by the user
            created_khatmas = Khatma.objects.filter(creator=request.user).order_by('-created_at')
            logger.info(f"Found {created_khatmas.count()} khatmas created by user {request.user.username}")

            # Get khatmas where the user is a participant
            participating_khatma_ids = Participant.objects.filter(
                user=request.user
            ).values_list('khatma_id', flat=True)

            participating_khatmas = Khatma.objects.filter(
                id__in=participating_khatma_ids
            ).exclude(
                creator=request.user  # Exclude khatmas created by the user
            ).order_by('-created_at')

            logger.info(f"Found {participating_khatmas.count()} khatmas where user {request.user.username} is a participant")

            # Get recent activity
            recent_parts = KhatmaPart.objects.filter(
                khatma__in=list(created_khatmas) + list(participating_khatmas),
                is_completed=True
            ).order_by('-completed_at')[:10]

            # Calculate statistics
            total_khatmas = created_khatmas.count() + participating_khatmas.count()
            completed_khatmas = (created_khatmas.filter(is_completed=True).count() +
                                participating_khatmas.filter(is_completed=True).count())

            # Calculate total parts and completed parts
            total_parts = KhatmaPart.objects.filter(
                khatma__in=list(created_khatmas) + list(participating_khatmas)
            ).count()

            completed_parts = KhatmaPart.objects.filter(
                khatma__in=list(created_khatmas) + list(participating_khatmas),
                is_completed=True
            ).count()

            # Calculate overall progress
            overall_progress = (completed_parts / total_parts * 100) if total_parts > 0 else 0

            context = {
                'created_khatmas': created_khatmas,
                'participating_khatmas': participating_khatmas,
                'recent_parts': recent_parts,
                'total_khatmas': total_khatmas,
                'completed_khatmas': completed_khatmas,
                'total_parts': total_parts,
                'completed_parts': completed_parts,
                'overall_progress': overall_progress
            }

            return render(request, 'core/khatma_merged_dashboard.html', context)
        except Exception as e:
            logger.error(f"Error retrieving khatma data: {str(e)}")
            context = {
                'error_message': 'حدث خطأ أثناء تحميل لوحة التحكم. يرجى المحاولة مرة أخرى لاحقاً.',
                'created_khatmas': [],
                'participating_khatmas': [],
                'recent_parts': [],
                'total_khatmas': 0,
                'completed_khatmas': 0,
                'total_parts': 0,
                'completed_parts': 0,
                'overall_progress': 0
            }
            return render(request, 'core/khatma_merged_dashboard.html', context)
    except Exception as e:
        # Log the error
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error in khatma_dashboard view: {str(e)}")
        logger.error(traceback.format_exc())

        # Return an error message
        context = {
            'error_message': 'حدث خطأ أثناء تحميل لوحة التحكم. يرجى المحاولة مرة أخرى لاحقاً.',
            'created_khatmas': [],
            'participating_khatmas': [],
            'recent_parts': [],
            'total_khatmas': 0,
            'completed_khatmas': 0,
            'total_parts': 0,
            'completed_parts': 0,
            'overall_progress': 0
        }

        return render(request, 'core/khatma_merged_dashboard.html', context)


@login_required
def notifications(request):
    """View for displaying user notifications"""
    try:
        from notifications.models import Notification
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Loading notifications for user: {request.user.username}")

        try:
            # Get user's notifications
            notifications = Notification.objects.filter(
                user=request.user
            ).order_by('-created_at')
            logger.info(f"Found {notifications.count()} notifications for user {request.user.username}")

            # Mark all as read
            if request.GET.get('mark_all_read'):
                try:
                    unread_count = notifications.filter(is_read=False).count()
                    notifications.filter(is_read=False).update(is_read=True)
                    logger.info(f"Marked {unread_count} notifications as read for user {request.user.username}")
                    messages.success(request, 'تم تحديد جميع الإشعارات كمقروءة')
                    return redirect('core:notifications')
                except Exception as e:
                    logger.error(f"Error marking notifications as read: {str(e)}")
                    messages.error(request, 'حدث خطأ أثناء تحديد الإشعارات كمقروءة')

            try:
                # Pagination
                paginator = Paginator(notifications, 20)  # 20 notifications per page
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)

                # Count unread notifications
                unread_count = notifications.filter(is_read=False).count()

                context = {
                    'notifications': notifications,
                    'page_obj': page_obj,
                    'unread_count': unread_count
                }

                return render(request, 'core/notifications.html', context)
            except Exception as e:
                logger.error(f"Error with pagination: {str(e)}")
                context = {
                    'notifications': notifications,
                    'unread_count': notifications.filter(is_read=False).count(),
                    'error_message': 'حدث خطأ أثناء عرض الإشعارات. يرجى المحاولة مرة أخرى لاحقاً.'
                }
                return render(request, 'core/notifications.html', context)
        except Exception as e:
            logger.error(f"Error retrieving notifications: {str(e)}")
            context = {
                'notifications': [],
                'unread_count': 0,
                'error_message': 'حدث خطأ أثناء تحميل الإشعارات. يرجى المحاولة مرة أخرى لاحقاً.'
            }
            return render(request, 'core/notifications.html', context)
    except Exception as e:
        # Log the error
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error in notifications view: {str(e)}")
        logger.error(traceback.format_exc())

        # Return an error message
        context = {
            'notifications': [],
            'unread_count': 0,
            'error_message': 'حدث خطأ أثناء تحميل الإشعارات. يرجى المحاولة مرة أخرى لاحقاً.'
        }

        return render(request, 'core/notifications.html', context)
