import streamlit as st
import user_simulated
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

def run_simulated():
    tab1, tab2, tab3 = st.tabs(["User Input", "Simulated Comments", "Analysis"])

    if not tab1 and not st.session_state.get('submitted_in_user_input', False):
        st.error("Please submit in the User Input section first.")
    else:
        with tab1:
            st.title("Simulated User Data Input")
            st.write("Generate your own simulated user group🤩!")
            # Sample Size
            st.markdown("### Sample Size")
            sample_size = st.number_input("Please enter the sample size (>1)", min_value=1)


            # Male Ratio
            st.markdown("### Male Ratio")
            male_ratio = st.slider("Male Ratio", 0.0, 1.0, 0.5)

            # Age Ratio
            st.markdown("### Age Ratio")
            col1, col2, col3 = st.columns(3)
            with col1:
                elder = st.number_input("Elder Ratio", min_value=0.0, max_value=1.0, value=0.3)
            with col2:
                middle_age = st.number_input("Middle aged Ratio", min_value=0.0, max_value=1.0, value=0.5)
            with col3:
                youth = st.number_input("Youth Ratio", value=1-(elder+middle_age))


            # Education Ratio
            st.markdown("### Education Level Ratio")
            col1, col2, col3 = st.columns(3)
            with col1:
                high_education_ratio = st.number_input("Postgraduate Ratio", min_value=0.0, max_value=1.0, value=0.3)
            with col2:
                middle_education_ratio = st.number_input("Bachelor Ratio", min_value=0.0, max_value=1.0, value=0.5)
            with col3:
                low_education_ratio = st.number_input("Below Bachelor Ratio", value=1-(high_education_ratio+middle_education_ratio))

            # Income Ratio
            st.markdown("### Income Ratio")
            col1, col2, col3 = st.columns(3)
            with col1:
                high_income = st.number_input("High Income Ratio", min_value=0.0, max_value=1.0, value=0.3)
            with col2:
                middle_income = st.number_input("Middle Income Ratio", min_value=0.0, max_value=1.0, value=0.5)
            with col3:
                low_income = st.number_input("Low Income Ratio", value=1-(high_income+middle_income))

            # Employment Ratio
            st.markdown("### Employment Ratio")
            col1, col2, col3 = st.columns(3)
            with col1:
                student = st.number_input("Student Ratio", min_value=0.0, max_value=1.0, value=0.3)
            with col2:
                working = st.number_input("Working Now Ratio", min_value=0.0, max_value=1.0, value=0.5)
            with col3:
                others = st.number_input("Others Ratio", value=1-(student+working))
            


            # Ideology
            st.markdown("### Ideology")
            col1, col2, col3 = st.columns(3)
            with col1:
                conservative = st.number_input("Conservative Ratio", min_value=0.0, max_value=1.0, value=0.3)
            with col2:
                liberal = st.number_input("Liberal Ratio", min_value=0.0, max_value=1.0, value=0.5)
            with col3:
                moderate = st.number_input("Moderate Ratio", value=1-(conservative + liberal))


            news = st.text_area(
                "Press Release to publish",
            )

            submit_button = st.button("Submit")

            if submit_button:
                if low_education_ratio<0 or low_income<0 or youth<0 or others <0 or moderate<0:
                    st.error("The ratio should be positive")
                elif not (high_education_ratio + middle_education_ratio + low_education_ratio == 1):
                    st.error("The sum of educatiob ratios should be 1")
                elif not (low_income + middle_income + high_income == 1):
                    st.error("The sum of income level ratios should be 1")
                elif not (elder + youth + middle_age == 1):
                    st.error("The sum of age ratios should be 1")
                elif not (student + working + others == 1):
                    st.error("The sum of employment ratios should be 1")
                elif not (conservative + liberal + moderate == 1):
                    st.error("The sum of ideology ratios should be 1")
                elif not news:
                    st.error("Please give the press release to publish")
                else:
                    st.session_state['sample_size'] = sample_size
                    st.session_state['male_ratio'] = male_ratio
                    st.session_state['low_education_ratio'] = low_education_ratio
                    st.session_state['high_education_ratio'] = high_education_ratio
                    st.session_state['high_income'] = high_income
                    st.session_state['middle_income'] = middle_income
                    st.session_state['elder'] = elder
                    st.session_state['youth'] = youth
                    st.session_state['student'] = student
                    st.session_state['working'] = working
                    st.session_state['conservative'] = conservative
                    st.session_state['liberal'] = liberal
                    st.session_state["news"] = news
                    st.session_state['submitted_in_user_input'] = True
                    st.session_state['profile'] = user_simulated.user_generate()
                    st.success("Done! Click on _Simulated Comments_ on the top to view the generated comments.")
                    

        with tab2:
            st.title("Check all comments from users")
            if not st.session_state.get('submitted_in_user_input', False):
                st.error("Please submit in the User Input section first.")
            else:
                profile = st.session_state['profile']

                with st.spinner('Generating comments...'):
                    for item in profile:
                        with st.container(border=True):
                            
                            st.markdown(f"<h5>{item['uid'][0]}</h5>", unsafe_allow_html=True)
                            expander = st.expander("click to show/hide more info", expanded=False)
                            with expander:
                                profile_info = ""
                                for key, value in item.items():
                                    if key == 'profile':
                                        match = re.search(r'"age": "(.*?)"', value)
                                        if match:
                                            age_value = match.group(1)
                                        match = re.search(r'"gender": "(.*?)"', value)
                                        if match:
                                            gender_value = match.group(1)
                                        match = re.search(r'"education": "(.*?)"', value)
                                        if match:
                                            education_value = match.group(1)
                                        match = re.search(r'"income": "(.*?)"', value)
                                        if match:
                                            income_value = match.group(1)
                                        match = re.search(r'"employment": "(.*?)"', value)
                                        if match:
                                            employment_value = match.group(1)
                                        match = re.search(r'"ideology": "(.*?)"', value)
                                        if match:
                                            ideology_value = match.group(1)
                                        profile_info += f"<small>**age:** {age_value}</small><br>"
                                        profile_info += f"<small>**gender:** {gender_value}</small><br>"
                                        profile_info += f"<small>**education:** {education_value}</small><br>"
                                        profile_info += f"<small>**income:** {income_value}</small><br>"
                                        profile_info += f"<small>**employment:** {employment_value}</small><br>"
                                        profile_info += f"<small>**ideology:** {ideology_value}</small><br>"
                                st.markdown(profile_info, unsafe_allow_html=True)

                            st.write(f"**Comment**: {item['comment']}")

        with tab3:
            st.title("Show analysis of the comments")
            if not st.session_state.get('submitted_in_user_input', False):
                st.error("Please submit in the User Input section first.")
            else:
                comment_text = ""
                hist_sentiment=[]
                hist_stance=[]
                profile = st.session_state['profile']

                for item in profile:
                    comment_text += str(item['comment'])
                    sentiment_score = item['Sentiment_score']
                    stance = item['Stance']
                    hist_sentiment.append(sentiment_score)
                    hist_stance.append(stance)

                wordcloud = WordCloud(width=800, height=400, background_color='white',colormap='tab20c',font_path='SIMHEI.TTF').generate(comment_text)

                st.markdown("### Comments Word Cloud")
                st.image(wordcloud.to_image())

                
                stance_counts = {
                    'Support': hist_stance.count('Support'),
                    'Neutral': hist_stance.count('Neutral'),
                    'Against': hist_stance.count('Against')
                }


                st.markdown("### Sentiment and Stance Analysis")
                col1, col2 = st.columns(2)
                with col1:
                    fig, ax = plt.subplots()
                    ax.hist(hist_sentiment, bins = 30)
                    ax.set_xlabel('Sentiment Score')
                    ax.set_ylabel('Frequency')
                    ax.set_title('Sentiment Analysis')
                    st.pyplot(fig)

                with col2:
                    categories = list(stance_counts.keys())
                    values = list(stance_counts.values())

                    fig, ax = plt.subplots()
                    ax.bar(categories, values)
                    ax.set_xlabel('Stance')
                    ax.set_ylabel('Frequency')
                    ax.set_title('Stance Analysis')
                    st.pyplot(fig)

                