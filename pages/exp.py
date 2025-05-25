import streamlit as st
from streamlit_gsheets import GSheetsConnection
import numpy as np
np.random.seed(1234)

baselines = ['gt', 'emage', 'lsm', 'mamba', 'cfm_inpainting']
models = ['gt', 'cfm', 'emage', 'lsm', 'mamba']

def get_video_url(row, name=''):
    group_id = int(row['group_id'])
    video_url = f'https://wu-cloud-bucket.s3.ap-northeast-3.amazonaws.com/2025_ral_exp/groups/group_{group_id}/{name}.mp4'
    return video_url

# Assign variables
if 'sheet_rows' not in st.session_state:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="1s")
    st.session_state['df'] = df
    st.session_state['sheet_rows'] = []
    st.session_state['conn'] = conn
    for _, row in df.iterrows():
        if not row['done']:
            st.session_state['sheet_rows'].append(row.to_dict())
        if len(st.session_state['sheet_rows']) == 3:
            break
if 'pairs' not in st.session_state:
    pairs = []
    for row in st.session_state['sheet_rows']:
        # Section A
        sub_pairs = []
        for baseline in baselines:
            sub_pairs.append({
                'group_id': row['group_id'],
                'section': 'A',
                'tgt_video_url': get_video_url(row, 'cfm_0'),
                'ref': baseline,
                'ref_video_url': get_video_url(row, baseline + '_0'),
                'swap': np.random.rand() >= 0.5
            })
        np.random.shuffle(sub_pairs)
        pairs.extend(sub_pairs)
        # Section B
        sub_pairs = []
        for model in models:
            sub_pairs.append({
                'group_id': row['group_id'],
                'section': 'B',
                'tgt_video_url': get_video_url(row, model),
                'ref': model,
                'ref_video_url': get_video_url(row, model + '_1'),
                'swap': np.random.rand() >= 0.5
            })
        np.random.shuffle(sub_pairs)
        pairs.extend(sub_pairs)
    st.session_state['pairs'] = pairs
if 'pair_idx' not in st.session_state:
    st.session_state['pair_idx'] = 0
if 'results' not in st.session_state:
    st.session_state['results'] = []

def on_form_submitted():
    # Record choice
    pair = st.session_state['pairs'][st.session_state['pair_idx']]
    choice = st.session_state[f'choice_{st.session_state["pair_idx"]}']
    if choice == 'Left':
        value = 0
    elif choice == 'Equal':
        value = 1
    else:
        value = 2
    if pair['swap']:
        if value == 0: value = 2
        elif value == 2: value = 0
    result = {
        'group_id': pair['group_id'],
        'section': pair['section'],
        'ref': pair['ref'],
        'value': value
    }
    st.session_state['results'].append(result)

    # Update pair
    st.session_state['pair_idx'] += 1

num_pairs = len(st.session_state['pairs'])
pair_idx = 0

# Interface
st.title('Experiment')
pbar_text = 'Progress'
pbar = st.progress(0, text=f'{pbar_text}: {0}/{num_pairs}')

@st.fragment
def exp_fragment():
    # Check if all completed
    if st.session_state['pair_idx'] == num_pairs:
        st.switch_page('pages/outro.py')

    # st.write(f'Pair idx: {st.session_state["pair_idx"]+1}/{num_pairs}')

    # Get pair info
    pair = st.session_state['pairs'][st.session_state['pair_idx']]
    # st.write(f'group_id: {pair["group_id"]}')
    left_video_url = pair['tgt_video_url']
    right_video_url = pair['ref_video_url']
    if pair['swap']:
        left_video_url, right_video_url = right_video_url, left_video_url
    section = pair['section']
    if section == 'A':
        question = '(No audio) Which of the gestures do you think is more natural in terms of human-likeness, smoothness and comfortablenss? '
    elif section == 'B':
        question = '(With audio) Which of the gestures do you think synchronize more with the spoken utterance?'
    else:
        raise ValueError('Unsupported section')

    # Place two videos
    with st.container(border=True):
        st.header('Watch videos and answer the question')
        columns = st.columns(2, border=True)
        columns[0].subheader('Left')
        columns[0].video(left_video_url)
        columns[1].subheader('Right')
        columns[1].video(right_video_url)

        # Add custom CSS for larger radio buttons
        st.markdown("""
        <style>
        div[data-testid="stRadio"] p {
            font-size: 1.2rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        choice = st.radio(
            label=f'Q: {question}',
            options=['Left', 'Equal', 'Right'],
            index=None,
            key=f'choice_{st.session_state["pair_idx"]}',
            horizontal=True
        )
        st.button(
            'Submit',
            on_click=on_form_submitted,
            disabled=choice==None
        )

    pbar.progress(st.session_state['pair_idx']/num_pairs, f'{pbar_text}: {st.session_state["pair_idx"]}/{num_pairs}')

exp_fragment()
