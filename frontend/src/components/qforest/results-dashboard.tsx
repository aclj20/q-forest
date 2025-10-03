"use client";

import * as React from "react";
import Image from "next/image";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, RefreshCw, DollarSign, Leaf, Target, Percent } from "lucide-react";
import metricsData from "@/data/metrics.json";
import { useToast } from "@/hooks/use-toast";
import { ResultsChatbot } from "@/components/qforest/results-chatbot";

interface ResultsDashboardProps {
  onRestart: () => void;
  graphFileName?: string; // <--- nombre dinámico de la imagen, opcional
}

const MetricCard = ({ icon, title, value, unit }: { icon: React.ReactNode; title: string; value: string | number; unit: string }) => (
  <Card className="bg-card/60 border-none shadow-lg backdrop-blur-sm">
    <CardContent className="flex flex-col items-center justify-center p-6 text-center">
      <div className="text-primary mb-3">
        {React.cloneElement(icon as React.ReactElement, { className: "h-10 w-10" })}
      </div>
      <p className="text-4xl font-bold text-foreground">
        {typeof value === "number" ? value.toLocaleString() : value}
        <span className="text-lg font-medium text-muted-foreground ml-1">{unit}</span>
      </p>
      <p className="text-sm font-semibold text-muted-foreground mt-1">{title}</p>
    </CardContent>
  </Card>
);

export function ResultsDashboard({ onRestart, graphFileName }: ResultsDashboardProps) {
  const { toast } = useToast();

  // Generar query param dinámico para forzar recarga de la imagen
  const timestamp = Date.now();
  const graphImageUrl = graphFileName
    ? `/${graphFileName}?t=${timestamp}` // si backend devuelve nombre dinámico
    : `/graph.png?t=${timestamp}`;      // fallback a nombre fijo

  const handleExportCsv = () => {
    const headers = ["Metric", "Value", "Unit"];
    const rows = [
      ["Total Cost", metricsData.totalCost, "USD"],
      ["Potential CO2 Impact", metricsData.potentialCO2Impact, "Tons"],
      ["Optimized Areas", metricsData.optimizedAreas, "Areas"],
      ["Efficiency", metricsData.efficiency, "%"],
    ];

    const csvContent = "data:text/csv;charset=utf-8," + [headers, ...rows].map(e => e.join(",")).join("\n");
    const link = document.createElement("a");
    link.setAttribute("href", encodeURI(csvContent));
    link.setAttribute("download", "qforest_metrics.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    toast({
      title: "Exportación Exitosa",
      description: "Tus métricas se han descargado como CSV.",
    });
  };

  return (
    <div className="p-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8">
        <div>
          <h2 className="text-3xl font-headline">Paso 3: Tu Reporte de Reforestación</h2>
          <p className="text-muted-foreground">Aquí están los resultados de tu análisis.</p>
        </div>
        <div className="flex gap-2 mt-4 sm:mt-0">
          <Button variant="outline" onClick={onRestart} className="bg-background">
            <RefreshCw className="mr-2 h-4 w-4" />
            Comenzar de Nuevo
          </Button>
          <Button size="lg" className="shadow-md" onClick={handleExportCsv}>
            <Download className="mr-2 h-5 w-5" />
            Descargar (CSV)
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
        <div className="lg:col-span-3 space-y-8">
          <Card className="shadow-lg bg-card">
            <CardHeader>
              <CardTitle>Mapa Procesado</CardTitle>
              <CardDescription>Las áreas resaltadas están optimizadas para la reforestación.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="relative aspect-video rounded-lg overflow-hidden border">
                <Image
                  key={graphImageUrl} // fuerza re-render si cambia
                  src={graphImageUrl}
                  alt="Mapa Procesado"
                  fill
                  className="object-cover"
                />
                <div className="absolute inset-0 bg-primary/30 mix-blend-multiply" />
                {/* Mocked highlighted areas */}
                <div className="absolute top-[20%] left-[15%] w-[25%] h-[30%] bg-accent/40 rounded-full blur-md animate-pulse"></div>
                <div className="absolute bottom-[10%] right-[10%] w-[35%] h-[40%] bg-accent/30 rounded-2xl blur-lg animate-pulse delay-500"></div>
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard icon={<DollarSign />} title="Costo Total" value={metricsData.totalCost} unit="USD" />
            <MetricCard icon={<Leaf />} title="Impacto CO2" value={metricsData.potentialCO2Impact} unit="Tons" />
            <MetricCard icon={<Target />} title="Áreas Optimizadas" value={metricsData.optimizedAreas} unit="Áreas" />
            <MetricCard icon={<Percent />} title="Eficiencia" value={metricsData.efficiency} unit="%" />
          </div>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <ResultsChatbot />
        </div>
      </div>
    </div>
  );
}
