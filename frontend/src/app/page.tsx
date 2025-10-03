import Link from 'next/link';
import { Leaf, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Image from 'next/image';

export default function WelcomePage() {
  return (
    <div className="relative min-h-screen w-full">
      <div className="absolute inset-0 z-0">
          <Image
              src="https://images.unsplash.com/photo-1448375240586-882707db888b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3NDE5ODJ8MHwxfHNlYXJjaHwyfHxkYXJrJTIwZm9yZXN0fGVufDB8fHx8MTc2MDMzMDIyNHww&ixlib=rb-4.1.0&q=80&w=1920"
              alt="Deep forest background"
              fill
              className="object-cover"
              data-ai-hint="dark forest"
          />
          <div className="absolute inset-0 bg-background/80 backdrop-blur-sm"></div>
      </div>
      <main className="relative z-10 flex min-h-screen flex-col items-center justify-center p-4 sm:p-8">
        <div className="w-full max-w-4xl mx-auto flex flex-col items-center text-center">
          <header className="mb-12">
            <div className="inline-flex items-center gap-4 mb-4">
              <div className="p-3 bg-primary/10 rounded-full">
                <Leaf className="w-12 h-12 text-primary" />
              </div>
              <h1 className="text-6xl md:text-7xl font-headline tracking-tight text-foreground">
                QForest
              </h1>
            </div>
            <p className="text-xl text-muted-foreground font-body max-w-3xl mx-auto">
              Bienvenido al futuro del análisis de reforestación. Utilice el poder de la IA para obtener información invaluable y optimizar su impacto ambiental.
            </p>
          </header>
          
          <Link href="/analysis">
            <Button size="lg" className="group text-lg py-7 px-10 shadow-lg shadow-primary/20">
              Empecemos
              <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
            </Button>
          </Link>
          
          <footer className="text-center mt-16 text-sm text-muted-foreground">
            <p>
              Transformando datos en árboles.
            </p>
          </footer>
        </div>
      </main>
    </div>
  );
}
