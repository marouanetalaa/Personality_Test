import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from advice import get_personality_traits, get_advice, save_img
import os
from dotenv import load_dotenv

def process_answers(answers,password):
    name = answers.get('0', '')
    chunks = [
        answers.get('3', ''),
        answers.get('4', ''),
        answers.get('5', ''),
        answers.get('6', ''),
        answers.get('7', ''),
        answers.get('8', ''),
        answers.get('9', '')
    ]

    if name:
        print(f"Hello, {name}!")

        i = answers.get('id', 0)
        personality_scores = get_personality_traits(chunks)
        print(f"Personality scores: {personality_scores}")

        advice = get_advice(personality_scores)
        save_img(i, personality_scores)

        if not os.path.exists('output/'):
            os.makedirs('output/')

        # save content of advice to markdown file
        with open(f'output/advice{i}.md', 'w') as f:
            f.write(advice.content)

        # add the image at the end of the markdown file
        with open(f'output/advice{i}.md', 'a') as f:
            f.write(f'\n \n![alt text](imgs/img{i}.png)')

        

        # Send the file in an email
        email = answers.get('2', '')
        return send_email(email, f'output/advice{i}.md',password)

    

def send_email(recipient, file_path,password):
    
    
    # Email configuration
    sender_email = "marouane.dev.debug@gmail.com"
    sender_password = password
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Create message
    msg = MIMEMultipart()
    msg['Subject'] = "Your Personalized Advice"
    msg['From'] = sender_email
    msg['To'] = recipient

    # Attach file
    with open(file_path, 'r') as f:
        body = f.read()
    msg.attach(MIMEText(body, 'plain'))

    # Send email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print(f"Email sent to {recipient}")
            return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


if __name__ == "__main__":
    answers = {
        '0': 'John Doe',
        '1': '24',
        '2': 'marouanetalaa101@gmail.com',
        '3': "Yeah, every day feels like a slog through mud. Nothing brings joy anymore, It's been a constant battle, but mostly it's just been a blur of sadness and stress, Confidence? Ha, what's that? I'm just trying to make it through each day.",
        '4': "Hopes and dreams? More like shattered illusions. The future looks bleak, Supported? I feel like I'm drowning, and no one's even noticed, Activities? Projects? They're just distractions, futile attempts to fill the void.",
        'id': 0

    }
    i=0
    load_dotenv()
    password=os.getenv("EMAIL_PASSWORD")

    process_answers(answers,password)