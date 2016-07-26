# Animation writer script

import bpy
import re
from math import pi
import random

### Assume the following objects exist and are set up correctly:
# Cameras:
#  Camera (child of and z-rotation tracking to object: spin)
# Lights:
#  Hemi
#  Point
#  Point.001
#  Spot
#  Sun (with energy initialized to 0)
#  redhemi
#  blue_spot
#  halo
# Walls:
#  floor
#  west_wall
#  east_wall
#  north_wall
#  south_wall
# Tori: (with existing materials initialized to 1 emission)
#  Torus
#  Torus1 - Torus[numtor]
# Orbs: (with existing materials initialized to 0 emission)
#  Glass
#  Glass1-Glass[numorb]
#  Orb
#  Orb1 - Orb[numorb]
# Eyeball:
#  eye.brown
# Drumsticks:
#  stick
#  stick2
# Spike

# Assume mididump text files are in the directory with correct names and MIDI numbers

### Constants and functions

tempo = 120
framerate = 25

numtor = 50
numorb = 150

def beat_to_frame(beat):
    # Note: supports float beat numbers, will output float frame numbers in this case
    # Conversion: frame_num = (beat_num - 1) / beat/min * sec/min * frame/sec + 1
    frame = ((beat - 1) / tempo) * 60 * framerate + 1
    return frame

def bar_to_frame(bar):
    # Assume 4/4 time signature
    return beat_to_frame(((bar - 1) * 4) + 1)

def note_onset_frames_from_file(filename, filter_midi_notes=[]):
    # Assume file has been output by mididump.py from vishnubob's python-midi project
    # python-midi last pull time: Thu Oct 9 13:58:37 2014
    f = open(filename)
    # We're going to search for strings of digits
    p = '\d+'
    ticks_elapsed = 0
    onsets = []
    for line in f:
        # If we are reading the first line of master metadata, midi.Pattern
        if 'Pattern' in line:
            matches = re.findall(p, line)
            # The resolution (ticks/beat) should be the second digit string
            res = int(matches[1])
        # If we are reading a note event
        if 'midi.Note' in line:
            matches = re.findall(p, line)
            # The first digit string should be the number of ticks since the last note event
            tick = int(matches[0])
            ticks_elapsed += tick
            # The third digit string should be the note number
            note = int(matches[2])
            # If we're filtering by note, check the note and continue if not a match
            if len(filter_midi_notes) != 0 and not note in filter_midi_notes:
                continue
            # Only include on events, not off events
            if 'OnEvent' in line:
                frame = int(round(beat_to_frame((ticks_elapsed / res) + 1)))
                onsets.append(frame)
    return onsets

# TODO: this is a temporary alternate function to add functionality, should be merged with the above
def note_onsets_from_file(filename, filter_midi_notes=[]):
        # Assume file has been output by mididump.py from vishnubob's python-midi project
    # python-midi last pull time: Thu Oct 9 13:58:37 2014
    f = open(filename)
    # We're going to search for strings of digits
    p = '\d+'
    ticks_elapsed = 0
    onsets = []
    for line in f:
        # If we are reading the first line of master metadata, midi.Pattern
        if 'Pattern' in line:
            matches = re.findall(p, line)
            # The resolution (ticks/beat) should be the second digit string
            res = int(matches[1])
        # If we are reading a note event
        if 'midi.Note' in line:
            matches = re.findall(p, line)
            # The first digit string should be the number of ticks since the last note event
            tick = int(matches[0])
            ticks_elapsed += tick
            # The third digit string should be the note number
            note = int(matches[2])
            # If we're filtering by note, check the note and continue if not a match
            if len(filter_midi_notes) != 0 and not note in filter_midi_notes:
                continue
            # Only include on events, not off events
            if 'OnEvent' in line:
                frame = int(round(beat_to_frame((ticks_elapsed / res) + 1)))
                onsets.append((frame, note))
    return onsets

def make_appear(objnames, frame):
    for name in objnames:
        obj = bpy.data.objects[name]
        # Don't render object or show in 3D view through previous frame
        obj.hide_render = True
        obj.keyframe_insert(data_path='hide_render', frame=frame-1)
        obj.hide = True
        obj.keyframe_insert(data_path='hide', frame=frame-1)
        # Render and show object starting at frame
        obj.hide_render = False
        obj.keyframe_insert(data_path='hide_render', frame=frame)
        obj.hide = False
        obj.keyframe_insert(data_path='hide', frame=frame)
        
