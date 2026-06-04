"""
Live integration tests for all new mixins and endpoints.
Run: python test_live_new.py
"""
import sys, time, os, wave
sys.path.insert(0, '.')
from valt.valt import VALT

HOST = 'https://ivstest1.ad.ipivs.com'
v = VALT(HOST, 'admin', 'admin', timeout=60)
time.sleep(2)

PASS_MARK = '[PASS]'
FAIL_MARK = '[FAIL]'
SKIP_MARK = '[SKIP]'

def check(label, value, expected=None, not_value=None):
    if not_value is not None:
        ok = value != not_value
    elif expected is not None:
        ok = value == expected
    else:
        ok = bool(value) and value != 0
    print(f'  {PASS_MARK if ok else FAIL_MARK} {label}: {value!r}')
    return ok

def section(title):
    print(f'\n[{title}]')

def ensure_auth():
    if v.accesstoken == 0:
        print('  [RECOVERY] re-authenticating...')
        v.auth()
        time.sleep(3)

# ── Rights ────────────────────────────────────────────────────
section('RIGHTS')
rights = v.get_rights()
check('get_rights returns list', isinstance(rights, list), expected=True)
if isinstance(rights, list) and rights:
    print(f'  {len(rights)} right type(s); first: {rights[0].get("name")!r}')
    right_name = rights[0].get('name')
    time.sleep(1)
    rights_by_type = v.get_rights_by_type(right_name)
    check(f'get_rights_by_type({right_name!r})', isinstance(rights_by_type, dict), expected=True)

ensure_auth()

# ── Records (cut / share / delete) ────────────────────────────
section('RECORDS')
# Start and stop a fresh recording to get a usable record
rec_room = 3
time.sleep(2)
rec_id = v.startrecording(rec_room, 'API Records Test')
check('startrecording for records test', rec_id, not_value=0)
if rec_id and rec_id != 0:
    time.sleep(8)
    v.stoprecording(rec_room)
    time.sleep(3)

    share_url = v.share_record(rec_id)
    check('share_record returns url', share_url, not_value=0)

    time.sleep(1)
    deactivated = v.deactivate_share(rec_id)
    check('deactivate_share', deactivated, expected=1)

    time.sleep(1)
    cut = v.cut_record(rec_id, 0, 4)
    check('cut_record returns dict', isinstance(cut, dict), expected=True)
    clip_id = cut.get('clip_id') if isinstance(cut, dict) else None
    print(f'  Clip id: {clip_id!r}')

    if clip_id:
        for _ in range(10):
            time.sleep(3)
            status = v.get_cut_status(clip_id)
            print(f'  get_cut_status: {status!r}')
            if status is True:
                break
        check('cut completed', status, expected=True)

        time.sleep(2)
        deleted = v.delete_record(clip_id)
        check('delete_record (clip)', deleted, expected=1)

    time.sleep(1)
    deleted_orig = v.delete_record(rec_id)
    check('delete_record (original)', deleted_orig, expected=1)
else:
    print(f'  {SKIP_MARK} Could not create recording — skipping records tests')

ensure_auth()

# ── Filters ───────────────────────────────────────────────────
section('FILTERS')
time.sleep(2)
fields = v.get_filter_template_fields()
check('get_filter_template_fields', fields, not_value=0)

time.sleep(1)
new_filter_id = v.create_filter('API Test Filter')
check('create_filter', new_filter_id, not_value=0)

if new_filter_id and new_filter_id != 0:
    time.sleep(1)
    filters = v.get_filters()
    check('get_filters returns list', isinstance(filters, list), expected=True)

    time.sleep(1)
    filt = v.get_filter(new_filter_id)
    check('get_filter', isinstance(filt, dict), expected=True)

    time.sleep(1)
    updated = v.update_filter(new_filter_id, name='API Test Filter Updated')
    check('update_filter', updated, not_value=0)

    time.sleep(1)
    deleted = v.delete_filter(new_filter_id)
    check('delete_filter', deleted, expected=1)

ensure_auth()

# ── Schedule ──────────────────────────────────────────────────
section('SCHEDULE')
time.sleep(2)
blocked = v.get_blocked_schedules()
check('get_blocked_schedules', blocked, not_value=0)

time.sleep(1)
conflicts = v.get_conflict_schedules()
check('get_conflict_schedules', conflicts, not_value=0)

future_start = int(time.time()) + 7200
time.sleep(1)
new_sched_id = v.create_schedule('API Test Schedule', 3, future_start, 3600)
check('create_schedule', new_sched_id, not_value=0)

