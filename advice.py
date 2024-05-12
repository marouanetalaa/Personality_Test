from typing import List, Tuple
import time
import torch
from typing import List, Tuple
from tqdm import tqdm 



from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
import langchain as lc
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_community.chat_models import ChatCohere
import matplotlib.pyplot as plt
import matplotlib



import dotenv
import os

dotenv.load_dotenv()

cohere_api_key = os.getenv("COHERE_API_KEY")
# Creating a list of all 50 sentences as specified
sentences = [
    "Am the life of the party.", #: score(1,5)
    "Feel little concern for others.",   # nsame
    "Am always prepared.",
    "Get stressed out easily.",
    "Have a rich vocabulary.",
    "Don't talk a lot.",
    "Am interested in people.",
    "Leave my belongings around.",
    "Am relaxed most of the time.",
    "Have difficulty understanding abstract ideas.",
    "Feel comfortable around people.",
    "Insult people.",
    "Pay attention to details.",
    "Worry about things.",
    "Have a vivid imagination.",
    "Keep in the background.",
    "Sympathize with others' feelings.",
    "Make a mess of things.",
    "Seldom feel blue.",
    "Am not interested in abstract ideas.",
    "Start conversations.",
    "Am not interested in other people's problems.",
    "Get chores done right away.",
    "Am easily disturbed.",
    "Have excellent ideas.",
    "Have little to say.",
    "Have a soft heart.",
    "Often forget to put things back in their proper place.",
    "Get upset easily.",
    "Do not have a good imagination.",
    "Talk to a lot of different people at parties.",
    "Am not really interested in others.",
    "Like order.",
    "Change my mood a lot.",
    "Am quick to understand things.",
    "Don't like to draw attention to myself.",
    "Take time out for others.",
    "Shirk my duties.",
    "Have frequent mood swings.",
    "Use difficult words.",
    "Don't mind being the center of attention.",
    "Feel others' emotions.",
    "Follow a schedule.",
    "Get irritated easily.",
    "Spend time reflecting on things.",
    "Am quiet around strangers.",
    "Make people feel at ease.",
    "Am exacting in my work.",
    "Often feel blue.",
    "Am full of ideas."
]

# Initialize the tensor with zeros
tensor = torch.zeros((5, 50))
labels=["Extraversion", "Agreeableness",  "Conscientiousness", "Emotional Stability" , "Intellect/Imagination"]

# Populate the tensor according to the instructions
# The mapping is as follows:
# 1+: Extraversion, 2-: Agreeableness (inversed), 3+: Conscientiousness, 4-: Emotional Stability (inversed), 5+: Intellect/Imagination
# We invert Agreeableness and Emotional Stability signs because a negative sign (-) in the input implies a positive trait for these dimensions

"""

Here is how to score IPIP scales:
 
For + keyed items, the response "Very Inaccurate" is assigned a value of 1, "Moderately Inaccurate" a value of 2, "Neither Inaccurate nor Accurate" a 3, "Moderately Accurate" a 4, and "Very Accurate" a value of 5.
 
For - keyed items, the response "Very Inaccurate" is assigned a value of 5, "Moderately Inaccurate" a value of 4, "Neither Inaccurate nor Accurate" a 3, "Moderately Accurate" a 2, and "Very Accurate" a value of 1.
 
Once numbers are assigned for all of the items in the scale, just sum all the values to obtain a total scale score.
"""

# Mapping input to the tensor
input_mapping = {
    1: [(1, +1), (6, -1), (11, +1), (16, -1), (21, +1), (26, -1), (31, +1), (36, -1), (41, +1), (46, -1)],
    2: [(2, -1), (7, +1), (12, -1), (17, +1), (22, -1), (27, +1), (32, -1), (37, +1), (42, +1), (47, +1)],
    3: [(3, +1), (8, -1), (13, +1), (18, -1), (23, +1), (28, -1), (33, +1), (38, -1), (43, +1), (48, +1)],
    4: [(4, -1), (9, +1), (14, -1), (19, +1), (24, -1), (29, -1), (34, -1), (39, -1), (44, -1), (49, -1)],
    5: [(5, +1), (10, -1), (15, +1), (20, -1), (25, +1), (30, -1), (35, +1), (40, +1), (45, +1), (50, +1)],
}

