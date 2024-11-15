import streamlit as st
import time
import asyncio

from metagpt.actions import Action, UserRequirement
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.environment import Environment
from metagpt.const import MESSAGE_ROUTE_TO_ALL

from pymilvus import MilvusClient
from openai import OpenAI
from tavily import TavilyClient
import os

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ["OPENAI_API_KEY"] = "your_api_key_here"

openai_client = OpenAI(base_url="your_api_base_here")
tavily_client = TavilyClient(api_key="your_tavily_api_key_here")




def rag_news(question):
    def emb_text(text):
        return (
            openai_client.embeddings.create(input=text, model="text-embedding-3-small")
            .data[0]
            .embedding
        )

    milvus_client = MilvusClient(uri="./milvus_demo.db")
    collection_name = "my_news_collection"

    search_res1 = milvus_client.search(
    collection_name=collection_name,
    data=[
        emb_text(question)
    ],  
    limit=3, 
    search_params={"metric_type": "IP", "params": {}}, 
    output_fields=["text"], 
)
    res_str1 = [item['entity']['text'] for item in search_res1[0]]
    return res_str1

    

def url_and_time(question):
    search_res=rag_news(question)
    res=[]
    extracted_res = []

    for item in search_res:
        sections = item.split("###")
        extracted_res.append((sections[0], sections[1]))

    for url, time in extracted_res:
        res.append(f"url: {url}, published_time: {time}")
        
    return res
        


def rag_fact(question):
    def emb_text(text):
        return (
            openai_client.embeddings.create(input=text, model="text-embedding-3-small")
            .data[0]
            .embedding
        )

    milvus_client = MilvusClient(uri="./milvus_demo.db")
    collection_name = "my_fact_collection"

    search_res1 = milvus_client.search(
    collection_name=collection_name,
    data=[
        emb_text(question)
    ],
    limit=3, 
    search_params={"metric_type": "IP", "params": {}}, 
    output_fields=["text"], 
)
    res_str1 = [item['entity']['text'] for item in search_res1[0]]
    return res_str1

def rag_internet(question):
    search_res2 = tavily_client.get_search_context(query=question, 
                                                   max_results=1, 
                                                   max_tokens=4000)
    res_str2=search_res2

    return res_str2

