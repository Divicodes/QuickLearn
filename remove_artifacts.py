import os
from generator import DEFAULT_IMAGE_DIR, DEFAULT_VIDEO_OUTPUT_DIR, DEFAULT_AUDIO_DIR

os.makedirs(DEFAULT_AUDIO_DIR, exist_ok=True)
os.makedirs(DEFAULT_IMAGE_DIR, exist_ok=True)

# Remove any files in the directories
for file in os.listdir(DEFAULT_AUDIO_DIR):
    os.remove(os.path.join(DEFAULT_AUDIO_DIR, file))

for file in os.listdir(DEFAULT_IMAGE_DIR):
    os.remove(os.path.join(DEFAULT_IMAGE_DIR, file))
