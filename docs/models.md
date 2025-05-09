# Model Documentation

## Core Models

### Post
Represents a social post in the community section.

#### Fields
- **id**: Primary key
- **user**: ForeignKey to User
- **content**: TextField
- **post_type**: CharField with choices (community, announcement)
- **created_at**: DateTimeField
- **updated_at**: DateTimeField
- **view_count**: IntegerField
- **is_pinned**: BooleanField

### PostReaction
Represents a reaction to a post (like, prayer, etc.).

#### Fields
- **id**: Primary key
- **user**: ForeignKey to User
- **post**: ForeignKey to Post
- **reaction_type**: CharField with choices (like, prayer, support, thanks)
- **message**: TextField (optional)
- **created_at**: DateTimeField

## Khatma Models

### Khatma
Represents a Quran reading group.

#### Fields
- **id**: Primary key
- **title**: CharField
- **description**: TextField
- **creator**: ForeignKey to User
- **khatma_type**: CharField with choices (regular, memorial, group)
- **deceased**: ForeignKey to Deceased (optional)
- **is_public**: BooleanField
- **is_completed**: BooleanField
- **created_at**: DateTimeField
- **completed_at**: DateTimeField (optional)
- **group**: ForeignKey to ReadingGroup (optional)
- **is_group_khatma**: BooleanField
- **auto_distribute_parts**: BooleanField

### KhatmaPart
Represents a part of the Quran assigned in a Khatma.

#### Fields
- **id**: Primary key
- **khatma**: ForeignKey to Khatma
- **part**: ForeignKey to QuranPart
- **assigned_to**: ForeignKey to User (optional)
- **is_completed**: BooleanField
- **completed_at**: DateTimeField (optional)
- **assigned_at**: DateTimeField

### Participant
Represents a user participating in a Khatma.

#### Fields
- **id**: Primary key
- **user**: ForeignKey to User
- **khatma**: ForeignKey to Khatma
- **joined_at**: DateTimeField
- **is_active**: BooleanField

### Deceased
Represents a deceased person for memorial Khatmas.

#### Fields
- **id**: Primary key
- **name**: CharField
- **death_date**: DateField
- **birth_date**: DateField (optional)
- **photo**: ImageField (optional)
- **added_by**: ForeignKey to User
- **relationship**: CharField (optional)
- **created_at**: DateTimeField

## Quran Models

### QuranPart
Represents a Juz' (part) of the Quran.

#### Fields
- **id**: Primary key
- **part_number**: IntegerField
- **name_arabic**: CharField
- **name_english**: CharField
- **start_page**: IntegerField
- **end_page**: IntegerField

### Surah
Represents a Surah (chapter) of the Quran.

#### Fields
- **id**: Primary key
- **surah_number**: IntegerField
- **name_arabic**: CharField
- **name_english**: CharField
- **name_simple**: CharField
- **revelation_place**: CharField (Mecca or Medina)
- **revelation_order**: IntegerField
- **verse_count**: IntegerField

### Ayah
Represents an Ayah (verse) of the Quran.

#### Fields
- **id**: Primary key
- **surah**: ForeignKey to Surah
- **verse_number**: IntegerField
- **text_arabic**: TextField
- **text_simple**: TextField
- **juz**: IntegerField
- **page**: IntegerField

### QuranReciter
Represents a Quran reciter.

#### Fields
- **id**: Primary key
- **name_arabic**: CharField
- **name_english**: CharField
- **bio**: TextField (optional)
- **photo**: ImageField (optional)
- **style**: CharField (optional)

## User Models

### Profile
Extends the User model with additional information.

#### Fields
- **id**: Primary key
- **user**: OneToOneField to User
- **bio**: TextField (optional)
- **avatar**: ImageField (optional)
- **account_type**: CharField with choices (individual, family, organization)
- **total_points**: IntegerField
- **level**: IntegerField
- **family_admin**: BooleanField
- **family_group**: ForeignKey to Profile (optional)

### UserAchievement
Represents an achievement earned by a user.

#### Fields
- **id**: Primary key
- **user**: ForeignKey to User
- **achievement_type**: CharField with choices
- **earned_at**: DateTimeField
- **points_earned**: IntegerField
- **description**: TextField (optional)

## Group Models

### ReadingGroup
Represents a reading group for collaborative study.

#### Fields
- **id**: Primary key
- **name**: CharField
- **description**: TextField
- **creator**: ForeignKey to User
- **image**: ImageField (optional)
- **is_active**: BooleanField
- **is_public**: BooleanField
- **created_at**: DateTimeField
- **allow_join_requests**: BooleanField
- **max_members**: IntegerField
- **enable_chat**: BooleanField
- **enable_khatma_creation**: BooleanField

### GroupMembership
Represents a user's membership in a reading group.

#### Fields
- **id**: Primary key
- **user**: ForeignKey to User
- **group**: ForeignKey to ReadingGroup
- **role**: CharField with choices (member, admin, moderator)
- **joined_at**: DateTimeField

## Notification Models

### Notification
Represents a notification for a user.

#### Fields
- **id**: Primary key
- **user**: ForeignKey to User
- **notification_type**: CharField with choices
- **message**: TextField
- **is_read**: BooleanField
- **created_at**: DateTimeField
- **related_khatma**: ForeignKey to Khatma (optional)
- **related_group**: ForeignKey to ReadingGroup (optional)
- **related_user**: ForeignKey to User (optional)

## Chat Models

### KhatmaChat
Represents a chat message in a Khatma.

#### Fields
- **id**: Primary key
- **khatma**: ForeignKey to Khatma
- **user**: ForeignKey to User
- **message**: TextField
- **created_at**: DateTimeField
- **is_pinned**: BooleanField
- **has_attachment**: BooleanField
- **attachment**: FileField (optional)
- **attachment_type**: CharField (optional)

### GroupChat
Represents a chat message in a reading group.

#### Fields
- **id**: Primary key
- **group**: ForeignKey to ReadingGroup
- **user**: ForeignKey to User
- **message**: TextField
- **created_at**: DateTimeField
- **is_pinned**: BooleanField
- **has_attachment**: BooleanField
- **attachment**: FileField (optional)
- **attachment_type**: CharField (optional)
