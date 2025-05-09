# View Documentation

## Core Views

### index
The main homepage view.

```python
index(request)
```

**URL Pattern**: `/`

### khatma_dashboard
View for displaying the khatma dashboard.

```python
khatma_dashboard(request)
```

**URL Pattern**: `/khatma/dashboard/`

### khatma_detail
View for displaying a specific khatma's details.

```python
khatma_detail(request, khatma_id)
```

**URL Pattern**: `/khatma/<int:khatma_id>/`

### create_khatma
View for creating a new khatma.

```python
create_khatma(request)
```

**URL Pattern**: `/khatma/create/`

### edit_khatma
View for editing an existing khatma.

```python
edit_khatma(request, khatma_id)
```

**URL Pattern**: `/khatma/<int:khatma_id>/edit/`

### delete_khatma
View for deleting a khatma.

```python
delete_khatma(request, khatma_id)
```

**URL Pattern**: `/khatma/<int:khatma_id>/delete/`

### join_khatma
View for joining a khatma.

```python
join_khatma(request, khatma_id)
```

**URL Pattern**: `/khatma/<int:khatma_id>/join/`

### leave_khatma
View for leaving a khatma.

```python
leave_khatma(request, khatma_id)
```

**URL Pattern**: `/khatma/<int:khatma_id>/leave/`

### assign_part
View for assigning a part to a user.

```python
assign_part(request, khatma_id, part_id)
```

**URL Pattern**: `/khatma/<int:khatma_id>/part/<int:part_id>/assign/`

### complete_part
View for marking a part as completed.

```python
complete_part(request, khatma_id, part_id)
```

**URL Pattern**: `/khatma/<int:khatma_id>/part/<int:part_id>/complete/`

### quran_part
View for displaying a specific part of the Quran.

```python
quran_part(request, part_number)
```

**URL Pattern**: `/quran/part/<int:part_number>/`

### surah_view
View for displaying a specific surah.

```python
surah_view(request, surah_number)
```

**URL Pattern**: `/quran/surah/<int:surah_number>/`

### reciters
View for displaying a list of Quran reciters.

```python
reciters(request)
```

**URL Pattern**: `/quran/reciters/`

### reciter_surahs
View for displaying a specific reciter's surahs.

```python
reciter_surahs(request, reciter_id)
```

**URL Pattern**: `/quran/reciters/<int:reciter_id>/`

### profile
View for displaying a user's profile.

```python
profile(request, username=None)
```

**URL Pattern**: `/profile/` or `/profile/<str:username>/`

### edit_profile
View for editing a user's profile.

```python
edit_profile(request)
```

**URL Pattern**: `/profile/edit/`

### user_achievements
View for displaying a user's achievements.

```python
user_achievements(request, username=None)
```

**URL Pattern**: `/achievements/` or `/achievements/<str:username>/`

### community
View for displaying the community page.

```python
community(request)
```

**URL Pattern**: `/community/`

### community_khatmas
View for displaying community khatmas.

```python
community_khatmas(request)
```

**URL Pattern**: `/community/khatmas/`

### community_leaderboard
View for displaying the community leaderboard.

```python
community_leaderboard(request)
```

**URL Pattern**: `/community/leaderboard/`

### notifications
View for displaying user notifications.

```python
notifications(request)
```

**URL Pattern**: `/notifications/`

### mark_notification_read
View for marking a notification as read.

```python
mark_notification_read(request, notification_id)
```

**URL Pattern**: `/notifications/<int:notification_id>/read/`

### about_page
View for displaying the about page.

```python
about_page(request)
```

**URL Pattern**: `/about/`

### contact_us
View for displaying the contact us page.

```python
contact_us(request)
```

**URL Pattern**: `/contact/`

### help_page
View for displaying the help page.

```python
help_page(request)
```

**URL Pattern**: `/help/`

## Group Views

### group_list
View for displaying a list of reading groups.

```python
group_list(request)
```

**URL Pattern**: `/groups/`

### group_detail
View for displaying a specific group's details.

```python
group_detail(request, group_id)
```

**URL Pattern**: `/groups/<int:group_id>/`

### create_group
View for creating a new reading group.

```python
create_group(request)
```

**URL Pattern**: `/groups/create/`

### edit_group
View for editing an existing reading group.

```python
edit_group(request, group_id)
```

**URL Pattern**: `/groups/<int:group_id>/edit/`

### delete_group
View for deleting a reading group.

```python
delete_group(request, group_id)
```

**URL Pattern**: `/groups/<int:group_id>/delete/`

### join_group
View for joining a reading group.

```python
join_group(request, group_id)
```

**URL Pattern**: `/groups/<int:group_id>/join/`

### leave_group
View for leaving a reading group.

```python
leave_group(request, group_id)
```

**URL Pattern**: `/groups/<int:group_id>/leave/`
