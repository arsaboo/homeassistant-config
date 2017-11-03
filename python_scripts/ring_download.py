# obtain ring doorbell camera object
# replace the camera.front_door by your camera entity
ring_cam = hass.states.get('camera.front_door')

subdir_name = 'ring_{}'.format(ring_cam.attributes.get('friendly_name').lower().replace(' ', '_'))

# get video URL
data = {
    'url': ring_cam.attributes.get('video_url'),
    'subdir': subdir_name,
    'overwrite': True,
    'filename': ring_cam.attributes.get('friendly_name').lower().replace(' ', '_')
}

# call downloader component to save the video
hass.services.call('downloader', 'download_file', data)
