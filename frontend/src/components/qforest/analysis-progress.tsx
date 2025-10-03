"use client";

import { useState, useEffect } from "react";
import { Progress } from "@/components/ui/progress";
import { Loader2 } from "lucide-react";

interface AnalysisProgressProps {
  file: File;
  onAnalysisComplete: (
    visualizationUrl: string,
    stats: any,
    files?: any
  ) => void;
}

const statusMessages = [
  { progress: 10, message: "Inicializando motor de análisis..." },
  { progress: 25, message: "Preprocesando imágenes satelitales..." },
  { progress: 50, message: "Identificando zonas potenciales de reforestación..." },
  { progress: 75, message: "Calculando impacto de CO2 y métricas de costo..." },
  { progress: 90, message: "Optimizando patrones de uso de la tierra..." },
  { progress: 100, message: "Finalizando reporte y generando insights..." },
];

export function AnalysisProgress({ file, onAnalysisComplete }: AnalysisProgressProps) {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("Preparando...");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let messageIndex = 0;

    const interval = setInterval(() => {
      if (messageIndex < statusMessages.length) {
        const current = statusMessages[messageIndex];
        setProgress(current.progress);
        setStatus(current.message);
        messageIndex++;
      }
    }, 800);

    const sendImage = async () => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("nodes", "36");
      formData.append("budget", "200");

      try {
        const res = await fetch("http://localhost:8000/optimize/full-pipeline", {
          method: "POST",
          body: formData,
        });

        const data = await res.json();

        clearInterval(interval);
        setProgress(100);

        if (res.ok && data.success) {
          setStatus("Análisis completado ✅");
          // ahora sí pasar al dashboard con datos reales
          onAnalysisComplete(
            data.files?.visualization || "",
            data.statistics || {},
            data.files || {}
          );
        } else {
          console.error("Error al procesar la imagen:", data.error);
          setStatus("Error en el análisis");
          setError(data.error || "Ocurrió un error durante el análisis.");
          // ❌ No avanzamos al dashboard
        }
      } catch (err) {
        clearInterval(interval);
        console.error("Error de conexión con el servidor:", err);
        setStatus("No se pudo conectar al servidor");
        setError("No se pudo conectar al servidor. Intenta nuevamente.");
        // ❌ No avanzamos al dashboard
      }
    };

    sendImage();

    return () => clearInterval(interval);
  }, [file, onAnalysisComplete]);

  return (
    <div className="flex flex-col items-center justify-center text-center p-8 min-h-[400px]">
      <h2 className="text-3xl font-headline mb-4">Paso 2: Análisis en Progreso</h2>
      <p className="text-muted-foreground mb-12 max-w-2xl">
        Nuestra IA está haciendo su magia. Esto puede tardar unos momentos. Por favor, espera mientras procesamos tu imagen y generamos tu reporte de reforestación personalizado.
      </p>

      <div className="w-full max-w-lg space-y-4">
        <Progress value={progress} className="h-4" />
        <div className="flex items-center justify-center text-lg font-medium text-primary">
          {!error && <Loader2 className="mr-2 h-5 w-5 animate-spin" />}
          <p>{status}</p>
        </div>

        {error && (
          <p className="text-red-500 mt-4">
            {error}
          </p>
        )}
      </div>
    </div>
  );
}
