import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from openai import OpenAI
load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
client = OpenAI(
  api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
)
if google_api_key:
    genai.configure(api_key=google_api_key)
else:
    st.error("Google API key not found.")

characteristics = [
    "Carbon Footprint",
    "Renewable Energy Usage",
    "Waste Management",
    "Biodiversity Preservation",
    "Water Conservation",
    "Air Quality",
    "Sustainable Agriculture",
    "Green Transportation",
    "Energy Efficiency",
    "Climate Resilience"
]

# CSS style for title, subtitles, and centered image
st.markdown("""
<style>
    .full-width-title {
        font-size: 50px;
        font-weight: bold;
        text-align: center;
        color: #333333;
        padding: 20px 0;
        margin: 0;
        width: 100%;
    }
    .subtitle {
        font-size: 24px;
        text-align: center;
        color: #333333;
        margin-top: -20px;
        padding-bottom: 20px;
    }
    div.stButton > button:first-child {
        background-color: #0066cc;
        color: white;
        font-size: 20px;
        font-weight: bold;
        padding: 14px 20px;
        border-radius: 10px;
        border: 2px solid #0066cc;
        transition: all 0.3s;
    }
    div.stButton > button:first-child:hover {
        background-color: #0052a3;
        border-color: #0052a3;
    }
    .full-width-section {
        padding: 20px;
        margin-top: 30px;
    }
    .centered-image {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 20px 0;
    }
    .centered-image img {
        max-width: 50%;
        height: auto;
    }
</style>
""", unsafe_allow_html=True)

# Full-width title
st.markdown('<p class="full-width-title">EcoTopia: The Green Game</p>', unsafe_allow_html=True)

# Subtitle
st.markdown('<p class="subtitle">Create your perfect sustainable society</p>', unsafe_allow_html=True)

# Function to analyze the society based on adjusted values
def analyze_society(values):
    average = sum(values.values()) / len(values)
    
    if average >= 7:
        analysis = "Highly Sustainable Utopia"
    elif average >= 4:
        analysis = "Moderately Sustainable Utopia"
    else:
        analysis = "Low Sustainability Utopia"
    
    return average, analysis

# Initialize the values dictionary
values = {characteristic: 5.0 for characteristic in characteristics}

# Split the screen into two equal columns
col1, col2 = st.columns(2)

# Create sliders for each characteristic in the left column
with col1:
    st.markdown('<p class="subtitle">Choose the characteristics</p>', unsafe_allow_html=True)
    for characteristic in characteristics:
        values[characteristic] = st.slider(characteristic, 0.0, 10.0, 5.0)

# Display the bar chart in the right column
with col2:
    st.markdown('<p class="subtitle">Characteristic Values</p>', unsafe_allow_html=True)
    
    # Create a DataFrame for the chart
    df = pd.DataFrame(list(values.items()), columns=['Characteristic', 'Value'])
    
    # Define a custom color palette
    color_palette = px.colors.qualitative.Prism

    # Create the bar chart using Plotly Express with different colors
    fig = px.bar(df, x='Characteristic', y='Value', 
                 labels={'Value': 'Score', 'Characteristic': ''},
                 height=400,
                 color='Characteristic',
                 color_discrete_sequence=color_palette)
    
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

# Analyze the society
average, analysis = analyze_society(values)

