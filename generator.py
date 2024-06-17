import openai
from dotenv import load_dotenv
from pexels_api import API
import os
import requests
from moviepy.editor import (
    ImageClip,
    concatenate_videoclips,
    AudioFileClip,
)

from PIL import Image
from openai import OpenAI
from pexels_api.tools import Photo
from typing import List, Tuple


load_dotenv()

DEFAULT_AUDIO_DIR = "audio"
DEFAULT_IMAGE_DIR = "images"
DEFAULT_VIDEO_OUTPUT_DIR = "videos"

# Create directories if they don't exist
os.makedirs(DEFAULT_AUDIO_DIR, exist_ok=True)
os.makedirs(DEFAULT_IMAGE_DIR, exist_ok=True)
os.makedirs(DEFAULT_VIDEO_OUTPUT_DIR, exist_ok=True)


def get_image_search_term(sentence: str) -> str:
    """Generate a keyword to search for a stock image based on the given sentence.

    Args:
        sentence (str): The sentence to generate the keyword from.

    Returns:
        str: The keyword to search for a stock image.
    """
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Based on the given sentence '{sentence}', generate one keyword which is used to search for the stock image related to the sentence.",
            },
        ],
        n=1,
        stop=None,
        temperature=0.7,
    )
    search_term = response.choices[0].message.content

    return search_term


def generate_analogy(interests: str, topic: str) -> str:
    """Generate an analogy to explain a topic based on the user's interests.

    Args:
        interests (str): The user's interests, specified as a comma-separated string.
        topic (str): The topic to explain using an analogy.

    Returns:
        str: The analogy to explain the topic based on the user's interests.
    """
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Based on the user's '{interests}', generation a short paragraph script in a way that user will explain the '{topic}' with analogy of the interests mentioned.",
            },
        ],
        n=1,
        stop=None,
        temperature=0.7,
    )

    script = response.choices[0].message.content

    return script


def get_photos(search_term: str, page=1, results_per_page=1) -> List[Photo]:
    """Get a list of photos based on the search term.

    Args:
        search_term (str): The search term to find photos.
        page (int, optional): Number of pages to retrieve. Defaults to 1.
        results_per_page (int, optional): Number of results to show per page. Defaults to 1.

    Returns:
        List[Photo]: A list of pexel photo objects based on the search term.
    """
    api = API(os.getenv("PEXELS_API_KEY"))

    api.search(search_term, page=page, results_per_page=results_per_page)
    photos = api.get_entries()

    return photos


def download_image(photo: Photo, output_dir: str = os.getcwd()) -> str:
    """Download an image from the Pexels API.

    Args:
        photo (Photo): The photo object to download.
        output_dir (str, optional): Output directory to save the image in. Defaults to os.getcwd().

    Raises:
        Exception: If the image download fails.

    Returns:
        str: The filename of the downloaded image.
    """
    # Get the image content
    response = requests.get(photo.large, allow_redirects=True)

    # Save the image content to a file
    filename = os.path.join(output_dir, f"{photo.id}.{photo.extension}")

    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
    else:
        raise Exception("Failed to retrieve image.")

    return filename


def resize_image(image_path, output_image_path, target_size):
    """Resize the image to the target size and pad the resized image with black color.

    Args:
        image_path (str): The path to the image file.
        output_image_path (str): The path to save the resized image.
        target_size (Tuple[int, int]): A tuple of the target width and height.
    """
    with Image.open(image_path) as img:
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

    return output_image_path


def generate_audio(
    text: str,
    output_file_path=os.path.join(DEFAULT_AUDIO_DIR, "narration.mp3"),
    voice="alloy",
    model="tts-1",
) -> str:
    """Generate an audio file from the given text using OpenAI's Text-to-Speech API.

    Args:
        text (str): The text to convert to speech.
        output_file_path (str, optional): Path to save generated audio file. Defaults to os.path.join(DEFAULT_AUDIO_DIR, "narration.mp3").
        voice (str, optional): Voice id from OpenAI's Text-to-speech API. Defaults to "alloy".
        model (str, optional): Voice model from OpenAI's Text-to-speech API. Defaults to "tts-1".

    Returns:
        str: The path to the generated audio file.
    """
    client = OpenAI()

    response = client.audio.speech.create(model=model, voice=voice, input=text)

    response.write_to_file(output_file_path)

    return output_file_path


def generate_video(
    topics: str, interests: str, debug_mode: bool = False
) -> Tuple[str, str]:
    video_dimension = (1280, 720)

    analogy_script = generate_analogy(interests, topics)

    # Get image keywords for each line in the analogy script
    image_search_terms = []

    for line in analogy_script.splitlines():
        keyword = get_image_search_term(line)
        image_search_terms.append(keyword)

    # Create stock photos API object
    for search_term in image_search_terms:
        photos = get_photos(search_term)

        assert len(photos) > 0, f"No photos found for search term: {search_term}"

        photo = photos[0]
        download_image(photo, DEFAULT_IMAGE_DIR)

    # Generate video narration
    audio_path = generate_audio(analogy_script)

    # Resize the images for video
    images = os.listdir(DEFAULT_IMAGE_DIR)
    images = [os.path.join(DEFAULT_IMAGE_DIR, image_path) for image_path in images]

    for i in range(len(images)):
        resize_image(images[i], images[i], video_dimension)

    # Load the audio clip once
    audio = AudioFileClip(audio_path)

    # Calculate the duration for each image clip based on the total audio duration
    clip_duration = audio.duration / len(images)

    clips = []  # To store each clip with audio

    # Generate a clip for each image
    for i in range(len(images)):
        # Create an image clip. Image displayed for an equal part of the audio.
        image_clip = ImageClip(images[i], duration=clip_duration)

        # Set the audio for the image clip starting221 from the right offset
        image_clip = image_clip.set_audio(
            audio.subclip(i * clip_duration, (i + 1) * clip_duration)
        )

        # Append the clip to the list of clips
        clips.append(image_clip)

    # Concatenate all the clips together
    final_clip = concatenate_videoclips(clips, method="compose")

    # Write the result to a file
    video_path = os.path.join(DEFAULT_VIDEO_OUTPUT_DIR, f"{interests}.mp4")

    final_clip.write_videofile(video_path, fps=24)

    # Remove the residual files
    if not debug_mode:
        for image_path in os.listdir(DEFAULT_IMAGE_DIR):
            os.remove(image_path)

        for audio_path in os.listdir(DEFAULT_AUDIO_DIR):
            os.remove(audio_path)

    return analogy_script, video_path
