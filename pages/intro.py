import streamlit as st

st.title('Intro')

with st.container(border=True):
    st.header('Purpose')
    st.text('People use body gestures when speaking, also called co-speech gestures.')
    st.text('Our purpose is to study the naturalness of different design of co-speech gestures, i.e., which gesture design is better in terms of naturalness and the appropriateness given the speech.')
    st.text('Your response will be considered when making co-speech gesture production systems for digital avatars or robots. We are grateful that you will provide your genuine opinion!')

    st.header('Task')
    st.text('You will compare 30 pairs of gestures, which are shown in 10-seconds videos. After watching the videos, you will answer questions regarding the gestures presented in the videos.')
    st.text('There are two types of videos: One is without audio, the other one has audio. The purpose of excluding the audio is to allow you to focus on the gesture movements itself, instead of being affected by the speech.')
    st.text('For the videos without audio, the question is: "Which of the gestures do you think is more natural in terms of human-likeness, smoothness and comfortableness?" For the videos with audio, the question is: "Which of the gestures do you think synchronize more with the spoken utterance?"')
    st.text('For both questions, you are given three options: "Left", "Equal" and "Right". "Left"/"Right" means you think the left/right one is better, whereas "Equal" means you think two gestures are similar, given the videos and the question.')
    st.text('It is recommended to focus on the overall impression, instead of specific details.')

    st.header('Interface')
    st.text('An example of the interface (not interactive) you will use is shown below.')
    st.text('- The videos are with audio, you can test your speaker by playing the videos.')
    st.text('- You can use zoom in/out of your browser if you find the window is too large/small.')
    st.text('- You will not be able to go back after submitted your response.')

    with st.container(border=True):
        st.header('(Example) Watch videos and answer the question')
        columns = st.columns(2, border=True)
        columns[0].subheader('Left')
        columns[0].video('https://wu-cloud-bucket.s3.ap-northeast-3.amazonaws.com/2025_ral_exp/groups/group_59/gt.mp4')
        columns[1].subheader('Right')
        columns[1].video('https://wu-cloud-bucket.s3.ap-northeast-3.amazonaws.com/2025_ral_exp/groups/group_59/cfm.mp4')

        # Add custom CSS for larger radio buttons
        st.markdown("""
        <style>
        div[data-testid="stRadio"] p {
            font-size: 1.2rem;
        }
        </style>
        """, unsafe_allow_html=True)
    
        choice = st.radio(
            label='Q: (With audio) Which of the gestures do you think synchronize more with the spoken utterance?',
            options=['Left', 'Equal', 'Right'],
            index=None,
            horizontal=True
        )
        st.button('Submit')

    st.header('Warning (Must Read)')
    st.warning(
        'We have included simple questions for checking your attention to ensure the responses are reasonable. However, it is so simple that you will not fail as long as you are not choosing randomly.'
    )

next_button = st.button(
    label="Proceed to the experiment"
)
if next_button:
    st.switch_page('pages/exp.py')