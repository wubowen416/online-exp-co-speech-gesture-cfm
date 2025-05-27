import gspread.utils
import streamlit as st
import datetime
import gspread

st.title('Outro')

if 'uploaded' not in st.session_state:
    st.session_state['uploaded'] = False

if not st.session_state['uploaded']:
    st.warning('Do not close the tab! Data is uploading!')
    # Write to worksheet
    worksheet: gspread.Worksheet = st.session_state['worksheet']
    columns: list = st.session_state['columns']
    batch_cells = []
    for result in st.session_state['results']:
        row_idx = int(result['group_id']) + 2
        col_name = f'{result["section"]}-{result["ref"]}'
        col_idx = columns.index(col_name) + 1
        batch_cells.append({'range': gspread.utils.rowcol_to_a1(row_idx, col_idx), 'values': [[result['value']]]})
        batch_cells.append({'range': f'B{row_idx}', 'values': [['2']]})
        batch_cells.append({'range': f'AH{row_idx}', 'values': [[datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]]})
        batch_cells.append({'range': f'AI{row_idx}', 'values': [[st.session_state['comment']]]})
    worksheet.batch_update(batch_cells)
    st.session_state['uploaded'] = True
    st.rerun()
else:
    st.info('Your response has been recorded.')
    st.text('Thank you for taking part in our experiment!')
    st.text('You can now close the tab.')
