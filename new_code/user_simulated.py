import random
import streamlit as st
import requests
import re
import pandas as pd
import numpy as np
import json

url = "your_api_base_here"
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your_api_key_here'
}

Prompt_comment = """
You are a {gender} who is {age}, with your highest education {education}. Your income level is {income}, and your current employment status is {employment}. You tend to be {ideology} when making comments.

Today you saw a news article as follows:
## news article:
{news}

You want to post your own comments in the comment section below the news article.
Remember, your comment doesn't have to be formal. It can be as casual as you want—use slang, emojis, or even a bit of sarcasm. Please make sure your comment conveys the perspective consistent with your role configuration.

Here is what you have posted in the past:
## past posted:
{historical_comment}
You can refer to your past tone and wording habits when posting your comment, but do not mention the events in your historical comment unless it is highly relevant to the current news.

Reply with your authentic voice:
"""

Prompt_name = """
You are a user review analyst responsible for judging the emotional tendency of user comments, and determining the user's viewpoint and stance based on the provided news articles and user comments. Meanwhile, please provide the user with a name. Please freely draft a name that is not related to user information and is as close as possible to the real name.
The news article is as follows:
{news}
The comments posted by users under the news article are as follows:
{comment}
## Sentiment inclination: Please determine whether the sentiments expressed in the comments posted by the user are positive, negative, or neutral
- Positive
- Neutral
- Negative
## Sentiment score: Please provide a score range of [-1,1] based on the comments posted by the user. The closer the score is to -1, the more negative it is, and the closer the score is to 1, the more positive it is. A score of 0 indicates neutrality
- The given score is between -1 and 1, with two decimal places retained
## Stance: Please judge whether the user supports, opposes, or is neutral towards the news viewpoint based on the comments posted by the user and the viewpoint of the news article
- Support
- Neutral
- Against
Output in the following JSON format:
{{"Sentiment_inclination":"Positive", "Sentiment_score":0.98, "Stance":"Support", "username":str}}
Please only return the json string.
Please strictly follow the options provided for selection, and do not return null.

"""

# 定义每个标签的可能值
genders = ['M', 'F']
education_levels = ['HE', 'LE', 'ME']
incomes = ['HI', 'MI', 'LI']
ages = ['HA', 'MA', 'LA']
employments = ['O','S','W']
ideology = ['C','L','Q']
                

def simulation_combine_info(category):
    combine_target={}
    category_list = category.split('_')
    for cat in category_list:
        if cat in genders:
            if cat == 'M':
                combine_target["gender"]="Male"
            else:
                combine_target["gender"]="Female"
        elif cat in education_levels:
            if cat == 'HE':
                combine_target["education"]="Bachelor's degree"
            elif cat == 'LE':
                combine_target["education"]="Below Bachelor's"
            else:
                combine_target["education"]="Postgraduate education"
        elif cat in incomes:
            if cat == 'HI':
                combine_target["income"]="High Income"
            elif cat == 'MI':
                combine_target["income"]="Middle Income"
            else:
                combine_target["income"]="Low Income"
        elif cat in ages:
            if cat == 'HA':
                combine_target["age"]="Elderly (over 65 years old)"
            elif cat == 'LA':
                combine_target["age"]="Youth (18-35 years old)"
            else:
                combine_target["age"]="Middle-aged (36-65 years old)"
        elif cat in employments:
            if cat == 'S':
                combine_target["employment"]="Student"
            elif cat == 'W':
                combine_target["employment"]="Working now"
            else:
                combine_target["employment"]="Others"
        else:
            if cat == 'C':
                combine_target["ideology"]="Conservative"
            elif cat == 'L':
                combine_target["ideology"]="Liberal"
            else:
                combine_target["ideology"]="Moderate"
    combine_target = json.dumps(combine_target,ensure_ascii=False)
    return combine_target
                

def get_samples():
   
    # 定义每个标签的占比
    male_ratio = st.session_state.male_ratio

    high_education_ratio = st.session_state.high_education_ratio
    low_education_ratio = st.session_state.low_education_ratio

    high_income_ratio = st.session_state.high_income
    mid_income_ratio = st.session_state.middle_income

    elder_ratio = st.session_state.elder
    youth_ratio = st.session_state.youth

    student_ratio = st.session_state.student
    working_ratio = st.session_state.working

    conservative_ratio = st.session_state.conservative
    liberal_ratio = st.session_state.liberal  


    # 计算所有组合的占比
    proportions = {}
    for gender in genders:
        for education in education_levels:
            for income in incomes:
                for age in ages:
                    for employment in employments:
                        for ide in ideology:
                            proportion = (male_ratio if gender == 'M' else 1 - male_ratio) * \
                                        (high_education_ratio if education == 'HE' else low_education_ratio if education == 'LE' else 1 - high_education_ratio - low_education_ratio) * \
                                        (high_income_ratio if income == 'HI' else mid_income_ratio if income == 'MI' else 1-high_income_ratio-mid_income_ratio) * \
                                        (elder_ratio if age == 'HA' else youth_ratio if age == 'LA' else 1-elder_ratio-youth_ratio) * \
                                        (student_ratio if employment == 'S' else working_ratio if employment == 'W' else 1-student_ratio-working_ratio) * \
                                        (conservative_ratio if ide == 'C' else liberal_ratio if ide == 'L' else 1-conservative_ratio-liberal_ratio)
                            key = f"{age}_{gender}_{income}_{education}_{employment}_{ide}"
                            proportions[key] = proportion

    proportions_without_zero = {category: proportion for category, proportion in proportions.items() if proportion != 0}

    total_samples = st.session_state.sample_size

    cumulative_proportions = []
    current_cumulative = 0
    for category, proportion in sorted(proportions_without_zero.items(), key=lambda x: x[1]):
        current_cumulative += proportion
        cumulative_proportions.append((category, current_cumulative))

    category_proportions = {}

    for i, (category, end) in enumerate(cumulative_proportions):
        if i == 0:
            start = 0
        else:
            start = cumulative_proportions[i-1][1]
        category_proportions[category]=(start,end)

    random_numbers = [random.random() for _ in range(total_samples)]

    category_counts = {key: 0 for key in category_proportions}

    for number in random_numbers:
        for category, (start, end) in category_proportions.items():
            if start <= number < end:
                category_counts[category] += 1
                break

    category_counts = {category: count for category, count in category_counts.items() if count != 0}
    
    for category, count in category_counts.items():
        print(f"{category}: {count}")

    df = pd.read_csv('twitter_with_profile.csv')

    grouped = df.groupby('Category')

    sampled_data = pd.DataFrame()

    for category, prop in category_counts.items():
        # 根据分类抽取样本
        group = grouped.get_group(category) if category in grouped.groups else pd.DataFrame()

        if len(group) >= prop:
            # 从当前分类中抽取样本
            sample = group.sample(n=prop)
            sampled_data = pd.concat([sampled_data, sample])
        else:
            if len(group) > 0:
                # 选择该分类下的所有数据
                selected_data = group.sample(frac=1)
                missing_samples = max(prop - len(selected_data), 0)
                to_copy_data = selected_data.sample(n=missing_samples,replace=True)
                selected_data = pd.concat([selected_data, to_copy_data])
            else:
                simulated_data = pd.DataFrame({
                'uid': [''] * prop,
                'sample_content': [''] * prop,
                'AGE':[''] * prop,
                'GENDER':[''] * prop,
                'INCOME':[''] * prop,
                'EDUCATION':[''] * prop,
                'EMPLOYMENT':[''] * prop,
                'IDEOLOGY':[''] * prop,
                'Education Category':[''] * prop,
                'Employment Category':[''] * prop,
                'Category': [category] * prop,
                'Profile':[simulation_combine_info(category)] * prop,
            })
                selected_data = simulated_data
            # 将当前分类的样本添加到最终样本集中
            sampled_data = pd.concat([sampled_data, selected_data])

    return sampled_data