if new_sched_id and new_sched_id != 0:
    time.sleep(1)
    sched = v.get_schedule(new_sched_id)
    check('get_schedule', isinstance(sched, dict), expected=True)

    time.sleep(1)
    updated = v.update_schedule(new_sched_id, name='API Test Schedule Updated')
    check('update_schedule', updated, expected=1)

    time.sleep(1)
    deleted = v.delete_schedule(new_sched_id)
    check('delete_schedule', deleted, expected=1)

ensure_auth()

# ── Help ──────────────────────────────────────────────────────
section('HELP')
time.sleep(2)
helps = v.get_helps()
check('get_helps', helps, not_value=0)

time.sleep(1)
new_help = v.create_help('API Test Help', 'This is a test help item.')
check('create_help returns dict', isinstance(new_help, dict), expected=True)
new_help_id = new_help.get('id') if isinstance(new_help, dict) else None
print(f'  Help id: {new_help_id!r}')

if new_help_id:
    time.sleep(1)
    got = v.get_help(new_help_id)
    check('get_help', isinstance(got, dict), expected=True)

    time.sleep(1)
    updated_id = v.update_help(new_help_id, 'API Test Help Updated', 'Updated content.')
    check('update_help', updated_id, not_value=0)

    time.sleep(1)
    deleted = v.delete_help(new_help_id)
    check('delete_help', deleted, expected=1)

ensure_auth()

# ── Admin Templates ───────────────────────────────────────────
section('ADMIN TEMPLATES')
time.sleep(2)
templates = v.get_admin_templates()
check('get_admin_templates returns list', isinstance(templates, list), expected=True)

existing_tmpl_id = None
if isinstance(templates, list) and templates:
    existing_tmpl_id = templates[0].get('id')
    tmpl = v.get_admin_template(existing_tmpl_id)
    check(f'get_admin_template({existing_tmpl_id})', isinstance(tmpl, dict), expected=True)

    time.sleep(1)
    fields_list = v.get_template_fields(existing_tmpl_id)
    check('get_template_fields', fields_list, not_value=0)

time.sleep(1)
entity_name = {'title': 'Test Entity', 'type': 'text', 'value': 'Test Value'}
new_tmpl_id = v.create_admin_template('API Test Template', 'info', entity_name)
check('create_admin_template', new_tmpl_id, not_value=0)

if new_tmpl_id and new_tmpl_id != 0:
    time.sleep(1)
    updated_id = v.update_admin_template(new_tmpl_id, name='API Test Template Updated', type='info')
    check('update_admin_template', updated_id, not_value=0)

    time.sleep(1)
    new_fields = v.add_template_fields(new_tmpl_id, [
        {'on': True, 'required': False, 'type': 'text', 'name': 'Test Field', 'data': ''}
    ])
    check('add_template_fields', new_fields, not_value=0)
    new_field_id = new_fields[0] if isinstance(new_fields, list) and new_fields else None

    if new_field_id:
        time.sleep(1)
        updated_field = v.update_template_field(new_tmpl_id, new_field_id, name='Updated Field')
        check('update_template_field', isinstance(updated_field, dict), expected=True)

        time.sleep(1)
        deleted_field = v.delete_template_field(new_tmpl_id, new_field_id)
        check('delete_template_field', deleted_field, expected=1)

    time.sleep(1)
    deleted_tmpl = v.delete_admin_template(new_tmpl_id)
    check('delete_admin_template', deleted_tmpl, expected=1)

ensure_auth()

# ── User Groups ───────────────────────────────────────────────
section('USER GROUPS')
time.sleep(2)
groups = v.get_user_groups()
check('get_user_groups', groups, not_value=0)

time.sleep(1)
# template requires comment (marker) and information IDs
all_tmpls = v.get_admin_templates()
info_tmpl_id = next((t['id'] for t in (all_tmpls or []) if t.get('type') == 'info'), 1)
comment_tmpl_id = next((t['id'] for t in (all_tmpls or []) if t.get('type') == 'marker'), None)
group_template = {'information': info_tmpl_id}
if comment_tmpl_id:
    group_template['comment'] = comment_tmpl_id
new_group_id = v.create_user_group('API Test Group', template=group_template)
check('create_user_group', new_group_id, not_value=0)

if new_group_id and new_group_id != 0:
    time.sleep(1)
    deleted = v.delete_user_group(new_group_id)
    check('delete_user_group', deleted, expected=1)

ensure_auth()

# ── Users ─────────────────────────────────────────────────────
section('USERS')
time.sleep(2)
user = v.get_user(1)
check('get_user(1) returns dict', isinstance(user, dict), expected=True)
print(f'  User 1: {user.get("name")!r}')