def make_disappear(objnames, frame):
    for name in objnames:
        obj = bpy.data.objects[name]
        # Render and show object through previous frame
        obj.hide_render = False
        obj.keyframe_insert(data_path='hide_render', frame=frame-1)
        obj.hide = False
        obj.keyframe_insert(data_path='hide', frame=frame-1)
        # Don't render object or show in 3D view starting at frame
        obj.hide_render = True
        obj.keyframe_insert(data_path='hide_render', frame=frame)
        obj.hide = True
        obj.keyframe_insert(data_path='hide', frame=frame)

def camera_shake(camera, start_frame, num_frames, max_disp):
    cur_rot = camera.rotation_euler.copy()
    camera.keyframe_insert(data_path='rotation_euler', frame=start_frame)
    random.seed(0)
    for i in range(1, num_frames):
        x_disp = random.uniform(-max_disp, max_disp)
        y_disp = random.uniform(-max_disp, max_disp)
        z_disp = random.uniform(-max_disp, max_disp)
        camera.rotation_euler = (cur_rot.x + x_disp, cur_rot.y + y_disp, cur_rot.z + z_disp)
        camera.keyframe_insert(data_path='rotation_euler', frame=start_frame+i)
        
    camera.rotation_euler = cur_rot
    camera.keyframe_insert(data_path='rotation_euler', frame=start_frame+num_frames)

### Animation timeline, in bars

act1_start = 1
act1_embellish = 9
act1_drums = 17
act1_melody = 25
act1_out = 33
act2_start = 41
act2_bass = 49
act2_drums = 53
act2_snare = 57
act2_embellish = 61
act3_start = 65
act3_theme = 67
act3_return = 81
act3_end = 83
act4_fade = 99
act4_end = 109

### Animation keyframes

# Deselect everything
for obj in bpy.data.objects:
    obj.select = False

# Shared object references and name lists
spin = bpy.data.objects['spin']
camera = bpy.data.objects['Camera']
eye = bpy.data.objects['eye.brown']
blue_sun = bpy.data.lamps['world_sun']
hemi = bpy.data.lamps['Hemi']
under_light = bpy.data.lamps['Point.001']
orb_names = ['Orb' + str(i) for i in range(1, numorb+1)]
glass_names = ['Glass' + str(i) for i in range(1, numorb+1)]
torus_names = ['Torus' + str(i) for i in range(1, numtor+1)]
wall_names = ['floor', 'west_wall', 'east_wall', 'south_wall', 'north_wall']
light_names = ['Hemi', 'Point', 'Point.001', 'redhemi']

# Initialize rotation and position of camera at start of act 1
spin.rotation_euler = (0, 0, pi)
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act1_start))
spin.location = (0, 0, 0)
spin.keyframe_insert(data_path='location', frame=bar_to_frame(act1_start))
# Spin center should not move until act 2 snare
# TODO: define all intervals like this
spin.keyframe_insert(data_path='location', frame=bar_to_frame(act2_snare))
camera.rotation_euler = (pi/2, 0, pi)
camera.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act1_start))
camera.location = (0, 75, 0)
camera.keyframe_insert(data_path='location', frame=bar_to_frame(act1_start))

# Initialize eye rotation
eye.rotation_euler = (0, 0, 0)
eye.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act1_start))

# Initialize blue sun
blue_sun.energy = 0.9
blue_sun.keyframe_insert('energy', frame=bar_to_frame(act1_start))
# Initialize hemi
hemi.color = (1, 1, 1)

# Revolve camera once until embellishment appears, then stop
spin.rotation_euler = (0, 0, 3*pi)
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act1_embellish)-1)

# Make orbs appear at start of act 1 embellishment
make_appear(orb_names, bar_to_frame(act1_embellish))
make_appear(glass_names, bar_to_frame(act1_embellish))

