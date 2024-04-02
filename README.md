# Personality Wellness Chatbot

This project is an implementation of a well-known personality test, where 50 questions are asked, and the answers are provided on a scale of 1 to 5, indicating the level of agreement with each statement. However, in this version, the format has been modified to include 10 open-ended questions, allowing users to express their stories and emotions freely.

## Project Overview

The main goal of this project is to analyze the user's responses and calculate scores for five different personality traits: Extraversion, Agreeableness, Conscientiousness, Emotional Stability, and Intellect/Imagination. These scores are then used to generate a personality profile, which can be helpful in various contexts, such as self-awareness, personal development, or even mental health assessments.

## Key Features

1. **User Input Collection**: A web interface is provided to collect user responses to the 10 open-ended questions. These responses are stored in a database for further processing.

2. **Response Chunking**: The user's responses are chunked into smaller segments to facilitate analysis.

3. **Correlation Scoring**: Each chunk of the user's response is compared against the original 50 statements using a custom language model prompt with a PyDantic parser. This process calculates a correlation score between the user's response and each statement, indicating the level of agreement or disagreement.

4. **Tensor Calculations**: The correlation scores are organized into a tensor data structure, which is then multiplied by a calculation matrix to determine the scores for the five personality traits.

5. **Personality Profile Generation**: The final personality scores are averaged across all response chunks, and a graphical representation of the user's personality profile is generated.

## Technologies Used

- Python
- Jupyter Notebook
- PyTorch
- LangChain
- Cohere AI (Language Model)
- Web Framework (e.g., Flask, Django) for the web interface

## Getting Started

1. Clone the repository
2. Install the required dependencies
3. Set up the necessary API keys and environment variables
4. Run the Jupyter Notebook to explore the code and calculations
5. Deploy the web interface to collect user responses
6. Run the analysis pipeline to generate personality profiles

## Contributing

Contributions to this project are welcome. If you find any issues or have suggestions for improvements, please create a new issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

This project was inspired by the well-known personality tests and the need for a more flexible and interactive approach to personality assessment.
