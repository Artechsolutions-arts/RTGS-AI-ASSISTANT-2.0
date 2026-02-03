'use client';

import { useEffect } from 'react';
import { useVoiceStore } from '@/store/voiceStore';

export function VoiceToggle() {
  const { enabled, listening, language, toggle, setListening, setLanguage } = useVoiceStore();

  useEffect(() => {
    if (!enabled) {
      setListening(false);
      return;
    }

    // Initialize Web Speech API
    if (typeof window === 'undefined') return;

    const SpeechRecognition = (window as any).SpeechRecognition || 
                             (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn('Speech Recognition not supported');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = language === 'te' ? 'te-IN' : 'en-IN';

    const synth = window.speechSynthesis;

    // Greet user when enabled
    const greet = () => {
      const greeting = language === 'te' 
        ? 'వాయిస్ అసిస్టెంట్ ప్రారంభించబడింది. మీరు ఏమి సహాయం కావాలి?'
        : 'Voice assistant activated. How can I help you?';
      
      const utterance = new SpeechSynthesisUtterance(greeting);
      utterance.lang = language === 'te' ? 'te-IN' : 'en-IN';
      synth.speak(utterance);
    };

    // Start listening
    const startListening = () => {
      try {
        recognition.start();
        setListening(true);
        greet();
      } catch (error) {
        console.error('Failed to start recognition:', error);
      }
    };

    recognition.onstart = () => {
      setListening(true);
    };

    recognition.onend = () => {
      setListening(false);
      if (enabled) {
        // Restart if still enabled
        setTimeout(() => {
          try {
            recognition.start();
          } catch (error) {
            // Ignore if already started
          }
        }, 100);
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setListening(false);
    };

    recognition.onresult = (event: any) => {
      const transcript = event.results[event.results.length - 1][0].transcript;
      console.log('Voice command:', transcript);
      
      // Process voice commands here
      // This would integrate with chatbot or dashboard actions
    };

    if (enabled) {
      startListening();
    }

    return () => {
      recognition.stop();
      synth.cancel();
      setListening(false);
    };
  }, [enabled, language, setListening]);

  return (
    <div className="flex items-center space-x-2">
      <button
        onClick={toggle}
        className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
          enabled
            ? 'bg-gov-secondary text-white hover:bg-teal-700'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        }`}
        title={enabled ? 'Disable Voice Assistant' : 'Enable Voice Assistant'}
      >
        🎤 Voice Assistant {enabled ? 'ON' : 'OFF'}
        {listening && <span className="ml-2 animate-pulse">●</span>}
      </button>
      
      {enabled && (
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value as 'en' | 'te')}
          className="px-2 py-1 text-sm border border-gov-border rounded"
        >
          <option value="en">English</option>
          <option value="te">తెలుగు</option>
        </select>
      )}
    </div>
  );
}
