import React from 'react';
import { Message } from '../types';

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  messagesEndRef: React.RefObject<HTMLDivElement>;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ messages, isLoading, messagesEndRef }) => {
  const formatDate = (timestamp?: string) => {
    if (!timestamp) {
      return {
        date: new Date().toLocaleDateString('en-US', { 
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        }),
        time: new Date().toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit'
        })
      };
    }

    const date = new Date(timestamp);
    return {
      date: date.toLocaleDateString('en-US', { 
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      }),
      time: date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      })
    };
  };

  return (
    <div className="flex-1 overflow-y-auto animate-fade-in space-y-8">
      {messages.map((message, index) => (
        <div key={index}>
          {message.role === 'user' ? (
            <div className="journal-page">
              <div className="date-header flex justify-between items-center">
                <span className="text-gray-600">
                  {formatDate(message.timestamp).date}
                </span>
                <span className="text-gray-500 text-sm pr-4">
                  {formatDate(message.timestamp).time}
                </span>
              </div>
              <div className="diary-entry">
                {(message.content || '').split('\n').map((paragraph, i) => (
                  <div key={i} className="diary-line">{paragraph}</div>
                ))}
              </div>
            </div>
          ) : (
            <div className="response-box">
              <div className="flex items-center mb-2">
                <span className="text-lg font-semibold text-purple-600">Joy 🌟</span>
              </div>
              <div className="prose max-w-none">
                {message.content.split('\n').map((paragraph, i) => (
                  <p key={i} className="text-gray-700 leading-relaxed mb-4">
                    {paragraph}
                  </p>
                ))}
              </div>
            </div>
          )}
        </div>
      ))}
      {isLoading && (
        <div className="response-box animate-pulse">
          <div className="flex items-center">
            <span className="text-lg font-semibold text-purple-600">Joy 🌟</span>
            <span className="ml-2 text-sm text-gray-500">is writing a response...</span>
          </div>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatWindow;