import os
import threading
from datetime import datetime, timedelta
from string import Template

from .constant import LIBRARY_PATH
from .util import arlotime_strftime, arlotime_to_datetime, http_get, http_stream


class ArloMediaDownloader(threading.Thread):
    def __init__(self, arlo, save_format):
        super().__init__()
        self._arlo = arlo
        self._save_format = save_format
        self._lock = threading.Condition()
        self._queue = []

    # noinspection PyPep8Naming
    def _output_name(self, media):
        """Calculate file name from media object.

        Uses `self._save_format` to work out the substitions.

        :param media: ArloMediaObject to download
        :return: The file name.
        """
        when = arlotime_to_datetime(media.created_at)
        Y = str(when.year).zfill(4)
        m = str(when.month).zfill(2)
        d = str(when.day).zfill(2)
        H = str(when.hour).zfill(2)
        M = str(when.minute).zfill(2)
        S = str(when.second).zfill(2)
        F = f"{Y}-{m}-{d}"
        T = f"{H}:{M}:{S}"
        t = f"{H}-{M}-{S}"
        s = str(int(when.timestamp())).zfill(10)
        try:
            return (
                Template(self._save_format).substitute(
                    SN=media.camera.device_id,
                    N=media.camera.name,
                    Y=Y,
                    m=m,
                    d=d,
                    H=H,
                    M=M,
                    S=S,
                    F=F,
                    T=T,
                    t=t,
                    s=s,
                )
                + f".{media.extension}"
            )
        except KeyError as _e:
            self._arlo.error(f"format error: {self._save_format}")
            return None

    def _download(self, media):
        """Download a single piece of media.

        :param media: ArloMediaObject to download
        :return: 1 if a file was downloaded, 0 if the file present and skipped or -1 if an error occured
        """
        # Calculate name.
        save_file = self._output_name(media)
        if save_file is None:
            return -1
        try:
            # See if it exists.
            os.makedirs(os.path.dirname(save_file), exist_ok=True)
            if not os.path.exists(save_file):
                # Download to temporary file before renaming it.
                self._arlo.debug(f"dowloading for {media.camera.name} --> {save_file}")
                save_file_tmp = f"{save_file}.tmp"
                http_get(media.url, save_file_tmp)
                os.rename(save_file_tmp, save_file)
                return 1
            else:
                self._arlo.vdebug(
                    f"skipping dowload for {media.camera.name} --> {save_file}"
                )
                return 0
        except OSError as _e:
            self._arlo.error(f"failed to dowload: {save_file}")
            return -1

    def run(self):
        if self._save_format == "":
            self._arlo.debug("not starting downloader")
            return
        while True:
            media = None
            result = 0
            with self._lock:
                if len(self._queue) > 0:
                    media = self._queue.pop(0)

            if media is not None:
                result = self._download(media)

            with self._lock:
                # Nothing else to do then just wait.
                if len(self._queue) == 0:
                    self._arlo.vdebug(f"waiting for media")
                    self._lock.wait(60.0)
                # We downloaded a file so inject a small delay.
                elif result == 1:
                    self._lock.wait(0.5)

    def queue_download(self, media):
        if self._save_format == "":
            return
        with self._lock:
            self._queue.append(media)
            if len(self._queue) == 1:
                self._lock.notify()


