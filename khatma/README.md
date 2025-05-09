# Khatma App

This app provides khatma functionality for the Khatma project.

## Features

- Feature 1
- Feature 2
- Feature 3

## Models

The app defines the following models:

- **Deceased**: Description of Deceased
- **Khatma**: Description of Khatma
- **Participant**: Description of Participant
- **KhatmaPart**: Description of KhatmaPart
- **PartAssignment**: Description of PartAssignment
- **QuranReading**: Description of QuranReading
- **PublicKhatma**: Description of PublicKhatma
- **KhatmaComment**: Description of KhatmaComment
- **KhatmaInteraction**: Description of KhatmaInteraction
- **PostReaction**: Description of PostReaction

## Views

The app provides the following views:

- **create_khatma**: Description of create_khatma
- **edit_khatma**: Description of edit_khatma
- **khatma_detail**: Description of khatma_detail
- **khatma_list**: Description of khatma_list
- **my_khatmas**: Description of my_khatmas
- **delete_khatma**: Description of delete_khatma
- **complete_khatma**: Description of complete_khatma
- **part_detail**: Description of part_detail
- **assign_part**: Description of assign_part
- **complete_part**: Description of complete_part
- **uncomplete_part**: Description of uncomplete_part
- **create_deceased**: Description of create_deceased
- **deceased_list**: Description of deceased_list
- **deceased_detail**: Description of deceased_detail
- **edit_deceased**: Description of edit_deceased
- **delete_deceased**: Description of delete_deceased
- **join_khatma**: Description of join_khatma
- **leave_khatma**: Description of leave_khatma
- **khatma_participants**: Description of khatma_participants
- **remove_participant**: Description of remove_participant
- **share_khatma**: Description of share_khatma
- **shared_khatma**: Description of shared_khatma
- **khatma_progress_api**: Description of khatma_progress_api
- **part_status_api**: Description of part_status_api
- **khatma_dashboard**: Description of khatma_dashboard
- **khatma_reading_plan**: Description of khatma_reading_plan
- **khatma_part_reading**: Description of khatma_part_reading
- **khatma_chat**: Description of khatma_chat
- **community_khatmas**: Description of community_khatmas
- **create_khatma_post**: Description of create_khatma_post

## URLs

The app defines the following URL patterns:

- `admin/dashboard/`: Description of admin/dashboard/
- `admin/`: Description of admin/
- `accounts/login/`: Description of accounts/login/
- `accounts/logout/`: Description of accounts/logout/
- `accounts/password_reset/`: Description of accounts/password_reset/
- `accounts/password_reset/done/`: Description of accounts/password_reset/done/
- `accounts/reset/<uidb64>/<token>/`: Description of accounts/reset/<uidb64>/<token>/
- `accounts/reset/done/`: Description of accounts/reset/done/
- `accounts/social/signup/`: Description of accounts/social/signup/
- `accounts/`: Description of accounts/
- ``: Description of 
- `users/`: Description of users/
- `quran/`: Description of quran/
- `groups/`: Description of groups/
- `notifications/`: Description of notifications/
- `chat/`: Description of chat/
- `create/`: Description of create/
- `<int:khatma_id>/`: Description of <int:khatma_id>/
- `list/`: Description of list/
- `my-khatmas/`: Description of my-khatmas/
- `<int:khatma_id>/edit/`: Description of <int:khatma_id>/edit/
- `<int:khatma_id>/delete/`: Description of <int:khatma_id>/delete/
- `<int:khatma_id>/complete/`: Description of <int:khatma_id>/complete/
- `<int:khatma_id>/dashboard/`: Description of <int:khatma_id>/dashboard/
- `reading-plan/`: Description of reading-plan/
- `<int:khatma_id>/part/<int:part_id>/`: Description of <int:khatma_id>/part/<int:part_id>/
- `<int:khatma_id>/part/<int:part_id>/assign/`: Description of <int:khatma_id>/part/<int:part_id>/assign/
- `<int:khatma_id>/part/<int:part_id>/complete/`: Description of <int:khatma_id>/part/<int:part_id>/complete/
- `<int:khatma_id>/part/<int:part_id>/uncomplete/`: Description of <int:khatma_id>/part/<int:part_id>/uncomplete/
- `<int:khatma_id>/part/<int:part_id>/read/`: Description of <int:khatma_id>/part/<int:part_id>/read/
- `deceased/create/`: Description of deceased/create/
- `deceased/list/`: Description of deceased/list/
- `deceased/<int:deceased_id>/`: Description of deceased/<int:deceased_id>/
- `deceased/<int:deceased_id>/edit/`: Description of deceased/<int:deceased_id>/edit/
- `deceased/<int:deceased_id>/delete/`: Description of deceased/<int:deceased_id>/delete/
- `<int:khatma_id>/join/`: Description of <int:khatma_id>/join/
- `<int:khatma_id>/leave/`: Description of <int:khatma_id>/leave/
- `<int:khatma_id>/participants/`: Description of <int:khatma_id>/participants/
- `<int:khatma_id>/remove-participant/<int:user_id>/`: Description of <int:khatma_id>/remove-participant/<int:user_id>/
- `share/<uuid:sharing_link>/`: Description of share/<uuid:sharing_link>/
- `<int:khatma_id>/share/`: Description of <int:khatma_id>/share/
- `<int:khatma_id>/post/create/`: Description of <int:khatma_id>/post/create/
- `community/`: Description of community/
- `<int:khatma_id>/chat/`: Description of <int:khatma_id>/chat/
- `api/khatma/<int:khatma_id>/progress/`: Description of api/khatma/<int:khatma_id>/progress/
- `api/khatma/<int:khatma_id>/part/<int:part_id>/status/`: Description of api/khatma/<int:khatma_id>/part/<int:part_id>/status/
- `khatma/`: Description of khatma/

## Forms

The app defines the following forms:

- **DeceasedForm**: Description of DeceasedForm
- **KhatmaCreationForm**: Description of KhatmaCreationForm
- **KhatmaEditForm**: Description of KhatmaEditForm
- **PartAssignmentForm**: Description of PartAssignmentForm
- **QuranReadingForm**: Description of QuranReadingForm
- **KhatmaPartForm**: Description of KhatmaPartForm
- **KhatmaShareForm**: Description of KhatmaShareForm
- **KhatmaFilterForm**: Description of KhatmaFilterForm
- **KhatmaChatForm**: Description of KhatmaChatForm
- **KhatmaInteractionForm**: Description of KhatmaInteractionForm

## Templates

The app uses the following templates:

- **create_deceased.html**: Description of create_deceased.html
- **create_khatma.html**: Description of create_khatma.html
- **deceased_detail.html**: Description of deceased_detail.html
- **deceased_list.html**: Description of deceased_list.html
- **khatma_detail.html**: Description of khatma_detail.html
- **khatma_list.html**: Description of khatma_list.html
- **my_khatmas.html**: Description of my_khatmas.html
- **part_detail.html**: Description of part_detail.html
- **share_khatma.html**: Description of share_khatma.html

## Static Files

The app uses the following static files:

