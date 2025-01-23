# RAG-Chatbot Application with Python Django and Google Gemini API

This RAG-chatbot is a powerful Django application build using Google Gemini API that allows the user to have a conversation with multiple PDF Documents, by asking questions in natural language and the application will respond with relevant answers based on the uploaded documents.

## Overview of the App

- **Upload a PDF Document:** When the app is launched, you have to choose a document file from your directory that you want to know any information. Right after you choose the file, you need to type the title for the chosen file, then upload a PDF, and wait for it to finish.
  
- **Start Chatting:**  You need to select your file from the dropdown option containing other uploaded documents. you can ask any question related to the selected document, by typing in the text area and wait for the response.

- **Engaging in the Chat:** The app will provide you a response that is relevant and concise information immediately. Every query is answered instantly, providing precise information from your documents. You can ask multiple questions in the chat.

- **Chat History:** You can explore your previous chats in the Topics section, every chat will be stored which can be accessed anytime so that you can able to resume your chat. You can also delete your chat history.

- **Finding Text Chunk:** The app incorporates another feature that will let you search similar text chunks based on your question. You can ask the app any question on the documents and will find you the most similar text chunk related to the input questions.

## RAG - ChatBot Interface

The very first time the user launches the app, this will be the screen of the app.

![User_Interface]()

When the user asks a question, the model will give a response based on the question, the content that was retrieved from the database, and the chat history.

## Here’s a quick demo:

[![APP Demo](https://img.youtube.com/vi/jWK2ZX2foAs/0.jpg)](https://youtu.be/jWK2ZX2foAs)

## How it Works

![Project_Schema](images/project_schema.png)

The App lets the user to ask questions about the documents. the App searches the best response in the vector database and the content retrieved from the database is passed to the GEMINI model, which generates a response based on the question, chat history and content fro the vector database.

## Getting Started With Code

To use this app, you need a Google GEMINI API Key. To get the Google GEMINI API use this link [here](https://aistudio.google.com/app/apikey), then create a new API key by clicking the `Create API Key` option. After creating the API key, you need to copy it and paste the key in a new txt file or else where, so that you can put it in the `.env` file after creating it.

### Step 1: Clone repository to your local machine:
Clone the App repo in the local machine

```shell
 git clone https://github.com/EthixDev/rag_chatbot.git
```

### Step 2: Create .env file
Navigate to the app folder where the files README and requirements are located,

```shell
cd rag_chatbot
```
Then create `.env` file in the app folder.

Now, paste the API key that you generated into the quotation marks. It should look something like this:

```shell
GOOGLE_API_KEY = "apikey"
```
### Step 3: Install Packages
Before install packages, Create a virtual environment to access the dependencies.

```shell
python -m venv .venv
```

To activate the virtual environment:

```shell
source venv/bin/activate     # For linux
```
```shell
.venv/Scripts/activate       # For windows 
```

Open a terminal in this folder, write this to install all the requirements for the app:

```shell
pip install -r requirements.txt
```

### Step 4: Run the docker compose
In this same terminal, run this command to startup the app:

```shell
docker compose up --build
```

### Step 5: Run the App server
Open your web browser and visit the chatbot URL defined in your project's URL configuration (http://localhost:8080/). This should render your chatbot interface.
