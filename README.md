# AIPress: A Muti-Agent News Generation and Feedback Simulation System

This repository is the implementation of our paper [AI-Press: A Multi-Agent News Generating and Feedback Simulation System Powered by Large Language Models](https://arxiv.org/abs/2410.07561).   


## Contents
- [Abstract](#Abstract)
- [Dataset](#Dataset)
- [Getting Started](#Getting-Started)
  - [Installation](#Installation)
  - [How to start](#How-to-start)
- [Citation](#Citation)

## Abstract 
The rise of various social platforms has transformed journalism. The growing demand for news content has led to the increased use of large language models (LLMs) in news production due to their speed and cost-effectiveness. However, LLMs still encounter limitations in professionalism and ethical judgment in news generation. Additionally, predicting public feedback is usually difficult before news is released. To tackle these challenges, we introduce AI-Press, an automated news drafting and polishing system based on multi-agent collaboration and Retrieval-Augmented Generation. We develop a feedback simulation system that generates public feedback considering demographic distributions. Through extensive quantitative and qualitative evaluations, our system shows significant improvements in news-generating capabilities and verifies the effectiveness of public feedback simulation.

## Dataset
To be **in compliance with Twitter’s terms of service**, we can not publish the raw data. Instead, we upload an example dataset **twitter_with_profile.csv**, in which all specific content related to user privacy has been masked.

If you want to use your news data to do **RAG**, you need to upload csv file with a format as below.

| URL  | Publish Time  | Article |
|:------------- |:---------------:| -------------:|
|  http://...    | years/month... |  xxxx |


## Getting Started
### Installation
```bash
conda create -n AIPress python=3.10
conda activate AIPress
```

```bash
pip install metagpt
pip install streamlit
pip install pymilvus
pip install tavily
```

```bash
git clone https://github.com/AIPress-Web/AIPress-code.git
cd AIPress
```

### Environment Variables
You need to replace your OpenAI API key in the files：
- news_writing.py
- user_simulated.py
- new_collection_sl.py
- fact_collection_sl.py


### Configuration

You can init the config of MetaGPT by running the following command, or manually create `~/.metagpt/config2.yaml` file:
```bash
# Check https://docs.deepwisdom.ai/main/en/guide/get_started/configuration.html for more details
metagpt --init-config  # it will create ~/.metagpt/config2.yaml, just modify it to your needs
```

You can configure `~/.metagpt/config2.yaml` according to the [example](https://github.com/geekan/MetaGPT/blob/main/config/config2.example.yaml) and [doc](https://docs.deepwisdom.ai/main/en/guide/get_started/configuration.html):

```yaml
llm:
  api_type: "openai"  # or azure / ollama / groq etc. Check LLMType for more options
  model: "gpt-4-turbo"  # or gpt-3.5-turbo
  base_url: "https://api.openai.com/v1"  # or forward url / other llm url
  api_key: "YOUR_API_KEY"
```



## Citation
Please consider citing this paper if you find this repository useful:
```bash
@misc{liu2024aipressmultiagentnewsgenerating,
      title={AI-Press: A Multi-Agent News Generating and Feedback Simulation System Powered by Large Language Models}, 
      author={Xiawei Liu and Shiyue Yang and Xinnong Zhang and Haoyu Kuang and Libo Sun and Yihang Yang and Siming Chen and Xuanjing Huang and Zhongyu Wei},
      year={2024},
      eprint={2410.07561},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2410.07561}, 
}
```