def get_profile_and_historical_comment(sampled_data):


    sampled_df = sampled_data

    # 指定两列的列名
    column1_name = 'uid'
    column2_name = 'sample_content'
    column3_name = 'Profile'
    column4_name = 'Category'

    all_profiles=[]

    
    for index, row in sampled_df.iterrows():
        user_profile={}
        user_profile['uid'] = row[column1_name]
        user_profile['sample_content'] = row[column2_name]
        profile = row[column3_name]
        profile_dict = json.loads(profile)
        match = re.search(r'\((.*?)\)', profile_dict['age'])
        if match:
            user_profile['age'] = match.group(1)
        user_profile['gender'] = profile_dict['gender']
        user_profile['income'] = profile_dict['income']
        user_profile['education'] = profile_dict['education']
        if profile_dict['employment'] == 'Others':
            user_profile['employment'] = 'Not working'
        else:
            user_profile['employment'] = profile_dict['employment']
        user_profile['ideology'] = profile_dict['ideology']
        user_profile['profile'] = profile
        user_profile['category'] = row[column4_name]
        all_profiles.append(user_profile)

    return all_profiles

def get_comment(all_profiles):
    news = st.session_state.news
    all_profile_with_comment = []
    total_profiles = len(all_profiles)
    progress = 0
    progress_bar = st.progress(0)
    for user_profile in all_profiles:
        uid=user_profile['uid']
        historical_comment = user_profile['sample_content']
        age = user_profile['age']
        gender = user_profile['gender']
        income = user_profile['income']
        education = user_profile['education']
        employment = user_profile['employment']
        ideology = user_profile['ideology']
        category = user_profile['category']
        profile = user_profile['profile']
        content = Prompt_comment.format(age = age, gender = gender, income = income, education= education, employment = employment, ideology = ideology,news = news,historical_comment = historical_comment)
        data = {"model": "gpt-4o","messages": [{"role": "user", "content": content}]}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            comment = response.json()['choices'][0]['message']['content']
            
            profile_with_comment = {}
            content = Prompt_name.format(news = news, comment = comment )
            data = {"model": "gpt-4o","messages": [{"role": "user", "content": content}]}
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                text = response.json()['choices'][0]['message']['content']
                text = re.sub(r'```json', '', text).strip()
                text = re.sub(r'```', '', text).strip()
                dict_name = json.loads(text)
                print(dict_name)
                username = dict_name["username"]
                Sentiment_inclination = dict_name["Sentiment_inclination"]
                Sentiment_score = dict_name["Sentiment_score"]
                Stance = dict_name["Stance"]
            else:
                print(str(progress)+":bad request when get username")
            profile_with_comment['uid'] = username,
            profile_with_comment['historical_comment'] = historical_comment
            profile_with_comment['profile'] = profile
            profile_with_comment['category'] = category
            profile_with_comment['comment'] = comment
            profile_with_comment['Sentiment_inclination'] = Sentiment_inclination
            profile_with_comment['Sentiment_score'] = Sentiment_score
            profile_with_comment['Stance'] = Stance
            all_profile_with_comment.append(profile_with_comment)
        else:
            print(str(progress)+":bad request when get comment")
        progress += 1
        progress_bar.progress(progress / total_profiles,text=f"Wait for comment writing: {progress}/{total_profiles}")
    return all_profile_with_comment

def user_generate():
    with st.spinner('Wait for user simulating...'):
        # 抽样
        sampled_data = get_samples()
        # 获取profile and comment
        all_profiles = get_profile_and_historical_comment(sampled_data)
        # 获取评论
        all_profile_with_comment = get_comment(all_profiles)

    return all_profile_with_comment