def run_writing():
    class News_Theme(Action):
        PROMPT_TEMPLATE: str = """
        {type}
        Please provide the news topic and related language materials:
        """

        name: str = "News_Theme"

        async def run(self, type: str, ):
            prompt = self.PROMPT_TEMPLATE.format(type=type)

            rsp = await self._aask(prompt)

            return rsp



    class Human_Reviewer(Role):
        name: str = "Dan"
        profile: str = "UserRequirement"

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.set_actions([News_Theme])
            self._watch([UserRequirement])
            
        async def _act(self) -> Message:
            logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
            todo = self.rc.todo
            
            msg = self.get_memories(k=1)[0]

            if st.session_state.user_input:
                news_content = await todo.run(msg.content)
                msg = Message(content=news_content, role=self.profile, cause_by=type(todo))
                st.session_state.tips1 =2
        
            return msg

    class Search1(Action):
        PROMPT_TEMPLATE: str = """
        news corpus:
        {context}
        Based on the above corpus, extract the core elements of the event, including time, place, and key people or organizations. Here are the detailed instructions:
        1. identify the exact date and timeframe of the event
        2. Identify the exact location of the incident, including the city, region, or even a specific place
        3. Identify the key people involved, such as the dominant person, the victim, or the relevant authority of the incident
        """
        name: str = "Search1"

        async def run(self, context: str):
            prompt = self.PROMPT_TEMPLATE.format(context=context)
            with chat_container_search:
                with st.status("Search1 Loading...",expanded=True) as status:
                    rsp = await self._aask(prompt)
                    st.session_state.past.append({"role":"searcher1","content":rsp})
                    st.write(rsp)
                    status.update(label="Search1 complete!",state="complete",expanded=False)
            my_bar.progress(20, text="search1 complete")
            return rsp
        
    class Search2(Action):
        PROMPT_TEMPLATE: str = """
        news corpus:
        {context}
        Sort out the passage timeline and key plot points based on the provided news corpus.
        1. Describe the course of events and record important steps and twists in time sequential order.
        2. Extract key episodes and details, e.g. flashpoints, important decisions or actions. For example, at YYYY-MM-DD, some events happened, etc.
        """
        name: str = "Search2"

        async def run(self, context: str):
            prompt = self.PROMPT_TEMPLATE.format(context=context)
            with chat_container_search:
                with st.status("Search2 Loading...",expanded=True) as status:
                    rsp = await self._aask(prompt)
                    st.session_state.past.append({"role":"searcher2","content":rsp})
                    st.write(rsp)
                    status.update(label="Search2 complete!",state="complete",expanded=False)
            my_bar.progress(40, text="search2 complete")    
            return rsp


    class Search3(Action):
        PROMPT_TEMPLATE: str = """
        news corpus:
        {context}
        Summarize the above news corpus in one sentence.
        """
        name: str = "Search3"

        async def run(self, context: str):
            prompt = self.PROMPT_TEMPLATE.format(context=context)
            with chat_container_search:
                with st.status("Search3 Loading...",expanded=True) as status:
                    st.write("***Summarize the news...***")
                    rsp = await self._aask(prompt)
                    st.write(stream_data(rsp))
                    st.write("***Searching in News Database...***")
                    a = rag_news(rsp)
                    st.session_state['news_database'] = a
                    
                    st.write("***Searching in Fact Database...***")
                    b = rag_fact(rsp)
                    st.session_state['fact_database'] = b
                    
                    st.write("***Searching in Internet...***")
                    c = rag_internet(rsp)
                    st.session_state['internet'] = c
                    
                    st.write("***Get the news source...***")
                    rsp2 = url_and_time(rsp)
                    rsp = "News Database:"+str(a)+"Fact Database:"+str(b)+"Internet:"+c+"\n"+ "\n" +str(rsp2)

                    st.session_state.past.append({"role":"searcher3","content":rsp})
                    status.update(label="Search3 complete!",state="complete")
            my_bar.progress(60, text="search3 complete")
            return rsp
        

    class Agent_Searcher(Role):
        name: str = "Alice"
        profile: str = "Searcher"

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self._watch([News_Theme])
            self.set_actions([Search1, Search2, Search3])
            self._set_react_mode(react_mode="by_order")


    class Title(Action):
        PROMPT_TEMPLATE: str = """
        Context:{context}
        Based on the content of UserRequirement, extract the core elements, process, and key plot of the event, as well as the collected background information and impact, and propose 3-5 headlines for the news.
        Please return the result based on the following JSON structure:
        [{{"title": str}}]
        """

        name: str = "Title"

        async def run(self, context: str, ):
            prompt = self.PROMPT_TEMPLATE.format(context=context)

            rsp = await self._aask(prompt)

            return rsp


    class Agent_Title(Role):
        name: str = "Bob"
        profile: str = "Title"

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.set_actions([Title])
            self._watch([Search3])

        async def _act(self) -> Message:
            logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
            todo = self.rc.todo
            with chat_container_write:
                with st.status("Writing Title...",expanded=True) as status:
                    context = self.get_memories()[1]

                    title_list = await todo.run(context)
                    st.session_state.past.append({"role":"Agent_Title","content":title_list})
                    st.write(title_list)
                    status.update(label="Title complete!",state="complete",expanded=False)

            msg = Message(content=title_list, role=self.profile, cause_by=type(todo))
            st.session_state.user_say = None
            my_bar.progress(80, text="title complete")

            return msg
            


    class Write_frame(Action):
        PROMPT_TEMPLATE: str = """
        Content:{content}
        Based on the above corpus, follow the steps below to complete the writing of the press release. Strictly follow the format of the press release.
        """

        name: str = "Write"

        async def run(self, content: str):
            prompt_base = self.PROMPT_TEMPLATE.format(content=content)
            if st.session_state.type1 == "News":
                prompt_tmp = """
                {prompt_base}
                1. Select the most suitable title from the Title. A good news headline should be accurate, concise, and attractive.
                2. Complete the writing of the press release and present a complete, professional, excellent, and directly publishable press release. requirement:
                (1) Refer to the language style, article structure, and narrative techniques of [News Database](**DO NOT REFER ANY CONTENT IN [News Database]**), use concise and clear language, avoiding lengthy and complex sentences as well as obscure vocabulary.
                (2) You can refer to the factual basis that may be used in the [Fact Database] (or not) to correct the misinformation in the press release. If there are references, please indicate the source.
                (3) Based on the information from [UserRequirement] and the [Internet Surfer] as the main basis and theme for your writing, use all facts as a benchmark and write according to the format of news reports, including titles, introductions, main body, and endings.
                """
                prompt = prompt_tmp.format(prompt_base=prompt_base)

            elif st.session_state.type1 == "Commentary":
                prompt_tmp = """
                {prompt_base}
                1. Select the most suitable title from the Title. A good comment title should introduce the event directly with a viewpoint or appeal.
                2. Complete the writing of news commentary and present a complete, professional, and in-depth news commentary manuscript.requirement:
                (1) Based on information from [UserRequirement] and the Internet, conduct in-depth analysis of the background, causes, and impact of the event.
                (2) Propose unique perspectives and analyses. Use logical reasoning and evidence to support viewpoints, avoiding subjective speculation and emotional expression.
                (3) Referring to the language style, article structure, and narrative techniques of [News Database](**DO NOT REFER ANY CONTENT IN [News Database]**), it is appropriate to cite factual evidence from [Fact Database] to support viewpoints and enhance the credibility and persuasiveness of comments.
                (4) Language expression should be persuasive and infectious, using vivid vocabulary and vivid metaphors to attract readers' attention and evoke resonance.
                """
                prompt = prompt_tmp.format(prompt_base=prompt_base)

            elif st.session_state.type1 == "Profile":
                prompt_tmp = """
                {prompt_base}
                1. Select the most suitable title from the Title. A good profile title for a character should highlight their characteristics and charm.
                2. Complete the writing of the character profile and present a complete, vivid, and in-depth close-up of the character. requirement:
                (1) Using information from [UserRequirement] and the [Internet Surfer] as the main materials, the characters' personalities, achievements, and stories are presented through descriptions of their appearance, personality, behavior, and language. By using detailed descriptions and scene reproduction, readers can feel the true existence and emotional world of the characters.
                (2) Referring to the language style, article structure, and narrative techniques of [News Database](**DO NOT REFER ANY CONTENT IN [News Database]**).
                (3) Referring to factual evidence from [Fact Database] that can be used to enrich character images, such as their experiences, achievements, and contributions.
                (4) Language expression should be delicate and emotional, using appropriate adjectives and adverbs to enhance the character's infectiousness and affinity.
                """
                prompt = prompt_tmp.format(prompt_base=prompt_base)

            logger.info(prompt)
            rsp = await self._aask(prompt)

            return rsp
        


    class Agent_Write(Role):
        name: str = "Edison"
        profile: str = "Write"

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.set_actions([Write_frame])
            self._watch([Title])

        async def _act(self) -> Message:
            logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
            todo = self.rc.todo
            
            content = self.get_memories()
            with chat_container_write:
                with st.status("Writing Press Release...",expanded=True) as status:
                    news_context = await todo.run(content)
                    st.session_state.past.append({"role":"Agent_Write","content":news_context})
                    st.write(news_context)
                    status.update(label="Write complete!",state="complete",expanded=True)

            msg = Message(content=news_context, role=self.profile, cause_by=type(todo))

            my_bar.progress(100, text="write complete")
            st.session_state.press["state"] = 1
            st.session_state.press["content"] = news_context

            with tab2:
                st.write(news_context)
            return msg

    news_company = Environment()

    async def main(topic: str, n_round=3):

        news_company.add_roles([Agent_Searcher(),
                                Human_Reviewer(is_human = True),
                                Agent_Title(),
                                Agent_Write(),
                            ])

        
        news_company.publish_message(
            Message(role="Human", content=topic, cause_by=UserRequirement,
                    send_to='' or MESSAGE_ROUTE_TO_ALL),
            peekable=False,
        )

        while n_round > 0:
            n_round -= 1
            logger.debug(f"max {n_round} left.")

            await news_company.run()
        return news_company.history
    
    st.session_state.setdefault('past', [])
    st.session_state.setdefault('tips1',None)
    st.session_state.setdefault('type1',None)
    st.session_state.setdefault('press',{"state":0,"content":"The press release is not generated."})

    tab1, tab2= st.tabs(["Generate Progress", "Press release"])
    with tab1:
        placeholder_write_1 = st.empty()
        up_container_write = placeholder_write_1.container()

        col1,col2= st.columns(2)
        with col1:
            st.markdown("### 🔍 Searcher")
            placeholder_search_2 = st.empty()
            chat_container_search = placeholder_search_2.container(height=300,border=True)
        with col2:
            st.markdown("### ✍️ Writer")
            placeholder_write_2 = st.empty()
            chat_container_write = placeholder_write_2.container(height=300,border=True)

        placeholder_write_3 = st.empty()
        down_container_write = placeholder_write_3.container()


    def update_value(key1,key2):
        if key1 == "type1":
            st.session_state.type1 = key2
        elif key1 == "user_say":
            st.session_state.user_say = key2


    with up_container_write:
        option = st.selectbox(
            "",
            ("News", "Commentary", "Profile"),
            index=None,
            placeholder="Choose the news type you wanna generate",
            key="option")
        if option:
            update_value("type1",option)
            with up_container_write:

                st.info("Please provide the news topic and related language materials.")
                my_bar = st.progress(0, text="provide the topic")

    def stream_data(word_content):
        for word in word_content.split(" "):
            yield word + " "
            time.sleep(0.02)

    def on_input_change(user_say):
        if "user_say" not in st.session_state:
            st.session_state.setdefault("user_say",user_say)
        else:
            st.session_state.user_say = user_say
        st.session_state.past.append({"role": "user", "content": user_say})

    with down_container_write:

        user_say = st.chat_input("User Input:",key="user_input")
        if user_say:
            on_input_change(user_say)

    if st.session_state.type1:
        asyncio.run(main(topic="The type of press release you have chosen is " + st.session_state.type1, n_round=6))