time.sleep(1)
new_user_id = v.create_user('api_test_user', 'ApiTest1234!')
check('create_user', new_user_id, not_value=0)

if new_user_id and new_user_id != 0:
    time.sleep(1)
    deleted = v.delete_user(new_user_id)
    check('delete_user', deleted, expected=1)

ensure_auth()

# ── Admin Rooms ───────────────────────────────────────────────
section('ADMIN ROOMS')
time.sleep(2)
admin_rooms = v.get_admin_rooms()
check('get_admin_rooms returns list', isinstance(admin_rooms, list), expected=True)

if isinstance(admin_rooms, list) and admin_rooms:
    room_id = admin_rooms[0].get('id')
    room_name = admin_rooms[0].get('name')
    print(f'  First room: id={room_id} name={room_name!r}')

    time.sleep(1)
    admin_room = v.get_admin_room(room_id)
    check('get_admin_room', isinstance(admin_room, dict), expected=True)

    time.sleep(1)
    updated = v.update_room(room_id, name=room_name, wowza=1)
    check('update_room (no-op)', updated, not_value=0)

ensure_auth()

# ── Admin Cameras ─────────────────────────────────────────────
section('ADMIN CAMERAS')
time.sleep(2)
brands = v.get_camera_brands()
check('get_camera_brands', brands, not_value=0)

cameras = v.get_all_cameras()
if isinstance(cameras, list) and cameras:
    cam_id = cameras[0].get('id')
    cam = v.get_camera(cam_id)
    check(f'get_camera({cam_id})', isinstance(cam, dict), expected=True)
    print(f'  Camera: {cam.get("name")!r} ip={cam.get("ip")!r}')

    time.sleep(1)
    updated = v.update_camera(cam_id, name=cam.get('name'))
    check('update_camera (no-op)', updated, not_value=0)

ensure_auth()

# ── Media Servers ─────────────────────────────────────────────
section('MEDIA SERVERS')
time.sleep(2)
servers = v.get_media_servers()
if isinstance(servers, list) and servers:
    srv_id = servers[0].get('id')
    srv = v.get_media_server(srv_id)
    check(f'get_media_server({srv_id})', isinstance(srv, dict), expected=True)

time.sleep(1)
new_srv_id = v.create_media_server('API Test Server', '10.0.0.99', 'test_folder')
check('create_media_server', new_srv_id, not_value=0)

if new_srv_id and new_srv_id != 0:
    time.sleep(1)
    updated = v.update_media_server(new_srv_id, name='API Test Server Updated')
    check('update_media_server', updated, not_value=0)

    time.sleep(1)
    deleted = v.delete_media_server(new_srv_id)
    check('delete_media_server', deleted, expected=1)

ensure_auth()

# ── Logs ──────────────────────────────────────────────────────
section('LOGS')
time.sleep(1)
log_cats = v.get_log_categories()
check('get_log_categories', log_cats, not_value=0)
if isinstance(log_cats, list):
    print(f'  Categories: {log_cats}')

# ── Audio ─────────────────────────────────────────────────────
section('AUDIO')
wav_path = 'test_audio_live.wav'
with wave.open(wav_path, 'w') as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(8000)
    wf.writeframes(b'\x00\x00' * 8000)
freqs = [round(i * 0.033, 3) for i in range(30)]

time.sleep(1)
audio = v.upload_audio(wav_path, 1, freqs)
check('upload_audio', isinstance(audio, dict), expected=True)
audio_id = audio.get('id') if isinstance(audio, dict) else None

if audio_id:
    time.sleep(1)
    got = v.get_audio(audio_id)
    check('get_audio', isinstance(got, dict), expected=True)

    time.sleep(1)
    updated = v.update_audio(audio_id, wav_path, 1, freqs)
    check('update_audio', isinstance(updated, dict), expected=True)

    time.sleep(1)
    deleted = v.delete_audio(audio_id)
    check('delete_audio', deleted, not_value=0)

os.remove(wav_path)

# ── Templates ─────────────────────────────────────────────────
section('TEMPLATES')
for t in ['comment', 'info', 'marker']:
    result = v.get_templates(t)
    if isinstance(result, dict):
        check(f'get_templates({t!r})', True, expected=True)
        print(f'  {len(result.get("templates", []))} template(s), default={result.get("default")!r}')
    else:
        check(f'get_templates({t!r})', result, not_value=0)

print('\n' + '=' * 60)
print('Done.')
print('=' * 60)
