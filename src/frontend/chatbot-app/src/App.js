import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
import './App.css';

/*
React Chat Interface:
- Chat UI with React, supporting Markdown in bot responses.
- Axios for backend communication.
- Error handling for message sending.
*/


function App() {
    const [input, setInput] = useState('');
    const [conversation, setConversation] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const messageEndRef = useRef(null);

    const scrollToBottom = () => {
        messageEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };
    useEffect(scrollToBottom, [conversation]);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const message = { author: 'user', content: input };
        setConversation([...conversation, message]);
        setIsLoading(true);

        try {
            const response = await axios.post('http://localhost:8000/chat/', { text: input });
            const botResponse = { author: 'bot', content: response.data.response };
            setConversation([...conversation, message, botResponse]);
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = { author: 'bot', content: 'Error processing your message. Please try again.' };
            setConversation([...conversation, message, errorMessage]);
        }
        
        setIsLoading(false);
        setInput('');
    };

    return (
        <div className="App">
            <header className="App-header">
              <h1>Intelligent Document Assistant</h1>
            </header>
            <div className="chat-container">
                {conversation.map((message, idx) => (
                    <div key={idx} className={`message ${message.author}`}>
                        {message.author === 'bot' ? <ReactMarkdown>{message.content}</ReactMarkdown> : message.content}
                    </div>
                ))}
                 <div ref={messageEndRef} />
                {isLoading && <div className="loading-indicator">Typing...</div>}
            </div>
            <div className="input-area">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Type your message here..."
                />
                <button onClick={sendMessage}>Send</button>
            </div>
        </div>
    );
}

export default App;