# Make random orbs flash for a few frames at each embellishment note onset
act1_embellish_onsets = note_onset_frames_from_file('C:\\Users\\Shamik\\Documents\\blender\\act1orbs.txt')
random.seed(0)
for onset in act1_embellish_onsets:
    numflash = 10
    for flash in range(1, numflash):
        orb_mat = bpy.data.materials['OrbMat' + str(random.randint(1, numorb))]
        # 0 emission through previous frame
        orb_mat.emit = 0
        orb_mat.keyframe_insert(data_path='emit', frame=bar_to_frame(act1_embellish)+onset-1)
        # 1 emission at onset frame
        orb_mat.emit = 2
        orb_mat.keyframe_insert(data_path='emit', frame=bar_to_frame(act1_embellish)+onset)
        # 0 emission 10 frames later
        orb_mat.emit = 0
        orb_mat.keyframe_insert(data_path='emit', frame=bar_to_frame(act1_embellish)+onset+10)

# Cut to a new, closer angle four bars after embellishment appears and spin twice in the next four bars
camera.keyframe_insert(data_path='location', frame=bar_to_frame(act1_embellish+4)-1)
camera.location = (0, 50, 0)
camera.keyframe_insert(data_path='location', frame=bar_to_frame(act1_embellish+4))
spin.rotation_euler = (0, 0, pi/2)
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act1_embellish+4))
spin.rotation_euler = (0, 0, pi/2 + 4*pi)
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act1_drums)-1)

# Make blue sun flash with kick drum
act1_kick_onsets = note_onset_frames_from_file('C:\\Users\\Shamik\\Documents\\blender\\act1kick.txt', [36])
sun = bpy.data.lamps['Sun']
for onset in act1_kick_onsets:
    # Energy is 0 through the previous frame
    sun.energy = 0
    sun.keyframe_insert(data_path='energy', frame=bar_to_frame(act1_drums)+onset-1)
    # Energy is 0.3 at onset frame
    sun.energy = 0.3
    sun.keyframe_insert(data_path='energy', frame=bar_to_frame(act1_drums)+onset)
    # Energy is 0 10 frames later
    sun.energy = 0
    sun.keyframe_insert(data_path='energy', frame=bar_to_frame(act1_drums)+onset+10)

# Cut to a new angle and spin slowly for 4 bars, a little further
spin.rotation_euler = (0, 0, pi/2)
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act1_drums))
spin.rotation_euler = (0, 0, pi/2 + 3*pi)
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act1_drums+4)-1)
camera.keyframe_insert(data_path='location', frame=bar_to_frame(act1_drums)-1)
camera.location = (0, 60, 0)
camera.keyframe_insert(data_path='location', frame=bar_to_frame(act1_drums))

# Cut to a higher angle and spin a little faster for 4 bars
spin.rotation_euler = (pi/4, 0, pi/2 + 3*pi)
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act1_drums+4))
spin.rotation_euler = (pi/4, 0, pi/2 + 8*pi)
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act1_drums+8)-1)

# Cut to a close, low angle still shot with camera shaking to kick for 2 bars
spin.rotation_euler = (-pi/16, 0, 3*pi/2)
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act1_drums+8))
camera.keyframe_insert(data_path='location', frame=bar_to_frame(act1_drums+8)-1)
camera.location = (0, 20, 0)
camera.keyframe_insert(data_path='location', frame=bar_to_frame(act1_drums+8))
for onset in act1_kick_onsets:
    # Ignore earlier kicks and kicks after cut changes
    if bar_to_frame(act1_drums) + onset >= bar_to_frame(act1_drums+8):
        camera_shake(camera, bar_to_frame(act1_drums) + onset, 5, pi/360)

# Start spinning after 2 bars, for 6 bars
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act1_drums+10))
spin.rotation_euler = (-pi/16, 0, 3*pi/2 - 4*pi)

# Cut to new, flat angle, rotating, moving inwards at end of act 1
# start turning down blue spotlight and blue sun
# TODO: any lights that are turned down without being initialized are not actually in use
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act1_out)-1)
spin.rotation_euler = (0, 0, pi)
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act1_out))
spin.rotation_euler = (0, 0, 5*pi)
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act2_start)-5)
camera.keyframe_insert(data_path='location', frame=bar_to_frame(act1_out)-1) 
camera.location = (0, 50, 0)
camera.keyframe_insert(data_path='location', frame=bar_to_frame(act1_out))    
camera.location = (0, 5, 0)
camera.keyframe_insert(data_path='location', frame=bar_to_frame(act2_start))
blue_spot = bpy.data.lamps['blue_spot']
blue_spot.energy = 1
blue_spot.keyframe_insert(data_path='energy', frame=bar_to_frame(act1_out))
blue_spot.energy = 0
blue_spot.keyframe_insert(data_path='energy', frame=bar_to_frame(act2_start))
blue_sun.keyframe_insert(data_path = 'energy', frame=bar_to_frame(act1_out))
blue_sun.energy = 0
blue_sun.keyframe_insert(data_path = 'energy', frame=bar_to_frame(act2_start))

