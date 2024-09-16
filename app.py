import base64
import json
from datetime import datetime

import pdfplumber
import streamlit as st
from deep_translator import GoogleTranslator
from fpdf import FPDF
from gtts import gTTS

base_dir = "./data/"

# st.title(f"Translate pdf document to english")
__header = '<h1 style="text-align: center;">Translate pdf document to english</h1>'

st.markdown(__header, unsafe_allow_html=True)


_description = (f"The app parse the document, translate the pdf\n"
        f" from any language and provides the text file for download\n"
        f" along with the audio file.")

__description = f'<div style="text-align: center;">{_description}</div>'

st.markdown(__description, unsafe_allow_html=True)

# style = "<style>h2 The app parse the document, translate the pdf\n {text-align: center;}</style>"
# st.markdown(style, unsafe_allow_html=True)


def generate_pdf(language):
    pdf_data = None
    try:
        pdf = FPDF()

        # Set font (Font, style, size)
        pdf.set_font("Arial", size=12)

        # Loop through the list of texts and add each to a new page
        for text in language:
            pdf.add_page()  # Add a new page for each text
            pdf.multi_cell(0, 10, text)  # Add the text to the page

        # Save the PDF file
        pdf.output("generated_list_texts.pdf")
        with open(f"generated_list_texts.pdf", "w", encoding='utf-8') as ff:
            pdf_data = ff.read().encode(..., 'ignore')

        print("PDF created successfully!")
    except Exception as e:
        st.error(f"Exception while generating pdf: {e}")

    return pdf_data


def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )


def convert_time(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)


def generate_audio(language):

    myobj = gTTS(text="\n\n\n".join(language), lang='en', slow=False)

    # Saving the converted audio in a mp3 file named
    myobj.save(f"{base_dir}local_audio.mp3")


uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    # st.write(bytes_data)
    filename = f"{base_dir}sample.pdf"
    filedata = None

    with open(f"{filename}", "wb") as ff:
        ff.write(bytes_data)

    start = datetime.now()

    full_text = []

    with pdfplumber.open(filename) as pdf:
        # Extract text from each page
        for page in pdf.pages:
            full_text.append(page.extract_text())

    st.write(f"Pdf contains {len(full_text)} pages.")

    with open(f"{filename}_list.txt", "w") as ff:
        json.dump(full_text, ff)

    language = []
    count = 0

    for text in full_text:
        _language = GoogleTranslator(source='auto', target='en').translate(
            text)  # output -> Weiter so, du bist großartig
        count += 1
        language.append(_language)

    with open(f"{filename}_translate.txt", "w") as ff:
        json.dump(language, ff)

    text_data = None
    with open(f"{filename}_translate.txt", "rb") as ff:
        text_data = ff.read()

    st.download_button(
        label="Download data as TXT",
        data=text_data,
        file_name=f"{filename}_translate.txt",
        mime="text/txt"
    )

    # pdf_data = generate_pdf(language)

    # st.download_button(
    #     label="Download data as PDF",
    #     data=pdf_data,
    #     file_name="large_df.pdf",
    #     mime="text/pdf"
    # )
    st.info(f"Generating Audio file")
    generate_audio(language)

    st.info("### Auto-playing Audio!")
    autoplay_audio(f"{base_dir}local_audio.mp3")


    end = datetime.now()

    difference = end - start

    seconds = difference.total_seconds()
    time_taken = convert_time(seconds)
    st.write(f"Total time taken: {time_taken}")
