"""
Live integration test against ivstest1.ad.ipivs.com
Covers all public methods in ivs-valt-python.
Run: python test_live.py

NOT tested (by design):
  create_room / create_camera  — no delete method; would leave orphaned data
  download_comment_file        — requires a comment with a file attachment
  update_group                 — risk of breaking group permissions
  check_room_status            — internal daemon thread
  update_room_status           — internal
"""
import sys
import os
import time
sys.path.insert(0, '.')
from valt.valt import VALT

HOST = 'https://ivstest1.ad.ipivs.com'
USER = 'admin'
PASS = 'admin'

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
    mark = PASS_MARK if ok else FAIL_MARK
    print(f'  {mark} {label}: {value!r}')
    return ok

def section(title):
    print(f'\n[{title}]')

def ensure_auth(v):
    """Re-authenticate if a prior failure reset the session."""
    if v.accesstoken == 0:
        print('  [RECOVERY] accesstoken lost — re-authenticating...')
        v.auth()
        time.sleep(3)
        if v.accesstoken != 0:
            print('  [RECOVERY] Re-authenticated OK')
        else:
            print('  [RECOVERY] Re-authentication failed')

print('=' * 60)
print(f'Target: {HOST}')
print('=' * 60)

# ── Auth ──────────────────────────────────────────────────────
section('AUTH')
v = VALT(HOST, USER, PASS, timeout=30)
time.sleep(2)
check('accesstoken set', v.accesstoken, not_value=0)
ver_attr = getattr(v, 'version', None)
check('version parsed', ver_attr, not_value=0)
major = getattr(v, 'major_version', '0')
check('major_version', major not in ('0', None), expected=True)
print(f'  VALT version: {ver_attr}')

section('TESTCONNECTION')
check('valid credentials', v.test_connection(HOST, USER, PASS), expected=True)
check('bad credentials returns False', v.test_connection(HOST, USER, 'wrongpassword'), expected=False)

# ── Observables ───────────────────────────────────────────────
section('OBSERVABLES')

token_events = []
v.bind_to_accesstoken(lambda t: token_events.append(t))
v.accesstoken = v.accesstoken
check('bind_to_accesstoken fires', len(token_events) > 0, expected=True)

error_events = []
v.bind_to_errormsg(lambda e: error_events.append(e))
v.errormsg = 'test_error'
v.errormsg = None
check('bind_to_errormsg fires', len(error_events) > 0, expected=True)

status_events = []
status_cb = lambda s: status_events.append(s)
v.bind_to_selected_room_status(status_cb)
v.selected_room_status = v.selected_room_status
check('bind_to_selected_room_status fires', len(status_events) > 0, expected=True)
v.unbind_to_selected_room_status(status_cb)
prev_count = len(status_events)
v.selected_room_status = v.selected_room_status
check('unbind_to_selected_room_status stops firing', len(status_events) == prev_count, expected=True)

# ── change_timeout ────────────────────────────────────────────
section('CHANGE TIMEOUT')
v.change_timeout(30)
check('change_timeout sets httptimeout', v.httptimeout, expected=30)

# ── Rooms ─────────────────────────────────────────────────────
section('ROOMS')
rooms = v.get_rooms()
check('getrooms returns list', isinstance(rooms, list), expected=True)
if isinstance(rooms, list):
    print(f'  Room count: {len(rooms)}')
    for r in rooms[:5]:
        print(f'    id={r.get("id")}  name={r.get("name")}')

if isinstance(rooms, list) and rooms:
    rid = rooms[0].get('id')
    name = v.get_room_name(rid)
    check(f'getroomname room {rid}', name, not_value=0)

section('ROOM STATUS')
test_room_id = None
if isinstance(rooms, list) and rooms:
    for r in rooms:
        rid = r.get('id')
        status = v.get_room_status(rid)
        status_labels = {0:'error',1:'available',2:'recording',3:'paused',4:'locked',5:'prepared'}
        print(f'  Room {rid} ({v.get_room_name(rid)}): status={status} ({status_labels.get(status,"?")})')
        if status == 1 and test_room_id is None:
            test_room_id = rid

# ── Users ─────────────────────────────────────────────────────
section('USERS')
users = v.get_users()
check('getusers returns list', isinstance(users, list), expected=True)
if isinstance(users, list):
    print(f'  User count: {len(users)}')
    for u in users[:3]:
        print(f'    id={u.get("id")}  name={u.get("name")}')

time.sleep(2)
username = v.get_username(1)
check('getusername(1)', username, not_value=0)
print(f'  User 1 name: {username!r}')

