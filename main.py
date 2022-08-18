import streamlit as st
import requests
import os
import json
import pandas as pd
import plotly.express as px
from bokeh.models.widgets import Div

st.set_page_config(page_title="News Aggregator", page_icon="🗞",
                   layout="centered", initial_sidebar_state="collapsed")

# BASE_API = "http://localhost:8000"
BASE_API=os.environ['FAST_API_URL']

def user_open_news(func_section, func_url, func_uri):
    headers = {}
    headers['Authorization'] = f"Bearer {st.session_state['access_token']}"
    requests.request("POST", f"{BASE_API}/feeds/post_read_mins?user_section={func_section}", headers=headers)
    requests.request("POST", f"{BASE_API}/mongodb/mark_news_as_red?news_uid={func_uri}", headers=headers)
    js = f"window.open('{func_url}')"  # New tab or window
    html = '<img src onerror="{}">'.format(js)
    div = Div(text=html)
    st.bokeh_chart(div)
    return


def send_link_to_im(title, url):
    headers = {}
    headers['Authorization'] = f"Bearer {st.session_state['access_token']}"
    requests.request("POST", f"{BASE_API}/notify/send_link?news_title={title}&news_url={url}&mobile={st.session_state['mobile']}", headers=headers)
    return


def set_default_language(option):
    st.session_state['language'] = option
    st.experimental_rerun()


if 'if_logged' not in st.session_state:
    st.session_state['if_logged'] = False
    st.session_state['access_token'] = ''
    st.session_state['mobile'] = ''


if st.session_state['if_logged'] == True:
    logout_button = st.button(label='Logout', disabled=False)

    if logout_button:
        st.session_state['if_logged'] = False
        st.experimental_rerun()


if st.session_state['if_logged'] == False:
    st.markdown("""
                # Welcome to News Aggregator,
                ### Login or to Continue
                """)
    login_tab, signup_tab = st.tabs(["Login", "SignUp"])
    with login_tab:
        with st.form(key='login', clear_on_submit=True):
            username = st.text_input('Your Email ✉️')
            password = st.text_input("Your Password", type="password")
            submit = st.form_submit_button("Submit")
            if submit:
                with st.spinner('Sending ...'):
                    url = f"{BASE_API}/login"
                    payload = {'username': username, 'password': password}
                    try:
                        response = requests.request("POST", url, data=payload)
                    except:
                        st.error("Service Unavailable")
                    
                    if response.status_code == 200:
                        json_data = json.loads(response.text)
                        st.session_state['access_token'] = json_data["access_token"]
                        st.session_state['if_logged'] = True
                        st.session_state['user_name'] = username
                        st.session_state['mobile'] = json_data['mobile']
                        st.session_state['fullname'] = json_data['name']
                        st.text("Login Successful")
                        st.experimental_rerun()
                    else:
                        st.warning("Invalid Credentials ⚠️")
    with signup_tab:
        with st.form(key='signup', clear_on_submit=True):
            userfullname = st.text_input('Your Name')
            im_number = st.text_input('Your IM Number')
            username = st.text_input('Your Email ✉️')
            password = st.text_input("Your Password", type="password")
            user_interest = st.multiselect(
            "Select one or more interest",
            options = ['arts',
                        'automobiles',
                        'books',
                        'business',
                        'climate',
                        'education',
                        'fashion',
                        'food',
                        'health',
                        # 'job+market',
                        'science',
                        'sports',
                        'technology',
                        'travel',
                        # 'u.s.',
                        'universal',
                        'world'],
            default=['automobiles', 'science', 'education'] )
            submit = st.form_submit_button("Submit")
            if submit:
                with st.spinner('Sending ...'):
                    if im_number.isnumeric() and len(im_number) != 10:
                        st.warning("Invalid Number")
                    else:
                        url = f"{BASE_API}/user/create"
                        payload = json.dumps({
                                    "name": userfullname,
                                    "email": username,
                                    "password": password,
                                    "mobile": str(im_number),
                                    "interest": "|".join(user_interest)
                                })
                        response = requests.request("POST", url, data=payload)
                        if response.status_code == 200:
                            json_data = json.loads(response.text)
                            st.text("Registration Successful")
                        else:
                            st.text("Cannot Register User, Try Again Later")


