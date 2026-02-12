import streamlit as st

# Other code...

if condition:
    # Some code...
else:
    col_left, col_right = st.columns(2)
    # The following lines should be indented:
    result_left = col_left.some_function()
    result_right = col_right.some_other_function()
    # More indented code...

# More code...