import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm">
      <div className="container mx-auto max-w-4xl p-6">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-purple-600">
            MoodScribe 🌟
          </h1>
          <p className="text-gray-600">
            Empathetic Digital Journal
          </p>
        </div>
      </div>
    </header>
  );
};

export default Header;