class ArloMediaLibrary(object):
    """Arlo Library Media module implementation."""

    def __init__(self, arlo):
        self._arlo = arlo
        self._lock = threading.Lock()
        self._load_cbs_ = []
        self._count = 0
        self._videos = []
        self._video_keys = []
        self._snapshots = {}

        self._downloader = ArloMediaDownloader(arlo, self._arlo.cfg.save_media_to)
        self._downloader.name = "ArloMediaDownloader"
        self._downloader.daemon = True
        self._downloader.start()

    def __repr__(self):
        return "<{0}:{1}>".format(self.__class__.__name__, self._arlo.cfg.name)

    # grab recordings from last day, add to existing library if not there
    def update(self):
        self._arlo.debug("updating image library")

        # grab today's images
        date_to = datetime.today().strftime("%Y%m%d")
        data = self._arlo.be.post(
            LIBRARY_PATH, {"dateFrom": date_to, "dateTo": date_to}
        )

        # get current videos
        with self._lock:
            keys = self._video_keys

        # add in new images
        videos = []
        snapshots = {}
        for video in data:

            # camera, skip if not found
            camera = self._arlo.lookup_camera_by_id(video.get("deviceId"))
            if not camera:
                continue

            # snapshots, use first found
            if video.get("reason", "") == "snapshot":
                if camera.device_id not in snapshots:
                    self._arlo.debug(f"adding snapshot for {camera.name}")
                    snapshots[camera.device_id] = ArloSnapshot(
                        video, camera, self._arlo
                    )
                continue

            # videos, add missing
            if video.get("contentType", "").startswith("video/"):
                key = "{0}:{1}".format(
                    camera.device_id, arlotime_strftime(video.get("utcCreatedDate"))
                )
                if key in keys:
                    self._arlo.vdebug(f"skipping {key} for {camera.name}")
                    continue
                self._arlo.debug(f"adding {key} for {camera.name}")
                video = ArloVideo(video, camera, self._arlo)
                videos.append(video)
                self._downloader.queue_download(video)
                keys.append(key)

        # note changes and run callbacks
        with self._lock:
            self._count += 1
            self._videos = videos + self._videos
            self._video_keys = keys
            self._snapshots = snapshots
            self._arlo.debug("ml:update-count=" + str(self._count))
            cbs = self._load_cbs_
            self._load_cbs_ = []

        # run callbacks with no locks held
        for cb in cbs:
            cb()

    def load(self):

        # set beginning and end
        days = self._arlo.cfg.library_days
        now = datetime.today()
        date_from = (now - timedelta(days=days)).strftime("%Y%m%d")
        date_to = now.strftime("%Y%m%d")
        self._arlo.debug("loading image library ({} days)".format(days))

        # save videos for cameras we know about
        data = self._arlo.be.post(
            LIBRARY_PATH, {"dateFrom": date_from, "dateTo": date_to}
        )
        if data is None:
            self._arlo.warning("error loading the image library")
            return

        videos = []
        keys = []
        snapshots = {}
        for video in data:

            # Look for camera, skip if not found.
            camera = self._arlo.lookup_camera_by_id(video.get("deviceId"))
            if camera is None:
                key = "{0}:{1}".format(
                    video.get("deviceId"),
                    arlotime_strftime(video.get("utcCreatedDate")),
                )
                self._arlo.vdebug("skipping {0}".format(key))
                continue

            # snapshots, use first found
            if video.get("reason", "") == "snapshot":
                if camera.device_id not in snapshots:
                    self._arlo.debug(f"adding snapshot for {camera.name}")
                    snapshots[camera.device_id] = ArloSnapshot(
                        video, camera, self._arlo
                    )
                continue

            # videos, add all
            if video.get("contentType", "").startswith("video/"):
                key = "{0}:{1}".format(
                    video.get("deviceId"),
                    arlotime_strftime(video.get("utcCreatedDate")),
                )
                self._arlo.vdebug(f"adding {key} for {camera.name}")
                video = ArloVideo(video, camera, self._arlo)
                videos.append(video)
                self._downloader.queue_download(video)
                keys.append(key)
                continue

        # set update count, load() never runs callbacks
        with self._lock:
            self._count += 1
            self._videos = videos
            self._video_keys = keys
            self._snapshots = snapshots
            self._arlo.debug("ml:load-count=" + str(self._count))

    def snapshot_for(self, camera):
        with self._lock:
            return self._snapshots.get(camera.device_id, None)

    @property
    def videos(self):
        with self._lock:
            return self._count, self._videos

    @property
    def count(self):
        with self._lock:
            return self._count

    def videos_for(self, camera):
        camera_videos = []
        with self._lock:
            for video in self._videos:
                if camera.device_id == video.camera.device_id:
                    camera_videos.append(video)
            return self._count, camera_videos

    def queue_update(self, cb):
        with self._lock:
            if not self._load_cbs_:
                self._arlo.debug("queueing image library update")
                self._arlo.bg.run_low_in(self.update, 2)
            self._load_cbs_.append(cb)


