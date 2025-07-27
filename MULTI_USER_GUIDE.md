# Multi-User Support

Autodidact now supports multiple users on the same system, allowing each person to have their own separate learning journey, projects, and learner profiles.

## Features

### User Management
- **Simple Username-Based System**: No complex authentication - just usernames for identification
- **Easy User Switching**: Select your user from the sidebar dropdown
- **User Creation**: Add new users with a simple form
- **User Deletion**: Remove users and all their associated data

### User Isolation
Each user has their own:
- **Projects**: Only see and access your own learning projects
- **Learner Profiles**: Separate generic and topic-specific learning profiles
- **Progress Tracking**: Individual mastery scores and session history
- **Learning Sessions**: Personal session transcripts and history

### Default User
- Existing data is automatically migrated to a "default" user
- Perfect for single-user setups or backward compatibility
- Can be renamed but not deleted

## How to Use

### Adding a New User
1. Look for the "👤 User" section in the sidebar
2. Click "➕ Add User"
3. Enter a User ID (3+ characters, alphanumeric, no spaces)
4. Enter a Display Name
5. Click "Create"

### Switching Users
1. Use the dropdown in the "👤 User" section
2. Select the desired user
3. The page will refresh showing that user's projects and data

### Deleting a User
1. Select the user you want to delete
2. Click "🗑️ Delete" (only available for non-default users)
3. Confirm the deletion (this removes ALL their data permanently)

## Technical Details

### Database Schema
- Added `user` table for user management
- Added `user_id` foreign keys to existing tables:
  - `project.user_id`
  - `generic_learner_profile.user_id`
  - `topic_learner_profile.user_id`

### Migration
- Existing data is automatically migrated to user_id='default'
- No manual migration required

### User Identification
- User IDs must be unique, 3+ characters, alphanumeric
- Display names can be any string
- User selection is stored in Streamlit session state

### Data Isolation
- All database queries filter by current user
- Projects are user-scoped
- Learner profiles are user-specific
- Session data belongs to the project owner

## Benefits

1. **Family/Shared Computer Use**: Multiple people can use the same installation
2. **Separate Learning Paths**: Each person's learning journey is independent
3. **Privacy**: Users don't see each other's projects or progress
4. **Personalization**: Learning profiles adapt to each individual user
5. **Easy Management**: Simple user management without complex authentication

## Backward Compatibility

- Existing installations work without changes
- All existing data is preserved under the "default" user
- No breaking changes to existing functionality