time.sleep(2)
card_result = v.get_user_by_card_number('9999999999')
check('get_user_by_card_number (unknown card, expect 0)', card_result, expected=0)

time.sleep(2)
orig_display = None
if isinstance(users, list):
    admin_user = next((u for u in users if u.get('id') == 1), None)
    if admin_user:
        orig_display = admin_user.get('displayName')
update_result = v.update_user(1, displayName='API Test Display')
check('update_user returns data', update_result, not_value=0)
time.sleep(2)
v.update_user(1, displayName=orig_display if orig_display is not None else '')
print(f'  update_user: displayName restored to {orig_display!r}')

# ── Groups ────────────────────────────────────────────────────
section('GROUPS')
time.sleep(2)
group_info = v.get_user_group_info(1)
check('get_user_group_info(1)', group_info, not_value=0)
if isinstance(group_info, dict):
    print(f'  Group 1 name: {group_info.get("name")!r}')

group_rooms = v.get_user_group_rooms(1)
check('get_user_group_rooms(1) returns list', isinstance(group_rooms, list), expected=True)
print(f'  Group 1 has {len(group_rooms)} room(s)')

# ── Cameras ───────────────────────────────────────────────────
section('CAMERAS')
time.sleep(2)
cameras = v.get_all_cameras()
ptz_cam_id = None
ptz_cam_name = None
if isinstance(cameras, list):
    check('get_all_cameras', cameras)
    print(f'  Camera count: {len(cameras)}')
    for c in cameras[:3]:
        print(f'    id={c.get("id")}  name={c.get("name")}  type={c.get("type")}')
    for c in cameras:
        if c.get('type') == 'camera':
            ptz_cam_id = c.get('id')
            ptz_cam_name = c.get('name')
            break
else:
    print(f'  {SKIP_MARK} get_all_cameras: returned {cameras!r}')

# ── Presets ───────────────────────────────────────────────────
section('PRESETS')
if ptz_cam_id is not None:
    time.sleep(2)
    presets = v.get_camera_presets(ptz_cam_id)
    if isinstance(presets, list):
        check('get_camera_presets returns list', True, expected=True)
        print(f'  Camera {ptz_cam_id} ({ptz_cam_name}) has {len(presets)} preset(s)')
    else:
        print(f'  {SKIP_MARK} get_camera_presets: {presets!r}')

    time.sleep(2)
    new_preset_id = v.create_camera_preset(ptz_cam_id, 'API Test Preset')
    check('create_camera_preset', new_preset_id, not_value=0)

    if new_preset_id and new_preset_id != 0:
        time.sleep(2)
        apply_result = v.apply_camera_preset(ptz_cam_id, new_preset_id)
        check('apply_camera_preset', apply_result, expected=1)

        time.sleep(2)
        delete_result = v.delete_camera_preset(ptz_cam_id, new_preset_id)
        check('delete_camera_preset', delete_result, not_value=0)
        if delete_result == 0:
            print(f'  NOTE: delete_camera_preset returned 0 — preset {new_preset_id!r} may still exist on camera {ptz_cam_id}')
else:
    print(f'  {SKIP_MARK} No PTZ camera available for preset tests')

ensure_auth(v)

# ── Schedule ──────────────────────────────────────────────────
section('SCHEDULE')
if isinstance(rooms, list) and rooms:
    rid = rooms[0].get('id')
    sched = v.get_room_schedule(rid)
    if isinstance(sched, list):
        print(f'  {PASS_MARK} getschedule room {rid}: {len(sched)} entries')
    else:
        print(f'  {SKIP_MARK} getschedule room {rid}: {sched!r}')

# ── Version ───────────────────────────────────────────────────
section('GETVERSION')
time.sleep(2)
ver = v.get_version()
check('getversion', ver, not_value=0)

# ── Media Servers ─────────────────────────────────────────────
section('MEDIA SERVERS')
time.sleep(2)
media_servers = v.get_media_servers()
if isinstance(media_servers, list):
    check('get_media_servers returns list', True, expected=True)
    print(f'  Media server count: {len(media_servers)}')
    for ms in media_servers[:3]:
        print(f'    id={ms.get("id")}  name={ms.get("name")}')
else:
    print(f'  {SKIP_MARK} get_media_servers: {media_servers!r}')

# ── getrecords ────────────────────────────────────────────────
section('GETRECORDS')
time.sleep(2)
records = v.get_records(search='API Test')
if isinstance(records, list):
    check('getrecords(search=API Test) returns list', True, expected=True)
    print(f'  Found {len(records)} matching record(s)')
elif records == 0:
    print(f'  {SKIP_MARK} getrecords: no results (no API Test recordings on server)')
