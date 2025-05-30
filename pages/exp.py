import streamlit as st
import time
import datetime
import gspread
import numpy as np

def claim_row_atomically(worksheet, row_idx_to_claim):
    """
    Attempts to claim a row by atomically changing column B from '0' to claim_value.
    Returns True if successful, False otherwise.
    """
    try:
        find_replace_request = {
            'findReplace': {
                'find': '0',  # Value indicating 'available'
                'replacement': '1', # Value indicating 'claimed by this user'
                'matchCase': True,
                'matchEntireCell': True,
                'range': {
                    'sheetId': worksheet.id,
                    'startRowIndex': row_idx_to_claim - 1,  # API is 0-indexed
                    'endRowIndex': row_idx_to_claim,
                    'startColumnIndex': 1,  # Assuming status is in Column B (0-indexed B is 1)
                    'endColumnIndex': 2,
                }
            }
        }
        body = {'requests': [find_replace_request]}
        response = worksheet.spreadsheet.batch_update(body)
        
        # Check if the replacement was made
        # The exact structure of response['replies'] might need verification
        if response['replies'] and response['replies'][0].get('findReplace'):
            occurrences_changed = response['replies'][0]['findReplace'].get('occurrencesChanged', 0)
            return occurrences_changed > 0
        return False
    except Exception as e:
        st.error(f"Error during atomic claim for row {row_idx_to_claim}: {e}")
        return False

# Retrieve data
if 'sheet_rows' not in st.session_state:
    st.warning('Retrieving data. Please wait...')
    try:
        credentials = st.secrets['connections']['gsheets']
        gc = gspread.service_account_from_dict(info=credentials)
        sh = gc.open_by_url(credentials['spreadsheet'])
        worksheet = sh.get_worksheet(0)
        st.session_state['worksheet'] = worksheet
    except Exception as e:
        st.error(f'Error connecting to Google Sheets: {e}')
        st.error('Attempting rerunning in 3 seconds...')
        time.sleep(3.0)
        st.rerun()

    columns = worksheet.row_values(1)
    st.session_state['columns'] = columns
    sheet_rows = []
    status_list = worksheet.col_values(2)[1:]
    batch_cells = []
    for idx, status in enumerate(status_list):
        if len(sheet_rows) == 3: # Each experiment contains N groups
            break
        if status != '0':
            continue
        row_idx = idx + 2
        status_label = f'B{row_idx}'
        if worksheet.acell(status_label).value != '0':
            continue
        
        if claim_row_atomically(worksheet, row_idx):
            batch_cells.append({'range': f'AG{row_idx}', 'values': [[datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]]})
            batch_cells.append({'range': f'AD{row_idx}', 'values': [[st.session_state['userid']]]})
            batch_cells.append({'range': f'AE{row_idx}', 'values': [[st.session_state['gender']]]})
            batch_cells.append({'range': f'AF{row_idx}', 'values': [[st.session_state['age']]]})
            row = worksheet.row_values(row_idx)
            sheet_rows.append({k:v for k, v in zip(columns, row)})

        time.sleep(0.1)
        
    worksheet.batch_update(batch_cells)
    st.session_state['sheet_rows'] = sheet_rows
    st.rerun()

np.random.seed(1234)
baselines = ['gt', 'emage', 'lsm', 'mamba', 'cfm_inpainting']
models = ['gt', 'cfm', 'emage', 'lsm', 'mamba']

def get_video_url(row, name=''):
    group_id = int(row['group_id'])
    video_url = f'https://wu-cloud-bucket.s3.ap-northeast-3.amazonaws.com/2025_ral_exp/groups/group_{group_id}/{name}.mp4'
    return video_url

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
    st.session_state['dummy_video_postfix'] = int(time.time())

num_pairs = len(st.session_state['pairs'])
pair_idx = 0
# A random identifier to prevent video from continue playing if the urls are the same
if 'dummy_video_postfix' not in st.session_state:
    st.session_state['dummy_video_postfix'] = int(time.time())

# Interface
st.title('Experiment')
st.warning('Do not refresh the page or close the tab! Your data will be lost!')
pbar_text = 'Progress'
pbar = st.progress(0, text=f'{pbar_text}: {0}/{num_pairs}')

@st.fragment
def exp_fragment():
    # Check if all completed
    if st.session_state['pair_idx'] == num_pairs:
        st.switch_page('pages/comment.py')

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
        question = 'Which of the two gestures appears more natural in terms of human-likeness, smoothness, and comfortableness?'
        including_audio = '(no audio)'
    elif section == 'B':
        question = 'Which of the two gestures corresponds better with the spoken utterance?'
        including_audio = '(with audio)'
    else:
        raise ValueError('Unsupported section')

    # Place two videos
    with st.container(border=True):
        
        st.header(f'Watch videos {including_audio} and answer:')
        st.subheader(question)
        columns = st.columns(2, border=True)
        columns[0].subheader('Left')
        columns[0].video(f'{left_video_url}?t={st.session_state["dummy_video_postfix"]}')
        columns[1].subheader('Right')
        columns[1].video(f'{right_video_url}?t={st.session_state["dummy_video_postfix"]}')
        
        choice = st.radio(
            label='Select your preference for the above question:',
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