class ArloMediaObject(object):
    """Object for Arlo Video file."""

    def __init__(self, attrs, camera, arlo):
        """Video Object."""
        self._arlo = arlo
        self._attrs = attrs
        self._camera = camera

    def __repr__(self):
        """Representation string of object."""
        return "<{0}:{1}>".format(self.__class__.__name__, self.name)

    @property
    def name(self):
        return "{0}:{1}".format(
            self._camera.device_id, arlotime_strftime(self.created_at)
        )

    # pylint: disable=invalid-name
    @property
    def id(self):
        """Returns unique id representing the video."""
        return self._attrs.get("name", None)

    @property
    def created_at(self):
        """Returns date video was creaed."""
        return self._attrs.get("utcCreatedDate", None)

    def created_at_pretty(self, date_format=None):
        """Returns date video was taken formated with `last_date_format`"""
        if date_format:
            return arlotime_strftime(self.created_at, date_format=date_format)
        return arlotime_strftime(self.created_at)

    @property
    def created_today(self):
        """Returns `True` if video was taken today, `False` otherwise."""
        return self.datetime.date() == datetime.today().date()

    @property
    def datetime(self):
        """Returns a python datetime object of when video was created."""
        return arlotime_to_datetime(self.created_at)

    @property
    def content_type(self):
        """Returns the video content type.

        Usually `video/mp4`
        """
        return self._attrs.get("contentType", None)

    @property
    def extension(self):
        if self.content_type.endswith("mp4"):
            return "mp4"
        return "jpg"

    @property
    def camera(self):
        return self._camera

    @property
    def triggered_by(self):
        return self._attrs.get("reason", None)

    @property
    def url(self):
        """Returns the URL of the video."""
        return self._attrs.get("presignedContentUrl", None)

    @property
    def thumbnail_url(self):
        """Returns the URL of the thumbnail image."""
        return self._attrs.get("presignedThumbnailUrl", None)

    def download_thumbnail(self, filename=None):
        return http_get(self.thumbnail_url, filename)


class ArloVideo(ArloMediaObject):
    """Object for Arlo Video file."""

    def __init__(self, attrs, camera, arlo):
        """Video Object."""
        super().__init__(attrs, camera, arlo)

    @property
    def media_duration_seconds(self):
        """Returns how long the recording last."""
        return self._attrs.get("mediaDurationSecond", None)

    @property
    def object_type(self):
        """Returns what object caused the video to start.

        Currently is `vehicle`, `person`, `animal` or `other`.
        """
        return self._attrs.get("objCategory", None)

    @property
    def object_region(self):
        """Returns the region of the thumbnail showing the object."""
        return self._attrs.get("objRegion", None)

    @property
    def video_url(self):
        """Returns the URL of the video."""
        return self._attrs.get("presignedContentUrl", None)

    def download_video(self, filename=None):
        return http_get(self.video_url, filename)

    @property
    def stream_video(self):
        return http_stream(self.video_url)


class ArloSnapshot(ArloMediaObject):
    """Object for Arlo Snapshot file."""

    def __init__(self, attrs, camera, arlo):
        """Snapshot Object."""
        super().__init__(attrs, camera, arlo)

    @property
    def image_url(self):
        """Returns the URL of the video."""
        return self._attrs.get("presignedContentUrl", None)


# vim:sw=4:ts=4:et:
