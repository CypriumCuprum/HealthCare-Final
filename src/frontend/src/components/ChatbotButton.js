import React from 'react';
import { Button } from 'react-bootstrap';
import { FaRobot } from 'react-icons/fa';
import './ChatbotButton.css';

const ChatbotButton = () => {
  const handleClick = () => {
    // redirect to the chatbot page
    // window.open('http://localhost:5000', '_blank', 'width=800,height=600');
    window.location.href = 'http://localhost:5000';
  };

  return (
    <Button
      className="chatbot-button"
      onClick={handleClick}
      variant="primary"
      title="Chat with our AI Assistant"
    >
      <FaRobot className="chatbot-icon" />
    </Button>
  );
};

export default ChatbotButton; 