import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def CompletionCall(
        prompt,
        model='gpt-3.5-turbo-instruct',
        max_tokens=300,
        temperature=0
):
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature
    )

    return response['choices'][0]['text'], response

def ChatCompletionCall(
        prompt,
        model='gpt-3.5-turbo',
        max_tokens=300,
        temperature=0
):
    messages=[
        {"role": "system", "content": "You are a helpful assistant. You job is to navigate in a unknown environment to find a certain object  with shortest path possible. Be consice with your response."},
        {"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )

    return response.choices[0].message['content'], response