# Full-width analysis section
st.markdown('<div class="full-width-section">', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Analysis of your sustainable utopia</p>', unsafe_allow_html=True)
st.write(f"Average of Values: {average:.2f}")
st.write(f"Classification: {analysis}")

# Function to generate the image prompt
def generate_image_prompt(values):
    prompt_lines = [
        "Create an image that represents a sustainable utopian society with the following characteristics:",
        ", ".join([f"{key}: {value}" for key, value in values.items()]),
        "The prompt should have 3 lines of text."
    ]
    return "\n".join(prompt_lines)

# Function to get the API key securely
def get_google_api_key():
    return os.getenv("GOOGLE_API_KEY")

# Analysis using Google Generative AI and OpenAI DALL-E 3
if 'generated_image' not in st.session_state:
    st.session_state['generated_image'] = None
if 'analysis_text' not in st.session_state:
    st.session_state['analysis_text'] = None

generate_image = st.button("Analyze your society with Google Gemini-pro")
if generate_image:
    if not google_api_key or not client.api_key:
        st.error("API key(s) not found. Please configure the GOOGLE_API_KEY and OPENAI_API_KEY in the environment variables.")
        st.info("If you're running this locally, you can set the API keys in your system's environment variables.")
    else:
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            # Generate prompt for image
            image_prompt_input = generate_image_prompt(values)
            image_prompt_response = model.generate_content(image_prompt_input)
            image_prompt = image_prompt_response.text
            
            # Generate image with DALL-E 3
            try:
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=image_prompt,
                    n=1,
                )
                st.session_state['generated_image'] = response.data[0].url
            except Exception as e:
                st.error(f"Error generating image with DALL-E 3: {str(e)}")
            
            # Generate text analysis
            input_text = (
                f"Analyze the sustainable utopian society with the following characteristics: {values}. "
                "Write the analysis with subtitles and 5 paragraphs of text."
            )
            response = model.generate_content(input_text)
            st.session_state['analysis_text'] = response.text
        
        except Exception as e:
            st.error(f"Error calling the AI APIs: {str(e)}")

if st.session_state['generated_image']:
    st.subheader("Generated Image of Your Sustainable Utopia")
    st.image(st.session_state['generated_image'], caption="AI-generated representation of your utopia", use_column_width=True)

if st.session_state['analysis_text']:
    st.subheader("Analysis of your utopia by Google Gemini-pro")
    paragraphs = st.session_state['analysis_text'].split('\n\n')
    for paragraph in paragraphs:
        if ': ' in paragraph:
            subtitle, text = paragraph.split(': ', 1)
            st.markdown(f"**{subtitle}**")
            st.write(text)
        else:
            st.write(paragraph)

# Utopia vs Reality section
st.subheader("Utopia vs Reality")

if 'comparison_text' not in st.session_state:
    st.session_state['comparison_text'] = None

compare_utopia = st.button("Use Google Gemini-pro to compare your utopia with the indices of the best countries")
if compare_utopia:
    if not google_api_key:
        st.error("Google API key not found. Please configure the GOOGLE_API_KEY in the environment variables.")
        st.info("If you're running this locally, you can set the API key in your system's environment variables.")
    else:
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            comparison_prompt = (
                f"Compare the sustainable utopian society with these characteristics: {values}\n"
                "to the highest Human Development Index (HDI) of the following countries: "
                "Norway – 0.957, Switzerland and Ireland – 0.955, "
                "Hong Kong (China) and Iceland - 0.949, Germany – 0.947, "
                "Sweden – 0.945, Australia and Netherlands – 0.944, "
                "Denmark -0.940, Singapore and Finland – 0.938, "
                "New Zealand and Belgium – 0.931, Canada – 0.929, United States – 0.926. "
                "Write the comparison in exactly two paragraphs, each with 10 lines."
                "Always mention some of the countries on the list in the comparison."
            )
            
            comparison_response = model.generate_content(comparison_prompt)
            st.session_state['comparison_text'] = comparison_response.text
        
        except Exception as e:
            st.error(f"Error calling the Google Generative AI API: {str(e)}")

if st.session_state['comparison_text']:
    st.subheader("Comparison with Real-World Indices")
    paragraphs = st.session_state['comparison_text'].split('\n\n')
    if len(paragraphs) >= 2:
        st.write(paragraphs[0])
        st.write(paragraphs[1])
    else:
        st.write(st.session_state['comparison_text'])

st.markdown('</div>', unsafe_allow_html=True)

# Final notice
# Subtitle
st.markdown('<p class="subtitle">To generate a new utopia, change the characteristics above!</p>', unsafe_allow_html=True)