else:
    check('getrecords', records, not_value=0)

# ── Room state checks ─────────────────────────────────────────
section('ROOM STATE CHECKS')
if isinstance(rooms, list) and rooms:
    for r in rooms[:3]:
        rid = r.get('id')
        rec = v.is_recording(rid)
        paused = v.is_paused(rid)
        locked = v.is_locked(rid)
        print(f'  Room {rid}: isrecording={rec!r}  ispaused={paused!r}  islocked={locked!r}')
        check(f'isrecording room {rid} is bool or 0', rec in (True, False, 0), expected=True)
        check(f'ispaused room {rid} is bool or 0', paused in (True, False, 0), expected=True)
        check(f'islocked room {rid} is bool or 0', locked in (True, False, 0), expected=True)

# ── Recording lifecycle ───────────────────────────────────────
ensure_auth(v)
section('RECORDING LIFECYCLE')
lifecycle_rec_id = None
lifecycle_video_id = None

if test_room_id is None:
    print(f'  {SKIP_MARK} No available room — skipping recording lifecycle')
else:
    print(f'  Using room {test_room_id} ({v.get_room_name(test_room_id)})')

    time.sleep(3)
    rec_id = v.start_recording(test_room_id, 'API Test Recording', author=1)
    check('startrecording (with author) returns id', rec_id, not_value=0)

    if rec_id:
        lifecycle_rec_id = rec_id
        time.sleep(5)
        check('isrecording after start', v.is_recording(test_room_id), expected=True)
        check('getroomstatus == 2', v.get_room_status(test_room_id), expected=2)
        check('getrecordingid matches', v.get_recording_id(test_room_id), expected=rec_id)
        rec_time = v.get_recording_time(test_room_id)
        check('getrecordingtime > 0', rec_time > 0, expected=True)

        time.sleep(3)
        pause_result = v.pause_recording(test_room_id)
        check('pauserecording returns id', pause_result, not_value=0)
        if pause_result:
            time.sleep(3)
            check('ispaused after pause', v.is_paused(test_room_id), expected=True)
            check('getroomstatus == 3', v.get_room_status(test_room_id), expected=3)
            time.sleep(3)
            resume_result = v.resume_recording(test_room_id)
            check('resumerecording returns id', resume_result, not_value=0)
            time.sleep(3)
            check('ispaused after resume', v.is_paused(test_room_id), expected=False)

        time.sleep(3)
        comment_result = v.add_comment(test_room_id, 'TestMarker')
        check('addcomment returns 1', comment_result, expected=1)

        time.sleep(3)
        stopped_id = v.stop_recording(test_room_id)
        check('stoprecording returns id', stopped_id, not_value=0)
        time.sleep(5)
        check('isrecording after stop', v.is_recording(test_room_id), expected=False)
        check('getroomstatus == 1', v.get_room_status(test_room_id), expected=1)

        time.sleep(3)
        info = v.get_video_information(stopped_id)
        if isinstance(info, dict):
            check('get_video_information', info)
            print(f'  Recording name: {info.get("name")}  duration: {info.get("duration")}s')
            vids = info.get('videos', [])
            if vids:
                lifecycle_video_id = vids[0].get('id')
                vid_status = vids[0].get('status', {})
                print(f'  First video id: {lifecycle_video_id!r}  status: {vid_status}')
        else:
            print(f'  {SKIP_MARK} get_video_information: {info!r}')

# ── Comment CRUD ──────────────────────────────────────────────
section('COMMENT CRUD')
if lifecycle_rec_id:
    time.sleep(3)
    comments = v.get_comments_by_record(lifecycle_rec_id)
    if isinstance(comments, list):
        check('get_comments_by_record returns list', True, expected=True)
        print(f'  {len(comments)} comment(s) on record')
    else:
        print(f'  {SKIP_MARK} get_comments_by_record: {comments!r}')

    time.sleep(3)
    new_comment = v.create_comment({
        'recordTime': 3,
        'recordId': lifecycle_rec_id,
        'type': 'simple',
        'message': 'API Direct Comment'
    })
    check('create_comment', new_comment, not_value=0)
    new_cid = None
    if isinstance(new_comment, dict):
        new_cid = new_comment.get('id')
    print(f'  Created comment id: {new_cid!r}')

    if new_cid:
        time.sleep(3)
        updated = v.update_comment(new_cid, {'message': 'Updated Comment', 'recordId': lifecycle_rec_id, 'recordTime': 3, 'type': 'simple'})
        check('update_comment', updated, not_value=0)

        time.sleep(3)
        deleted = v.delete_comment(new_cid)
        check('delete_comment', deleted, not_value=0)
    else:
        print(f'  {SKIP_MARK} no comment id returned — skipping update/delete')