# Make orbs disappear before act 2
make_disappear(orb_names, bar_to_frame(act2_start) - 50)
make_disappear(glass_names, bar_to_frame(act2_start) - 50)

# Make halo disappear before act 2
make_disappear(['halo'], bar_to_frame(act2_start) - 25)

# Make wood floor disappear right before act 2
make_disappear(['world_floor'], bar_to_frame(act2_start) - 25)

# Make inner walls appear right before act 2
make_appear(wall_names, bar_to_frame(act2_start)- 25)

# Make spot light appear at start of act 2
make_appear(['Spot'], bar_to_frame(act2_start))

# Make spot light flash with bass swells
swell_onsets = note_onset_frames_from_file('C:\\Users\\Shamik\\Documents\\blender\\swells.txt')
red_spot = bpy.data.lamps['Spot']
for onset in swell_onsets:
    # 0 energy through previous frame
    red_spot.energy = 0
    red_spot.keyframe_insert(data_path='energy', frame=bar_to_frame(act2_start)+onset-1)
    # .5 energy at onset
    red_spot.energy = .5
    red_spot.keyframe_insert(data_path='energy', frame=bar_to_frame(act2_start)+onset)
    # 0 energy 20 frames later
    red_spot.energy = 0
    red_spot.keyframe_insert(data_path='energy', frame=bar_to_frame(act2_start)+onset+20)

# Cut to over the shoulder angle between first and second swells
spin.keyframe_insert(data_path='rotation_euler', frame=2125)
spin.rotation_euler = (0.331613, 0, 1.256637)
spin.keyframe_insert(data_path='rotation_euler', frame=2126)

# Cut to under shot between second and third swells
spin.keyframe_insert(data_path='rotation_euler', frame=2204)
spin.rotation_euler = (-0.593412, 0, 2.757620)
spin.keyframe_insert(data_path='rotation_euler', frame=2205)
camera.keyframe_insert(data_path='location', frame=2204)
camera.location = (0, 4, 0)
camera.keyframe_insert(data_path='location', frame=2205)

# Cut to askew close up between third and fourth swells
spin.keyframe_insert(data_path='rotation_euler', frame=2280)
spin.rotation_euler = (0, 0, pi)
spin.keyframe_insert(data_path='rotation_euler', frame=2281)
camera.keyframe_insert(data_path='location', frame=2280)
camera.location = (0, 3.5, 0)
camera.keyframe_insert(data_path='location', frame=2281)
camera.keyframe_insert(data_path='rotation_euler', frame=2280)
camera.rotation_euler = (pi/2, -0.349066, pi)
camera.keyframe_insert(data_path='rotation_euler', frame=2281)

# Make lights appear at start of act 2 bass
make_appear(light_names, bar_to_frame(act2_bass))

# Make red hemi flash with bass
bass_onsets = note_onset_frames_from_file('C:\\Users\\Shamik\\Documents\\blender\\act2bass.txt')
red_hemi = bpy.data.lamps['redhemi']
for onset in bass_onsets:
    # 0 energy through previous frame
    red_hemi.energy = 0
    red_hemi.keyframe_insert(data_path='energy', frame=bar_to_frame(act2_bass)+onset-1)
    # .5 energy at onset
    red_hemi.energy = .5
    red_hemi.keyframe_insert(data_path='energy', frame=bar_to_frame(act2_bass)+onset)
    # 0 energy 3 frames later
    red_hemi.energy = 0
    red_hemi.keyframe_insert(data_path='energy', frame=bar_to_frame(act2_bass)+onset+3)

# Make camera tilt back to level and zoom out soon after bass enters
camera.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act2_bass)+25)
camera.rotation_euler = (pi/2, 0, pi)
camera.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act2_bass)+50)
# Camera does not rotate again until act 3
camera.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act3_start)+25)
camera.keyframe_insert(data_path='location', frame=bar_to_frame(act2_bass)+50)
camera.location = (0, 15, 0)
camera.keyframe_insert(data_path='location', frame=bar_to_frame(act2_drums))
# Camera does not zoom again until act 3
camera.keyframe_insert(data_path='location', frame=bar_to_frame(act3_start))

