import React, { useState } from 'react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  className?: string;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading, className = '' }) => {
  const [entry, setEntry] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (entry.trim() && !isLoading) {
      onSendMessage(entry);
      setEntry('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className={`mt-6 ${className}`}>
      <div className="space-y-4">
        <div className="journal-page">
          <div className="date-header">
            <span className="text-gray-600">{new Date().toLocaleDateString('en-US', { 
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}</span>
          </div>
          <textarea
            id="journal-entry"
            rows={12}
            value={entry}
            onChange={(e) => setEntry(e.target.value)}
            placeholder="Dear Diary..."
            disabled={isLoading}
            className="w-full bg-transparent resize-none focus:outline-none"
          />
        </div>
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isLoading || !entry.trim()}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-purple-400 disabled:cursor-not-allowed transition-colors duration-200"
          >
            {isLoading ? 'Processing...' : 'Share Entry'}
          </button>
        </div>
      </div>
    </form>
  );
};

export default ChatInput;