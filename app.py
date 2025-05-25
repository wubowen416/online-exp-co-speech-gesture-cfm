import streamlit as st
import datetime

st.title('Welcome')

if 'agree' not in st.session_state:
    st.session_state['agree'] = False

if not st.session_state['agree']:
    with st.container(border=True):
        st.header('Consent Form')
        st.text(
            'In our experiment, we will collect some of your personal information, i.e., gender and age. These data will not be used for purpose other than data analysis.'
        )
        st.text(
            'By clicking on "Agree" button below, you understand and agree to the above statement. If you do not agree, please exit the experiment.'
        )
        if st.button(label='Agree'):
            st.session_state['agree'] = True
            st.rerun()
else:
    with st.container(border=True):
        userid = st.text_input(
            label='User ID',
            placeholder='Input your user ID'
        )
        userid_reinput = st.text_input(
            label='Confirm your user ID',
            placeholder='Input your user ID'
        )
        gender = st.radio(
            label='Gender',
            options=['Male', 'Female', 'Others'],
            horizontal=True,
            index=None
        )
        age = st.radio(
            label='Age',
            options=['~20', '21~30', '31~40', '41~50', '50~'],
            horizontal=True,
            index=None
        )

        if st.button(
            label='Submit',
            disabled=userid is None or gender is None or age is None
        ):
            if userid_reinput != userid:
                st.warning('Two times input of user ID is not the same. Check your user ID!')
            else:
                st.session_state['userid'] = userid
                st.session_state['gender'] = gender
                st.session_state['age'] = age
                st.session_state['start_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                st.switch_page('pages/intro.py')
