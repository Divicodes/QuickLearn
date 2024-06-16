import streamlit as st
import os
import openai
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


load_dotenv()


def generate_keywords(script):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Based on the given sentence '{script}', generate one keyword which is used to search for the stock image related to the sentence.",
            },
        ],
        n=1,
        stop=None,
        temperature=0.7,
    )
    script = response.choices[0].message.content
    # print(script)
    return script  # Ensure the API returns a valid Python dictionary


def generate_openai(interests, topic):
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
    print(script)
    return script  # Ensure the API returns a valid Python dictionary


def get_explanation(topics, interests):
    # Get script
    print(interests)
    print(topics)
    ini_script = generate_openai(interests, topics)

    keywords = []
    # Get image keywords
    for line in ini_script.splitlines():
        keyword = generate_keywords(line)
        keywords.append(keyword)

    # Get image
    from pexels_api import API
    import os

    # Create API object
    api = API(os.getenv("PEXELS_API_KEY"))

    # Search for photos
    api.search("kitten", page=1, results_per_page=1)

    # Get photo entries
    photos = api.get_entries()

    import requests

    def download_image(photo, filename):
        response = requests.get(photo.large, allow_redirects=True)
        filename = f"{photo.id}.{photo.extension}"
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)

    for i, keyword in enumerate(keywords):
        api.search(keyword, page=1, results_per_page=1)
        photos = api.get_entries()
        download_image(photos[0], f"images/{i}.jpg")

    # Generate video
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

    # Generate narration
    from openai import OpenAI

    client = OpenAI()

    speech_file_path = "audio/speech.mp3"
    response = client.audio.speech.create(
        model="tts-1", voice="alloy", input=ini_script
    )

    response.write_to_file(speech_file_path)

    # Get the images from the images folder. Use os listdir
    images = os.listdir("images")

    # Get audio
    audios = os.listdir("audio")

    clips = []

    # Resize the images
    for i in range(len(images)):
        resized_image_path = images[i].replace(".jpg", "_resized.jpg")
        resize_image(images[i], resized_image_path, (1280, 720))
        images[i] = resized_image_path

    # find duration of the audio from the audio file
    from pydub import AudioSegment

    audio = AudioSegment.from_file("audio/speech.mp3")
    audio_duration = audio.duration_seconds

    # Generate a clip for each image
    for i in range(len(images)):
        # Create an image clip. Image displayed for 20 seconds.
        image_clip = ImageClip(images[i], duration=audio_duration / len(images))

        # # Create a text clip for subtitles
        # txt_clip = TextClip(subtitles[i], fontsize=50, color="white", bg_color="black")
        # txt_clip = txt_clip.set_position("bottom").set_duration(20)

        # Load the corresponding audio
        audio = AudioFileClip(audios[0])

        # Set the audio of the image clip
        image_clip = image_clip.set_audio(audio)

        # Overlay text on image
        # video = CompositeVideoClip([image_clip, image_clip])

        # Append the clip to the list of clips
        clips.append(image_clip)

    # Concatenate all the clips together
    final_clip = concatenate_videoclips(clips)

    # Write the result to a file
    final_clip.write_videofile("output_video.mp4", fps=24)

    # explanation = f"Imagine each castle as a node (or vertex) in a graph. The roads connecting these castles are the edges of the graph. Graph theory studies how these castles are connected. For example, it can answer questions like how many different routes you can take to get from one castle to another, which castle is the easiest to reach from all others, or if there's a way to visit every castle without crossing the same road twice. This kind of analysis helps in planning the best paths for travel, defense strategies, or even in understanding relationships between different entities represented by the castles and roads."
    video_url = "output_video.mp4"

    return ini_script, video_url


# Creating a tab interface for navigation
tab1, tab2 = st.tabs(["Home", "Settings"])

# Content for the 'Home' tab
with tab1:
    st.header("EUERK.Ai 💡")
    topic = st.text_input("What topic do you want to learn", key="topic")
    if st.button("Explain"):
        if topic:
            # Get explanation and video URL
            interests = st.session_state["user_info"]
            explanation, video_url = get_explanation(topic, interests)
            # Save to session state
            st.session_state["explanation"] = explanation
            st.session_state["video_url"] = video_url
        else:
            st.warning("Please enter a topic to explain.")

    if "explanation" in st.session_state:
        st.subheader("Explanation")
        st.write(st.session_state["explanation"])
    if "video_url" in st.session_state:
        st.subheader("Video Explanation")
        st.video(st.session_state["video_url"])

# Content for the 'Settings' tab
with tab2:
    st.header("Settings")
    user_info = st.text_area("Tell us about yourself", key="user_info")
    if st.button("Save", key="save_settings"):
        st.session_state["user_info"] = user_info
        st.success("Settings saved!")
