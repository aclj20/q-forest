'use server';

/**
 * @fileOverview Generates an initial reforestation analysis summary.
 *
 * - generateInitialAnalysis - A function that creates a starting recommendation.
 * - GenerateInitialAnalysisInput - The input type for the generateInitialAnalysis function.
 * - GenerateInitialAnalysisOutput - The return type for the generateInitialAnalysis function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';
import { googleAI } from '@genkit-ai/google-genai';

const GenerateInitialAnalysisInputSchema = z.object({
  totalCost: z.number().describe('The total cost of the reforestation project in USD.'),
  potentialCO2Impact: z.number().describe('The potential CO2 impact of the reforestation project in tons.'),
  optimizedAreas: z.number().describe('The number of optimized areas in the reforestation project.'),
});
export type GenerateInitialAnalysisInput = z.infer<typeof GenerateInitialAnalysisInputSchema>;

const GenerateInitialAnalysisOutputSchema = z.object({
  analysis: z.string().describe('A detailed initial analysis and recommendation for the reforestation project.'),
});
export type GenerateInitialAnalysisOutput = z.infer<typeof GenerateInitialAnalysisOutputSchema>;

export async function generateInitialAnalysis(input: GenerateInitialAnalysisInput): Promise<GenerateInitialAnalysisOutput> {
  return generateInitialAnalysisFlow(input);
}

const analysisPrompt = ai.definePrompt({
  name: 'initialAnalysisPrompt',
  input: {schema: GenerateInitialAnalysisInputSchema},
  output: {schema: GenerateInitialAnalysisOutputSchema},
  model: googleAI.model('gemini-2.5-flash'),
  prompt: `You are an AI assistant for QForest, providing an initial analysis of a reforestation project.
Based on the following metrics, generate a summary and a recommendation.

Metrics:
- Total Cost: \${{{totalCost}}}
- Potential CO2 Impact: {{{potentialCO2Impact}}} tons
- Optimized Areas: {{{optimizedAreas}}} areas

Your response should follow this structure:
"Para las {{{optimizedAreas}}} áreas optimizadas, se recomienda un patrón de reforestación utilizando [nombre de árbol apropiado para reforestación general, ej. Pino Ponderosa, Roble, etc.]. Este plan proyecta un costo total de \${{{totalCost}}} y un impacto potencial de secuestro de {{{potentialCO2Impact}}} toneladas de CO2. ¿Sobre qué métrica te gustaría profundizar?"

Be specific, helpful, and set the stage for a conversation.`,
});

const generateInitialAnalysisFlow = ai.defineFlow(
  {
    name: 'generateInitialAnalysisFlow',
    inputSchema: GenerateInitialAnalysisInputSchema,
    outputSchema: GenerateInitialAnalysisOutputSchema,
  },
  async input => {
    const {output} = await analysisPrompt(input);
    return output!;
  }
);
