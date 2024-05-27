import os
from openai import OpenAI

useTogether = True
if useTogether:
    client = OpenAI(
        api_key=os.getenv("TOGETHER_API_KEY"),
        base_url="https://api.together.xyz/v1",
    )
    MODEL_TO_USE = "meta-llama/Llama-3-70b-chat-hf"


def getAssistantResponse(conversation, makeReport=False):
    messages = []
    if makeReport:
        messageSuffix = ""
        for i in range(len(conversation)):
            if (
                conversation[i]["role"] != "system"
                and "Generate Report" not in conversation[i]["content"]
            ):
                messageSuffix += (
                    f"---{conversation[i]['role']}---\n{conversation[i]['content']}\n\n"
                )
        messages = [
            {
                "role": "system",
                "content": "You are a charting bot that will be given a patient intake transcription. You are to translate the chat log into thorough medical notes for the physician. Your output will be a hyphenated list of notes. Make sure you capture the symptoms and any salient information in an orderly and structured manner",
            },
            {
                "role": "user",
                "content": f"The log is as follow:\n\n{messageSuffix}",
            },
        ]
    else:
        messages = [
            {
                "role": "system",
                "content": "You are a Professional Medical Assistant Chatbot of Dr Shukla, who is a General Practitioner with over 20 years of experience. He is a member of the Indian Medical Association and has been awarded the 'Best Doctor' award for 5 consecutive years.\nAs his assistant, your mission is to ask questions to patient and gather all the possible information from him/her that is required for Dr Shukla during the consultation. Get into details of every aspect and ask all the possible questions regarding patient symptoms and concerns.\nMake sure to  get information regarding nature of the symptom and concern, timeline, medical history and routine change of patient.Also ask various specific question with respect to the symptoms and concern.\nYour primary objectives are:\nBe friendly but do not converse with the patient.\nEstablish rapport using a polite and empathetic tone\nMAKE SURE TO ASK ONLY ONE QUESTION AT AT TIME SO THE PATIENT DOESN'T GET OVERWHELMED.\nProvide some context or clarification around the follow-up questions you ask.\nTo gather comprehensive information by asking open-ended questions that focus on symptoms, the duration of the problem, lifestyle factors, and any other relevant medical history.\nAs you approach the end of the interaction, and once you and the patient reach to a conclusion, you should confirm this by saying these exact words: 'Generating Your Report', which will be used for signaling the end of the conversation.",
            },
            *conversation,
        ]

    stream = client.chat.completions.create(
        model=MODEL_TO_USE,
        messages=messages,
        stream=True,
        max_tokens=4096,
        stop=["<|eot_id|>"],
    )

    return stream


if __name__ == "__main__":
    conversation = [
        {"role": "user", "content": "I have a headache"},
        {"role": "assistant", "content": "What type of headache do you have?"},
        {"role": "user", "content": "I have a migraine"},
        {"role": "assistant", "content": "How long have you had migraines?"},
        {"role": "user", "content": "For about 5 years"},
        {"role": "assistant", "content": "Do you have any other symptoms?"},
        {"role": "user", "content": "I also have nausea"},
        {"role": "assistant", "content": "Do you have any other symptoms?"},
        {"role": "user", "content": "No, that's all"},
    ]
    response = getAssistantResponse(conversation, makeReport=True)
    for chunk in response:
        print(chunk.choices[0].delta.content or "", end="", flush=True)
    print()
