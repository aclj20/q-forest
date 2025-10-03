"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { UploadCloud, FileImage, PlayCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { PlaceHolderImages } from "@/lib/placeholder-images";

interface FileUploadProps {
  onStartAnalysis: () => void;
}

export function FileUpload({ onStartAnalysis }: FileUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const { toast } = useToast();
  const forestImage = PlaceHolderImages.find(img => img.id === 'reforestation-area');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (["image/png", "image/jpeg", "image/jpg"].includes(selectedFile.type)) {
        setFile(selectedFile);
        setPreviewUrl(URL.createObjectURL(selectedFile));
        toast({
          title: "Imagen Seleccionada",
          description: `Has seleccionado ${selectedFile.name}.`,
        });
      } else {
        toast({
          variant: "destructive",
          title: "Tipo de Archivo Inválido",
          description: "Por favor, sube una imagen .PNG o .JPG.",
        });
      }
    }
  };

  useEffect(() => {
    // Clean up the object URL to avoid memory leaks
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  return (
    <div className="flex flex-col items-center text-center p-4">
      <h2 className="text-3xl font-headline mb-2">Paso 1: Sube tu Imagen</h2>
      <p className="text-muted-foreground mb-8 max-w-2xl">
        Selecciona una imagen satelital o de dron (.PNG, .JPG) de tu área de interés. Nuestra IA la analizará para identificar zonas óptimas de reforestación.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-4xl">
        <div className="flex flex-col justify-center items-center gap-4">
          <label
            htmlFor="file-upload"
            className="relative flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer bg-secondary/50 hover:bg-secondary transition-colors"
          >
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              <UploadCloud className="w-10 h-10 mb-3 text-primary" />
              <p className="mb-2 text-sm text-muted-foreground">
                <span className="font-semibold text-foreground">Haz clic para subir</span> o arrastra y suelta
              </p>
              <p className="text-xs text-muted-foreground">PNG o JPG</p>
            </div>
            <input id="file-upload" type="file" className="hidden" accept=".png,.jpg,.jpeg" onChange={handleFileChange} />
          </label>
          
          {file && (
            <div className="flex items-center gap-2 p-2 rounded-md bg-secondary text-secondary-foreground w-full">
              <FileImage className="w-5 h-5 text-primary" />
              <span className="text-sm font-medium truncate">{file.name}</span>
            </div>
          )}
        </div>

        <Card className="overflow-hidden shadow-lg bg-card">
          <CardHeader>
            <CardTitle>Vista Previa de la Imagen</CardTitle>
            <CardDescription>Esta es el área a analizar.</CardDescription>
          </CardHeader>
           <div className="relative aspect-[4/3] w-full bg-secondary/30">
              <Image
                  src={previewUrl || forestImage?.imageUrl || 'https://placehold.co/800x600'}
                  alt={previewUrl ? "Vista previa de la imagen subida" : forestImage?.description || "Área de reforestación"}
                  fill
                  className="object-cover"
                  data-ai-hint={forestImage?.imageHint}
              />
          </div>
        </Card>
      </div>

      <Button
        size="lg"
        className="mt-12 group shadow-lg shadow-primary/20"
        onClick={() => file && onStartAnalysis(file)}
        disabled={!file}
      >
        Comenzar Análisis
        <PlayCircle className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
      </Button>
    </div>
  );
}
