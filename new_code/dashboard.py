import streamlit as st
from streamlit_option_menu import option_menu
import yaml
import os

st.set_page_config(
    page_title="Welcome to AIPress!",
    page_icon="✡️",
)

def on_change(key):
    selection = st.session_state[key]

with st.sidebar:
    selected5 = option_menu(None,["Welcome","News Drafting", "News Polishing", 'Simulation', "Upload"],
                        icons=['house','feather', "slash-square", 'people', 'file-earmark-arrow-up'],
                        on_change=on_change, key='menu_5')

if selected5 == "Welcome":
    st.write("# Welcome to NewsAgent!")

    str_1 = """
    This demo relies on ChatGPT and GPT-3.5 from OpenAI.\n
    It needs a valid OpenAI API key to show its magic.\n
    Follow the instructions and see how it help to writing press release!
    """

    str_2 = """
    Please enter your OpenAI API Key:\n
    (we will only use it for this demo)
    """

    str_3 = """
    You can try **generate a press release**, **polishing your press release** and **Comment Simulation** by clicking the corresponding pages 👈on the side bar.
    """

    str_4="""
    Please enter your Tavily API Key:\n
    (we will only use it for this demo)
    """

    str_5="""
    Now enter your Tavily API Key below:\n"""

    st.markdown(str_1)

    st.write("## Enter OpenAI API Key")
    st.markdown(str_2)
    API_key = st.text_input("OpenAI API Key", placeholder = "sk-xxxxxx")

    if st.button("Submit OpenAI API Key"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(current_dir, '..', 'config')
        config_file_path = os.path.join(config_dir, 'config2.yaml')

        with open(config_file_path, 'r') as file:
            config = yaml.safe_load(file)

        config['llm']['api_key'] = API_key
        config['embedding']['api_key'] = API_key

        with open(config_file_path, 'w') as file:
            yaml.dump(config, file)

        news_collection_sl_path = os.path.join(current_dir, 'news_collection_sl.py')
        with open(news_collection_sl_path, 'r') as file:
            content = file.readlines()

        for i, line in enumerate(content):
            if 'OPENAI_API_KEY' in line and "=" in line:
                content[i] = f'os.environ["OPENAI_API_KEY"] = "{API_key}"\n'

        with open(news_collection_sl_path, 'w') as file:
            file.writelines(content)

        fact_collection_sl_path = os.path.join(current_dir, 'fact_collection_sl.py')
        with open(fact_collection_sl_path, 'r') as file:
            content = file.readlines()

        for i, line in enumerate(content):
            if 'OPENAI_API_KEY' in line and "=" in line:
                content[i] = f'os.environ["OPENAI_API_KEY"] = "{API_key}"\n'

        with open(fact_collection_sl_path, 'w') as file:
            file.writelines(content)


        current_dir = os.path.dirname(os.path.abspath(__file__))
        news_writing_path = os.path.join(current_dir, 'page', 'news_writing.py')
        with open(news_writing_path, 'r') as file:
            content = file.readlines()

        for i, line in enumerate(content):
            if 'OPENAI_API_KEY' in line and "=" in line:
                content[i] = f'os.environ["OPENAI_API_KEY"] = "{API_key}"\n'

        with open(news_writing_path, 'w') as file:
            file.writelines(content)


        user_simulated_path = os.path.join(current_dir, 'user_simulated.py')
        with open(user_simulated_path, 'r') as file:
            content = file.readlines()

        for i, line in enumerate(content):
            if 'Authorization' in line and "Bearer" in line:
                content[i]=f'    \'Authorization\': \'Bearer {API_key}\'\n'

        with open(user_simulated_path, 'w') as file:
            file.writelines(content)



        st.markdown(str_5)

    st.write("## Enter Tavily API Key")
    st.markdown(str_4)
    Tavily_API_key = st.text_input("Tavily API Key", placeholder = "tvly-xxxxxx")

    if st.button("Submit Tavily API Key"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        news_writing_path = os.path.join(current_dir, 'page', 'news_writing.py')
        with open(news_writing_path, 'r') as file:
            content = file.readlines()

        for i, line in enumerate(content):
            if 'TavilyClient' in line and "=" in line:
                content[i]=f'tavily_client = TavilyClient(api_key="{Tavily_API_key}")\n'

        with open(news_writing_path, 'w') as file:
            file.writelines(content)

        st.write("## Let's Start!")
        st.markdown(str_3)


elif selected5 == "Nes Drafting":
    import page.news_writing
    page.news_writing.run_writing()

elif selected5 == "Upload":
    import page.upload
    page.upload.upload_news_file()
    page.upload.upload_fact_file()
    

elif selected5 == "News Polishing":
    import page.news_polishing
    page.news_polishing.run_polish()


elif selected5 == "Simulation":
    import page.simulated_user
    page.simulated_user.run_simulated()