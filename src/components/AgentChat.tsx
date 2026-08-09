import { useState, useRef, useEffect } from 'react';
import { Bot, X, Send, Loader2, ChevronDown, Mountain, Maximize2, Minimize2, Sparkles, RefreshCw } from 'lucide-react';

interface Message {
  role: 'user' | 'agent';
  text: string;
  resorts?: Array<{ name: string; snowMountain: number }>;
  loading?: boolean;
}

const EXAMPLE_QUERIES = [
  '🇦🇹 Suche ein Gebiet in Österreich mit ≥ 50cm Schnee & maximal geöffneten Liften',
  '🚗 Suche ein Gebiet mit Fahrtzeit unter 3h ab München und frischem Neuschnee',
  '⚡ Zeige Top Powder-Spots mit viel Neuschnee & hohem Shred Score',
  '🏔️ Beste Pistenbedingungen mit geringer Lawinenwarnstufe',
];

export const AgentChat = () => {
  const [open, setOpen] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'agent',
      text: 'Hallo! Ich bin dein intelligenter Ski-Trip-Agent 🎿 Frage mich nach maßgeschneiderten Skigebieten – zum Beispiel nach Fahrtzeiten ab München, Kombinationen aus Neuschnee & geöffneten Liften oder Shred Scores!',
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 100);
    } else {
      setIsFullscreen(false);
    }
  }, [open]);

  const sendMessage = async (text?: string) => {
    const msg = (text ?? input).trim();
    if (!msg || isLoading) return;
    setInput('');

    const userMessage: Message = { role: 'user', text: msg };
    const loadingMessage: Message = { role: 'agent', text: '', loading: true };
    setMessages((prev) => [...prev, userMessage, loadingMessage]);
    setIsLoading(true);

    try {
      const res = await fetch('/api/agent/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg }),
      });

      if (!res.ok || !res.body) {
        // Fallback to standard endpoint
        const fallbackRes = await fetch('/api/agent', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: msg }),
        });
        const data = await fallbackRes.json();
        setMessages((prev) => [
          ...prev.slice(0, -1),
          { role: 'agent', text: data.answer || 'Keine Antwort erhalten.', loading: false },
        ]);
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let accumulatedText = '';
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data: ')) {
            const dataStr = trimmed.slice(6);
            if (dataStr === '[DONE]') continue;
            try {
              const parsed = JSON.parse(dataStr);
              if (parsed.text) {
                accumulatedText += parsed.text;
                setMessages((prev) => [
                  ...prev.slice(0, -1),
                  { role: 'agent', text: accumulatedText, loading: false },
                ]);
              }
            } catch {
              // Ignore partial chunks
            }
          }
        }
      }

      if (!accumulatedText) {
        setMessages((prev) => [
          ...prev.slice(0, -1),
          { role: 'agent', text: 'Keine Antwort erhalten.', loading: false },
        ]);
      }
    } catch (e: unknown) {
      const errorText = e instanceof Error ? e.message : 'Unbekannter Fehler';
      setMessages((prev) => [
        ...prev.slice(0, -1),
        { role: 'agent', text: `⚠️ Fehler: ${errorText}`, loading: false },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        role: 'agent',
        text: 'Hallo! Ich bin dein intelligenter Ski-Trip-Agent 🎿 Stelle mir eine Frage zu Skigebieten!',
      },
    ]);
  };

  return (
    <>
      {/* Floating toggle button */}
      <button
        id="agent-chat-toggle"
        onClick={() => setOpen((o) => !o)}
        aria-label="Agent Chat öffnen"
        className={`fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-3 rounded-full shadow-2xl text-white font-semibold text-sm transition-all duration-300 ${
          open
            ? 'bg-slate-700 hover:bg-slate-800'
            : 'bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-500 hover:scale-105 hover:shadow-cyan-500/30'
        }`}
      >
        {open ? (
          <>
            <ChevronDown className="w-4 h-4" />
            Schließen
          </>
        ) : (
          <>
            <Bot className="w-5 h-5 animate-pulse" />
            <span>Ski-Agent</span>
            <Sparkles className="w-3.5 h-3.5 text-yellow-300" />
          </>
        )}
      </button>

      {/* Dark backdrop overlay for full screen mode */}
      {open && isFullscreen && (
        <div
          className="fixed inset-0 bg-slate-950/70 backdrop-blur-md z-40 transition-opacity duration-300 animate-in fade-in"
          onClick={() => setIsFullscreen(false)}
        />
      )}

      {/* Chat container */}
      <div
        className={`fixed z-50 flex flex-col overflow-hidden bg-background border border-border/80 shadow-2xl transition-all duration-300 ${
          open ? 'opacity-100 scale-100 pointer-events-auto' : 'opacity-0 scale-95 pointer-events-none'
        } ${
          isFullscreen
            ? 'inset-4 sm:inset-8 md:inset-12 lg:inset-16 rounded-3xl'
            : 'bottom-20 right-6 w-[420px] max-w-[calc(100vw-2rem)] h-[560px] max-h-[82vh] rounded-2xl origin-bottom-right'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3.5 bg-gradient-to-r from-blue-700 via-indigo-700 to-cyan-600 text-white shrink-0 shadow-md">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-white/10 backdrop-blur-sm">
              <Mountain className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm tracking-wide">Ski-Trip Assistant</span>
                <span className="text-[10px] font-semibold tracking-wider uppercase opacity-90 bg-white/20 px-2 py-0.5 rounded-full">
                  Gemini 3.5
                </span>
              </div>
              <p className="text-[11px] opacity-80 font-normal">Intelligente Skigebiets-Suche & Beratung</p>
            </div>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={clearChat}
              title="Chat zurücksetzen"
              aria-label="Chat zurücksetzen"
              className="p-1.5 rounded-lg hover:bg-white/20 transition-colors opacity-80 hover:opacity-100"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsFullscreen((f) => !f)}
              title={isFullscreen ? 'Verkleinern' : 'Vollbild öffnen'}
              aria-label={isFullscreen ? 'Verkleinern' : 'Vollbild'}
              className="p-1.5 rounded-lg hover:bg-white/20 transition-colors opacity-80 hover:opacity-100"
            >
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>
            <button
              onClick={() => setOpen(false)}
              aria-label="Schließen"
              className="p-1.5 rounded-lg hover:bg-white/20 transition-colors opacity-80 hover:opacity-100"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Messages list */}
        <div
          className={`flex-1 overflow-y-auto px-4 py-4 space-y-4 min-h-0 bg-gradient-to-b from-background to-muted/20 ${
            isFullscreen ? 'max-w-4xl mx-auto w-full px-6 py-6 space-y-5' : ''
          }`}
        >
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`rounded-2xl px-4 py-3 text-sm shadow-sm transition-all ${
                  isFullscreen ? 'max-w-[80%]' : 'max-w-[88%]'
                } ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white rounded-br-xs'
                    : 'bg-muted/80 backdrop-blur-sm border border-border/50 text-foreground rounded-bl-xs'
                }`}
              >
                {msg.loading && !msg.text ? (
                  <span className="flex items-center gap-2 text-muted-foreground italic">
                    <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                    Analysiere Skigebiete & Daten…
                  </span>
                ) : (
                  <>
                    <p className="whitespace-pre-wrap leading-relaxed font-normal">{msg.text}</p>
                    {/* Resort result cards if present */}
                    {msg.resorts && msg.resorts.length > 0 && (
                      <div className="mt-3 space-y-1.5 border-t border-border/40 pt-2">
                        {msg.resorts.slice(0, 5).map((r, ri) => (
                          <div
                            key={ri}
                            className="flex items-center justify-between bg-background/80 rounded-xl px-3 py-2 text-xs border border-border/60 shadow-2xs hover:border-blue-300 transition-colors"
                          >
                            <span className="font-semibold truncate text-foreground">{r.name}</span>
                            <span className="ml-2 shrink-0 font-bold text-cyan-600 dark:text-cyan-400 bg-cyan-50 dark:bg-cyan-950/60 px-2 py-0.5 rounded-md">
                              {r.snowMountain} cm
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        {/* Meaningful example prompts */}
        {messages.length === 1 && (
          <div
            className={`px-4 pb-3 pt-1 flex flex-col gap-2 shrink-0 border-t border-border/40 bg-muted/10 ${
              isFullscreen ? 'max-w-4xl mx-auto w-full px-6' : ''
            }`}
          >
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-medium">
              <Sparkles className="w-3.5 h-3.5 text-amber-500" />
              <span>Vorgeschlagene Fragen:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_QUERIES.map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="text-xs px-3 py-1.5 rounded-xl bg-background hover:bg-blue-50 dark:hover:bg-blue-950/60 text-foreground border border-border/80 hover:border-blue-300 dark:hover:border-blue-700 shadow-2xs transition-all text-left"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input box */}
        <div
          className={`p-3 border-t border-border/60 bg-background shrink-0 ${
            isFullscreen ? 'max-w-4xl mx-auto w-full p-4' : ''
          }`}
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              sendMessage();
            }}
            className="flex items-center gap-2"
          >
            <input
              ref={inputRef}
              id="agent-chat-input"
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Frage nach Schneehöhe, Fahrtzeit, Liften..."
              disabled={isLoading}
              className="flex-1 text-sm bg-muted/60 rounded-xl px-4 py-2.5 outline-none border border-border/60 focus:border-blue-500 focus:bg-background transition-all placeholder:text-muted-foreground disabled:opacity-50"
            />
            <button
              id="agent-chat-send"
              type="submit"
              disabled={isLoading || !input.trim()}
              aria-label="Senden"
              className="p-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm shrink-0"
            >
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </button>
          </form>
        </div>
      </div>
    </>
  );
};
