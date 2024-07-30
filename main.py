
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import requests
import json
import functools
import gradio as gr
from decouple import config


api_key = config('API_KEY')
def getlocation(location):

   

    url = "https://ai-weather-by-meteosource.p.rapidapi.com/time_machine"

    querystring = {"lat":"37.81021","lon":"-122.42282","date":"2021-08-24","units":"auto"}

    headers = {
	"x-rapidapi-key": "c06be0f3e1mshe58bc1d1e7005dcp18858cjsnc768ca0b06c9",
	"x-rapidapi-host": "ai-weather-by-meteosource.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

   
    return response.json

def runchat(user_prompt):
    messages = [
      ChatMessage(role="user", content=user_prompt)
     ]
    tools = [
         {
        "type": "function",
        "function": {
            "name": "getlocation",
            "description": "Get the current temperature for a specific location  ",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, district, or ZIP code, e.g., San Francisco, CA",
                    }
                },
                "required": ["location"],
               },
            },
           }
         ]
    
    model = "mistral-large-latest"
      

    client = MistralClient(api_key=api_key)
    response = client.chat(
     model=model,
     messages=messages,
     tools=tools,
     tool_choice="auto"
      )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    if tool_calls:
        available_functions = {
            "getlocation": getlocation,
        }
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                location=function_args.get("location")
            )
  
    messages.append(ChatMessage(role="tool", 
                            name=function_name, 
                            content=user_prompt,
                            tool_call_id=tool_call.id)
                                  )

    second_response = client.chat(model=model, messages=messages)
    return second_response.choices[0].message.content
def gradio_interface(user_prompt):
    return runchat(user_prompt)

interface = gr.Interface(fn=gradio_interface, inputs="text", outputs="text")
interface.launch()

 

    
      