# Insert close up frame on eyeball
def flash_cut(frame):
    # TODO: is this frame / property restoration necessary? I'll comment it for now
    # Save scene camera position and current frame
    #cur_frame = bpy.context.scene.frame_current
    #spin_loc = spin.location
    #spin_rot = spin.rotation_euler
    #cam_loc = camera.location
    # Add keyframes in previous and next frames
    bpy.context.scene.frame_set(frame - 1)
    spin.keyframe_insert(data_path='location', frame=frame-1)
    spin.keyframe_insert(data_path='rotation_euler', frame=frame-1)
    camera.keyframe_insert(data_path='location', frame=frame-1)
    bpy.context.scene.frame_set(frame + 1)
    spin.keyframe_insert(data_path='location', frame=frame+1)
    spin.keyframe_insert(data_path='rotation_euler', frame=frame+1)
    camera.keyframe_insert(data_path='location', frame=frame+1)
    # Add close up at frame
    bpy.context.scene.frame_set(frame)
    spin.location = (0, 0, 0)
    spin.rotation_euler = (0, 0, pi)
    camera.location = (0, 5, 0)
    spin.keyframe_insert(data_path='location', frame=frame)
    spin.keyframe_insert(data_path='rotation_euler', frame=frame)
    camera.keyframe_insert(data_path='location', frame=frame)
    # Restore scene camera position and frame
    #spin.location = spin_loc
    #spin.rotation_euler = spin_rot
    #camera.location = cam_loc
    #bpy.context.scene.frame_set(cur_frame)
    

# Make camera spin 3 rotations until snare enters
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act2_drums))
spin.rotation_euler = (0, 0, 7*pi)
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act2_snare))

for fcu in spin.animation_data.action.fcurves:
    if fcu.data_path == 'rotation_euler':
        for kp in fcu.keyframe_points:
            kp.interpolation = 'LINEAR'

# Add flash cuts
flash_cut(bar_to_frame(act2_bass)+250)
flash_cut(bar_to_frame(act2_bass)+300)

# Make spike appear at start of act 2 drums
make_appear(['Spike'], bar_to_frame(act2_drums))

# Make spike threaten eyeball with kick
spike = bpy.data.objects['Spike']
spike.location.z = -14
act2_kick_onsets = note_onset_frames_from_file('C:\\Users\\Shamik\\Documents\\blender\\act2kick.txt', [38])
for onset in act2_kick_onsets:
    spike.keyframe_insert(data_path='location', frame=bar_to_frame(act2_drums)+onset-1)
    spike.location.z = -7
    spike.keyframe_insert(data_path='location', frame=bar_to_frame(act2_drums)+onset)
    spike.location.z = -14
    spike.keyframe_insert(data_path='location', frame=bar_to_frame(act2_drums)+onset+5)

# Make drumsticks appear at start of act 2 snare
make_appear(['stick', 'stick2'], bar_to_frame(act2_snare))

# Make spike disappear at start of act 2 snare
make_disappear(['Spike'], bar_to_frame(act2_snare))

# Make drumsticks strike alternately to snare beat
sticks = [bpy.data.objects['stick'], bpy.data.objects['stick2']]
sticks[0].rotation_euler = (pi/2, 0, 0)
sticks[1].rotation_euler = (pi/2, 0, 0)
snare_onsets = note_onset_frames_from_file('C:\\Users\\Shamik\\Documents\\blender\\act2snare.txt', [42])
which_stick = 0
snare_count = 0
for onset in snare_onsets:
    # 2 frame attack and release to each 90 degree rotational strike
    #sticks[which_stick].rotation_euler = (pi/2, 0, 0)
    sticks[which_stick].keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act2_snare)+onset-2)
    sticks[which_stick].rotation_euler = (0, 0, 0)
    sticks[which_stick].keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act2_snare)+onset)
    if snare_count < len(snare_onsets) - 1 and snare_onsets[snare_count+1] - snare_onsets[snare_count] < 5:
        angle = pi/4
    else:
        angle = pi/2
    snare_count += 1
    sticks[which_stick].rotation_euler = (angle, 0, 0)
    sticks[which_stick].keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act2_snare)+onset+2)
    # Toggle between 0 and 1
    which_stick = (which_stick + 1) % 2

# Spin around sticks 2 times until arpeggiation comes in
spin.location = (-4.22, 3.3, 0)
spin.keyframe_insert(data_path='location', frame=bar_to_frame(act2_snare)+1)
spin.keyframe_insert(data_path='location', frame=bar_to_frame(act2_embellish-1))
spin.rotation_euler = (0, 0, pi)
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act2_snare)+1)
spin.rotation_euler = (0, 0, -3*pi)
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act2_embellish)-1)

# Add flash cut
flash_cut(bar_to_frame(act2_snare)+100)

# Make spike reappear with embellishment
make_appear(['Spike'], bar_to_frame(act2_embellish))
# Make melody ring appear with embellishment
make_appear(['MelodyRing'], bar_to_frame(act2_embellish))

# Make melody ring rise and fall with embellishment melody
melody_ring = bpy.data.objects['MelodyRing']
act2_embellish_onsets = note_onsets_from_file('C:\\Users\\Shamik\\Documents\\blender\\act2embellish.txt')
for (onset, note) in act2_embellish_onsets:
    melody_ring.keyframe_insert(data_path='location', frame=bar_to_frame(act2_embellish)+onset-1)
    melody_ring.location.z = (note - 90) / 4.
    melody_ring.keyframe_insert(data_path='location', frame=bar_to_frame(act2_embellish)+onset)
    
# Make melody ring float up and then disappear
melody_ring.location.z = 10
melody_ring.keyframe_insert(data_path='location', frame=bar_to_frame(act3_start))
make_disappear(['MelodyRing'], bar_to_frame(act3_start))

# Spin less than twice around center point between eye and sticks
spin.location = (-2.25, 2.18, 0)
spin.keyframe_insert(data_path='location', frame=bar_to_frame(act2_embellish))
spin.rotation_euler = (0, 0, pi)
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act2_embellish))
spin.rotation_euler = (0, 0, 7.033677+2*pi)
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act3_start))
# Camera center doesn't move again until act 3 starts
spin.keyframe_insert(data_path='location', frame=bar_to_frame(act3_start))
# Camera doesn't spin again until after act 3 starts
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act3_start+4))

# Add a bunch of flash cuts
flash_cut(bar_to_frame(act2_embellish)+5)
flash_cut(bar_to_frame(act2_embellish)+7)
flash_cut(bar_to_frame(act2_embellish)+9)
flash_cut(bar_to_frame(act2_embellish)+11)
flash_cut(bar_to_frame(act2_embellish)+13)

# Make spike disappear
make_disappear(['Spike'], bar_to_frame(act3_start))

# Make drumsticks disappear
make_disappear(['stick', 'stick2'], bar_to_frame(act3_start))

# Make under light change color
hemi.keyframe_insert(data_path='color', frame=bar_to_frame(act3_start-1))
hemi.color = (.25, 1, .25)
hemi.keyframe_insert(data_path='color', frame=bar_to_frame(act3_start))

# Make ring tunnel appear and fly past camera
make_appear(torus_names, bar_to_frame(act3_start))
torus = bpy.data.objects['Torus']
torus.location = (0, 0, -100)
torus.keyframe_insert(data_path='location', frame=bar_to_frame(act3_start))
torus.location = (0, 0, 1000)
torus.keyframe_insert(data_path='location', frame=bar_to_frame(act3_return))

# Make eyeball spin
eye.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act3_start))
eye.rotation_euler = (0, 0, 20*pi)
eye.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act3_return))

# Zoom camera in and recenter
spin.location = (0, 0, 0)
spin.keyframe_insert(data_path='location', frame=bar_to_frame(act3_start+4))
# Camera center doesn't move again
spin.keyframe_insert(data_path='location', frame=bar_to_frame(act4_end))
camera.location = (0, 3, 0)
camera.keyframe_insert(data_path='location', frame=bar_to_frame(act3_start+4))

# Spin vertically around eyeball
spin.rotation_euler = (4*pi, 0, 7.033677+2*pi)
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act3_return))

# Zoom camera out a little
camera.keyframe_insert(data_path='location', frame=bar_to_frame(act3_start+5))
camera.location = (0, 6, 0)
camera.keyframe_insert(data_path='location', frame=bar_to_frame(act3_start+7))
# Camera doesn't move again until return from act 3
camera.keyframe_insert(data_path='location', frame=bar_to_frame(act3_return))

