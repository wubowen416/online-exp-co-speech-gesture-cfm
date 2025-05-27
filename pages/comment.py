import streamlit as st

st.title('Comment')

comment = st.text_area(
    label='Comment',
    placeholder='Input any comment if you have'
)

if st.button(
    label='Submit'
):
    st.session_state['comment'] = comment
    st.switch_page('pages/outro.py')