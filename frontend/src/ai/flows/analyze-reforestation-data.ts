'use server';

/**
 * @fileOverview A conversational AI flow to answer questions about reforestation metrics.
 *
 * - analyzeReforestationData - A function that answers questions based on reforestation data.
 * - AnalyzeReforestationDataInput - The input type for the analyzeReforestationData function.
 * - AnalyzeReforestationDataOutput - The return type for the analyzeReforestationData function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';
import { googleAI } from '@genkit-ai/google-genai';

const MetricsSchema = z.object({
  totalCost: z.number().describe('The total cost of the reforestation project in USD.'),
  potentialCO2Impact: z.number().describe('The potential CO2 impact of the reforestation project in tons.'),
  optimizedAreas: z.number().describe('The number of optimized areas in the reforestation project.'),
  efficiency: z.number().describe('The efficiency of the reforestation project as a percentage.'),
});

const AnalyzeReforestationDataInputSchema = z.object({
  metrics: MetricsSchema.describe("The key metrics from the reforestation analysis."),
  question: z.string().describe('The user\'s question about the reforestation data.'),
});
export type AnalyzeReforestationDataInput = z.infer<typeof AnalyzeReforestationDataInputSchema>;

const AnalyzeReforestationDataOutputSchema = z.object({
  answer: z.string().describe('A conversational and helpful answer to the user\'s question.'),
});
export type AnalyzeReforestationDataOutput = z.infer<typeof AnalyzeReforestationDataOutputSchema>;


export async function analyzeReforestationData(input: AnalyzeReforestationDataInput): Promise<AnalyzeReforestationDataOutput> {
  return analyzeReforestationDataFlow(input);
}

const chatPrompt = ai.definePrompt({
  name: 'reforestationChatPrompt',
  input: {schema: AnalyzeReforestationDataInputSchema},
  output: {schema: AnalyzeReforestationDataOutputSchema},
  model: googleAI.model('gemini-2.5-flash'),
  prompt: `You are an AI assistant for QForest, specializing in analyzing reforestation project data. Your goal is to answer user questions clearly and concisely based on the provided metrics.

Here are the metrics for the current project analysis:
- Total Cost: \${{{metrics.totalCost}}}
- Potential CO2 Impact: {{{metrics.potentialCO2Impact}}} tons
- Optimized Areas: {{{metrics.optimizedAreas}}}
- Efficiency: {{{metrics.efficiency}}}%

Use this data to answer the following user question. Be friendly and helpful. If the question is unclear or unrelated to the data, ask for clarification.

User Question: "{{{question}}}"`,
});

const analyzeReforestationDataFlow = ai.defineFlow(
  {
    name: 'analyzeReforestationDataFlow',
    inputSchema: AnalyzeReforestationDataInputSchema,
    outputSchema: AnalyzeReforestationDataOutputSchema,
  },
  async (input) => {
    const {output} = await chatPrompt(input);
    return output!;
  }
);
