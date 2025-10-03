"use client";

import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Bot, Loader2, Send, User } from 'lucide-react';
import { analyzeReforestationData, AnalyzeReforestationDataInput } from '@/ai/flows/analyze-reforestation-data';
import { generateInitialAnalysis } from '@/ai/flows/generate-initial-analysis';
import metricsData from '@/data/metrics.json';
import { useToast } from '@/hooks/use-toast';

type Message = {
  role: 'user' | 'assistant';
  content: string;
};

export function ResultsChatbot() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // This single effect handles the initial analysis generation on mount.
    const fetchInitialAnalysis = async () => {
      setIsLoading(true);
      try {
        const result = await generateInitialAnalysis({
          totalCost: metricsData.totalCost,
          potentialCO2Impact: metricsData.potentialCO2Impact,
          optimizedAreas: metricsData.optimizedAreas,
        });
        setMessages([{ role: 'assistant', content: result.analysis }]);
      } catch (error) {
        console.error("Initial analysis error:", error);
        toast({
          variant: 'destructive',
          title: 'Error de Análisis Inicial',
          description: 'No se pudo generar el resumen inicial. Por favor, intenta de nuevo más tarde.',
        });
        setMessages([{ role: 'assistant', content: 'Lo siento, no pude generar el análisis inicial en este momento. Aún puedes hacerme preguntas sobre las métricas.' }]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchInitialAnalysis();
  }, [toast]);
  
  useEffect(() => {
    // This effect scrolls to the bottom of the chat on new messages.
    if (scrollAreaRef.current) {
        const viewport = scrollAreaRef.current.querySelector<HTMLDivElement>('div');
        if (viewport) {
          viewport.scrollTop = viewport.scrollHeight;
        }
    }
  }, [messages]);


  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const chatInput: AnalyzeReforestationDataInput = {
        metrics: metricsData,
        question: input,
      };
      const result = await analyzeReforestationData(chatInput);
      const assistantMessage: Message = { role: 'assistant', content: result.answer };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Chatbot error:", error);
      toast({
        variant: 'destructive',
        title: 'Error del Chatbot',
        description: 'No se pudo obtener una respuesta. Inténtalo de nuevo.',
      });
      const assistantMessage: Message = { role: 'assistant', content: "Lo siento, tuve un problema para responder. Por favor, intenta de nuevo." };
      setMessages((prev) => [...prev, assistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="shadow-lg bg-card h-[500px] flex flex-col">
      <CardHeader>
        <CardTitle className="flex items-center">
          <Bot className="mr-2 h-6 w-6 text-primary" />
          Chatea con tus Resultados
        </CardTitle>
        <CardDescription>
          Haz preguntas sobre tu análisis de reforestación.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex-grow flex flex-col p-0">
        <ScrollArea className="flex-grow p-4 md:p-6" ref={scrollAreaRef}>
          <div className="space-y-4">
            {isLoading && messages.length === 0 && (
               <div className="flex flex-col items-center justify-center text-center text-muted-foreground p-8">
                  <Loader2 className="w-8 h-8 animate-spin text-primary mb-4" />
                  <p>Generando análisis inicial...</p>
              </div>
            )}
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex items-start gap-3 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' ? (
                  <Bot className="w-6 h-6 text-primary flex-shrink-0" />
                ) : (
                  <User className="w-6 h-6 text-muted-foreground flex-shrink-0" />
                )}
                <div
                  className={`max-w-[85%] rounded-lg px-3 py-2 text-sm ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-secondary text-secondary-foreground'
                  }`}
                >
                  {message.content}
                </div>
              </div>
            ))}
            {isLoading && messages.length > 0 && (
               <div className="flex items-start gap-3 justify-start">
                  <Bot className="w-6 h-6 text-primary flex-shrink-0" />
                  <div className="max-w-[85%] rounded-lg px-3 py-2 text-sm bg-secondary">
                      <Loader2 className="w-5 h-5 animate-spin text-primary" />
                  </div>
              </div>
            )}
          </div>
        </ScrollArea>
        <div className="p-4 border-t bg-background">
          <form onSubmit={handleSendMessage} className="flex items-center gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ej: ¿Cuál es el costo total?"
              disabled={isLoading}
              className="bg-secondary/40"
            />
            <Button type="submit" size="icon" disabled={isLoading || !input.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </CardContent>
    </Card>
  );
}
