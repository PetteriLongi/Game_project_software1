"""
music.py - Simple music manager for the game

INSTRUCTIONS:
--------------
1. Import this module in your main game file:
       from game import music

2. To play a music track (lazy-inits the mixer on first use):
       music.play_music("path/to/your/music_file.mp3", volume=0.5)
   - 'volume' is optional and ranges from 0.0 (silent) to 1.0 (max volume).

3. To explicitly initialize audio (optional):
       music.init_audio()
   - Useful to handle/diagnose audio init errors early.

4. To stop the music:
       music.stop_music()

5. To change volume while playing:
       music.set_volume(0.3)

Notes:
- The mixer is lazily initialized on first use to avoid import-time side effects.
- If initialization fails (e.g., missing audio device), functions will no-op gracefully.
"""

import pygame

_mixer_ready = False
_SFX_CACHE = {}
_SFX_CHANNELS = {}


# ==========================================
# LAZY MIXER INIT (SAFE ON IMPORT)
# ==========================================
def _ensure_mixer():
    """Initialize pygame.mixer on first use. Safe to call multiple times."""
    global _mixer_ready
    if _mixer_ready:
        return True
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        _mixer_ready = True
        return True
    except Exception as e:
        # Graceful degradation: print once and disable audio functions
        if not _mixer_ready:
            print(f"\033[93m[Audio Disabled]\033[0m Could not initialize audio: {e}")
        _mixer_ready = False
        return False


def init_audio():
    """Explicitly initialize audio. Returns True on success, False on failure."""
    return _ensure_mixer()


# ==========================================
# PUBLIC API: MUSIC CONTROLS
# ==========================================
def play_music(file_path, volume=0.5, loop=True):
    """
    Plays a music file.

    Args:
        file_path (str): Path to music file
        volume (float): 0.0 to 1.0
        loop (bool): If True, music loops indefinitely
    """
    if not _ensure_mixer():
        return
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1 if loop else 0)


def stop_music():
    """Stops the currently playing music."""
    if not _ensure_mixer():
        return
    pygame.mixer.music.stop()


# ==========================================
# PUBLIC API: VOLUME CONTROL
# ==========================================
def set_volume(volume):
    """Adjust volume while music is playing (0.0 to 1.0)."""
    if not _ensure_mixer():
        return
    pygame.mixer.music.set_volume(volume)


# ==========================================
# SFX MANAGEMENT (CACHE + CHANNELS)
# ==========================================
def load_sfx(name, path, volume=0.15, channel_id=None):
    """
    Load (and cache) a sound effect by name. Optionally reserve a mixer channel.
    Safe to call multiple times; returns the Sound instance or None on failure.
    """
    if not _ensure_mixer():
        return None
    snd = _SFX_CACHE.get(name)
    if snd is None:
        try:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(max(0.0, min(1.0, float(volume))))
            _SFX_CACHE[name] = snd
        except Exception as e:
            print(f"\033[93m[SFX]\033[0m Failed to load '{path}': {e}")
            return None
    # Reserve channel if requested
    if channel_id is not None and channel_id not in _SFX_CHANNELS:
        try:
            _SFX_CHANNELS[channel_id] = pygame.mixer.Channel(int(channel_id))
        except Exception as e:
            print(f"\033[93m[SFX]\033[0m Failed to reserve channel {channel_id}: {e}")
    return snd


def play_sfx(name, channel_id=None):
    """
    Play a previously loaded SFX by name. If channel_id is provided and reserved,
    plays on that channel; otherwise uses Sound.play().
    """
    if not _ensure_mixer():
        return
    snd = _SFX_CACHE.get(name)
    if not snd:
        return
    if channel_id is not None and channel_id in _SFX_CHANNELS:
        try:
            _SFX_CHANNELS[channel_id].play(snd)
        except Exception:
            snd.play()
    else:
        snd.play()


def set_sfx_volume(name, volume):
    """Adjust volume for a loaded SFX by name."""
    snd = _SFX_CACHE.get(name)
    if snd:
        try:
            snd.set_volume(max(0.0, min(1.0, float(volume))))
        except Exception:
            pass


def unload_sfx(name):
    """Remove a loaded SFX from cache. Does not stop currently playing sound."""
    _SFX_CACHE.pop(name, None)