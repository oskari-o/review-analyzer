main_caption = \
  """This app allows you to filter and analyze reviews using 2 large language models
  (LLMs), GPT-4 Turbo and Mistral 7B. This is a proof of concept created for the
  course TU-E5030 *Creating Value with Analytics* at Aalto University in Spring 2024.
  """

usage_caption = \
  """### Usage
  1. **Filter reviews** using the selectors below.
  2. **Combine reviews** by pressing the button if the filtered dataset is more than 50
  rows, if it's less the combining happens automatically. 
  
  ⚠️  **Attention**: ⚠️ *The filtered reviews should have less than 50,000 tokens to enable
  analysis with GPT-4 Turbo, and less than 30,000 for analysis with Mistral 7B.*
  
  3. **Analyze reviews** by selecting a model and pressing Analyze. You can also change
  the main prompt if needed.
  4. **View analysis results** below the analysis button.
  5. *(**To reset** the default prompts, refresh the page.)*
  """