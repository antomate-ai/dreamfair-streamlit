
import streamlit as st
from openai import OpenAI
# Set up logger for error logging
LOGGER = st.logger.get_logger(__name__)

# Initialize OpenAI client with API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["openai"])
def extract_image_prompts(storyboard):
    """
    Extract image prompts from the storyboard text.

    Args:
    storyboard (str): A string containing the storyboard descriptions.

    Returns:
    list: A list of prompts for image generation.
    """
    # Split the storyboard into lines
    lines = storyboard.split('\n')
    image_prompts = []

    # Iterate through each line to find those that start with "Image"
    for line in lines:
        if line.startswith("Image ("):
            # Extract the prompt by removing the initial "Image (number):" part
            prompt = line.split(':', 1)[1].strip()
            image_prompts.append(prompt)

    return image_prompts
def generate_script(synopsis, script_style, video_duration):
    """Generates a script using OpenAI based on user inputs.
    
    Args:
        synopsis (str): User-provided synopsis for the script.
        script_style (str): The desired style of the script.
        video_duration (str): The desired duration of the video.

    Returns:
        str: The generated script or an error message.
    """
    prompt = f"Generate a script in the style of {script_style} for a video lasting {video_duration}, inspired by the following synopsis: {synopsis}. After generating the script write the storyboards as image or storyboard descriptions with the following annotation: Image (Image Number): Storyboard descriptions. Be aware the every image description is in sperated line and without any additional characters "
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a senior scripts writer and artist."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        LOGGER.error(f"Error generating script: {e}")
        return "Failed to generate script."

def generate_storyboards(script, storyboard_style, detailed, colored):
    """Generates storyboards using DALL·E based on the script and user preferences.
    
    Args:
        script (str): The generated script to base the storyboards on.
        storyboard_style (str): The style of the storyboard.
        detailed (bool): Whether the storyboard should be detailed.
        colored (bool): Whether the storyboard should be colored.

    Returns:
        list: URLs of the generated storyboard images or error message placeholders.
    """
    detail_description = "Detailed" if detailed else "Simple"
    color_description = "Colored" if colored else "Black and white"
    prompts_images = extract_image_prompts(script)
    images_urls = []
    for idx,image_prompt in enumerate(prompts_images):
        prompt = f"Create a {color_description}, {detail_description} storyboard in the style of {storyboard_style} based on this storyboard description: {image_prompt}"
    
        try:
            response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
            )
            images_urls.append(response.data[0].url)
            
            st.image(response.data[0].url,caption=image_prompt,width=400)
        except Exception as e:
            images_urls.append("img.png")
            LOGGER.error(f"Error generating storyboards: {e}")
    
    
    return images_urls
   

def run():
    """Main function to run the Streamlit app."""
    st.set_page_config(page_title="AI Storyboard Generator", layout="wide")

    if 'generated_script' not in st.session_state:
        st.session_state.generated_script = ""

    with st.form("script_generator_form"):
        st.header('1. Write/Paste Your Synopsis (Optional)')
        synopsis = st.text_area("Your Synopsis", height=250)
        st.header('2. Script Details')
        script_style = st.selectbox("Script Style", ('Action', 'Comic', 'Explainer', 'Drama'))
        video_duration = st.selectbox("Video Duration", ('30s', '1m', '2m', '5m', '10m'))
        submitted = st.form_submit_button("Generate Script")
        if submitted:
            st.session_state.generated_script = generate_script(synopsis, script_style, video_duration)

    if st.session_state.generated_script:
        st.text_area("Generated Script", st.session_state.generated_script, height=300)

    st.header('3. Generate Storyboard')
    storyboard_style = st.radio("Storyboard Style", ('Doodle', 'Sketchy', 'Reality', 'Shaded'))
    board_details = st.checkbox("Detailed")
    board_color = st.checkbox("Colored")
    if st.button('Generate Storyboard'):
        if st.session_state.generated_script:
            generate_storyboards(st.session_state.generated_script, storyboard_style, board_details, board_color)
        else:
            st.error("Please generate a script first before creating storyboards.")
run()