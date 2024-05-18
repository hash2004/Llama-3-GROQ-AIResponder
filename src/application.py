import streamlit as st
from chatting import initialize_api_connections, run_chat
from speech_to_text import speech_to_text
from st_audiorec import st_audiorec


# Initialize API connections
llm, astra_vector_index = initialize_api_connections() 

# Check if the connections were successfully initialized
if not llm or not astra_vector_index:
    st.error("Failed to initialize API connections. Please check the logs for details.")
else:
    st.title("AI Chatbot with Khadija Mahmood")
    
    # Chat window and input options
    chat_container = st.container()
    input_container = st.container()
    input_mode = st.radio("Choose your input mode:", ("Text", "Speech"))

    # Initialize session state for conversation history if it does not exist
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # Function to update chat history and display using Markdown with styled text
    def update_chat(question, answer):
        st.session_state.chat_history.append(f'<span style="color:blue;">**You**: {question}</span>')
        st.session_state.chat_history.append(f'**Khadija**: {answer}')

    with input_container:
        if input_mode == "Text":
            user_input = st.text_input("Enter your question here:", key="user_input")
            submit_button = st.button("Send")
        elif input_mode == "Speech":
            # Record, save, and transcribe audio
            audio_data   = st_audiorec()
            st.audio(audio_data, format='audio/wav')
            submit_button = st.button("Process Speech")
            user_input = ""

            if submit_button and audio_data is not None:
                try:
                    user_input = speech_to_text(audio_data)
                    st.write(type(audio_data))
                    st.write(f"Recognized Text: {user_input}")
                except Exception as e:
                    st.error(f"Error in speech recognition: {str(e)}")

    if submit_button and user_input:
        if user_input.strip() == "quit":
            st.session_state.chat_history = []  # Reset the chat history
            st.experimental_rerun()
        elif user_input.strip() == "":
            st.warning("Please enter a question.")
        else:
            # Call the chat function and get the response
            try:
                answer = run_chat(llm, astra_vector_index, user_input)
                update_chat(user_input, answer)
            except Exception as e:
                st.error(f"Error processing your question: {str(e)}")

    # Display the entire chat history in a separate container
    with chat_container:
        st.markdown("---")
        for chat in st.session_state.chat_history:
            st.markdown(chat, unsafe_allow_html=True)

        # Clear Chat Button
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.experimental_rerun()
