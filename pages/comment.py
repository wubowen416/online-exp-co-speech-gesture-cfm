import streamlit as st

st.title('Comment')
st.warning('Do not refresh the page or close the tab! Your data will be lost!')

comment = st.text_area(
    label='Comment',
    placeholder='Input any comment if you have'
)

if st.button(
    label='Submit'
):
    st.session_state['comment'] = comment
    st.switch_page('pages/outro.py')