if st.session_state['if_logged'] == True:
    st.markdown(f"""
    ### Hello {st.session_state['fullname'].split(' ')[0]}, Check out what's happening ..
    """)
    lang_option = st.selectbox(label="Set a default Language", options=("English", "Hindi", "Chinese"), index=0)
    st.markdown(f"""
    ---
    """)
    
    
    st.markdown(f"""
    #### Article Stats

    Find out what topic are most discussed most
    """)
    
    # Count of Article
    with st.container():
        with st.spinner('Analyzing ...'):
            url = f"{BASE_API}/mongodb/weekly"
            headers = {}
            headers['Authorization'] = f"Bearer {st.session_state['access_token']}"
            response = requests.request("GET", url, headers=headers)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                df = pd.read_json(json_data)
                fig = px.bar(df, 
                            x = df['_id'], 
                            y = df['count'],
                            hover_data=['count'],
                            color='count', 
                            title="Article Count",
                            labels={'count':'Count of Articles',
                                    '_id':'Article Section'
                                    },
                            text_auto=True
                            )
                st.plotly_chart(fig)
            else:
                st.error("Error response")
    
    # Read Articles
    with st.container():
        st.markdown(f"""
            ---
            #### Articles Read 
            """)
        with st.spinner('Fetching ...'):
            url = f"{BASE_API}/mongodb/read_articles"
            headers = {}
            headers['Authorization'] = f"Bearer {st.session_state['access_token']}"
            response = requests.request("GET", url, headers=headers)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                md_text = ""
                for element in json_data:
                    md_text = md_text + f"• {element['language'][lang_option.lower()]['title']} - [Link]({element['url']})" + "<br>"                
                st.markdown(md_text, unsafe_allow_html=True)
            else:
                st.error("Error response")
    
    # Top3 Artciles per Section
    with st.container():
        st.markdown(f"""
            ---
            #### Personalized News Feeds
            """)
        with st.spinner('Preparing Personalized Feed ...'):
            url = f"{BASE_API}/feeds/personalized_section"
            headers = {}
            headers['Authorization'] = f"Bearer {st.session_state['access_token']}"
            response = requests.request("GET", url, headers=headers)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                section_one = list(json_data)[0].upper()
                st.subheader(section_one)
                row1_col1, row1_col2, row1_col3 = st.columns(3)

                with row1_col1:
                    news_title11 = json_data[list(json_data)[0]][0]['language'][lang_option.lower()]['title']
                    st.subheader(news_title11)
                    try:
                        st.image(json_data[list(json_data)[0]][0]['thumbnail'])
                    except:
                        print("No thumbnail")
                    st.caption(json_data[list(json_data)[0]][0]['language'][lang_option.lower()]['summary'])
                    article_url11 = json_data[list(json_data)[0]][0]['url']
                    article_uri11 = json_data[list(json_data)[0]][0]['_id']
                    
                    st.button(label = "Open Article",key = "row1_col1_link", on_click = user_open_news, args = (section_one.lower(), article_url11, article_uri11) )
                    st.button(label = "Send IM",key = "row1_col1_wa", on_click = send_link_to_im, args = (news_title11, article_url11) )

                with row1_col2:
                    news_title12 = json_data[list(json_data)[0]][1]['language'][lang_option.lower()]['title']
                    st.subheader(news_title12)
                    try:
                        st.image(json_data[list(json_data)[0]][1]['thumbnail'])
                    except:
                        print("No thumbnail")
                    st.caption(json_data[list(json_data)[0]][1]['language'][lang_option.lower()]['summary'])
                    article_url12 = json_data[list(json_data)[0]][1]['url']
                    article_uri12 = json_data[list(json_data)[0]][1]['_id']
                    st.button(label = "Open Article",key = "row1_col2_link", on_click = user_open_news, args = (section_one.lower(), article_url12, article_uri12) )
                    st.button(label = "Send IM",key = "row1_col2_wa", on_click = send_link_to_im, args = (news_title12, article_url12) )

                with row1_col3:
                    news_title13 = json_data[list(json_data)[0]][2]['language'][lang_option.lower()]['title']
                    st.subheader(news_title13)
                    try:
                        st.image(json_data[list(json_data)[0]][2]['thumbnail'])
                    except:
                        print("No thumbnail")
                    st.caption(json_data[list(json_data)[0]][2]['language'][lang_option.lower()]['summary'])
                    article_url13 = json_data[list(json_data)[0]][2]['url']
                    article_uri13 = json_data[list(json_data)[0]][2]['_id']
                    st.button(label = "Open Article",key = "row1_col3_link", on_click = user_open_news, args = (section_one.lower(), article_url13, article_uri13) )
                    st.button(label = "Send IM",key = "row1_col3_wa", on_click = send_link_to_im, args = (news_title13, article_url13) )
                
                section_two = list(json_data)[1].upper()
                st.subheader(section_two)
                row2_col1, row2_col2, row2_col3 = st.columns(3)

                with row2_col1:
                    news_title21 = json_data[list(json_data)[1]][0]['language'][lang_option.lower()]['title']
                    st.subheader(news_title21)
                    try:
                        st.image(json_data[list(json_data)[1]][0]['thumbnail'])
                    except:
                        print("No thumbnail")
                    st.caption(json_data[list(json_data)[1]][0]['language'][lang_option.lower()]['summary'])
                    article_url21 = json_data[list(json_data)[1]][0]['url']
                    article_uri21 = json_data[list(json_data)[1]][0]['_id']
                    st.button(label = "Open Article",key = "row2_col1_link", on_click = user_open_news, args = (section_two.lower(), article_url21, article_uri21) )
                    st.button(label = "Send IM",key = "row2_col1_wa", on_click = send_link_to_im, args = (news_title21, article_url21) )
                    
                with row2_col2:
                    news_title22 = json_data[list(json_data)[1]][1]['language'][lang_option.lower()]['title']
                    st.subheader(news_title22)
                    try:
                        st.image(json_data[list(json_data)[1]][1]['thumbnail'])
                    except:
                        print("No thumbnail")
                    st.caption(json_data[list(json_data)[1]][1]['language'][lang_option.lower()]['summary'])
                    article_url22 = json_data[list(json_data)[1]][1]['url']
                    article_uri22 = json_data[list(json_data)[1]][1]['_id']
                    st.button(label = "Open Article",key = "row2_col2_link", on_click = user_open_news, args = (section_two.lower(), article_url22, article_uri22) )
                    st.button(label = "Send IM",key = "row2_col2_wa", on_click = send_link_to_im, args = (news_title22, article_url22) )

                with row2_col3:
                    news_title23 = json_data[list(json_data)[1]][2]['language'][lang_option.lower()]['title']
                    st.subheader(news_title23)
                    try:
                        st.image(json_data[list(json_data)[1]][2]['thumbnail'])
                    except:
                        print("No thumbnail")
                    st.caption(json_data[list(json_data)[1]][2]['language'][lang_option.lower()]['summary'])
                    article_url23 = json_data[list(json_data)[1]][2]['url']
                    article_uri23 = json_data[list(json_data)[1]][2]['_id']
                    st.button(label = "Open Article",key = "row2_col3_link", on_click = user_open_news, args = (section_two.lower(), article_url23, article_uri23) )
                    st.button(label = "Send IM",key = "row2_col3_wa", on_click = send_link_to_im, args = (news_title23, article_url23) )
                
                section_three = list(json_data)[2].upper()
                st.subheader(section_three)
                row3_col1, row3_col2, row3_col3 = st.columns(3)

                with row3_col1:
                    news_title31 = json_data[list(json_data)[2]][0]['language'][lang_option.lower()]['title']
                    st.subheader(news_title31)
                    try:
                        st.image(json_data[list(json_data)[2]][0]['thumbnail'])
                    except:
                        print("No thumbnail")
                    st.caption(json_data[list(json_data)[2]][0]['language'][lang_option.lower()]['summary'])
                    article_url31 = json_data[list(json_data)[2]][0]['url']
                    article_uri31 = json_data[list(json_data)[2]][0]['_id']
                    st.button(label = "Open Article",key = "row3_col1_link", on_click = user_open_news, args = (section_three.lower(), article_url31, article_uri31) )
                    st.button(label = "Send IM",key = "row3_col1_wa", on_click = send_link_to_im, args = (news_title31, article_url31) )
                    
                with row3_col2:
                    news_title32 = json_data[list(json_data)[2]][1]['language'][lang_option.lower()]['title']
                    st.subheader(news_title32)
                    # st.subheader(news_title31)
                    try:
                        st.image(json_data[list(json_data)[2]][1]['thumbnail'])
                    except:
                        print("No thumbnail")
                    st.caption(json_data[list(json_data)[2]][1]['language'][lang_option.lower()]['summary'])
                    article_url32 = json_data[list(json_data)[2]][1]['url']
                    article_uri32 = json_data[list(json_data)[2]][1]['_id']
                    st.button(label = "Open Article",key = "row3_col2_link", on_click = user_open_news, args = (section_three.lower(), article_url32, article_uri32) )
                    st.button(label = "Send IM",key = "row3_col2_wa", on_click = send_link_to_im, args = (news_title32, article_url32) )

                with row3_col3:
                    news_title33 = json_data[list(json_data)[2]][2]['language'][lang_option.lower()]['title']
                    st.subheader(news_title33)
                    # st.subheader(news_title31)
                    try:
                        st.image(json_data[list(json_data)[2]][2]['thumbnail'])
                    except:
                        print("No thumbnail")
                    st.caption(json_data[list(json_data)[2]][2]['language'][lang_option.lower()]['summary'])
                    article_url33 = json_data[list(json_data)[2]][2]['url']
                    article_uri33 = json_data[list(json_data)[2]][2]['_id']
                    st.button(label = "Open Article",key = "row3_col3_link", on_click = user_open_news, args = (section_three.lower(), article_url33, article_uri33) )
                    st.button(label = "Send IM",key = "row3_col3_wa", on_click = send_link_to_im, args = (news_title33, article_url33) )

            else:
                st.error("Cannot fetch personalized feed")
    
    # Other Section News
    with st.container():
        st.markdown(f"""
            ---
            #### News from other sections
            """)
        with st.spinner('Preparing Other Section Feed ...'):
            url = f"{BASE_API}/feeds/other_section_news"
            headers = {}
            headers['Authorization'] = f"Bearer {st.session_state['access_token']}"
            response = requests.request("GET", url, headers=headers)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                row4_col1, row4_col2, row4_col3 = st.columns(3)

                with row4_col1:
                    section_one = list(json_data)[0].upper()
                    st.subheader(section_one)
                    news_title41 = json_data[list(json_data)[0]][0]['language'][lang_option.lower()]['title']
                    st.subheader(news_title41)
                    try:
                        st.image(json_data[list(json_data)[0]][0]['thumbnail'])
                    except:
                        print("No thumbnail")
                    st.caption(json_data[list(json_data)[0]][0]['language'][lang_option.lower()]['summary'])
                    article_url41 = json_data[list(json_data)[0]][0]['url']
                    article_uri41 = json_data[list(json_data)[0]][0]['_id']
                    
                    st.button(label = "Open Article",key = "row4_col1_link", on_click = user_open_news, args = (section_one.lower(), article_url41, article_uri41) )
                    st.button(label = "Send IM",key = "row1_col4_wa", on_click = send_link_to_im, args = (news_title41, article_url41) )

                
                
                with row4_col2:
                    section_two = list(json_data)[1].upper()
                    st.subheader(section_two)
                    news_title42 = json_data[list(json_data)[1]][0]['language'][lang_option.lower()]['title']
                    st.subheader(news_title42)
                    try:
                        st.image(json_data[list(json_data)[1]][0]['thumbnail'])
                    except:
                        print("No thumbnail")
                    st.caption(json_data[list(json_data)[1]][0]['language'][lang_option.lower()]['summary'])
                    article_url42 = json_data[list(json_data)[1]][0]['url']
                    article_uri42 = json_data[list(json_data)[1]][0]['_id']
                    st.button(label = "Open Article",key = "row4_col2_link", on_click = user_open_news, args = (section_two.lower(), article_url42, article_uri42) )
                    st.button(label = "Send IM",key = "row4_col2_wa", on_click = send_link_to_im, args = (news_title42, article_url42) )

                with row4_col3:
                    section_three = list(json_data)[2].upper()
                    st.subheader(section_three)
                    news_title43 = json_data[list(json_data)[2]][0]['language'][lang_option.lower()]['title']
                    st.subheader(news_title43)
                    try:
                        st.image(json_data[list(json_data)[2]][0]['thumbnail'])
                    except:
                        print("No thumbnail")
                    st.caption(json_data[list(json_data)[2]][2]['language'][lang_option.lower()]['summary'])
                    article_url43 = json_data[list(json_data)[2]][0]['url']
                    article_uri43 = json_data[list(json_data)[2]][0]['_id']
                    st.button(label = "Open Article",key = "row4_col3_link", on_click = user_open_news, args = (section_three.lower(), article_url43, article_uri43) )
                    st.button(label = "Send IM",key = "row4_col3_wa", on_click = send_link_to_im, args = (news_title43, article_url43) )
            else:
                st.error("Cannot fetch other section feed")