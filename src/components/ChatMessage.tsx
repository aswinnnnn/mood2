import React from 'react';
import { Message } from '../types';

interface ChatMessageProps {
  message: Message;
}

function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-lg p-4 ${
          isUser
            ? 'bg-purple-600 text-white rounded-br-none'
            : 'bg-gray-100 text-gray-800 rounded-bl-none'
        }`}
      >
        {!isUser && <div className="font-medium mb-1">Joy 🌟</div>}
        <div className="whitespace-pre-wrap">{message.content}</div>
      </div>
    </div>
  );
}

export default ChatMessage;