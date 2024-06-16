from moviepy.editor import (
    ImageClip,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip,
    AudioFileClip,
)

from PIL import Image


def resize_image(input_image_path, output_image_path, target_size):
    with Image.open(input_image_path) as img:
        # Calculate the new size preserving the aspect ratio
        img_ratio = img.width / img.height
        target_ratio = target_size[0] / target_size[1]
        if target_ratio > img_ratio:
            new_height = target_size[1]
            new_width = int(new_height * img_ratio)
        else:
            new_width = target_size[0]
            new_height = int(new_width / img_ratio)

        # Resize the image
        img = img.resize((new_width, new_height))

        # Create a new image with black background
        new_img = Image.new("RGB", target_size)
        # Calculate position to paste resized image
        top_left_x = (target_size[0] - new_width) // 2
        top_left_y = (target_size[1] - new_height) // 2
        new_img.paste(img, (top_left_x, top_left_y))

        # Save the padded image
        new_img.save(output_image_path)


# Define the paths to your images and audio files
images = [
    "experiments/images/pexels-1786350-3358880.jpg",
    "experiments/images/pexels-cristian-rojas-7586656.jpg",
    "experiments/images/pexels-pixabay-87651.jpg",
]
audios = [
    "experiments/audios/audio1.mp3",
    "experiments/audios/audio1.mp3",
    "experiments/audios/audio1.mp3",
]
subtitles = [
    "This is the first subtitle.",
    "Second subtitle",
    "3rd subtitle",
]

clips = []

# Resize the images
for i in range(3):
    resized_image_path = images[i].replace(".jpg", "_resized.jpg")
    resize_image(images[i], resized_image_path, (1280, 720))
    images[i] = resized_image_path

# Generate a clip for each image
for i in range(3):
    # Create an image clip. Image displayed for 20 seconds.
    image_clip = ImageClip(images[i], duration=20)

    # Create a text clip for subtitles
    txt_clip = TextClip(subtitles[i], fontsize=50, color="white", bg_color="black")
    txt_clip = txt_clip.set_position("bottom").set_duration(20)

    # Load the corresponding audio
    audio = AudioFileClip(audios[i])

    # Set the audio of the image clip
    image_clip = image_clip.set_audio(audio)

    # Overlay text on image
    video = CompositeVideoClip([image_clip, txt_clip])

    # Append the clip to the list of clips
    clips.append(video)

# Concatenate all the clips together
final_clip = concatenate_videoclips(clips)

# Write the result to a file
final_clip.write_videofile("output_video.mp4", fps=24)