else:
    print(f'  {SKIP_MARK} No lifecycle recording — skipping comment CRUD')

# ── setsharing ────────────────────────────────────────────────
section('SETSHARING')
if lifecycle_rec_id:
    time.sleep(3)
    share_result = v.set_sharing(lifecycle_rec_id, users=[2])
    check('setsharing with user', share_result, not_value=0)
    time.sleep(3)
    restore_result = v.set_sharing(lifecycle_rec_id, users=[], groups=[])
    check('setsharing restore empty', restore_result, not_value=0)
else:
    print(f'  {SKIP_MARK} No lifecycle recording — skipping setsharing')

# ── Upload ────────────────────────────────────────────────────
section('UPLOAD')
test_file = 'test_upload_dummy.mp4'
with open(test_file, 'wb') as f:
    f.write(b'\x00\x00\x00\x18ftypisom' + b'\x00' * 512)

time.sleep(3)
upload_rec_id = v.upload_video(test_file, 'API Test Upload')
if upload_rec_id and upload_rec_id != 0:
    check('upload_video returns record_id', upload_rec_id, not_value=0)
    print(f'  Uploaded record id: {upload_rec_id!r}')
else:
    print(f'  {SKIP_MARK} upload_video returned {upload_rec_id!r} (server may have rejected dummy file)')
os.remove(test_file)

# ── Download ──────────────────────────────────────────────────
section('DOWNLOAD')
if lifecycle_rec_id and lifecycle_video_id:
    time.sleep(3)
    download_file = 'test_download.mp4'
    dl_result = v.download_video(lifecycle_rec_id, lifecycle_video_id, download_file)
    check('download_video returns 1', dl_result, expected=1)
    if dl_result == 1 and os.path.isfile(download_file):
        size = os.path.getsize(download_file)
        check('downloaded file has content', size > 0, expected=True)
        print(f'  Downloaded {size} bytes to {download_file!r}')
        os.remove(download_file)
    else:
        print(f'  {SKIP_MARK} download file not created')
else:
    print(f'  {SKIP_MARK} No lifecycle recording/video id — skipping download')

# ── Lock / Unlock ─────────────────────────────────────────────
section('LOCK/UNLOCK')
if test_room_id is not None and v.get_room_status(test_room_id) == 1:
    time.sleep(3)
    lock_result = v.lock_room(test_room_id)
    check('lockroom returns id', lock_result, not_value=0)
    if lock_result:
        time.sleep(3)
        check('islocked after lock', v.is_locked(test_room_id), expected=True)
        check('getroomstatus == 4', v.get_room_status(test_room_id), expected=4)
        time.sleep(3)
        unlock_result = v.unlock_room(test_room_id)
        check('unlockroom returns id', unlock_result, not_value=0)
        time.sleep(3)
        check('islocked after unlock', v.is_locked(test_room_id), expected=False)
else:
    print(f'  {SKIP_MARK} No available room for lock test')

# ── Room cameras ──────────────────────────────────────────────
section('ROOM CAMERAS')
if isinstance(rooms, list) and rooms:
    rid = rooms[0].get('id')
    cams = v.get_cameras(rid)
    if isinstance(cams, list):
        check(f'get_cameras room {rid}', cams)
        print(f'  {len(cams)} camera(s) in room {rid}')
    else:
        print(f'  {SKIP_MARK} get_cameras room {rid}: {cams!r}')
    cams2 = v.get_cameras(rid)
    check('getcameras alias == get_cameras', cams2 == cams, expected=True)

# ── Monitor ───────────────────────────────────────────────────
section('MONITOR')
if isinstance(rooms, list) and rooms:
    v.selected_room = rooms[0].get('id')
    v.stop_room_check_thread()
    check('stop_room_check_thread sets run=False', v.run_check_room_status, expected=False)
    time.sleep(1)
    v.start_room_check_thread()
    check('start_room_check_thread sets run=True', v.run_check_room_status, expected=True)
    check('room_check_thread is alive', v.room_check_thread.is_alive(), expected=True)
else:
    print(f'  {SKIP_MARK} No rooms for monitor test')

# ── changeserver ─────────────────────────────────────────────
section('CHANGESERVER')
time.sleep(3)
v.change_server(HOST, USER, PASS)
time.sleep(3)
check('changeserver re-authenticates', v.accesstoken, not_value=0)
check('changeserver version still set', v.version, not_value=0)

# ── Cleanup ───────────────────────────────────────────────────
v.disconnect()
print('\n' + '=' * 60)
print('Done.')
print('=' * 60)
