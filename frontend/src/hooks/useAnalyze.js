import { useState, useCallback } from 'react';
import api from '../services/api';
import mockReport from '../utils/mockData';

/**
 * Custom hook for the analyze workflow.
 * Manages loading states, progress steps, error handling.
 *
 * Set useMock=true to use mock data during frontend development.
 */
export function useAnalyze(useMock = true) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);

  const analyze = useCallback(async (repoUrl) => {
    setLoading(true);
    setError(null);
    setReport(null);
    setCurrentStep(0);

    try {
      if (useMock) {
        // Simulate loading steps for demo
        const steps = [0, 1, 2, 3, 4, 5, 6, 7];
        for (const step of steps) {
          setCurrentStep(step);
          await new Promise((r) => setTimeout(r, 600 + Math.random() * 400));
        }
        setReport(mockReport);
      } else {
        // Real API call
        setCurrentStep(1);
        const result = await api.analyzeRepository(repoUrl);
        setReport(result);
      }
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [useMock]);

  const reset = useCallback(() => {
    setReport(null);
    setLoading(false);
    setError(null);
    setCurrentStep(0);
  }, []);

  return { report, loading, error, currentStep, analyze, reset };
}
