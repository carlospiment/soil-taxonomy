"""Small record forms. Persistent models are independent of widget lifetimes."""
import math
import streamlit as st


def _sync(key, value):
    if key in st.session_state and st.session_state[key] != value:
        del st.session_state[key]


def field(record, name, key, *, label=None, options=None, numeric=False,
          minimum=0.0, maximum=None, help=None, multiline=False, changed=None):
    value = record.get(name)
    label = label or name
    if numeric:
        value = float(value) if value is not None and isinstance(value, (int, float)) and math.isfinite(value) else None
        # Keep imported out-of-range observations editable instead of clamping them.
        low = min(minimum, value) if minimum is not None and value is not None else minimum
        high = max(maximum, value) if maximum is not None and value is not None else maximum
    elif options is None:
        value = '' if value is None else str(value)
    _sync(key, value)
    def commit():
        record[name] = st.session_state[key]
        if changed:
            changed()
    args = dict(key=key, help=help, on_change=commit)
    if numeric:
        result = st.number_input(label, value=value, min_value=low, max_value=high, **args)
        if result is not None and ((minimum is not None and result < minimum) or (maximum is not None and result > maximum)):
            st.error(f'{label}: revisa el valor importado; intervalo permitido {minimum}–{maximum}.')
    elif options is not None:
        choices = [None] + [v for v in options if v is not None]
        if value == '':
            value = None
        if value not in choices:
            choices.append(value)
        result = st.selectbox(label, choices, index=choices.index(value), format_func=lambda v: 'No evaluado' if v is None else str(v), **args)
    else:
        result = (st.text_area if multiline else st.text_input)(label, value=value, **args)
    # Do not create null/empty entries merely by displaying a field.
    if name in record or result not in (None, ''):
        record[name] = result
    return result


def interval(record, key, depth=None):
    left, right = st.columns(2)
    with left:
        top = field(record, 'Techo (cm)', key + '_top', numeric=True)
    with right:
        bottom = field(record, 'Base (cm)', key + '_bottom', numeric=True)
    if top is not None and bottom is not None:
        if bottom <= top:
            st.error('La base debe ser mayor que el techo.')
        else:
            st.caption(f'Espesor del intervalo: {bottom-top:g} cm.')
        if depth is not None and bottom > depth:
            st.error('El intervalo supera la profundidad observada del perfil.')
    return top, bottom


def choose_record(rows, key, label, describe):
    options = list(range(len(rows)))
    if st.session_state.get(key) not in options:
        st.session_state.pop(key, None)
    return st.selectbox(label, options, format_func=lambda i: f'{i+1}. {describe(rows[i])}', key=key)
