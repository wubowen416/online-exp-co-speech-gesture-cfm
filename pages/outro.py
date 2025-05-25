import streamlit as st
import datetime

st.title('Outro')

if 'uploaded' not in st.session_state:
    st.session_state['uploaded'] = False

if not st.session_state['uploaded']:
    st.warning('Do not close the tab! Data is uploading!')
    # Modify df
    df = st.session_state['df']
    for result in st.session_state['results']:
        rows = df['group_id'] == result['group_id']
        df.loc[rows, f'{result["section"]}-{result["ref"]}'] = result['value']
        df.loc[rows, 'done'] = 1
        df.loc[rows, 'userid'] = str(st.session_state['userid'])
        df.loc[rows, 'gender'] = st.session_state['gender']
        df.loc[rows, 'age'] = st.session_state['age']
        df.loc[rows, 'start_time'] = st.session_state['start_time']
        df.loc[rows, 'end_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Write df to google sheet
    conn = st.session_state['conn']
    conn.update(data=df)
    st.session_state['uploaded'] = True
    st.rerun()
else:
    st.info('Your response has been recorded.')
    st.text('Thank you for taking part in our experiment!')
    st.text('You can now close the tab.')
