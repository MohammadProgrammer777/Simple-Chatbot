import streamlit as st
from bot.bot import Chat

# Style of the app
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cascadia+Code:ital,wght@0,200..700;1,200..700&family=Lalezar&display=swap');
        p, textarea, input, label, h1, h2, h3, h4, h5, h6, span, a, button, li {
            direction: RTL;
            text-align: right;
            font-family: "Lalezar";
        }
        div {
            font-family: "Lalezar";
        }
        h1 {
            font-family: "Lalezar";
        }
        h2 {
            font-family: "Lalezar";
        }
        .stSelectbox {
            width: 170px;
        }
    </style>
""", unsafe_allow_html=True)

# App parameters
if 'chats' not in st.session_state:
    st.session_state.chats = [Chat(name='چت 1', chatbot='deepseek-chat', temperature=.6)]
if 'current_chat_idx' not in st.session_state:
    st.session_state.current_chat_idx = 0
if 'was_summerized' not in st.session_state:
    st.session_state.was_summerized = [False]
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = 'deepseek-chat'

# Selecting chatbot
def select_chatbot(chatbot_name):
    model_map = {
        'Deepseek': 'deepseek-chat',
        'ChatGPT 4.1': 'gpt-4.1',
        'ChatGPT 4.1 mini': 'gpt-4.1-mini',
        'ChatGPT 4O': 'gpt-4o',
        'Gemini 2.5 Flash': 'gemini-2.5-flash',
    }
    reverse_model_map = {v: k for k, v in model_map.items()}

    if chatbot_name in model_map:
        return model_map[chatbot_name]
    elif chatbot_name in reverse_model_map:
        return reverse_model_map[chatbot_name]
    else:
        return 'deepseek-chat'

# Add new chat
def add_new_chat():
    chatbot = st.session_state.chatbot
    new_chat_name = f'چت {len(st.session_state.chats) + 1}'
    new_chat = Chat(name=new_chat_name, chatbot=chatbot, temperature=.9)
    st.session_state.chats.append(new_chat)
    st.session_state.current_chat_idx = len(st.session_state.chats) - 1
    st.session_state.was_summerized.append(False)

# Summerize chat for chat name
def chat_summarizer(chat, minimum_prompts):
    summerizer = Chat(name='خلاصه ساز چت های قبلی', chatbot=chat.chatbot, temperature=.65)
    first_prompts = chat.get_chat_history().get('Human')

    if len(first_prompts) >= minimum_prompts:
        prompts_to_summerize = first_prompts[:minimum_prompts]
    else:
        return False, None

    if first_prompts:
        while True:
            chats_name = [c.name for c in st.session_state.chats]
            chat_summery = summerizer.ask_question(
                question=f'لیست چند پیام اول که یکی از کاربران با تو چت کرده را به صورت یک لیست پایتون به تو میدهم.\nباید آنها را بخوانی و در خروجی فقط یک عبارت نهایتا 6 کلمه ای فارسی بگو که خلاصه و یا تیتر آن چت باشد.\n{prompts_to_summerize}'
            )
            if chat_summery not in chats_name:
                break

        return True, chat_summery

    return False, chat.name

# Showing messages in page
def show_messages_ui():
    if len(st.session_state.chats) != 0:
        chat_obj = st.session_state.chats[st.session_state.current_chat_idx]
        chat_history = chat_obj.get_chat_history()
        human_messages = chat_history.get('Human')
        ai_messages = chat_history.get('AI')

        # Temperature

        # Summerize the chat
        if not st.session_state.was_summerized[st.session_state.current_chat_idx] and len(chat_obj.get_chat_history().get('Human')) == 3:
            summery = chat_summarizer(chat_obj, minimum_prompts=3)

            if summery[0]:
                chat_summery = summery[1]
                chat_obj.name = chat_summery
                st.session_state.was_summerized[st.session_state.current_chat_idx] = True

        for message_idx in range(len(human_messages)):
            # Preparing messages
            human_msg = human_messages[message_idx]
            ai_msg = ai_messages[message_idx]

            # Printing messages in ui
            st.chat_message('user').write(human_msg)
            st.chat_message('assistant').write(ai_msg)

# Sidebar view
def sidebar():
    chats_name = [c.name for c in st.session_state.chats]

    with st.sidebar:
        st.header('لیست چت‌ها')

        selected_chat_name = st.radio(
            '',
            chats_name,
            index=st.session_state.current_chat_idx,
            key="chat_selector"
        )

        for i, chat in enumerate(st.session_state.chats):
            if chat.name == selected_chat_name:
                if st.session_state.current_chat_idx != i:
                    st.session_state.current_chat_idx = i
                    st.rerun()
                break

        st.button('چت جدید', on_click=add_new_chat, key="new_chat_button")

        model_options_display = ['Deepseek', 'ChatGPT 4O', 'ChatGPT 4.1', 'ChatGPT 4.1 mini', 'Gemini 2.5 Flash']

        try:
            current_model_display_name = select_chatbot(st.session_state.chatbot)
            default_index = model_options_display.index(current_model_display_name)
        except ValueError:
            default_index = 0

        selected_model_display_name = st.selectbox(
            'انتخاب مدل',
            options=model_options_display,
            index=default_index,
            key="model_selector"
        )
        if st.session_state.chatbot != select_chatbot(selected_model_display_name):
            st.session_state.chatbot = select_chatbot(selected_model_display_name)
            st.rerun()

# Send prompt
def send_prompt(p):
    response = ''
    chat = st.session_state.chats[st.session_state.current_chat_idx]

    try:
        response = chat.ask_question(p)
    except Exception as e:
        print(e)

# Create ui
st.set_page_config(
    page_title='چرخ‌یار شخصی',
    page_icon='🤖',
    layout='centered',
)

sidebar()

col1, col2, col3 = st.columns([1, 2, 1], vertical_alignment='center')
current_chat = st.session_state.chats[st.session_state.current_chat_idx]
with col1:
    st.header('دستیار')
    st.subheader(select_chatbot(current_chat.chatbot) if current_chat.chatbot.lower() == current_chat.chatbot else current_chat.chatbot)

with col3:
    st.header(current_chat.name)

show_messages_ui()

prompt = st.chat_input('هر چه می‌خواهد دل تنگت بگو...')
if prompt:
    send_prompt(prompt)
    st.rerun()