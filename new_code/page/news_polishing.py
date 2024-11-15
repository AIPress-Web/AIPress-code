import streamlit as st
import json

import asyncio

from metagpt.actions import Action, UserRequirement
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.environment import Environment
from metagpt.const import MESSAGE_ROUTE_TO_ALL

def run_polish():
    tab1,tab2= st.tabs(["Polish","History Polish Version"])
    

    with tab1:
        st.session_state.setdefault('type2', None)

        class News_Theme(Action):
            PROMPT_TEMPLATE: str = """
            {type}
            Please provide the news need to be polished:
            """

            name: str = "News_Theme"

            async def run(self, type: str, ):
                prompt = self.PROMPT_TEMPLATE.format(type=type)

                rsp = await self._aask(prompt)

                return rsp

        class Human_Reviewer(Role):
            name: str = "June"
            profile: str = "SimpleReviewer"

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
                    st.session_state.tips =2

                return msg

        class Comments_A(Action):
            if st.session_state.type2=='News':
                PROMPT_TEMPLATE: str = """
                Press Release: {content}
                Please review the press release and provide critical comments based on these aspects:
                1. Timeliness: Whether the latest and most important information was reported on time?
                2. Accuracy: Whether the factual statements are accurate and reliable, and whether the data and references are reliable?
                3. Concise and clear: Can the core information be conveyed clearly in concise language, avoiding lengthy and complex expressions?
                4. Key emphasis: Have the key elements and focus of the event been clearly identified?
                """

            elif st.session_state.type2=='Commentary':
                PROMPT_TEMPLATE: str = """
                Commentary: {content}
                Please review the commentary news article and provide critical comments based on these aspects:
                1. Depth and breadth: Conduct comprehensive and in-depth analyses on the topic, presenting extensive background information and details.
                2. Sufficiency of evidence: Provide sufficient facts, data, cases, and other evidence to support the viewpoints and arguments.
                3. Clarity of opinions: Express viewpoints clearly and distinctly, avoiding ambiguous language and ensuring that the stance taken is easily understandable. State the main argument upfront and provide coherent explanations and examples to support it.
                """

            elif st.session_state.type2=='Profile':
                PROMPT_TEMPLATE: str = """
                Profile: {content}
                Please review the profile and provide critical comments based on these aspects:
                1. Unique perspective: Whether a unique and innovative angle has been chosen to present the theme or characters?
                2. Detail description: Whether it contains vivid and specific details that enable readers to have a strong sensory experience?
                3. Personalization: Can the personality traits of the theme or character be highlighted to distinguish it from other similar individuals?
                """


            name: str = "Comments"

            async def run(self, content: str):
                prompt = self.PROMPT_TEMPLATE.format(content=content)

                rsp = await self._aask(prompt)

                return rsp

        class Agent_Comment(Role):
            name: str = "Glory"
            profile: str = "Agent_Comment"

            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.set_actions([Comments_A])
                self._watch([News_Theme,Write])

            async def _act(self) -> Message:
                logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
                todo = self.rc.todo 

                msg = self.get_memories(k=1)[0]
                with chat_container_polish_1:
                    with st.status("Making comments...", expanded=True) as status:
                        comments = await todo.run(msg.content)
                        st.session_state.past.append({"role": "Agent_Comment", "content": comments})
                        st.write(comments)
                        status.update(label="Comments writen!",state="complete",expanded=True)

                msg = Message(content=comments, role=self.profile, cause_by=type(todo))
                st.session_state.user_say = None
                return msg

        class Write(Action):
            PROMPT_TEMPLATE: str = """
            Content:{content}
            You have received the following comments on the news draft.
            Please revise the news accordingly and provide a revised version of the news. Also, list the changes made in bullet points to highlight the improvements. Your response should be in the following JSON format:
            {{
            "revised_news": "Your revised news content here",
            "changes_made": [
                "Point 1: Description of the first change made",
                "Point 2: Description of the second change made",
                ...
            ]
            }}
            
            """

            name: str = "Write"

            async def run(self, content: str):
                prompt = self.PROMPT_TEMPLATE.format(content=content)

                rsp = await self._aask(prompt)

                return rsp

        class Agent_Write(Role):
            name: str = "Edison"
            profile: str = "Write"

            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.set_actions([Write])
                self._watch([Comments_A])

            async def _act(self) -> Message:
                logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
                todo = self.rc.todo

                content = self.get_memories()
                with chat_container_polish_2:
                    with st.status("Writing Press Release...", expanded=True) as status:
                        news_context = await todo.run(content)
                        json_data = json.loads(news_context)
                        changes_made = json_data['changes_made']
                        st.session_state.past.append({"role": "Agent_Write", "content": changes_made})
                        st.write(changes_made)
                        status.update(label="changes detected!",state="complete",expanded=False)

                with container_compare:
                    
                    json_data = json.loads(news_context)
                    revised_news = json_data['revised_news']
                    st.session_state.past.insert(0, {"role": "Agent_Write", "content": revised_news})
                    st.write(revised_news)
                    st.divider()
                        
                msg = Message(content=str(changes_made), role=self.profile, cause_by=type(todo))

                return msg

        news_company = Environment()

        async def main(topic: str, n_round=3):
            news_company.add_roles([Human_Reviewer(is_human=True),
                                    Agent_Comment(),
                                    Agent_Write()
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
        st.session_state.setdefault('tips', None)
        st.session_state.setdefault('type2', None)


        def update_value(key1, key2):
            if key1 == "type2":
                st.session_state.type2 = key2
            elif key1 == "user_say":
                st.session_state.user_say = key2

        def on_input_change(user_say):
            if "user_say" not in st.session_state:
                st.session_state.setdefault("user_say", user_say)
            else:
                st.session_state.user_say = user_say
            st.session_state.past.append({"role": "user", "content": user_say})
            


        col1, col2 = st.columns(2)

        with col1:
            placeholder_polish_1 = st.empty()
            up_container_polish = placeholder_polish_1.container()

            st.markdown("### 📒 Comment")
            with up_container_polish:
                option = st.selectbox(
                    "Choose the news type you wanna polish",
                    ("News", "Feature", "Profile"),
                    index=0,
                    key="option")

            placeholder_polish_2_1 = st.empty()
            chat_container_polish_1 = placeholder_polish_2_1.container(height=300,border=True)

            if option:
                update_value("type2", option)

        with col2:
            placeholder_polish_3 = st.empty()
            down_container_polish = placeholder_polish_3.container()

            st.markdown("### 👓 Diff")
            with down_container_polish:
                n_round = st.number_input("Fill in the number of polishing rounds", min_value=1,value=1)

            placeholder_polish_2_2 = st.empty()
            chat_container_polish_2 = placeholder_polish_2_2.container(height=300,border=True)



        st.info("Please provide the news need to be polished.")
        user_say = st.chat_input("User Input:", key="user_input")
        if user_say:
            on_input_change(user_say)

        

    with tab2:
        st.markdown("### ✨ News After Polishing")
        st.write('Pull down to the bottom of the page to see past versions.')
        placeholder_container_compare = st.empty()
        container_compare = placeholder_container_compare.container(border=True)

        


    if st.session_state.type2:
        asyncio.run(main(topic="The type of press release you have chosen is " + st.session_state.type2, n_round=n_round*2))