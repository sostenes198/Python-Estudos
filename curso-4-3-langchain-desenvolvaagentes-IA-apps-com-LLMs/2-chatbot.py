import openai
import dotenv

dotenv.load_dotenv()

client = openai.Client()


def text_generator(messages):
    answer = client.chat.completions.create(
        messages=messages,
        model='gpt-3.5-turbo-0125',
        max_tokens=1000,
        stream=True
    )
    print('Bot: ', end="\n\n")

    completed_text = ""

    for answer_stream in answer:
        text = answer_stream.choices[0].delta.content
        if text:
            print(text, end="")
            completed_text += text
    print()
    messages.append({"role": "assistant", "content": completed_text})
    return messages


if __name__ == '__main__':
    print("Welcome to soso ChatBot")
    messages = []
    while True:
        in_user = input("User: ")
        messages.append({"role": "user", "content": in_user})
        messages = text_generator(messages)