for label, updates in input_mapping.items():
    for index, value in updates:
        if value<0:
            tensor[label-1, index-1] = -value
        else:
            tensor[label-1, index-1] = value

for key,value in input_mapping.items():
    for x,y in value:
        sentences[x-1] = (sentences[x-1],y)

tensor=tensor.type(torch.LongTensor)


class correlationScore(BaseModel):
    correlation_score: float = Field(description="a correlation score between sentence1 and sentence2 following the instructions in the prompt")
    


model1 = ChatCohere(cohere_api_key=cohere_api_key,temperature=0,max_tokens=40)

# And a query intented to prompt a language model to populate the data structure.
#sentence1 = "I hate rainy days."
#sentence2 = "nothing makes me happier than rainy weather."
def get_correlation_score(sentence1: str, sentence2: str) -> correlationScore:
    # Set up a parser + inject instructions into the prompt template.
    parser = JsonOutputParser(pydantic_object=correlationScore)

    prompt1 = PromptTemplate(
        template="""
    Calculate the correlation score between two sentences, where -1 indicates maximum negative correlation (opposite meanings), and 1 indicates maximum positive correlation (similar or related meanings). Provide the correlation score based on the context and meaning of the sentences.
    "{format_instructions}"

    Sentence 1: "{sentence1}"
    Sentence 2: "{sentence2}"

    Provide the correlation score.
    """,
        input_variables=["sentence1", "sentence2"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt1 | model1 | parser

    ch=chain.invoke({"sentence1": sentence1, "sentence2": sentence2})
    return ch['correlation_score']

def convert_score_based_on_key(old_score: float, key: int) -> int:
    """
    Converts a score from a -1 to 1 scale to either a 1 to 5 scale or an inverted 5 to 1 scale
    based on the specified key.

    Parameters:
    - old_score: A float representing the score to convert, expected to be between -1 and 1.
    - key: An integer, where 1 indicates a direct conversion to a 1 to 5 scale, and -1 indicates
           an inverted conversion to a 5 to 1 scale.

    Returns:
    - An integer score on the specified scale.
    """
    # Define the old range
    old_min, old_max = -1, 1
    
    if key == 1:
        # Direct conversion to a 1 to 5 scale
        new_min, new_max = 1, 5
    elif key == -1:
        # Inverted conversion to a 5 to 1 scale
        new_min, new_max = 5, 1
    else:
        raise ValueError("Key must be 1 or -1")

    # Apply the linear transformation formula
    new_score = (old_score - old_min) * (new_max - new_min) / (old_max - old_min) + new_min

    # Round the result to the nearest whole number
    # Ensure the result is within the bounds of the target scale
    new_score = round(new_score)
    new_score = max(min(new_score, max(new_min, new_max)), min(new_min, new_max))

    return new_score




def apply_correlation(input: str, sentences: List[Tuple[str, int]]):
    correlation_scores = []
    call_interval = 60.0 / 19  # Calculate the interval in seconds to stay within the limit special to cohere

    for sentence in tqdm(sentences, desc="Calculating correlation scores"):  # Add tqdm loading bar
        start_time = time.time()  # Record the start time of the API call

        correlation_score = convert_score_based_on_key(get_correlation_score(input, sentence[0]),sentence[1]) # is value from 1 to 5 or 5 to 1 based on (sentence[1]: key)
        correlation_scores.append(correlation_score)

        end_time = time.time()  # Record the end time of the API call
        elapsed_time = end_time - start_time  # Calculate how long the API call took

        if elapsed_time < call_interval:
            time.sleep(call_interval - elapsed_time)  # Sleep to maintain the API call rate limit

    return torch.tensor(correlation_scores)


def get_personnality_scores(chunks:List[str])->List[torch.Tensor]:
    personality_scores = []
    for chunk in chunks:
        if chunk != '':
            sentence_scores= apply_correlation(chunk,sentences)
            personality_scores.append(tensor @ sentence_scores)
    return personality_scores


class Percentage:
    def __init__(self, value: float):
        if not (0 <= value <= 100):
            raise ValueError("Percentage value must be between 0 and 100")
        self.value = value

    def __str__(self):
        return f"{self.value}%"
    def __repr__(self):
        return f"{self.value:.2f}%"
    def __add__(self, other):
        if isinstance(other, Percentage):
            return Percentage(self.value + other.value)
        elif isinstance(other, (int, float)):
            return Percentage(self.value + other)
        else:
            raise TypeError("Unsupported operand type(s) for +: 'Percentage' and '{}'".format(type(other).__name__))
    
    def __radd__(self, other):
        return self.__add__(other)
    # get value of the percentage
    def get_value(self):
        return self.value
    # lets code the mean function
    def mean(self, percentages: List["Percentage"]):
        if isinstance(percentages, list):
            values = [p.value for p in percentages]
            values.append(self.value)
            x = sum(values) / len(values)
            return Percentage(x)
        else:
            raise TypeError("Unsupported operand type(s) for +: 'Percentage' and '{}'".format(type(values).__name__))




def get_personality_traits(chunks: List[str]) -> List[Tuple[str, Percentage]]:
    personality_scores = get_personnality_scores(chunks)
    traits_scores = [list(zip(labels, personality_scores[i])) for i in range(len(personality_scores))]
    output = [(a[0][0], Percentage(a[0][1]).mean([Percentage(a[i][1]) for i in range(len(traits_scores))]))  for a in zip(*traits_scores)]
    return output     # Example :  [('Extraversion', 30.67%),('Agreeableness', 31.33%),('Conscientiousness', 28.00%),('Emotional Stability', 29.00%),('Intellect/Imagination', 25.33%)]


model2 = ChatCohere(cohere_api_key=cohere_api_key,temperature=0.3)

# get items from json file called description
import json
with open('description.json') as f:
    items = json.load(f)
    print(type(items['items'])==list)

# And a query intented to prompt a language model to populate the data structure.
#sentence1 = "I hate rainy days."
#sentence2 = "nothing makes me happier than rainy weather."
def get_advice(scores : List[Tuple[str, Percentage]]):
    # Set up a parser + inject instructions into the prompt template.
    #parser = JsonOutputParser(pydantic_object=Advice)

    prompt = PromptTemplate(
        template="""
    Give advice based on the personality traits of the user, which are determined by the following scores:

    Scores: {scores}
    based on these items
    items: {items}

    Use markdown format to provide the advice.
    Provide the advice.
    """,
        input_variables=["scores","items"],
        #partial_variables={"format_instructions": parser.get_format_instructions()},   "{format_instructions}"
    )

    chain = prompt | model2

    ch=chain.invoke({"scores": scores, "items": items['items']})
    return ch

def save_img(i,personality_scores):
    results = personality_scores
    # Extracting factors and percentages
    factors = [result[0] for result in results]
    percentages = [result[1].value for result in results]
    plt.switch_backend('Agg') 

    # Plot
    plt.figure(figsize=(10, 6))
    plt.barh(factors, percentages, color=plt.cm.tab10.colors)
    plt.xlabel('Percentage')
    plt.title('Classification Results')
    plt.gca().invert_yaxis()
    plt.subplots_adjust(left=0.17, right=0.9, top=0.9, bottom=0.1)
    # Check if directory exists
    if not os.path.exists('imgs/'):
        os.makedirs('imgs/')


    plt.savefig(f'imgs/img{i}.png')

if __name__ == "__main__":
    i=0
    chunks = [
        "Yeah, every day feels like a slog through mud. Nothing brings joy anymore.",
    "It's been a constant battle, but mostly it's just been a blur of sadness and stress.",
    "Confidence? Ha, what's that? I'm just trying to make it through each day.",
    "Hopes and dreams? More like shattered illusions. The future looks bleak.",
    "Supported? I feel like I'm drowning, and no one's even noticed.",
    "Activities? Projects? They're just distractions, futile attempts to fill the void."
]


    personality_scores = get_personality_traits(chunks)
    personality_scores
    advice=get_advice(personality_scores)



    save_img(i,personality_scores)
    
    if not os.path.exists('output/'):
        os.makedirs('output/')


    # save content of advice to markdown file
    with open(f'output/advice{i}.md', 'w') as f:
        f.write(advice.content)

    # add the image at the end of the markdown file
    with open(f'output/advice{i}.md', 'a') as f:
        f.write(f'\n \n![alt text](imgs/img{i}.png)')