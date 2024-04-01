import streamlit as st
import pandas as pd
import hmac

from prompts import default_prompt, system_prompt
from captions import main_caption, usage_caption
from llms import get_gpt4_completion, count_gpt4_tokens, get_mistral_completion


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

st.title('Review Analyzer 🔍')
st.write(main_caption)
st.write(usage_caption)

st.divider()

st.caption('View the full dataset below. Data source: [Kaggle](https://www.kaggle.com/datasets/PromptCloudHQ/reviews-of-londonbased-hotels?resource=download)')

data = pd.read_csv('data/London_hotel_reviews.csv', encoding='ISO-8859-1')

with st.expander(f'###### Full dataset - {len(data)} reviews', expanded=False):
  st.dataframe(data)

# Add a new first column to be the index
data.insert(0, '#', range(1, 1 + len(data)))

data['Date Of Review as Date'] = pd.to_datetime(data['Date Of Review'])

min_date = data['Date Of Review as Date'].min()
max_date = data['Date Of Review as Date'].max()

unique_property_names = data['Property Name'].unique()
unique_review_ratings = sorted(data['Review Rating'].unique())

st.divider()
st.write('##### Filter the dataset')
selected_name = st.selectbox('Select a property name', unique_property_names)
col1, col2 = st.columns(2)
with col1:
  selected_ratings = st.multiselect('Select review rating(s)', unique_review_ratings, default=[1, 2])
with col2:
  selected_date_range = st.date_input("Select review date range:",
                                      value=(min_date, max_date),
                                      min_value=min_date,
                                      max_value=max_date)
if not len(selected_date_range) == 2:
  st.stop()
selected_start_date, selected_end_date = pd.to_datetime(selected_date_range[0]), pd.to_datetime(selected_date_range[1])

filtered_data = data[(data['Property Name'] == selected_name) & 
                     (data['Review Rating'].isin(selected_ratings)) & 
                     (data['Date Of Review as Date'] >= selected_start_date) & 
                     (data['Date Of Review as Date'] <= selected_end_date)]

st.markdown(f'###### Filtered dataset - {len(filtered_data)} reviews')
st.dataframe(filtered_data.drop(columns=['#']))

def serialize_filters():
  return f"Data for Hotel: {selected_name} | Ratings: {' '.join([str(r) for r in selected_ratings])} | Date Range: {str(selected_start_date.date())} - {str(selected_end_date.date())} | Total reviews: {len(filtered_data)}"

def combine_reviews():
  combined = ''
  filtered_data['Review Text'] = filtered_data['Review Text'].fillna('')
  filtered_data['Review Title'] = filtered_data['Review Title'].fillna('')
  for i in range(len(filtered_data)):
    combined += '###### #' + str(filtered_data.iloc[i]['#']) + ' - Title: ' + filtered_data.iloc[i]['Review Title'] + '\n\n' + filtered_data.iloc[i]['Review Text'] + '\n\n'
  st.session_state['combine_reviews'] = combined
  num_tokens = count_gpt4_tokens(combined)
  st.session_state['num_tokens_reviews'] = num_tokens

if len(filtered_data) < 50:
  combine_reviews()
else:
  st.write(f'Filtered dataset length is {len(filtered_data)} rows - it was not automatically combined - press the button below to combine reviews:')
  st.button('Combine new reviews', on_click=combine_reviews)

with st.expander(f'Filtered reviews - {st.session_state.get("num_tokens_reviews", 0)} tokens', expanded=False):
  reviews_holder = st.empty()
  reviews_holder.write(st.session_state.get('combine_reviews', ''))

st.divider()

st.write('##### Analyze Filtered Reviews')

selected_model = st.selectbox('Select a llm', ['GPT-4-Turbo', 'Mistral 7B'])
prompt_input = st.text_area('Main prompt for the LLM', value=st.session_state.get('prompt_input', default_prompt))
with st.expander('System prompt for the LLM'):
  system_prompt_input = st.text_area('*Edit if needed*',
                                     value=st.session_state.get('system_prompt_input', system_prompt),
                                     help='This is the system prompt that is used for the LLM analysis, and it is provided before the main prompt above. You can change it if needed.')
analyze_button_caption_holder = st.empty()
analyze_button_holder = st.empty()

st.divider()

text_holder = st.empty()
text_holder.write("#### Analysis results:\n\n" + st.session_state.get('analysis_result', '\n\n*Filter the reviews and press "Analyze reviews" to get the analysis.*'))
  
def analyze_reviews():
  st.session_state['prompt_input'] = prompt_input
  st.session_state['latest_filters'] = serialize_filters()
  combined_prompt = prompt_input + '\n\nReview data:\n\n' + st.session_state['combine_reviews']
  match selected_model:
    case 'Mistral 7B':
      api_key = st.secrets['mistral_api_key']
      with text_holder:
        with st.spinner('Analyzing reviews with Mistral 7B...'):
          completion = get_mistral_completion(combined_prompt, api_key)
    case 'GPT-4-Turbo':
      api_key = st.secrets['openai_api_key']
      with text_holder:
        with st.spinner('Analyzing reviews with GPT-4 Turbo...'):
          completion = get_gpt4_completion(combined_prompt, api_key)
  st.session_state['analysis_result'] = st.session_state['latest_filters'] + '\n\n' + f"Model: {selected_model}" + '\n\n' + completion

analyze_button_text = "Analyze reviews"
analyze_button_disabled = True
analyze_button_caption = "Filter reviews and combine them to enable LLM analysis."

if 'combine_reviews' in st.session_state:
  if 'num_tokens_reviews' in st.session_state and st.session_state['num_tokens_reviews'] < 50000:
    analyze_button_text = "Analyze reviews"
    if 'analysis_result' in st.session_state and 'latest_filters' in st.session_state and st.session_state['latest_filters'] == serialize_filters():
      analyze_button_text = "Re-analyze reviews"
    analyze_button_caption = ""
    analyze_button_disabled = False
  elif 'num_tokens_reviews' in st.session_state:
    analyze_button_caption = "Combine reviews must have less than 50,000 tokens to enable LLM analysis. Apply stricter filters."

analyze_button_caption_holder.caption(analyze_button_caption)
analyze_button_holder.button(analyze_button_text, disabled=analyze_button_disabled, on_click=lambda: analyze_reviews())