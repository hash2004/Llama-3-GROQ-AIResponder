# Llama-3-GROQ-AIResponder

The AI Philosophy Chatbot is a sophisticated conversational agent designed to engage users in discussions about artificial intelligence-related philosophy. This innovative application is built using Streamlit, providing a user-friendly interface that accommodates both speech and text input via OpenAI's Whisper technology.

## Features:

1. **Speech and Text Interaction**: Users can choose to interact with the chatbot using either speech or text, thanks to the integration of OpenAI's Whisper, ensuring accessibility and convenience.

2. **Efficient Query Processing with GROQ**: The chatbot leverages Llama3 accessed through GROQ, a cutting-edge technology developed by Twitter. GROQ uses NLUs instead of traditional GPUs, significantly enhancing query processing efficiency.

3. **Dynamic Context Management**: To handle memory limitations and maintain coherent conversations, the chatbot employs a secondary instance of Llama3, also accessed through GROQ. This instance is tasked with evaluating and updating the conversational context after each user interaction.

4. **Persistent Context Storage**: The updated context is stored in MongoDB, ensuring that the chatbot can maintain continuity in conversations over multiple interactions, providing a seamless and engaging user experience.

## DISCLAIMER 
This project is still in the BETA phase and might be prone to some inconsistencies. 

## Architecture 
The following picture is a high-level overview of the architecture. Its only purpose is to make the user understand what's going on in the back. 
![](https://github.com/hash2004/Llama-3-GROQ-AIResponder/blob/main/images/Architecture.png "Architecture"))

## License
This project is licensed under the [MIT License](https://opensource.org/license/MIT)- see the LICENSE file for details.
