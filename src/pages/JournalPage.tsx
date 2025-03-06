import { useState, useRef, useEffect } from 'react';
import Header from '../components/Header';
import ChatWindow from '../components/ChatWindow';
import ChatInput from '../components/ChatInput';
import { Message } from '../types';
import { sendMessage } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { getConversationHistory } from '../services/api';

function JournalPage() {
  const [entries, setEntries] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasFirstEntry, setHasFirstEntry] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user } = useAuth();

  useEffect(() => {
    // Load user's conversation history when component mounts
    if (user?.id) {
      getConversationHistory(user.id)
        .then(history => setEntries(history))
        .catch(error => console.error('Error loading history:', error));
    }
  }, [user]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [entries]);

  const handleJournalEntry = async (entry: string) => {
    if (!user?.id) return; // Prevent entries without user ID
    
    setHasFirstEntry(true);
    const timestamp = new Date().toISOString();
    
    try {
      setEntries(prev => [...prev, { 
        role: 'user', 
        content: entry,
        timestamp 
      }]);
      setIsLoading(true);

      const response = await sendMessage(entry, timestamp, user.id); // Pass user ID
      setEntries(prev => [...prev, response]);
    } catch (error) {
      console.error('Error:', error);
      setEntries(prev => [...prev, { 
        role: 'assistant', 
        content: "I apologize, but I'm having trouble processing your entry right now. Please try again later.",
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-purple-50 via-white to-purple-50">
      <Header />
      
      <main className="flex-1 container mx-auto max-w-4xl p-6 flex flex-col">
        {!hasFirstEntry && !isLoading ? (
          <div className="flex-1 flex items-center">
            <ChatInput 
              onSendMessage={handleJournalEntry}
              isLoading={isLoading}
              className="w-full"
            />
          </div>
        ) : (
          <>
            <ChatWindow 
              messages={entries}
              isLoading={isLoading}
              messagesEndRef={messagesEndRef}
            />
            <ChatInput 
              onSendMessage={handleJournalEntry}
              isLoading={isLoading}
            />
          </>
        )}
      </main>
    </div>
  );
}

export default JournalPage; 