# ivs-valt-python

A Python client library for the **Intelligent Video Solutions (IVS) VALT** REST API (v3). Covers room control, recordings, comments, audio, presets, scheduling, filters, templates, users, groups, cameras, and full administrative management.

## Installation

```bash
git clone https://github.com/IntelligentVideoSolutions/ivs-valt-python.git
cd ivs-valt-python
pip install -e .
```

## Quick Start

```python
from valt.valt import VALT

v = VALT('https://your-valt-server.com', 'username', 'password', timeout=30)

# Start a recording
rec_id = v.startrecording(room_id=3, name='My Recording')

# Stop it
v.stoprecording(room_id=3)

# List recordings
records = v.getrecords(search='My Recording')
```

## Constructor

```python
VALT(valt_address, username, password, timeout=5, logpath='ivs.log', room=None, room_check_interval=5)
```

| Parameter | Description |
|---|---|
| `valt_address` | Server URL, e.g. `https://valt.example.com` |
| `username` | VALT username |
| `password` | VALT password |
| `timeout` | HTTP timeout in seconds (default 5) |
| `logpath` | Path for log file (default `ivs.log`) |
| `room` | Room ID to monitor (optional) |
| `room_check_interval` | Seconds between room status polls (default 5) |

---

## Method Reference

### Authentication

| Method | Description |
|---|---|
| `auth()` | Authenticate (called automatically on init) |
| `testconnection(address, username, password)` | Test credentials, returns `True`/`False` |
| `changeserver(address, username, password)` | Switch to a different VALT server |
| `disconnect()` | Stop background threads and cancel reauth timer |
| `change_timeout(seconds)` | Update HTTP timeout |

---

### Room Control

| Method | Description |
|---|---|
| `getrooms()` | List all rooms |
| `getroomname(room_id)` | Get room name |
| `getroomstatus(room_id)` | Returns 1=available, 2=recording, 3=paused, 4=locked, 5=prepared |
| `isrecording(room_id)` | Returns `True` if room is recording |
| `ispaused(room_id)` | Returns `True` if recording is paused |
| `islocked(room_id)` | Returns `True` if room is locked |
| `getrecordingid(room_id)` | Returns active recording ID |
| `getrecordingtime(room_id)` | Returns elapsed recording time in seconds |
| `startrecording(room_id, name, author=None)` | Start a recording, returns recording ID |
| `stoprecording(room_id)` | Stop the active recording |
| `pauserecording(room_id)` | Pause the active recording |
| `resumerecording(room_id)` | Resume a paused recording |
| `addcomment(room_id, name, color='red')` | Add a live marker to the active recording |
| `lockroom(room_id)` | Lock a room |
| `unlockroom(room_id)` | Unlock a room |
| `get_cameras(room_id)` | List cameras in a room |
| `getcameras(room_id)` | Alias for `get_cameras` |

---

### Records

| Method | Description |
|---|---|
| `getrecords(search=None, start_date=None)` | Search recordings |
| `get_video_information(recording_id)` | Get full recording metadata |
| `setsharing(record_id, users=[], groups=[])` | Set sharing permissions |
| `share_record(record_id)` | Generate a public share URL |
| `deactivate_share(record_id)` | Remove the public share URL |
| `cut_record(record_id, start_time, end_time)` | Clip a recording (seconds), returns `{clip_id, message}` |
| `get_cut_status(clip_id)` | Returns `True` when cut is complete |
| `delete_record(record_id)` | Delete a recording |
| `upload_video(file_path, name)` | Upload a video file, returns new record ID |
| `download_video(recording_id, video_id, file_path)` | Download a video to disk |

---

### Comments

| Method | Description |
|---|---|
| `get_comments_by_record(record_id)` | List all comments on a recording |
| `create_comment(comment_data)` | Create a comment (dict with `recordId`, `recordTime`, `type`, `message`) |
| `update_comment(comment_id, update_data)` | Update a comment (include `recordId`, `recordTime`, `type`) |
| `delete_comment(comment_id)` | Delete a comment |
| `download_comment_file(comment_id, file_id, output_path)` | Download a file attached to a comment |

---

### Audio

| Method | Description |
|---|---|
| `get_audio(audio_id)` | Get audio metadata and stream URL |
| `upload_audio(file_path, duration, frequencies)` | Upload an audio file (`frequencies` is a list of 30+ floats in `[0, 1]`) |
| `update_audio(audio_id, file_path, duration, frequencies)` | Replace an existing audio file |
| `delete_audio(audio_id)` | Delete an audio file |

---

### Presets

| Method | Description |
|---|---|
| `get_camera_presets(camera_id)` | List presets for a camera |
| `create_camera_preset(camera_id, name)` | Create a new preset |
| `apply_camera_preset(camera_id, preset_id)` | Apply a preset to a camera |
| `delete_camera_preset(camera_id, preset_id)` | Delete a preset |

---

### Filters

| Method | Description |
|---|---|
| `get_filters()` | List all saved filters |
| `get_filter(filter_id)` | Get a filter |
| `get_filter_template_fields()` | List template fields available for filtering |
| `create_filter(name, fields=None, rooms=None, authors=None, date=None)` | Create a filter |
| `update_filter(filter_id, **kwargs)` | Update a filter |
| `delete_filter(filter_id)` | Delete a filter |

---

### Scheduling

| Method | Description |
|---|---|
| `getschedule(room_id)` | List schedules for a room |
| `get_schedule(schedule_id)` | Get a specific schedule |
| `get_blocked_schedules()` | List blocked schedules |
| `get_conflict_schedules()` | List conflicting schedules |
| `create_schedule(name, room, start_at, duration, template=None, recurrence=None, share=None)` | Create a schedule |
| `update_schedule(schedule_id, **kwargs)` | Update a schedule |
| `delete_next_schedule(schedule_id)` | Delete the next occurrence of a recurring schedule |
| `stop_schedule(schedule_id)` | Stop a running schedule |
| `delete_schedule(schedule_id)` | Delete a schedule |

---

### Templates

| Method | Description |
|---|---|
| `get_templates(template_type)` | Get templates by type: `'comment'`, `'info'`, or `'marker'` |

---

### Rights

| Method | Description |
|---|---|
| `get_rights()` | List all rights |
| `get_rights_by_type(right_type)` | Get rights for a specific type (e.g. `'general'`) |

---

### Help

| Method | Description |
|---|---|
| `get_helps()` | List all help items |
| `get_help(help_id)` | Get a help item |
| `create_help(title, content)` | Create a help item |
| `update_help(help_id, title, content)` | Update a help item |
| `delete_help(help_id)` | Delete a help item |

---

### Users

| Method | Description |
|---|---|
| `getusers()` | List all users |
| `get_user(user_id)` | Get a user |
| `getusername(user_id)` | Get a user's name |
| `get_user_by_card_number(card_number)` | Find a user by I/O card number |
| `create_user(name, password, display_name=None, user_group=None, card_number=None, rooms=None, video_access=None)` | Create a user |
| `update_user(user_id, **kwargs)` | Update a user |
| `delete_user(user_id)` | Delete a user |

---

### User Groups

| Method | Description |
|---|---|
| `get_user_groups()` | List all user groups |
| `get_user_group_info(group_id)` | Get a user group |
| `get_user_group_rooms(group_id)` | List rooms accessible to a group |
| `create_user_group(name, template=None, rights=None, rooms=None, **kwargs)` | Create a user group (`template` requires `comment` and `information` IDs) |
| `update_group(group_id, **kwargs)` | Update a user group |
| `delete_user_group(group_id)` | Delete a user group |

---

### Cameras (Admin)

| Method | Description |
|---|---|
| `get_all_cameras()` | List all cameras |
| `get_camera(camera_id)` | Get a camera |
| `create_camera(name, ip, username, password, **kwargs)` | Create a camera |
| `update_camera(camera_id, **kwargs)` | Update a camera |
| `delete_camera(camera_id)` | Delete a camera |
| `get_camera_brands()` | List camera brands and models |

---

### Rooms (Admin)

| Method | Description |
|---|---|
| `get_admin_rooms()` | List all rooms with full device details |
| `get_admin_room(room_id)` | Get a room with full device details |
| `create_room(name, wowza=1, **kwargs)` | Create a room |
| `update_room(room_id, wowza=1, **kwargs)` | Update a room (always pass `wowza`) |
| `delete_room(room_id)` | Delete a room |

---

### Media Servers (Admin)

| Method | Description |
|---|---|
| `get_media_servers()` | List all media servers |
| `get_media_server(server_id)` | Get a media server |
| `create_media_server(name, address, storage_folder, port=None, ssl=None)` | Create a media server |
| `update_media_server(server_id, **kwargs)` | Update a media server |
| `delete_media_server(server_id)` | Delete a media server |

---

### Templates (Admin)

| Method | Description |
|---|---|
| `get_admin_templates()` | List all admin templates |
| `get_admin_template(template_id)` | Get a template |
| `create_admin_template(name, type, entity_name, hidden=False, fields=None)` | Create a template (`type` is `'info'` or `'comment'`) |
| `update_admin_template(template_id, type, **kwargs)` | Update a template (always pass `type`) |
| `delete_admin_template(template_id)` | Delete a template |
| `get_template_fields(template_id)` | List fields in a template |
| `add_template_fields(template_id, fields)` | Add fields to a template |
| `update_template_field(template_id, field_id, **kwargs)` | Update a template field |
| `delete_template_field(template_id, field_id)` | Delete a template field |

---

### General (Admin)

| Method | Description |
|---|---|
| `getversion()` | Get VALT software version string |
| `get_log_categories()` | List log category names |

---

### Room Status Monitoring

The library runs a background thread that polls room status. Bind a callback to react to changes:

```python
v.selected_room = 3
v.bind_to_selected_room_status(lambda status: print(f'Room status: {status}'))
v.bind_to_accesstoken(lambda token: print(f'Token changed'))
v.bind_to_errormsg(lambda msg: print(f'Error: {msg}'))
```

Status values: `1` = available, `2` = recording, `3` = paused, `4` = locked, `5` = prepared

---

## Logging

Logs are written to `ivs.log` by default. Adjust level at runtime:

```python
v.log_level('debug')   # debug | info | warn | error | critical
```