# Flash cut on hits
act3_hits = note_onset_frames_from_file('C:\\Users\\Shamik\\Documents\\blender\\act3drums.txt', [40])
for onset in act3_hits:
    # TODO: onsets are a beat forward
    flash_cut(bar_to_frame(act3_theme - .25) + onset)

# Make walls disappear
make_disappear(wall_names, bar_to_frame(act3_return))
# Make drumsticks disappear
make_disappear(['stick', 'stick2'], bar_to_frame(act3_return))
# Make lights fade then disappear
hemi.keyframe_insert(data_path='energy', frame=bar_to_frame(act3_return-1))
hemi.energy = 0
hemi.keyframe_insert(data_path='energy', frame=bar_to_frame(act3_return))
under_light.keyframe_insert(data_path='energy', frame=bar_to_frame(act3_return-1))
under_light.energy = 0
under_light.keyframe_insert(data_path='energy', frame=bar_to_frame(act3_return))
make_disappear(light_names, bar_to_frame(act3_return))
# Make wood floor reappear
make_appear(['world_floor'], bar_to_frame(act3_return))
# Make blue sun reappear
blue_sun.keyframe_insert(data_path = 'energy', frame=bar_to_frame(act3_return))
blue_sun.energy = 0.9
blue_sun.keyframe_insert(data_path = 'energy', frame=bar_to_frame(act3_end))

# Make ring tunnel disappear after exiting
tor_names = ['Torus' + str(i) for i in range(1, numtor+1)]
make_disappear(tor_names, bar_to_frame(act3_return))

# Make orbs reappear for last act
make_appear(orb_names, bar_to_frame(act3_return))
make_appear(glass_names, bar_to_frame(act3_return))

# Make random orbs flash for a few frames at each embellishment note onset
act4_embellish_onsets = note_onset_frames_from_file('C:\\Users\\Shamik\\Documents\\blender\\act4orbs.txt')
random.seed(0)
for onset in act4_embellish_onsets:
    numflash = 10
    for flash in range(1, numflash):
        orb_mat = bpy.data.materials['OrbMat' + str(random.randint(1, numorb))]
        # 0 emission through previous frame
        orb_mat.emit = 0
        orb_mat.keyframe_insert(data_path='emit', frame=bar_to_frame(act3_end)+onset-1)
        # 1 emission at onset frame
        orb_mat.emit = 2
        orb_mat.keyframe_insert(data_path='emit', frame=bar_to_frame(act3_end)+onset)
        # 0 emission 10 frames later
        orb_mat.emit = 0
        orb_mat.keyframe_insert(data_path='emit', frame=bar_to_frame(act3_end)+onset+10)

# Go back to eyeball
camera.location = (0, 15, 0)
camera.keyframe_insert(data_path='location', frame=bar_to_frame(act3_return)+75)

# Spin away into distance, 3 times
camera.location = (0, 98, 0)
camera.keyframe_insert(data_path='location', frame=bar_to_frame(act4_end))
spin.rotation_euler = (4*pi, 0, 7.033677+6*pi)
spin.keyframe_insert(data_path='rotation_euler', frame=bar_to_frame(act4_end))

# Fade out blue sun
blue_sun.keyframe_insert(data_path = 'energy', frame=bar_to_frame(act4_fade))
blue_sun.energy = 0
blue_sun.keyframe_insert(data_path = 'energy', frame=bar_to_frame(act4_fade+2))

# TODO: constants frame values in keyframe_insert calls should be dependent on frame rate
#       this also applies to calls to make_appear, make_disappear, flash_cut
# TODO: make adjacent keyframes consistent: -1 and 0 or 0 and +1?
#       probably should make intervals end at -1 and start at 0
# TODO: should keyframes be made for entire section when setting is applied?
#       now new settings need a prior guard keyframe
#       probably, because guard keyframe assumes value has not changed in intermediate code
#       also, all intervals are defined in once place
#       however, keyframe insertion no longer has time locality in code
#       the only reason to delocalize is to accommodate flash cuts
# TODO: clarify light naming and other object naming, unify camelcase vs underscore
# TODO: revisit lights that have been accidentally removed from scene by
#       uninitialized animation
# TODO: make rotations/positions relative instead of hardcoded?