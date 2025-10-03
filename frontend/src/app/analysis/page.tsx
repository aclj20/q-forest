"use client";

import { useState } from "react";
import { Leaf, Home as HomeIcon } from "lucide-react";
import { FileUpload } from "@/components/qforest/file-upload";
import { AnalysisProgress } from "@/components/qforest/analysis-progress";
import { ResultsDashboard } from "@/components/qforest/results-dashboard";
import { Card, CardContent } from "@/components/ui/card";
import Link from "next/link";
import { Button } from "@/components/ui/button";

type Step = "upload" | "processing" | "results";

export default function AnalysisPage() {
  const [step, setStep] = useState<Step>("upload");
  const [file, setFile] = useState<File | null>(null);

  // Guardar archivo y avanzar al siguiente paso
  const handleStartAnalysis = (selectedFile: File) => {
    setFile(selectedFile);
    setStep("processing");
  };

  // Completar análisis y pasar a resultados
  const handleAnalysisComplete = () => {
    setStep("results");
  };

  // Reiniciar todo el flujo
  const handleRestart = () => {
    setFile(null);
    setStep("upload");
  };

  // Renderizar paso correspondiente
  const renderStep = () => {
    switch (step) {
      case "upload":
        return <FileUpload onStartAnalysis={handleStartAnalysis} />;
      case "processing":
        return file ? (
          <AnalysisProgress file={file} onAnalysisComplete={handleAnalysisComplete} />
        ) : null;
      case "results":
        return <ResultsDashboard onRestart={handleRestart} />;
      default:
        return <FileUpload onStartAnalysis={handleStartAnalysis} />;
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center bg-secondary/30 p-4 sm:p-8">
      <div className="w-full max-w-7xl mx-auto">
        <header className="flex justify-between items-center mb-8">
          <Link href="/" className="flex items-center gap-3">
            <div className="p-2 bg-background rounded-lg shadow-sm">
              <Leaf className="w-8 h-8 text-primary" />
            </div>
            <h1 className="text-4xl font-headline tracking-tight text-foreground hidden sm:block">
              QForest
            </h1>
          </Link>
          <p className="text-lg text-muted-foreground font-body hidden md:block">
            Análisis de Impacto de Reforestación Potenciado por IA
          </p>
          <Link href="/" className="">
            <Button variant="outline" className="bg-background">
              <HomeIcon className="h-4 w-4 sm:mr-2" />
              <span className="hidden sm:inline">Volver a la bienvenida</span>
            </Button>
          </Link>
        </header>

        <Card className="w-full shadow-lg border-none bg-card/80 backdrop-blur-lg">
          <CardContent className="p-4 sm:p-8">
            {renderStep()}
          </CardContent>
        </Card>

        <footer className="text-center mt-8 text-sm text-muted-foreground">
          <p>
            Sube una imagen satelital para comenzar tu análisis de reforestación.
          </p>
        </footer>
      </div>
    </main>
  );
}
